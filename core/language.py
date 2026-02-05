import spacy
import nltk
import os
from pathlib import Path

# NLTK setup (cloud-safe, no downloads)
nltk_data_path = Path("./nltk_data")
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(str(nltk_data_path))

# Create minimal spaCy pipelines (NO model downloads needed)
nlp_en = spacy.blank("en")
nlp_en.add_pipe("senter")  # Sentence detection only

nlp_hi = spacy.blank("hi")
nlp_hi.add_pipe("senter")

def detect_language(text: str) -> str:
    """Unicode detection for Hindi."""
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return "hi" if hindi_chars > len(text) * 0.1 else "en"

def get_nlp_pipeline(lang: str):
    """Get spaCy pipeline."""
    return nlp_hi if lang == "hi" else nlp_en
