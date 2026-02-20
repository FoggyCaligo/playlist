<start>
1. clone repo
  git clone --depth 1 --single-branch https://github.com/FoggyCaligo/playlist.git
2. download downloader
  winget install yt-dlp



<update>
yt-dlp --update-to master
<update-simple>
yt-dlp --update

<use>
yt-dlp --no-abort-on-error --no-write-thumbnail --paths [TYPES:]./playlist    [OPTIONS] [--] URL [URL...]

<download - single song>
yt-dlp --no-abort-on-error --no-write-thumbnail -P "./playlist"  --audio-format m4a --audio-quality 0 [URL]

<download - playlist>
yt-dlp --no-abort-on-error --no-write-thumbnail --yes-playlist -P "./playlist" --audio-format m4a --audio-quality 0 -t sleep [URL]

<download - video>
yt-dlp --keep-video --no-abort-on-error --no-write-thumbnail --paths [TYPES:]./playlist --audio-format mp4 --audio-quality 0 [URL]
yt-dlp -t mp4 [URL]

<help>
yt-dlp -h
