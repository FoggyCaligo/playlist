import yt_dlp

def down_audio(url):
 ydlOpts = {
  'format': 'bestaudio/best',
  'outtmpl': '%(title)s.%(ext)s',
  'overwrites': True,
  'postprocessors': [{
    'key': 'FFmpegExtractAudio',
    'preferredcodec': 'mp3',
    'preferredquality': '192',
  }],
  'extractor_args': {'youtube': {'player_client': ['web']}},
 }
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
  ydl.download([url])

def down_video(url):
 ydlOpts = {
   'format': 'bestaudio/best',
   'outtmpl': '%(title)s.%(ext)s',
   'overwrites': True,
   'postprocessors': [{
       'key': 'FFmpegExtractAudio',
       'preferredcodec': 'mp4',
       'preferredquality': '192',
   }],
   'extractor_args': {'youtube': {'player_client': ['web']}},
 }
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
    ydl.download([url])


def main():
 print("오디오1/비디오2")
 i = input()
 print("url 입력:")
 if i=="2":
  down_video(input())
 else:
  down_audio(input())
 
 #down_audio(input())

main()
