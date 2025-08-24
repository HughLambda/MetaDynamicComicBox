import os
import subprocess
import mdcb.util as util

#------Download Video Functions------
def downloadVideo(url: str, file: util.MediaFile) -> util.MediaFile:
    file.addTag("raw")
    print(f"Downloading video from {url} to {file.getPath()}...")
    command = ["yt-dlp",
               '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                "-o",file.getPath(),
                  url]
    subprocess.run(command, check=True)
    return file
#------Crop Video Functions------
def cropVideoSubtiles(file: util.MediaFile, ratio: float) -> util.MediaFile:
    print(f"Cropping video {file.getPath()} to ratio {ratio}...")
    if not (0.0 < ratio <= 1.0):
        raise ValueError("Ratio must be between 0.0 and 1.0"
                         " (0.0 exclusive, 1.0 inclusive).")
    inputPath = file.getPath()
    file.addTag("cropped")
    outputPath = file.getPath()
    command = ["ffmpeg",
                "-i", inputPath,
                "-vf", f"crop=iw:iw*{ratio}:0:0",
                "-c:a", "copy",
                outputPath
                ]
    subprocess.run(command, check=True)
    return file
#------Merge Audio and Video Functions------
def mergeAudioVideo(video: util.MediaFile, audio: util.MediaFile) -> util.MediaFile:
    print(f"Merging video {video.getPath()} and audio {audio.getPath()}...")
    inputVideoPath = video.getPath()
    video.addTag("merged")
    outputVideoPath = video.getPath()
    inputAudioPath = audio.getPath()
    #------is this correct?------
    command = ["ffmpeg",
                "-i", inputVideoPath,
                "-i", inputAudioPath,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                outputVideoPath
                ]
    subprocess.run(command, check=True)
    return video    