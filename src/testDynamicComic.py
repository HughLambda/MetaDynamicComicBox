import mdcb.util as util
import mdcb.audio as a
import mdcb.video as v
import mdcb.audioAI as audioAI


#------I must think about how to run it in a better way------
#------That I can run it one by one for the hardware limitation------
def testTextToAudio():
    text = util.AudioSentence(
        start=0.0,
        end=5.0,
        speaker="./speakers/thi.wav",
        text="Hello, this is a test of the text to speech functionality.",
        lang="en"
    )
    outputFile = util.MediaFile(
        base="./tmp",
        title="text_to_audio_test",
        ext=".wav"
    )
    audioAI.textToAudioFile(text, outputFile)
    pass
def mainProcess():
    url="https://www.bilibili.com/video/BV1HYmNYkEBv"
    title="fenpeinvyou"
    video = util.MediaFile(
        base="./tmp",
        title=title,
        ext=".mp4"
    )
    videoFile=v.downloadVideo(url,video)
    audio = util.MediaFile(
        base="./tmp",
        title=title,
        ext=".wav"
    )
    audioFile=a.downloadAudio(url,audio)
    audioSentences:list[util.AudioSentence]=audioAI.getAudioSentences(audioFile,lang='zh-cn')
    audioSentenceList:util.MediaFile = util.MediaFile(
        base="./tmp",
        title=title,
        ext=".json"
    )
    audioAI.saveAudioSentences(audioSentences,audioSentenceList)
    pass



if __name__ == "__main__":
    testTextToAudio()