from pytube import YouTube
from pytube import Playlist
import os

class Download_each:
  def __init__(self,isaudio):
    url = input("유튜브 url 입력 후 엔터 : ")
    yt = YouTube(url)
    try:
      filePath = yt.streams.filter(only_audio=isaudio).first().download()
    except:
      print("error")
      return
    if isaudio==True:
      mp3FilePath = filePath.replace('mp4','mp3')
      os.rename(filePath,mp3FilePath)

class Download_Playlist:
  def __init__(self,isaudio):
    pllink = input("유튜브 플레이리스트 url 입력 후 enter : ")
    pl = Playlist(pllink)

    counter = 1
    for url in pl.video_urls:
      # print(counter,":",len(pl.video_urls)*counter/100)
      print(counter,":",counter/len(pl.video_urls)*100,"%")
      yt = YouTube(url)
      try:
        filePath = yt.streams.filter(only_audio=isaudio).first().download()
      except:
        continue

      if isaudio==True:
        mp3FilePath = filePath.replace('mp4','mp3')
        os.rename(filePath,mp3FilePath)
    counter+=1

#-----------------------------------


isaudio = True

filetype = input("음악파일 다운로드 : 1 입력 후 엔터\n영상파일 다운로드 : 2 입력 후 엔터\n")
if filetype=='1':
    isaudio=True
elif filetype=='2':
    isaudio=False
else:
    print('잘못된 입력!')


type = input("유튜브 단일 영상 다운로드        : 1 입력 후 엔터\n유튜브 플레이리스트 음원 다운로드 : 2 입력 후 엔터\n")
if type=='1':
    downloader = Download_each(isaudio)
elif type=='2':
    downloader = Download_Playlist(isaudio)
else:
    print("잘못된 입력!")
