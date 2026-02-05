import streamlit as st
import fitz  # PyMuPDF
import docx
from core.language import get_nlp_pipeline

def clean_text(text: str) -> str:
    """Clean extracted text."""
    text = text.replace("\n", " ").replace("\t", " ")
    return " ".join(text.split())

def read_pdf(file) -> str:
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return clean_text(text)

def read_docx(file) -> str:
    document = docx.Document(file)
    text = " ".join([p.text for p in document.paragraphs])
    return clean_text(text)

def read_txt(file) -> str:
    text = file.read().decode("utf-8", errors="ignore")
    return clean_text(text)

def get_input_text(mode: str) -> str:
    """Handle file upload or text input."""
    if mode == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload contract (PDF/DOCX/TXT)", 
            type=["pdf", "docx", "txt"]
        )
        if uploaded_file is None:
            return ""

        filename = uploaded_file.name.lower()
        try:
            if filename.endswith(".pdf"):
                return read_pdf(uploaded_file)
            elif filename.endswith(".docx"):
                return read_docx(uploaded_file)
            elif filename.endswith(".txt"):
                return read_txt(uploaded_file)
            else:
                st.error("❌ Unsupported format")
                return ""
        except Exception as e:
            st.error(f"❌ File error: {e}")
            return ""
    else:
        return st.text_area("Paste contract text:", height=300)

def preprocess_text(text: str, lang: str) -> str:
    """Simple cleaning (no heavy lemmatization)."""
    nlp = get_nlp_pipeline(lang)
    doc = nlp(text)
    # Remove stopwords/punctuation only
    tokens = [token.text for token in doc if not token.is_punct and len(token.text) > 2]
    return " ".join(tokens)
