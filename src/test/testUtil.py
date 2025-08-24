

def testAudioSentence():
    from mdcb.util import AudioSentence
    import json
    text = "Hello, world!"
    audio = AudioSentence(0.0, 1.5, text, "Speaker1")
    audioJson = audio.getJson()
    audioData = json.loads(audioJson)
    assert audioData["start"] == 0.0
    assert isinstance(audio, bytes)
    assert len(audio) > 0
    print("AudioSentence test passed.")