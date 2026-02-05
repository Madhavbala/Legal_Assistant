import streamlit as st
import re
import os
import json
from datetime import datetime
import fitz  # PyMuPDF
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(layout="wide", page_title="Legal Analyzer")
st.title("Legal Contract Risk Analyzer for SMEs")

def detect_language(text):
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return "hi" if hindi_chars > len(text) * 0.1 else "en"

def split_clauses(text, lang="en"):
    text = re.sub(r'\s+', ' ', text.strip())
    patterns = [
        r'(?:Section|Clause|Article|धारा|अनुच्छेद)\s*\d+[^.]*?(?=\.|धारा|\n|$)',
        r'\d+\.[^.]*?(?=\.|धारा|\n|$)'
    ]
    
    clauses = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        clauses.extend(matches)
    
    if not clauses:
        clauses = re.split(r'(?<=[.?!])\s+', text)
        clauses = [c.strip() for c in clauses if len(c) > 40]
    
    return clauses[:10]

def extract_entities(clause):
    text_lower = clause.lower()
    ip_terms = re.findall(r'intellectual\s+property|IP|ownership|assign|license|exclusive|non-compete|patent|copyright|trademark', clause, re.I)
    money = re.findall(r'₹?\s*[\d,]+\.?\d*\s*(?:lakh|crore)?', clause)
    
    return {
        "IP_TERMS": ip_terms,
        "MONEY": money,
        "risk_keywords": len(re.findall(r'shall|must|exclusive|assign|transfer|terminate|liable', text_lower))
    }

def calculate_risk(clause):
    score = 0
    text_lower = clause.lower()
    
    if any(word in text_lower for word in ['assign', 'transfer', 'exclusive', 'perpetual']):
        score += 40
    if any(word in text_lower for word in ['shall', 'must', 'obligation']):
        score += 25
    if 'buyer' in text_lower and 'seller' in text_lower:
        score += 20
    if any(word in text_lower for word in ['terminate', 'indemnity', 'non-compete']):
        score += 15
    
    score = min(score, 100)
    risk_level = "High" if score >= 60 else "Medium" if score >= 30 else "Low"
    return risk_level, score

# **FIXED PDF UPLOAD FUNCTION**
def read_pdf(file):
    """Robust PDF reading with error handling"""
    try:
        # Reset file pointer
        file.seek(0)
        
        # Open with PyMuPDF
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                page_text = page.get_text()
                if page_text.strip():  # Only add non-empty pages
                    text += page_text + "\n"
        
        # Clean and return
        cleaned_text = re.sub(r'\s+', ' ', text.strip())
        return cleaned_text if cleaned_text else "No readable text found in PDF"
    
    except Exception as e:
        return f"PDF reading error: {str(e)}"

def get_input_text(mode):
    if mode == "Upload File":
        uploaded = st.file_uploader("Upload Contract (PDF)", type=["pdf"], key="pdf_upload")
        if uploaded is not None:
            st.info(f"File uploaded: {uploaded.name} ({uploaded.size} bytes)")
            text = read_pdf(uploaded)
            st.success("PDF processed successfully")
            return text
        return ""
    return st.text_area("Paste contract text:", height=300, key="text_area")

def create_pdf_report(results):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    story = []
    story.append(Paragraph("Legal Contract Risk Analysis Report", styles['Title']))
    story.append(Spacer(1, 20))
    
    total_score = sum(r["score"] for r in results)
    avg_score = total_score / len(results)
    story.append(Paragraph(f"Composite Risk Score: {avg_score:.0f}/100", styles['Heading2']))
    
    for i, r in enumerate(results, 1):
        story.append(Paragraph(f"Clause {i} - {r['risk']} Risk ({r['score']}/100)", styles['Heading3']))
        story.append(Paragraph(r['clause'][:400] + "..." if len(r['clause']) > 400 else r['clause'], styles['Normal']))
        story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# MAIN UI
st.markdown("---")
mode = st.radio("Input method:", ["Upload File", "Paste Text"])
raw_text = get_input_text(mode)

if st.button("Analyze Contract", use_container_width=True) and raw_text.strip():
    if len(raw_text) < 100:
        st.warning("Please provide more contract text (100+ characters)")
        st.stop()
    
    lang = detect_language(raw_text)
    clauses = split_clauses(raw_text, lang)
    
    if not clauses:
        st.error("No valid clauses detected.")
        st.stop()
    
    st.success(f"Language: {'Hindi' if lang == 'hi' else 'English'} | Clauses found: {len(clauses)}")
    
    results = []
    for i, clause in enumerate(clauses, 1):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"Clause {i}")
            risk_level, score = calculate_risk(clause)
            st.metric("Risk Score", f"{score}/100")
        
        with col2:
            st.write(clause[:500] + "..." if len(clause) > 500 else clause)
        
        entities = extract_entities(clause)
        risk_explanation = []
        
        if entities.get('IP_TERMS'):
            risk_explanation.append(f"{len(entities['IP_TERMS'])} IP terms: {', '.join(entities['IP_TERMS'][:3])}")
        if score >= 60:
            risk_explanation.append("HIGH RISK: Complete rights/assets transfer")
        elif score >= 30:
            risk_explanation.append("MEDIUM RISK: Exclusive obligations")
        if 'buyer' in clause.lower() and 'seller' in clause.lower():
            risk_explanation.append("One-sided: Favors Buyer")
        if entities.get('MONEY'):
            risk_explanation.append(f"Financial terms: {', '.join(entities['MONEY'][:2])}")
        
        explanation = "; ".join(risk_explanation) if risk_explanation else "Low risk - standard terms"
        
        st.markdown("---")
        st.markdown(f"""
**Ownership:** {'Assigned' if any(t in clause.lower() for t in ['assign', 'transfer']) else 'Retained'}  
**Exclusivity:** {'Exclusive' if 'exclusive' in clause.lower() else 'Shared'}  
**Favor:** {'One-sided' if ('buyer' in clause.lower() and 'seller' in clause.lower()) else 'Balanced'}  
**Risk score (0-100):** **{score}** ({risk_level})
        """)
        
        st.markdown("**Why this is risky**")
        st.warning(explanation)
        
        st.markdown("**Suggested Fix**")
        if score >= 60:
            st.success("Negotiate IP retention, liability caps, mutual termination rights")
        elif score >= 30:
            st.success("Add time limits to exclusivity, clarify payment terms")
        else:
            st.success("Clause appears balanced")
        
        results.append({
            "clause": clause, 
            "risk": risk_level, 
            "score": score,
            "entities": entities,
            "explanation": explanation
        })
        
        st.divider()
    
    # Summary
    avg_score = sum(r["score"] for r in results) / len(results)
    col1, col2, col3 = st.columns(3)
    col1.metric("Composite Risk", f"{avg_score:.0f}/100")
    col2.metric("Clauses Analyzed", len(results))
    col3.metric("High Risk Clauses", sum(1 for r in results if r["score"] >= 60))
    
    # Audit
    os.makedirs("data", exist_ok=True)
    audit_data = {
        "timestamp": datetime.now().isoformat(),
        "language": lang,
        "clauses_analyzed": len(results),
        "avg_risk_score": avg_score
    }
    with open("data/audit.json", "w") as f:
        json.dump(audit_data, f, indent=2)
    
    # PDF
    pdf_bytes = create_pdf_report(results)
    st.download_button("Download PDF Report", pdf_bytes, "report.pdf")

st.markdown("For legal advice, consult a qualified lawyer.")
