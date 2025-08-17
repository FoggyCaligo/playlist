import yt_dlp

def down_audio(url):
 ydlOpts={
  'format':'bestaudio[ext=m4a]/best[ext=mp3]/best',
  'extract_audio': True,
  'overwrites':True,
  'merge_output_format': 'mp3',
  'outtmpl': '%(title)s.%(ext)s',
 }
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
  ydl.download([url])

#https://youtu.be/_0f5FjEQzsg?si=5Lyx4CSP-yXaEwg0

def down_video(url):
 ydlOpts={
   'format': 'best[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
   'merge_output_format': 'mp4',
   'overwrites': True,
   'outtmpl': '%(title)s.%(ext)s',
 }
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
  ydl.download([url])



def main():
 print("오디오1/비디오2")
 i = input()
 print("url 입력:")
 url = input()
 if i=="2":
  down_video(url)
 else:
  down_audio(url)
 
 #down_audio(input())

main()
