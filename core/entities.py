IP_KEYWORDS = [
    "intellectual property",
    "ownership",
    "assign",
    "license",
    "royalty",
    "exclusive",
    "perpetual"
]

def extract_entities(text):
    found = []
    for k in IP_KEYWORDS:
        if k in text.lower():
            found.append(k)
    return found
