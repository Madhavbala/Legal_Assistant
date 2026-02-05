import re

def split_clauses(text: str, lang: str = "en") -> list[str]:
    """Pure regex clause splitter - NO NLTK dependency."""
    
    if not text or len(text.strip()) < 50:
        return []
    
    # Clean text
    text = re.sub(r'\s+', ' ', text.strip())
    
    if lang == "hi":
        # Hindi legal patterns: धारा, अनुच्छेद, numbers
        patterns = [
            r'धारा\s*\d+[^\.]*(?=\.|धारा|\n|$)',
            r'अनुच्छेद\s*\d+[^\.]*(?=\.|अनुच्छेद|\n|$)',
            r'परिच्छेद\s*\d+[^\.]*(?=\.|धारा|\n|$)',
            r'\d+\.[^\.]*(?=\.|धारा|\n|$)'
        ]
    else:
        # English legal patterns
        patterns = [
            r'(?:Section|Clause|Article)\s*\d+[^\.]*(?=\.|Section|Clause|\n|$)',
            r'\d+\.[^\.]*(?=\.|Section|Clause|\n|$)'
        ]
    
    clauses = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        clauses.extend(matches)
    
    # Fallback: Split by sentences (periods + 30+ chars)
    if not clauses:
        fallback = re.split(r'(?<=[।.?!])\s+', text)
        clauses = [c.strip() for c in fallback if len(c) > 30]
    
    # Limit + clean
    clauses = clauses[:15]
    return [c.strip() for c in clauses if len(c) > 40]
