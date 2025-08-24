import os
import json

#------Audio Sentence class------

class AudioSentence:    
    """
    A class representing a sentence in an audio file, with start and end times.
    """
    def __init__(self,
                 start: float,
                    end: float,
                      text: str,
                      speaker: str):
        self.start = start
        self.end = end
        self.text = text
        self.speaker = speaker
    def getJson(self) -> str:
        return json.dumps({
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "speaker": self.speaker
        })
#------Audio Sentence Functions------
"""
loadAudioSentencesFromJson: Load a list of AudioSentence objects from a JSON string.
loadAudioSentencesFromFile: Load a list of AudioSentence objects from a JSON file.
saveAudioSentencesToFile: Save a list of AudioSentence objects to a JSON file.
"""
def loadAudioSentencesFromJson(jsonStr: str) -> list[AudioSentence]:
    data = json.loads(jsonStr)
    sentences = []
    for item in data:
        sentence = AudioSentence(
            start=item.get("start", 0.0),
            end=item.get("end", 0.0),
            text=item.get("text", ""),
            speaker=item.get("speaker", "")
        )
        sentences.append(sentence)
    return sentences

def loadAudioSentencesFromFile(filePath: str) -> list[AudioSentence]:
    with open(filePath, 'r', encoding='utf-8') as f:
        jsonStr = f.read()
    return loadAudioSentencesFromJson(jsonStr)

def saveAudioSentencesToFile(sentences: list[AudioSentence], filePath: str):
    data = []
    for sentence in sentences:
        data.append({
            "start": sentence.start,
            "end": sentence.end,
            "text": sentence.text,
            "speaker": sentence.speaker
        })
    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
#------Processing Tag class------

class ProcessingTag:
    """
    A tag to indicate that a certain processing step has been applied to the media file.
    """
    def __init__(self, name: str):
        self.name = name
        pass

#------Media File class------

class MediaFile:
    """
    A class representing a media file with various attributes and processing tags.
    """
    def __init__(self, base: str, title: str, ext: str):
        """
        Ext must include the leading dot, e.g. ".mp4"
        """
        self.base = base
        self.title = title
        self.tags = []
        self.ext = ext
    def addTag(self, tag: ProcessingTag):
        self.tags.append(tag)
    def getNewFile(self, tag: ProcessingTag):
        newFile = MediaFile(self.base, self.title, self.ext)
        newFile.tags = self.tags.copy()
        newFile.addTag(tag)
        return newFile
    def getPath(self) -> str:
        tagText = ""
        for tag in self.tags:
            tagText += f"-{tag.name}"
        return os.path.join(self.base, f"{self.title}{tagText}{self.ext}")