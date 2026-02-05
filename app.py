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

st.set_page_config(layout="wide", page_title="Legal Analyzer")
st.title("Legal Contract Risk Analyzer")

def detect_language(text):
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return "hi" if hindi_chars > len(text) * 0.1 else "en"

def read_pdf(file):
    """Better PDF extraction"""
    try:
        file.seek(0)
        doc = fitz.open(stream=file.read(), filetype="pdf")
        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            full_text += page_text + "\n"
        doc.close()
        return re.sub(r'\s+', ' ', full_text.strip())
    except:
        return ""

def read_docx(file):
    try:
        file.seek(0)
        doc = docx.Document(file)
        full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return re.sub(r'\s+', ' ', full_text.strip())
    except:
        return ""

def split_clauses(text):
    """FIXED: Better clause extraction - full sentences around section headers"""
    # Find section headers
    section_patterns = [
        r'(?:ARTICLE|Section|Clause)\s*\d+\.?\s*[^.!?]{10,300}',
        r'(?:धारा|अनुच्छेद)\s*\d+\.?\s*[^.!?]{10,300}',
        r'\d+\.\s*[^.!?]{20,400}'
    ]
    
    clauses = []
    for pattern in section_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if len(match) > 50:
                clauses.append(match.strip())
    
    # Fallback: meaningful sentences
    if len(clauses) < 5:
        sentences = re.split(r'(?<=[\.?!])\s+', text)
        for sent in sentences:
            if any(keyword in sent.lower() for keyword in ['shall', 'must', 'buyer', 'seller', 'transfer', 'assign', 'exclusive']):
                if 60 < len(sent) < 800:
                    clauses.append(sent.strip())
    
    # Remove duplicates and limit
    unique_clauses = []
    for clause in clauses[:15]:
        if clause not in unique_clauses and len(clause) > 80:
            unique_clauses.append(clause)
    
    return unique_clauses[:10]

def extract_entities(clause):
    """FIXED: Better entity detection"""
    text_lower = clause.lower()
    
    # IP/Legal terms (more specific)
    ip_terms = re.findall(r'\b(?:intellectual property|IP rights?|ownership|assign|license|exclusive|non-compete|patent|copyright|trademark)\b', clause, re.I)
    obligations = re.findall(r'\b(?:shall|must|obligation|required|liable|responsible)\b', clause, re.I)
    
    # Real money amounts only
    money = re.findall(r'[\$₹€]\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?', clause)
    
    buyer_seller = 'buyer' in text_lower and 'seller' in text_lower
    
    return {
        "ip_terms": ip_terms,
        "obligations": obligations,
        "money": money,
        "buyer_seller": buyer_seller,
        "ip_count": len(ip_terms),
        "obligation_count": len(obligations)
    }

def calculate_risk(clause, entities):
    """FIXED: Proper risk scoring"""
    score = 0
    
    # IP Transfer Risk (highest)
    if entities["ip_count"] >= 1 or any(word in clause.lower() for word in ['transfer', 'assign', 'convey']):
        score += 35
    
    # Strong obligations
    if entities["obligation_count"] >= 2:
        score += 25
    elif entities["obligation_count"] == 1:
        score += 15
    
    # Buyer/Seller imbalance
    if entities["buyer_seller"]:
        score += 20
    
    # Termination/penalty clauses
    if any(word in clause.lower() for word in ['terminate', 'indemnify', 'penalty']):
        score += 15
    
    # Exclusive language
    if 'exclusive' in clause.lower():
        score += 10
    
    score = min(score, 100)
    risk_level = "High" if score >= 60 else "Medium" if score >= 35 else "Low"
    return risk_level, score

def get_input_text(mode):
    if mode == "Upload File":
        uploaded = st.file_uploader("Upload Contract", type=["pdf", "docx"], key="file_upload")
        if uploaded is not None:
            st.info(f"File: {uploaded.name} ({uploaded.size:,} bytes)")
            
            uploaded.seek(0)
            if uploaded.name.lower().endswith('.pdf'):
                text = read_pdf(uploaded)
            elif uploaded.name.lower().endswith('.docx'):
                text = read_docx(uploaded)
            else:
                text = uploaded.read().decode("utf-8")
            
            if text.strip():
                st.success(f"Extracted {len(text):,} characters")
                st.text_area("Extracted text preview:", text[:1000], height=100)
                return text
            else:
                st.error("Could not extract text from file")
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
    story.append(Paragraph(f"Overall Risk: {avg_score:.0f}/100", styles['Heading2']))
    
    for i, r in enumerate(results, 1):
        story.append(Paragraph(f"Clause {i}: {r['risk']} ({r['score']}/100)", styles['Heading3']))
        story.append(Paragraph(r['clause'][:400], styles['Normal']))
        story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# MAIN UI
st.markdown("---")
mode = st.radio("Input:", ["Upload File", "Paste Text"])
raw_text = get_input_text(mode)

if st.button("Analyze Contract", use_container_width=True) and raw_text.strip():
    if len(raw_text) < 200:
        st.warning("Need more text (200+ characters)")
        st.stop()
    
    lang = detect_language(raw_text)
    clauses = split_clauses(raw_text)
    
    if not clauses:
        st.error("No clauses found. Try full contract sections.")
        st.stop()
    
    st.success(f"Language: {'Hindi' if lang == 'hi' else 'English'} | Clauses: {len(clauses)}")
    
    results = []
    for i, clause in enumerate(clauses, 1):
        st.markdown(f"**Clause {i}** ({len(clause)} chars)")
        
        # Show FULL clause text
        with st.expander(f"View full clause text ({len(clause)} characters)"):
            st.write(clause)
        
        col1, col2 = st.columns([1, 4])
        with col1:
            entities = extract_entities(clause)
            risk_level, score = calculate_risk(clause, entities)
            st.metric("Risk Score", f"{score}/100")
        
        with col2:
            st.info(clause[:300] + "..." if len(clause) > 300 else clause)
        
        # Analysis display
        st.markdown("---")
        st.markdown(f"""
**Ownership:** {'Assigned' if entities["ip_count"] > 0 or 'transfer' in clause.lower() else 'Retained'}  
**Exclusivity:** {'Exclusive' if 'exclusive' in clause.lower() else 'Shared'}  
**Favor:** {'One-sided' if entities["buyer_seller"] else 'Balanced'}  
**Risk score (0-100):** **{score}** ({risk_level})
        """)
        
        # DETAILED risk explanation
        explanation = []
        if entities["ip_count"] > 0:
            explanation.append(f"{entities['ip_count']} IP/legal terms: {', '.join(entities['ip_terms'][:2])}")
        if entities["obligation_count"] > 0:
            explanation.append(f"{entities['obligation_count']} obligation terms")
        if entities["buyer_seller"]:
            explanation.append("Buyer vs Seller - potential imbalance")
        if entities["money"]:
            explanation.append(f"Financial terms detected")
        
        risk_msg = "; ".join(explanation) if explanation else "Standard commercial terms"
        
        st.markdown("**Why this is risky**")
        st.warning(risk_msg)
        
        # Specific fixes
        if score >= 60:
            st.markdown("**Suggested Fix**")
            st.success("Negotiate IP retention, liability caps, mutual termination rights")
        elif score >= 35:
            st.markdown("**Suggested Fix**")
            st.success("Add time limits, clarify obligations, balance terms")
        else:
            st.markdown("**Suggested Fix**")
            st.success("Terms appear reasonable")
        
        results.append({"clause": clause, "risk": risk_level, "score": score, "entities": entities})
        st.divider()
    
    # Summary
    avg_score = sum(r["score"] for r in results) / len(results)
    col1, col2, col3 = st.columns(3)
    col1.metric("Composite Risk", f"{avg_score:.0f}/100")
    col2.metric("Clauses", len(results))
    col3.metric("High Risk", sum(1 for r in results if r["score"] >= 60))
    
    # PDF Export
    pdf_bytes = create_pdf_report(results)
    st.download_button("Download PDF Report", pdf_bytes, "report.pdf")

st.markdown("For legal advice, consult qualified counsel.")
