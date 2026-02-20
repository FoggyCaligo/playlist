import yt_dlp

def down_audio(url, name):
 ydlOpts={
  'format':'bestaudio[ext=m4a]/best[ext=mp3]/best',
  'extract_audio': True,
  'overwrites':True,
  "merge_output_format": 'mp3',
  "outtmpl":"./"+name+".%(ext)s",
  
 }
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
  ydl.download([url])


def down_video(url, name):
 ydlOpts={
    "format": 'best[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    "merge_output_format": 'mp4',
    "overwrites": True,
    
 }
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
  ydl.download([url])



def main():
 print("오디오1/비디오2")
 i = input()
 print("파일명 입력")
 name = input()
 print("url 입력:")
 if i=="2":
  down_video(input(), name)
 else:
  down_audio(input(),  name)
 
 #down_audio(input())

main()
