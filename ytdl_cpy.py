import yt_dlp

def down_audio(url):
 ydlOpts={
  'extract_audio':True,
  #"merge_output_format": 'mp3',
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



def main():
 i = input()
 down_audio(i)
    
main()





#all about you
#https://youtu.be/gRjO2JJT3qk?si=bKcj448M0WNqDQnn

#test playlist
#https://www.youtube.com/watch?v=gRjO2JJT3qk&list=PLR1UKOR9SpbEZ2fJ82rBAc1oq_rmT6djW
