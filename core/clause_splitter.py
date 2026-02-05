import nltk
from nltk.tokenize import sent_tokenize
from core.entities import extract_entities

def split_clauses(text: str, lang: str = "en") -> list[str]:
    """NLTK sent_tokenize + legal pattern split."""
    # NLTK sentence tokenizer (excellent for legal docs)
    sentences = sent_tokenize(text)
    
    # Legal clause patterns
    import re
    clauses = []
    for sent in sentences:
        if len(sent.strip()) > 30:
            # Split on numbered clauses
            clause_splits = re.split(r'(?i)(?:section|clause|धारा|अनुच्छेद)\s+\d+', sent)
            clauses.extend([cs.strip() for cs in clause_splits if len(cs.strip()) > 40])
    
    if not clauses:
        clauses = [s.strip() for s in sentences if len(s.strip()) > 40][:15]
    
    return clauses
