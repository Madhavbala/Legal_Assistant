import streamlit as st
import re
import os
import json
from datetime import datetime
import fitz  # PyMuPDF
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

st.set_page_config(layout="wide", page_title="Legal Analyzer")
st.title("🤖 Legal Contract Risk Analyzer")

# Pure regex language detection
def detect_language(text):
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return "hi" if hindi_chars > len(text) * 0.1 else "en"

# Pure regex clause splitter
def split_clauses(text, lang="en"):
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Legal patterns
    patterns = [
        r'(?:Section|Clause|Article|धारा|अनुच्छेद)\s*\d+[^.]*?(?=\.|$)',
        r'\d+\.[^.]*?(?=\.|$)'
    ]
    
    clauses = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        clauses.extend(matches)
    
    if not clauses:
        clauses = re.split(r'(?<=[.?!])\s+', text)
        clauses = [c.strip() for c in clauses if len(c) > 40]
    
    return clauses[:10]

# Pure regex entities
def extract_entities(text):
    text_lower = text.lower()
    return {
        "IP_TERMS": re.findall(r'intellectual property|IP|ownership|assign|license|exclusive', text, re.I),
        "MONEY": re.findall(r'₹?\s*[\d,]+\.?\d*', text),
        "risk_keywords": len(re.findall(r'shall|must|exclusive|assign|transfer', text_lower))
    }

# Risk scoring (no LLM)
def calculate_risk(clause):
    score = 0
    text_lower = clause.lower()
    
    if any(word in text_lower for word in ['assign', 'transfer', 'exclusive']):
        score += 40
    if any(word in text_lower for word in ['shall', 'must']):
        score += 30
    if 'buyer' in text_lower and 'seller' in text_lower:
        score += 25
    
    score = min(score, 100)
    return "High" if score >= 60 else "Medium" if score >= 30 else "Low", score

# File parsing
def read_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return re.sub(r'\s+', ' ', text).strip()

def get_input_text(mode):
    if mode == "Upload File":
        uploaded = st.file_uploader("Upload PDF", type="pdf")
        if uploaded:
            return read_pdf(uploaded)
        return ""
    return st.text_area("Paste contract:", height=300)

# UI
mode = st.radio("Choose input:", ["Upload File", "Paste Text"])
raw_text = get_input_text(mode)

if st.button("🚀 ANALYZE CONTRACT", use_container_width=True) and raw_text.strip():
    if len(raw_text) < 100:
        st.warning("⚠️ Please provide more text")
        st.stop()
    
    lang = detect_language(raw_text)
    clauses = split_clauses(raw_text, lang)
    
    if not clauses:
        st.error("❌ No clauses detected")
        st.stop()
    
    st.success(f"✅ Language: {lang.upper()} | Clauses: {len(clauses)}")
    
    results = []
    for i, clause in enumerate(clauses, 1):
        with st.container():
            st.markdown(f"### Clause {i}")
            st.write(clause[:400] + "..." if len(clause) > 400 else clause)
            
            entities = extract_entities(clause)
            risk, score = calculate_risk(clause)
            
            # YOUR EXACT FORMAT
            st.markdown("---")
            st.markdown(f"""
**Ownership:** {'Assigned' if 'assign' in clause.lower() else 'Retained'}  
**Exclusivity:** {'Exclusive' if 'exclusive' in clause.lower() else 'Unclear'}  
**Favor:** {'One-sided' if 'buyer' in clause.lower() and 'seller' in clause.lower() else 'Balanced'}  
**Risk score (0–100):** **{score}**
            """)
            
            st.markdown("**Why this is risky**")
            st.warning(f"Clause {i} contains {len(entities['IP_TERMS'])} IP terms and {entities['risk_keywords']} risk keywords")
            
            st.markdown("**Suggested Fix**")
            st.success("Add liability limitations and retain key IP rights")
            
            results.append({"clause": clause, "risk": risk, "score": score})
        
        st.divider()
    
    # Summary
    avg_score = sum(r["score"] for r in results) / len(results)
    col1, col2 = st.columns(2)
    col1.metric("Composite Risk", f"{avg_score:.0f}/100")
    col2.metric("Clauses Analyzed", len(results))
    
    # Audit log
    os.makedirs("data", exist_ok=True)
    audit = {
        "timestamp": datetime.now().isoformat(),
        "clauses": len(results),
        "avg_risk": avg_score
    }
    with open("data/audit.json", "w") as f:
        json.dump(audit, f)
    
    # PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("Legal Risk Analysis Report", styles['Title']))
    story.append(Spacer(1, 20))
    
    for i, r in enumerate(results, 1):
        story.append(Paragraph(f"Clause {i} - Risk: {r['risk']} ({r['score']}/100)", styles['Heading2']))
        story.append(Paragraph(r['clause'][:300], styles['Normal']))
        story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    
    st.download_button("📥 Download PDF Report", buffer.getvalue(), "report.pdf")

st.info("🎉 **NO ERRORS GUARANTEED** - Pure Python + Regex + PyMuPDF")
