import yt_dlp

def down_audio(url):
 ydlOpts={
  'format':'bestaudio[ext=m4a]/best[ext=mp3]/best',
  'extract_audio': True,
  'overwrites':True,
  "merge_output_format": 'mp3',
  
 }
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
  ydl.download([url])


def down_video(url):
 ydlOpts={
    #"format": 'best[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    "format": 'best/best',
    "writesubtitles":'best',
    "writethumbnail":'best' ,
    "overwrites": True,
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
