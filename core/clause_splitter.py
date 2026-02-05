import re
import spacy
import streamlit as st


@st.cache_resource(show_spinner=False)
def load_spacy():
    try:
        nlp = spacy.load(
            "en_core_web_sm",
            disable=["ner", "parser", "tagger"]
        )
        nlp.enable_pipe("senter")
        return nlp
    except Exception:
        return None


def split_clauses(text: str, lang: str = "English"):
    if not text or not text.strip():
        return []

    text = re.sub(r"\s+", " ", text).strip()

    if lang.lower() != "english":
        return _fallback(text)

    nlp = load_spacy()
    if nlp is None:
        return _fallback(text)

    doc = nlp(text)

    clauses = []
    current = ""

    LEGAL_START = re.compile(
        r"^(section|clause|article)\s+\d+|\d+\.",
        re.IGNORECASE
    )

    for sent in doc.sents:
        s = sent.text.strip()

        if LEGAL_START.match(s):
            if current.strip():
                clauses.append(current.strip())
            current = s
        else:
            current += " " + s

    if current.strip():
        clauses.append(current.strip())

    return [c for c in clauses if len(c) > 40]


def _fallback(text):
    parts = re.split(r"(?<=\.)\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 40]
