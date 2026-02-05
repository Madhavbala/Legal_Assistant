import streamlit as st
import re
import os
import json
from datetime import datetime
import fitz  # PyMuPDF
import docx
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# spaCy for better clause detection
import spacy
nlp = spacy.blank("en")
nlp.add_pipe("senter")

st.set_page_config(layout="wide", page_title="Legal Analyzer")
st.title("Legal Contract Risk Analyzer")

def detect_language(text):
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return "hi" if hindi_chars > len(text) * 0.1 else "en"

def read_pdf(file):
    """Enhanced PDF extraction"""
    try:
        file.seek(0)
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            page_text = page.get_text()
            text += page_text
        doc.close()
        return re.sub(r'\s+', ' ', text).strip()
    except:
        return ""

def read_docx(file):
    """DOCX extraction"""
    try:
        file.seek(0)
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return re.sub(r'\s+', ' ', text).strip()
    except:
        return ""

def split_clauses(text):
    """spaCy + regex clause extraction"""
    # spaCy sentence splitting
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 30]
    
    # Legal clause patterns
    clauses = []
    patterns = [
        r'(Section|Clause|Article|धारा)\s*\d+[^.]*?(?=\.|Section|Clause|$)',
        r'\d+\.\s*[^.]*?(?=\.|$)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        clauses.extend(matches)
    
    # Combine best results
    all_clauses = clauses + sentences
    unique_clauses = []
    for clause in all_clauses:
        if len(clause) > 40 and clause not in unique_clauses:
            unique_clauses.append(clause)
    
    return unique_clauses[:12]

def extract_entities(clause):
    """Enhanced entity extraction"""
    text_lower = clause.lower()
    
    ip_score = sum(1 for term in ['intellectual property', 'IP', 'ownership', 'assign', 'license', 'exclusive', 
                                 'non-compete', 'patent', 'copyright'] if term in text_lower)
    
    obligation_score = sum(1 for term in ['shall', 'must', 'obligation', 'required', 'liable'] if term in text_lower)
    termination_score = sum(1 for term in ['terminate', 'indemnity'] if term in text_lower)
    
    return {
        "ip_score": ip_score,
        "obligation_score": obligation_score,
        "termination_score": termination_score,
        "ip_terms": re.findall(r'intellectual\s+property|IP|ownership|assign|license|exclusive', clause, re.I),
        "buyer_seller": ('buyer' in text_lower and 'seller' in text_lower)
    }

def calculate_risk(clause, entities):
    """Accurate risk scoring"""
    base_score = 0
    
    # IP Risk (40 points max)
    if entities["ip_score"] >= 2:
        base_score += 40
    elif entities["ip_score"] == 1:
        base_score += 20
    
    # Obligation Risk (30 points max)
    if entities["obligation_score"] >= 2:
        base_score += 30
    elif entities["obligation_score"] == 1:
        base_score += 15
    
    # Termination Risk (20 points max)
    if entities["termination_score"] > 0:
        base_score += 20
    
    # Buyer/Seller imbalance (10 points)
    if entities["buyer_seller"]:
        base_score += 10
    
    score = min(base_score, 100)
    risk_level = "High" if score >= 60 else "Medium" if score >= 30 else "Low"
    return risk_level, score

def get_input_text(mode):
    if mode == "Upload File":
        uploaded = st.file_uploader("Upload Contract", type=["pdf", "docx"], key="file_upload")
        if uploaded is not None:
            st.info(f"Processing: {uploaded.name}")
            
            # Reset file pointer
            uploaded.seek(0)
            
            if uploaded.name.lower().endswith('.pdf'):
                text = read_pdf(uploaded)
            elif uploaded.name.lower().endswith('.docx'):
                text = read_docx(uploaded)
            else:
                text = uploaded.read().decode("utf-8", errors="ignore")
            
            if text.strip():
                st.success(f"Extracted {len(text)} characters")
                return text
            else:
                st.error("No text could be extracted from file")
                return ""
        return ""
    return st.text_area("Paste contract text:", height=300)

def create_pdf_report(results):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    story = []
    story.append(Paragraph("Legal Contract Risk Analysis Report", styles['Title']))
    story.append(Spacer(1, 20))
    
    avg_score = sum(r["score"] for r in results) / len(results)
    story.append(Paragraph(f"Overall Risk Score: {avg_score:.0f}/100", styles['Heading2']))
    
    for i, r in enumerate(results, 1):
        story.append(Paragraph(f"Clause {i}: {r['risk']} Risk ({r['score']}/100)", styles['Heading3']))
        story.append(Paragraph(r['clause'][:300], styles['Normal']))
        story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# MAIN UI
st.markdown("---")
mode = st.radio("Select input:", ["Upload File", "Paste Text"])

raw_text = get_input_text(mode)

if st.button("Analyze Contract", use_container_width=True) and raw_text.strip():
    if len(raw_text) < 100:
        st.warning("Please provide more text (100+ characters)")
        st.stop()
    
    lang = detect_language(raw_text)
    clauses = split_clauses(raw_text)
    
    if not clauses:
        st.error("No clauses detected. Try different text.")
        st.stop()
    
    st.success(f"Language: {'Hindi' if lang=='hi' else 'English'} | Clauses: {len(clauses)}")
    
    results = []
    for i, clause in enumerate(clauses, 1):
        st.markdown(f"**Clause {i}**")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            entities = extract_entities(clause)
            risk_level, score = calculate_risk(clause, entities)
            st.metric("Risk Score", f"{score}/100")
        
        with col2:
            st.write(clause[:600])
        
        # Risk analysis display
        st.markdown("---")
        st.markdown(f"""
**Ownership:** {'Assigned' if entities["ip_score"] > 0 else 'Retained'}  
**Exclusivity:** {'Exclusive' if 'exclusive' in clause.lower() else 'Shared'}  
**Favor:** {'One-sided' if entities["buyer_seller"] else 'Balanced'}  
**Risk score (0-100):** **{score}** ({risk_level})
        """)
        
        # Detailed risk explanation
        explanation_parts = []
        if entities["ip_score"] > 0:
            explanation_parts.append(f"{entities['ip_score']} IP terms detected")
        if entities["obligation_score"] > 0:
            explanation_parts.append(f"{entities['obligation_score']} obligation terms")
        if entities["termination_score"] > 0:
            explanation_parts.append("Termination/indemnity clauses")
        if entities["buyer_seller"]:
            explanation_parts.append("Buyer-Seller imbalance")
        
        explanation = "; ".join(explanation_parts) if explanation_parts else "Standard business terms"
        
        st.markdown("**Why this is risky**")
        st.warning(explanation)
        
        fix_text = "Negotiate IP retention and liability limits" if score >= 60 else \
                  "Add time limits and clarify terms" if score >= 30 else \
                  "Clause appears balanced"
        st.markdown("**Suggested Fix**")
        st.success(fix_text)
        
        results.append({
            "clause": clause,
            "risk": risk_level,
            "score": score,
            "entities": entities
        })
        
        st.markdown("---")
    
    # Summary dashboard
    avg_score = sum(r["score"] for r in results) / len(results)
    col1, col2, col3 = st.columns(3)
    col1.metric("Composite Risk", f"{avg_score:.0f}/100")
    col2.metric("Clauses", len(results))
    col3.metric("High Risk", sum(1 for r in results if r["score"] >= 60))
    
    # Audit log
    os.makedirs("data", exist_ok=True)
    audit_data = {
        "timestamp": datetime.now().isoformat(),
        "clauses": len(results),
        "avg_score": avg_score
    }
    with open("data/audit.json", "w") as f:
        json.dump(audit_data, f, indent=2)
    
    # PDF export
    pdf_bytes = create_pdf_report(results)
    st.download_button("Download PDF Report", pdf_bytes, "report.pdf")

st.markdown("For legal advice, consult qualified counsel.")
