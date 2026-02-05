import streamlit as st
import fitz
import docx

def clean_text(text: str) -> str:
    return " ".join(text.replace("\n", " ").split())

def read_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return clean_text(text)

def read_docx(file):
    document = docx.Document(file)
    return clean_text(" ".join(p.text for p in document.paragraphs))

def read_txt(file):
    return clean_text(file.read().decode("utf-8", errors="ignore"))

def get_input_text(mode: str):
    if mode == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload contract file",
            ["pdf", "docx", "txt"]
        )
        if not uploaded_file:
            return ""

        if uploaded_file.name.endswith(".pdf"):
            return read_pdf(uploaded_file)
        if uploaded_file.name.endswith(".docx"):
            return read_docx(uploaded_file)
        if uploaded_file.name.endswith(".txt"):
            return read_txt(uploaded_file)

        return ""

    return st.text_area("Paste contract text", height=300)
