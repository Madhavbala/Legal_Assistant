# ... (keep existing read_pdf, read_docx, read_txt, get_input_text)

from core.language import get_nlp_pipeline

def preprocess_text(text: str, lang: str) -> str:
    """spaCy lemmatization + cleaning."""
    nlp = get_nlp_pipeline(lang)
    doc = nlp(text)
    return " ".join([token.lemma_.strip() for token in doc if not token.is_stop and not token.is_punct])
