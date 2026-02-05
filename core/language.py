import spacy
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt', quiet=True)

# Load models (small, cloud-safe)
try:
    nlp_en = spacy.load("en_core_web_sm")
    nlp_hi = spacy.load("hi_core_news_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm", "hi_core_news_sm"], check=False)
    nlp_en = spacy.load("en_core_web_sm")
    nlp_hi = spacy.load("hi_core_news_sm")

def detect_language(text: str) -> str:
    """spaCy-based language detection."""
    doc = nlp_en(text[:500])
    hindi_ratio = sum(1 for token in doc if '\u0900' <= token.text[0] <= '\u097F')
    return "hi" if hindi_ratio / len(doc) > 0.3 else "en"

def get_nlp_pipeline(lang: str):
    """Get spaCy pipeline."""
    return nlp_hi if lang == "hi" else nlp_en
