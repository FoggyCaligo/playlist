import yt_dlp

def down_audio(url):
 ydlOpts={
  'extract_audio':True,
  "merge_output_format": 'mp3',
  
 }
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
  ydl.download([url])


def down_video(url):
 ydlOpts={
    "format": f'best[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    "merge_output_format": 'mp4',
    "overwrites": True,
 }
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
  ydl.download([url])


def down_video2(url):
 ydlOpts={}
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
  ydl.download([url])


def main():
 print("오디오1/비디오2")
 i = input()
 print("url 입력:")
 rl= input()
 if i==1:
  down_audio(rl)
 elif i==2:
  down_video(rl)


main()
