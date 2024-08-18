import yt_dlp

def down_audio(url):
 ydlOpts={
<<<<<<< Updated upstream
  'extract_audio': True,
  #"merge_output_format": 'mp3'
  
=======
  'extract_audio':True,
  #"merge_output_format": 'mp3',
>>>>>>> Stashed changes
 }
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
  ydl.download([url])


def down_video(url):
 ydlOpts={
    "format": 'best[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    "merge_output_format": 'mp4',
    "overwrites": True,
 }
 with yt_dlp.YoutubeDL(ydlOpts) as ydl:
  ydl.download([url])



def main():
 print("영상 다운: 1 입력\n음악 다운: 2 입력\n")
 i = input()
 print("url 입력:")
 url = input
 if i == "1" :
  down_video(url)
  print("complete")
 elif i == "2":
  down_audio(url)
  print("complete")
 else:
  print("wrong input")
    
main()





#all about you
#https://youtu.be/gRjO2JJT3qk?si=bKcj448M0WNqDQnn

#test playlist
#https://www.youtube.com/watch?v=gRjO2JJT3qk&list=PLR1UKOR9SpbEZ2fJ82rBAc1oq_rmT6djW
