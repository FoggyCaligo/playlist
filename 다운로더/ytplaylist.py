import os
import yt_dlp

COMMON_OPTS = {
    # 브라우저 쿠키가 있으면 자동으로 사용
    # 파일이 없으면 옵션이 무시되어도 무방
    'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,

    # 최신 브라우저 UA 흉내 (간혹 필요)
    'http_headers': {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/129.0.0.0 Safari/537.36'),
        'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
    },

    # YouTube 추출기 설정: web 우선, 안되면 android 시도
    'extractor_args': {
        'youtube': {
            'player_client': ['web', 'android', 'ios', 'mweb'],
            # 문제시 다음도 시도해볼 수 있음:
            # 'skip': ['dash', 'configs']  # 특정 구성 우회
        }
    },

    # Windows 파일명 안전 + 중복 구분
    'outtmpl': '%(title).100s [%(id)s].%(ext)s',
    'overwrites': True,

    # 재시도
    'retries': 10,
    'fragment_retries': 10,
    'extractor_retries': 5,
    'ignoreerrors': 'only_download',  # 일부 실패 시 계속
}

def down_audio(url: str):
    ydl_opts = {
        **COMMON_OPTS,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def down_video(url: str):
    ydl_opts = {
        **COMMON_OPTS,
        # 최상 화질 비디오+오디오 병합 → mp4 시도
        'format': 'bv*+ba/best',
        'merge_output_format': 'mp4',
        # 필요 시 mp4 선호(웹m만 있으면 웹m로 저장될 수 있음)
        'prefer_free_formats': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def main():
    print("오디오1/비디오2")
    mode = input().strip()
    print("url 입력:")
    url = input().strip()
    try:
        if mode == "2":
            down_video(url)
        else:
            down_audio(url)
    except yt_dlp.utils.DownloadError as e:
        print("\n[다운로드 오류 감지]\n", e)
        print("\n대처 팁:")
        print("1) yt-dlp 최신 업데이트 여부 확인")
        print("2) 브라우저 쿠키 cookies.txt 적용(로그인 필요 영상/제한 영상)")
        print("3) extractor_args.youtube.player_client에 ['web','android','ios'] 등 추가")
        print("4) 동일 오류가 지속되면 해당 영상 자체가 앱/임베드 제한일 수 있음(웹으로만 재생 허용)")

if __name__ == "__main__":
    main()
