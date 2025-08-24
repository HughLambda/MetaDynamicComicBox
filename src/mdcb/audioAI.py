import mdcb.util as util
import asyncio
import os
import json
import whisper
import torch
from pyannote.audio import Pipeline
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig
import gc
#------Model Global Variable------#
whisperModel = None
ttsModel = None
diarizationModel = None
diarizationAceessToken = None
#------Main Audio AI trnascription------#
#------Get Audio Sentences------
def getAudioSentences(audio:util.MediaFile,lang:str) -> list[util.AudioSentence]:
    return mergeAudioSentences(
        diarizeAudioFile(audio,diarizationAceessToken),
        transcribeAudioFile(audio,lang,"medium")
    )
    del whisperModel
    del diarizationModel
    gc.collect()
    pass
#------Save Audio Sentences------
def saveAudioSentences(sentences: list[util.AudioSentence],file:util.MediaFile):
    util.saveAudioSentencesToFile(sentences,file.getPath())

#------Merge diarization and segments into AudioSentences------
def mergeAudioSentences(diarization, segments) -> list[util.AudioSentence]:
    audioSentences: list[util.AudioSentence] = []
    # Implement logic to merge diarization and segments into a list of util.AudioSentence
    segmentsRemaining = segments.copy()  # Keep unprocessed segments

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        turnStart = turn.start
        turnEnd = turn.end
        print(f"Matching time segment for speaker {speaker}: {turnStart:.1f}s - {turnEnd:.1f}s")

        # 1. Filter segments within current turn time range
        currentTexts = []
        processedInTurn = 0  # Count segments processed in this turn
        for seg in segmentsRemaining:
            segStart = seg['start']
            segEnd = seg['end']
            
            # Determine if segment overlaps with current turn (core logic)
            # Considered overlapping if segment's end is after turn start AND segment's start is before turn end
            if segEnd > turnStart and segStart < turnEnd:
                currentTexts.append(seg['text'])
                processedInTurn += 1
            else:
                # Since both segments and turns are time-ordered, subsequent segments won't overlap
                break

        # 2. Concatenate text (if there are matching segments)
        if currentTexts:
            fullText = ''.join(currentTexts).strip()  # Concatenate and remove leading/trailing spaces
            # Calculate actual valid duration for this speaker (minimum of turn duration and total text duration)
            textDuration = sum(seg['end'] - seg['start'] for seg in segmentsRemaining[:processedInTurn])
            actualDuration = min(turnEnd - turnStart, textDuration)
            audioSentences.append(util.AudioSentence(actualDuration, speaker, fullText))
            print(f"Matched text: {fullText[:30]}.. (duration: {actualDuration:.2f}s)")
        else:
            print(f"Warning: No matching text for speaker {speaker} in {turnStart:.1f}s - {turnEnd:.1f}s")

        # 3. Remove processed segments (keep unprocessed part to avoid index out of bounds)
        segmentsRemaining = segmentsRemaining[processedInTurn:]
        
    return audioSentences
#------Transcribe:get segments------

def transcribeAudioFile(audio:util.MediaFile,
                        lang:str,
                        modelSize:str):
    global whisperModel
    if whisperModel is None:
        print(f"Loading Whisper model: {modelSize}")
        whisperModel = whisper.load_model(modelSize,dtype=torch.float16)
    print(f"Transcribing audio file: {audio.filePath} with language: {lang}")
    result = whisperModel.transcribe(audio.filePath, language=lang)
    return result["segments"]
#------Diarization:get diarization------
def diarizeAudioFile(audio:util.MediaFile,accessToken:str = diarizationAceessToken):
    global diarizationModel
    if diarizationModel is None:
        print("Loading Diarization model")
        diarizationModel = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=accessToken)
    print(f"Diarizing audio file: {audio.getPath()}")
    diarization = diarizationModel(audio.getPath())
    return diarization




#------TTS:text to audio and save audio------
def ttsInit():
    torch.serialization.add_safe_globals([XttsConfig,XttsAudioConfig,BaseDatasetConfig
                                      ,XttsArgs])
# Get device
#device = "metal" if torch.cuda.is_available() else "cpu"
    device = "mps" if torch.backends.mps.is_available() else "cpu"

# List available 🐸TTS models
    print(TTS().list_models())
# Init TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2",progress_bar=True).to(device)
    return tts

def textToAudioFile(sentence:util.AudioSentence,file:util.MediaFile,speaker:str):
    global ttsModel
    if ttsModel is None:
        print("Loading TTS model")
        ttsModel = ttsInit()
    print(f"Generating speech for text: {sentence.text[:30]}... with speaker:{speaker}")
    ttsModel.tts_to_file(text=sentence.text,speaker=speaker, file_path=file.getPath())
    pass
