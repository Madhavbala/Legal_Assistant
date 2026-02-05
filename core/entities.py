import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Keyword lists for clause classification
IP_PATTERNS = [
    r"intellectual\s+property|IP|ownership|assign|license|royalty|exclusive|non-compete",
    r"trade\s+secret|patent|copyright|trademark"
]

OBLIGATION_KW = ["shall", "must", "obligation", "liable", "responsible"]
RIGHT_KW = ["right", "entitled", "may", "permitted"]
PROHIBIT_KW = ["prohibited", "shall not", "cannot", "restrict"]

def extract_entities(text: str) -> dict:
    """Extract entities using regex + NLTK."""
    text_lower = text.lower()
    
    entities = {
        "IP_TERMS": re.findall("|".join(IP_PATTERNS), text, re.I),
        "ORG": re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b(?<!Inc\.|Ltd\.)", text),
        "MONEY": re.findall(r"₹?\s*\d+(?:,\d{3})*(?:\.\d{2})?", text),
        "DATE": re.findall(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", text)
    }
    
    # Clause classification (THE MISSING FUNCTION)
    tokens = word_tokenize(text.lower())
    scores = {"obligation": 0, "right": 0, "prohibition": 0}
    
    for token in tokens:
        if token in OBLIGATION_KW: 
            scores["obligation"] += 1
        if token in RIGHT_KW: 
            scores["right"] += 1
        if token in PROHIBIT_KW: 
            scores["prohibition"] += 1
    
    entities["CLAUSE_TYPE"] = max(scores, key=scores.get)
    
    return entities

def classify_clause_type(text: str) -> str:
    """Classify clause as obligation/right/prohibition."""
    entities = extract_entities(text)
    return entities["CLAUSE_TYPE"]
