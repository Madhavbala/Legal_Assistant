import re

def split_clauses(text: str, lang: str = "en"):
    """
    Split legal contract text into clauses.
    Supports English and Hindi using rule-based logic.
    Streamlit Cloud safe (no spaCy model loading).
    """

    if not text or not text.strip():
        return []

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    clauses = []

    if lang == "hi":
        # Hindi legal markers
        patterns = [
            r"धारा\s+\d+",
            r"अनुच्छेद\s+\d+",
            r"\d+\.",
            r"\(\d+\)"
        ]
    else:
        # English legal markers
        patterns = [
            r"Section\s+\d+",
            r"Clause\s+\d+",
            r"Article\s+\d+",
            r"\d+\.",
            r"\(\d+\)"
        ]

    combined_pattern = "(" + "|".join(patterns) + ")"

    splits = re.split(combined_pattern, text)

    current = ""
    for part in splits:
        if re.match(combined_pattern, part):
            if current.strip():
                clauses.append(current.strip())
            current = part
        else:
            current += " " + part

    if current.strip():
        clauses.append(current.strip())

    # Fallback if splitting fails
    if not clauses:
        clauses = [p.strip() for p in text.split(".") if len(p.strip()) > 30]

    return clauses
