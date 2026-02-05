import nltk
from nltk.text import TextCollection
from nltk.tokenize import word_tokenize
nltk.download('punkt', quiet=True)

def detect_ambiguity(clause: str) -> str:
    """NLTK-based ambiguity score."""
    tokens = word_tokenize(clause)
    text = TextCollection([clause])
    avg_similarity = sum(text.similarity(' '.join(tokens[:5]), ' '.join(tokens[5:])) for _ in range(3)) / 3
    return "High" if avg_similarity > 0.4 else "Low"

def calculate_risk(analysis: dict, entities: dict, clause_type: str) -> tuple[str, int]:
    """Composite risk scoring."""
    score = 0
    
    # LLM factors (60%)
    if analysis.get("ownership") == "assigned":
        score += 40
    if analysis.get("exclusivity") == "exclusive":
        score += 25
    if analysis.get("favor") == "one-sided":
        score += 20
    
    # Entity risks (20%)
    if entities.get("IP_TERMS"):
        score += 15
    
    # Clause type (10%)
    if clause_type == "prohibition":
        score += 10
    
    # Ambiguity (10%)
    if detect_ambiguity(analysis.get("clause_text", "")) == "High":
        score += 10
    
    score = min(score, 100)
    
    risk_level = "High" if score >= 60 else "Medium" if score >= 30 else "Low"
    return risk_level, score
