#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
duplicates_report.csv 생성기 (Chromaprint fpcalc 기반)
- 앞/뒤 몇 초 트림/추가에도 강한 중복 후보 탐지 (fingerprint shingle Jaccard)
- 출력: 중복 후보 쌍 + 유사도 + 그룹ID(Union-Find)

요구사항:
- fpcalc (Chromaprint) 가 PATH에 있어야 함
"""

#test
# fpcalc -version

#fail : 다운로드
# winget install chromaprint

#succees : 사용 cmd 
# python reporter.py "C:\Users\user\Music\playlist" --out duplicates_report.csv --threshold 0.28 --min-shared 40 --dur-ratio-min 0.70 --dur-ratio-max 1.35

# python reporter.py "../" --out duplicates_report.csv --threshold 0.45 --min-shared 100 --dur-ratio-min 0.75 --dur-ratio-max 1.30


from __future__ import annotations

import argparse
import csv
import hashlib
import os
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Set, Iterable


AUDIO_EXTS_DEFAULT = {
    ".opus", ".webm", ".m4a", ".mp3", ".flac", ".wav", ".ogg", ".aac", ".mp4", ".mkv"
}


@dataclass
class AudioItem:
    idx: int
    path: Path
    duration: float
    fp: List[int]
    shingles: Set[int]


class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            self.parent[ra] = rb
        elif self.rank[ra] > self.rank[rb]:
            self.parent[rb] = ra
        else:
            self.parent[rb] = ra
            self.rank[ra] += 1


def run_fpcalc(file_path: Path, fpcalc: str) -> Tuple[float, List[int]]:
    """
    fpcalc -raw 출력 파싱:
      DURATION=123
      FINGERPRINT=1,2,3,4,...
    """
    try:
        proc = subprocess.run(
            [fpcalc, "-raw", str(file_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        raise RuntimeError(
            f"fpcalc를 찾을 수 없음: '{fpcalc}'\n"
            f"PATH에 fpcalc.exe를 추가하거나 --fpcalc 경로를 지정해줘."
        )

    if proc.returncode != 0:
        raise RuntimeError(
            f"fpcalc 실패({proc.returncode}): {file_path}\n"
            f"stderr: {proc.stderr.strip()}"
        )

    duration = None
    fp_str = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("DURATION="):
            duration = float(line.split("=", 1)[1])
        elif line.startswith("FINGERPRINT="):
            fp_str = line.split("=", 1)[1]

    if duration is None or fp_str is None:
        raise RuntimeError(
            f"fpcalc 출력 파싱 실패: {file_path}\nstdout:\n{proc.stdout}"
        )

    # fingerprint는 int 리스트(콤마 구분)
    fp = []
    # 일부 파일에서 fp가 매우 길 수 있음 -> split 성능 고려
    for s in fp_str.split(","):
        s = s.strip()
        if s:
            try:
                fp.append(int(s))
            except ValueError:
                # 혹시 모를 이상치 방어
                continue

    if len(fp) < 50:
        raise RuntimeError(f"fingerprint가 너무 짧음(지원 안되는 포맷일 수 있음): {file_path}")

    return duration, fp


def shingle_hashes(fp: List[int], k: int, step: int) -> Set[int]:
    """
    fingerprint int 시퀀스에서 k-그램을 만들고,
    안정적인 64-bit 해시로 변환하여 set으로 반환.
    - step을 2~4로 두면 메모리/속도 절약
    """
    if k <= 0:
        raise ValueError("k는 1 이상이어야 함")
    if step <= 0:
        raise ValueError("step은 1 이상이어야 함")
    n = len(fp)
    if n < k:
        return set()

    out: Set[int] = set()
    # k-그램 tuple을 바로 해싱하면 느려질 수 있어서 bytes로 직렬화
    # fpcalc fingerprint는 int 범위가 비교적 작지만 안전하게 4바이트로 pack-like 처리
    # 여기선 단순히 str join 후 blake2b를 사용(충분히 빠르고 구현 간단)
    for i in range(0, n - k + 1, step):
        chunk = fp[i:i+k]
        # "1,2,3,..." 문자열은 비용이 있지만 k가 작고 step이 있어서 감당 가능
        s = ",".join(map(str, chunk)).encode("utf-8")
        h = hashlib.blake2b(s, digest_size=8).digest()  # 64-bit
        out.add(int.from_bytes(h, "little"))
    return out


def iter_audio_files(root: Path, exts: Set[str]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def jaccard(a: Set[int], b: Set[int]) -> float:
    if not a or not b:
        return 0.0
    # 작은 쪽 기준으로 교집합 계산
    if len(a) > len(b):
        a, b = b, a
    inter = sum(1 for x in a if x in b)
    union = len(a) + len(b) - inter
    return inter / union if union else 0.0


def build_candidates(items: List[AudioItem], min_shared_shingles: int) -> Dict[Tuple[int, int], int]:
    """
    inverted index(shingle -> 파일들)로 후보쌍을 만들고
    공유 shingle 개수(교집합 근사)를 카운팅.
    """
    inv: Dict[int, List[int]] = defaultdict(list)
    for it in items:
        for sh in it.shingles:
            inv[sh].append(it.idx)

    pair_shared: Dict[Tuple[int, int], int] = defaultdict(int)

    for sh, ids in inv.items():
        if len(ids) < 2:
            continue
        ids.sort()
        # 같은 shingle을 공유하는 파일들끼리 pair 카운트
        for i in range(len(ids)):
            a = ids[i]
            for j in range(i + 1, len(ids)):
                b = ids[j]
                pair_shared[(a, b)] += 1

    # 너무 약한 후보는 제거
    pair_shared = {k: v for k, v in pair_shared.items() if v >= min_shared_shingles}
    return pair_shared


def main():
    ap = argparse.ArgumentParser(description="Generate duplicates_report.csv using fpcalc fingerprints.")
    ap.add_argument("root", type=str, help="음원 폴더 경로 (재귀 스캔)")
    ap.add_argument("--out", type=str, default="duplicates_report.csv", help="출력 CSV 파일명")
    ap.add_argument("--fpcalc", type=str, default="fpcalc", help="fpcalc 실행파일 이름 또는 경로")
    ap.add_argument("--exts", type=str, default=",".join(sorted(AUDIO_EXTS_DEFAULT)),
                    help="스캔 확장자 목록 (콤마 구분). 예: .opus,.m4a,.mp3")
    ap.add_argument("--k", type=int, default=10, help="shingle 길이(k-그램). 기본 10")
    ap.add_argument("--step", type=int, default=2, help="shingle 샘플링 간격. 기본 2 (1이면 더 정확, 느림/메모리↑)")
    ap.add_argument("--threshold", type=float, default=0.35,
                    help="Jaccard 유사도 임계값(0~1). 기본 0.35")
    ap.add_argument("--min-shared", type=int, default=60,
                    help="후보쌍으로 고려할 최소 공유 shingle 수. 기본 60 (파일 길이에 따라 조정)")
    ap.add_argument("--dur-ratio-min", type=float, default=0.80,
                    help="길이 비율 하한(짧/긴). 기본 0.80")
    ap.add_argument("--dur-ratio-max", type=float, default=1.25,
                    help="길이 비율 상한(짧/긴). 기본 1.25")
    ap.add_argument("--max-files", type=int, default=0,
                    help="디버깅용: 0이면 제한 없음, N이면 처음 N개만 처리")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"폴더가 존재하지 않음: {root}", file=sys.stderr)
        sys.exit(1)

    exts = {e.strip().lower() for e in args.exts.split(",") if e.strip()}
    if not exts:
        exts = set(AUDIO_EXTS_DEFAULT)

    files = sorted(iter_audio_files(root, exts))
    if args.max_files and args.max_files > 0:
        files = files[:args.max_files]

    if not files:
        print("대상 오디오 파일이 없음.", file=sys.stderr)
        sys.exit(1)

    items: List[AudioItem] = []
    errors: List[Tuple[str, str]] = []

    print(f"스캔 파일 수: {len(files)}")
    print("fingerprint 생성 중... (fpcalc)")

    for i, f in enumerate(files):
        try:
            dur, fp = run_fpcalc(f, args.fpcalc)
            sh = shingle_hashes(fp, k=args.k, step=args.step)
            items.append(AudioItem(idx=i, path=f, duration=dur, fp=fp, shingles=sh))
        except Exception as e:
            errors.append((str(f), str(e)))

        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(files)} 처리됨...")

    if not items:
        print("fingerprint 생성에 성공한 파일이 없음.", file=sys.stderr)
        for p, err in errors[:20]:
            print(f"- {p}: {err}", file=sys.stderr)
        sys.exit(1)

    print(f"fingerprint 성공: {len(items)}개, 실패: {len(errors)}개")
    print("중복 후보 생성 중(인버티드 인덱스)...")
    pair_shared = build_candidates(items, min_shared_shingles=args.min_shared)

    print(f"후보쌍 수(공유 shingle>= {args.min_shared}): {len(pair_shared)}")
    print("유사도 계산 및 필터링...")

    uf = UnionFind(len(items))
    rows = []

    for (a, b), shared in pair_shared.items():
        ia, ib = items[a], items[b]
        # 길이 비율 필터 (앞뒤 몇 초 차이만 허용)
        short = min(ia.duration, ib.duration)
        long = max(ia.duration, ib.duration)
        ratio = (short / long) if long > 0 else 0.0
        if ratio < args.dur_ratio_min or ratio > args.dur_ratio_max:
            continue

        sim = jaccard(ia.shingles, ib.shingles)
        if sim >= args.threshold:
            uf.union(a, b)
            rows.append({
                "file_a": str(ia.path),
                "file_b": str(ib.path),
                "duration_a_sec": f"{ia.duration:.2f}",
                "duration_b_sec": f"{ib.duration:.2f}",
                "duration_ratio_short_over_long": f"{ratio:.3f}",
                "shared_shingles_count": shared,
                "jaccard_similarity": f"{sim:.4f}",
                "decision": "DUPLICATE_CANDIDATE",
            })

    # group id 부여
    root_to_gid: Dict[int, int] = {}
    gid_counter = 1
    for r in rows:
        # rows는 pair 기반이라 대표 그룹 id를 pair의 a 기준으로 붙임
        # (필요하면 사후에 파일별 그룹 테이블을 따로 출력할 수 있음)
        a_idx = None
        # file_a 경로에서 idx 역매핑 (간단히 items에서 찾기)
        # 성능 위해 dict를 만들자
    path_to_idx = {str(it.path): it.idx for it in items}
    for r in rows:
        a_idx = path_to_idx.get(r["file_a"])
        if a_idx is None:
            continue
        root_id = uf.find(a_idx)
        if root_id not in root_to_gid:
            root_to_gid[root_id] = gid_counter
            gid_counter += 1
        r["group_id"] = root_to_gid[root_id]

    out_path = Path(args.out).expanduser().resolve()
    print(f"CSV 저장: {out_path}")

    fieldnames = [
        "group_id",
        "file_a", "file_b",
        "duration_a_sec", "duration_b_sec",
        "duration_ratio_short_over_long",
        "shared_shingles_count",
        "jaccard_similarity",
        "decision",
    ]

    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in sorted(rows, key=lambda x: (x["group_id"], -float(x["jaccard_similarity"]))):
            w.writerow(r)

    # 에러 로그도 같이 남김
    if errors:
        err_path = out_path.with_suffix(".errors.csv")
        with err_path.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["file", "error"])
            w.writerows(errors)
        print(f"에러 로그 저장: {err_path}")

    print("완료.")
    print(f"중복 후보(임계값 통과): {len(rows)}개")
    print("팁: threshold(기본 0.35) / min-shared(기본 60) / dur-ratio 범위를 조정해 정확도 튜닝 가능.")


if __name__ == "__main__":
    main()
