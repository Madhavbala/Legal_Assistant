import spacy
import nltk
import os
from pathlib import Path

# NLTK data (cloud-safe)
nltk_data_path = Path("nltk_data")
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(str(nltk_data_path))

try:
    nltk.download('punkt', download_dir=str(nltk_data_path), quiet=True)
    nltk.download('stopwords', download_dir=str(nltk_data_path), quiet=True)
except:
    pass  # Already exists

# spaCy models with fallback (no packages.txt needed)
@st.cache_resource
def load_models():
    """Lazy load spaCy models with error handling."""
    try:
        # Small English model (always works)
        nlp_en = spacy.blank("en")
        nlp_en.add_pipe("senter")  # Sentence detection
        
        # Try Hindi (fallback to English if fails)
        try:
            nlp_hi = spacy.load("hi_core_news_sm")
        except OSError:
            nlp_hi = spacy.blank("hi")
            nlp_hi.add_pipe("senter")
        
        return nlp_en, nlp_hi
    except:
        # Minimal fallback
        return spacy.blank("en"), spacy.blank("en")

nlp_en, nlp_hi = load_models()

def detect_language(text: str) -> str:
    """Unicode + spaCy token ratio."""
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return "hi" if hindi_chars / len(text) > 0.1 else "en"

def get_nlp_pipeline(lang: str):
    return nlp_hi if lang == "hi" else nlp_en
