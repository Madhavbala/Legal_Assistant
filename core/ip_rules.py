def detect_language(text: str) -> str:
    for c in text:
        if '\u0900' <= c <= '\u097F':
            return "Hindi"
    return "English"
