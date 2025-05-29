import whisper
import spacy
import re
import os

# Load Whisper model and spaCy model once
model = whisper.load_model("base")
nlp = spacy.load("en_core_web_sm")

def transcribe_audio(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]