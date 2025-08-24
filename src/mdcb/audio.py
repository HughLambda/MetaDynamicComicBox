import mdcb.util as util
import json
import subprocess
import os


#------Get Media info------
def getMediaInfo(file: util.MediaFile) -> json:
    try:
        result = subprocess.run(
            ['ffprobe',
             '-v',
             'quiet',
             '-print_format',
             'json',
             '-show_format',
             '-show_streams',
             file.getPath()],
             stderr=subprocess.STDOUT,
             text=True
        )
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error getting media info: {e}")
        return {}
    pass
#------merge audio files------
def mergeAudioFiles(files: list[util.MediaFile], file: util.MediaFile) -> util.MediaFile:
    """
    Merge multiple audio files into a single file
    
    Parameters:
        files: List of audio files to be merged (MediaFile objects)
        file: Base media file used to generate output file path
        
    Returns:
        Merged audio file (MediaFile object)
    """
    # Print list of audio file paths being merged
    print(f"Merging audio files {[file.getPath() for file in files]}")
    
    # Get paths for all input files
    inputPaths = [file.getPath() for file in files]
    
    # Create output file object, generate new file named "merged" based on base file
    outputFile = file.getNewFile("merged")
    
    # Check if all input files exist
    for f in inputPaths:
        if not os.path.exists(f):
            raise FileNotFoundError(f"Audio file not exist: {f}")
    
    # Create temporary list file for FFmpeg concatenation
    tmpListFile: util.MediaFile = file.getNewFile("list")
    tmpListFile.ext = ".txt"
    
    # Write file paths to temporary list file (required for FFmpeg concat)
    with open(tmpListFile.getPath(), "w", encoding="utf-8") as f:
        for path in inputPaths:
            path = os.path.abspath(path) # Escape single quotes in path  
            f.write(f"file '{path}'\n")
    
    # FFmpeg command to concatenate audio files
    cmd = [
        "ffmpeg",
        "-f", "concat",          # Use concat demuxer
        "-safe", "0",            # Allow absolute file paths
        "-i", tmpListFile.getPath(),  # Input list file
        "-c", "copy",            # Copy streams without re-encoding
        outputFile.getPath()     # Output file path
    ]
    cmd.insert(1, "-y")
    
    try:
        # Execute FFmpeg command
        subprocess.run(
            cmd,
            check=True,            # Raise error if command fails # Merge stdout and stderr
            text=True              # Return output as string
        )
    except subprocess.CalledProcessError as e:
        print(f"Error merging audio files: {e}")
        raise e
    finally:
        # Clean up temporary list file
        if os.path.exists(tmpListFile.getPath()):
            os.remove(tmpListFile.getPath())
    
    return outputFile
#------Get Media Duration------
def getMediaDuration(file: util.MediaFile) -> float:
    if not os.path.exists(file.getPath()):
        raise FileNotFoundError(f"Media file not exist: {file.getPath()}")
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        file.getPath()
    ]
    try:
        result = subprocess.run(
            cmd,
            check=True,  # Raise error if command fails
            text=True,   # Return output as string
            capture_output=True  # Capture stdout and stderr
        )
        info = json.loads(result.stdout)
        if "format" in info and "duration" in info["format"]:
            return float(info["format"]["duration"])
        else:
            raise ValueError("Duration not found in media info")
    except subprocess.CalledProcessError as e:
        print(f"Error getting media duration: {e}")
        raise e
    pass
#------Merge Audio With Loop BGM------
def mergeAudioLoopBGM(audio: util.MediaFile,bgm: util.MediaFile,volume: float) -> util.MediaFile:
    audioDuration = getMediaDuration(audio)
    bgmDuration = getMediaDuration(bgm)
    loopCount = max(1,int(audioDuration // bgmDuration) + 1)
    print(f"Audio duration: {audioDuration}, BGM duration: {bgmDuration}, Loop count: {loopCount}")
    bgmFiles =[]
    bgmFilters = []
    for i in range(loopCount):
        bgmFiles.append(f"-i {bgm.getPath()}")
        bgmFilters.append(f"[{i+1}:a]volume={volume}[bgm{i}]")
    if loopCount > 1:
        mergeFilter = "".join([f"[bgm{i}]" for i in range(loopCount)])
        mergeFilter += f"concat=n={loopCount}:v=0:a=1[bgm_merged]"
        bgmFilters.append(mergeFilter)
    else:
        bgmFilters.append("[bgm0]asplit[bgm_merged]")
        pass
    bgmFilters.append(f"[bgm_merged]atrim=0:{audioDuration},apad=whole_dur={audioDuration}[bgm]")
    mainFilter = f"[0:a]volume={1},atrim=0:{audioDuration}[main]"
    
    finalFilter = f"[main][bgm]amerge=inputs=2[a]"
    
    allFilters = ";".join([mainFilter] + bgmFilters + [finalFilter])
    cmd = [
        'ffmpeg',
        '-i', audio.getPath()  # 主音频输入
    ]
    # 添加所有BGM输入
    for _ in range(loopCount):
        cmd.extend(['-i', bgm.getPath()])
    outputFile = audio.getNewFile("bgmMerged")
    cmd.extend([
        '-filter_complex', allFilters,
        '-map', '[a]',
        '-c:a', 'pcm_s16le',  # WAV格式
        '-y',  # 覆盖现有文件
        outputFile.getPath()
    ])
    try:
        subprocess.run(
            cmd,
            check=True,  # Raise error if command fails
            text=True    # Return output as string
        )
        return outputFile
    except subprocess.CalledProcessError as e:
        print(f"Error merging audio with BGM: {e}")
        raise e
    pass
#------Download Audio------
def downloadAudio(url: str, file: util.MediaFile) -> util.MediaFile:
    print(f"Downloading audio from {url} to {file.getPath()}")
    if not os.path.exists(file.base):
        os.makedirs(file.base)
    file = file.getNewFile("raw")
    cmd = [
        "yt-dlp",
        "-k",  # Extract audio only
        "-f", "ba",
        "--extract-audio",
        "--audio-format", "wav",  # Convert to mp3
        "--audio-quality", "0",  # Best quality
        "-o", file.getPath(),  # Output file path
        url
    ]
    print(f"Running command: {' '.join(cmd)}")
    try:
        subprocess.run(
            cmd,
            check=True,  # Raise error if command fails
            text=True    # Return output as string
        )
    except subprocess.CalledProcessError as e:
        print(f"Error downloading audio: {e}")
        raise e
    return file
    pass
#------Adjust Audio Duration------
def adjustAudioDuration(audio: util.MediaFile, duration: float) -> util.MediaFile:
    originDuration = getMediaDuration(audio)
    if originDuration is None:
        raise ValueError("Could not get audio duration")
    if originDuration <= 0:
        raise ValueError("Audio duration is zero or negative")
    speed = originDuration / duration
    print(f"Adjusting audio duration from {originDuration} to {duration}, speed: {speed}")
    outputFile = audio.getNewFile("durationAdjusted")
    cmd = [
        "ffmpeg",
        "-i", audio.getPath(),
        "-filter:a", f"atempo={speed}",
        "-vn",
        "-y",  # Overwrite output file if exists
        outputFile.getPath()
    ]
    try:
        subprocess.run(
            cmd,
            check=True,  # Raise error if command fails
            text=True    # Return output as string
        )
        return outputFile
    except subprocess.CalledProcessError as e:
        print(f"Error adjusting audio duration: {e}")
        raise e
    pass