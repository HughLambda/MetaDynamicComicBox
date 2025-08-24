import mdcb.audio as audio
import mdcb.util as util


def testMergeAudioFiles():
    baseAudio = util.MediaFile(
        base="./tmp",
        title="shangsanxiusi_en",
        ext=".wav"
    )
    audioFiles = [
        util.MediaFile(
            base="./tmp",
            title=f"shangsanxiusi_en_{i}",
            ext=".wav"
        ) for i in range(0, 27)
    ]
    mergedFile = audio.mergeAudioFiles(audioFiles, baseAudio)
    pass

if __name__ == "__main__":
    testMergeAudioFiles()
