import yt_dlp

def down_audio(url):
 ydlOpts={
  'extract_audio': True,
  #"merge_output_format": 'mp3'
  
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
 down_audio(input())

main()
