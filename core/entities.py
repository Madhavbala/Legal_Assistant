import re

def extract_entities(text: str) -> dict:
    """Pure regex entity extraction."""
    text_lower = text.lower()
    
    return {
        "IP_TERMS": re.findall(r'intellectual\s+property|IP|ownership|assign|license|exclusive|non-compete|patent|copyright', text, re.I),
        "ORG": re.findall(r'\b[A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z]{2,})?\b', text),
        "MONEY": re.findall(r'₹?\s*[\d,]+\.?\d*\s*(?:lakh|crore|thousand)?', text),
        "DATE": re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text),
        "CLAUSE_TYPE": "obligation"  # Default
    }

def classify_clause_type(text: str) -> str:
    """Simple keyword classification."""
    text_lower = text.lower()
    if any(word in text_lower for word in ['shall', 'must', 'obligation']):
        return "obligation"
    elif any(word in text_lower for word in ['right', 'entitled', 'may']):
        return "right"
    elif any(word in text_lower for word in ['prohibited', 'cannot', 'restrict']):
        return "prohibition"
    return "neutral"
