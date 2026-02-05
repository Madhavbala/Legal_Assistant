def detect_language(text: str) -> str:
    # Simple heuristic: Hindi characters present?
    for c in text:
        if '\u0900' <= c <= '\u097F':
            return "Hindi"
    return "English"
