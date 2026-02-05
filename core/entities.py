import re
from nltk.corpus import stopwords
nltk.download('stopwords', quiet=True)

IP_KEYWORDS = ["intellectual property", "IP", "ownership", "assign", "license", "royalty", "exclusive", "non-compete"]
OBLIGATION_KEYWORDS = ["shall", "must", "obligation", "responsible", "liable"]
RIGHT_KEYWORDS = ["right", "entitled", "may", "permission"]
PROHIBITION_KEYWORDS = ["prohibited", "shall not", "cannot", "restrict"]

STOP_WORDS = set(stopwords.words('english'))

def extract_entities(doc):
    """spaCy NER + keyword extraction."""
    entities = {"ORG": [], "PERSON": [], "DATE": [], "MONEY": [], "GPE": [], "IP_TERMS": []}
    
    for ent in doc.ents:
        entities[ent.label_].append(ent.text)
    
    text_lower = doc.text.lower()
    for kw in IP_KEYWORDS:
        if kw.lower() in text_lower:
            entities["IP_TERMS"].append(kw)
    
    return entities

def classify_clause_type(doc):
    """Obligation/Right/Prohibition via NLTK keywords."""
    text = doc.text.lower()
    scores = {"obligation": 0, "right": 0, "prohibition": 0}
    
    for kw in OBLIGATION_KEYWORDS:
        scores["obligation"] += text.count(kw)
    for kw in RIGHT_KEYWORDS:
        scores["right"] += text.count(kw)
    for kw in PROHIBITION_KEYWORDS:
        scores["prohibition"] += text.count(kw)
    
    return max(scores, key=scores.get)
