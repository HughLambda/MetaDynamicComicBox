import mdcb.util as util
import mdcb.video as v


def testMergeAudioVideo():
    video: util.MediaFile = util.MediaFile(
        base="./tmp",
        title="nanjing",
        ext=".mp4")
    audio: util.MediaFile = util.MediaFile(
        base="./tmp",
        title="nanjing",
        ext=".wav")
    videoMerged = v.mergeAudioVideo(video, audio)
    print("Merged video:", videoMerged.getPath())
    pass


if __name__ == "__main__":
    testMergeAudioVideo()