import re

def split_clauses(text: str, lang: str = "en"):
    if not text or not text.strip():
        return []

    text = re.sub(r"\s+", " ", text).strip()
    clauses = []

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

    if not clauses:
        clauses = [p.strip() for p in text.split(".") if len(p.strip()) > 30]

    return clauses
