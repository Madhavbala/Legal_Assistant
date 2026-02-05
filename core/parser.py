# core/parser.py

import streamlit as st
import fitz  # PyMuPDF
import docx


def clean_text(text: str) -> str:
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
    """
    Handles BOTH file upload and pasted text.
    Returns clean text or empty string.
    """

    if mode == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload contract file",
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
                st.error("Unsupported file format")
                return ""

        except Exception as e:
            st.error(f"File read error: {e}")
            return ""

    else:
        return st.text_area(
            "Or paste contract text here",
            height=300
        )
