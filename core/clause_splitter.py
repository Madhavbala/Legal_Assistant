import nltk
from core.language import get_nlp_pipeline

nltk.download('punkt', quiet=True)

def split_clauses(text: str, lang: str = "en") -> list[str]:
    """spaCy sentence detection + regex fallback."""
    nlp = get_nlp_pipeline(lang)
    
    # spaCy sentence splitting (accurate for legal docs)
    doc = nlp(text)
    clauses = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 40]
    
    if len(clauses) < 3:
        # Fallback regex
        import re
        patterns = [r"\d+\.", r"Section\s+\d+", r"धारा\s+\d+"] if lang == "en" else [r"धारा\s+\d+", r"\d+\."]
        clauses = re.split("|".join(patterns), text)
        clauses = [c.strip() for c in clauses if len(c.strip()) > 40][:20]
    
    return clauses
