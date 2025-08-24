

def testAudioSentence():
    from mdcb.util import AudioSentence
    import json
    text = "Hello, world!"
    audio = AudioSentence(0.0, 1.5, text, "Speaker1")
    audioJson = audio.getJson()
    audioData = json.loads(audioJson)
    assert audioData["start"] == 0.0
    print(audioJson)
    print(audioData)
    print("audio datas")
    audioDataSet = [audioData for _ in range(3)]
    audioDataSetJson = json.dumps(audioDataSet, ensure_ascii=False)
    print(audioDataSetJson)
    audioDataSet2 = json.loads(audioDataSetJson)
    print(audioDataSet2[0])
    print("AudioSentence test passed.")
    import mdcb.util as util
    sentences = util.loadAudioSentencesFromJson(audioDataSetJson)
    for s in sentences:
        print(s.getJson())
    util.saveAudioSentencesToFile(sentences, "test_sentences.json")
    print("Saved to test_sentences.json")
    sentences2 = util.loadAudioSentencesFromFile("test_sentences.json")
    print("Loaded from test_sentences.json")
    for s in sentences2:
        print(s.getJson())
    pass

if __name__ == "__main__":
    testAudioSentence()