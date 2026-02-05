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
st.title("🤖 Legal Contract Risk Analyzer for SMEs")

# Pure regex language detection
def detect_language(text):
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return "hi" if hindi_chars > len(text) * 0.1 else "en"

# Pure regex clause splitter
def split_clauses(text, lang="en"):
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Legal patterns - English + Hindi
    patterns = [
        r'(?:Section|Clause|Article|धारा|अनुच्छेद)\s*\d+[^.]*?(?=\.|धारा|\n|$)',
        r'\d+\.[^.]*?(?=\.|धारा|\n|$)'
    ]
    
    clauses = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        clauses.extend(matches)
    
    # Fallback sentence split
    if not clauses:
        clauses = re.split(r'(?<=[.?!])\s+', text)
        clauses = [c.strip() for c in clauses if len(c) > 40]
    
    return clauses[:10]

# Enhanced entity extraction
def extract_entities(clause):
    text_lower = clause.lower()
    ip_terms = re.findall(r'intellectual\s+property|IP|ownership|assign|license|exclusive|non-compete|patent|copyright|trademark', clause, re.I)
    money = re.findall(r'₹?\s*[\d,]+\.?\d*\s*(?:lakh|crore)?', clause)
    
    return {
        "IP_TERMS": ip_terms,
        "MONEY": money,
        "risk_keywords": len(re.findall(r'shall|must|exclusive|assign|transfer|terminate|liable', text_lower))
    }

# Smart risk scoring
def calculate_risk(clause):
    score = 0
    text_lower = clause.lower()
    
    # High risk factors
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

# File parsing
def read_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return re.sub(r'\s+', ' ', text).strip()

def get_input_text(mode):
    if mode == "Upload File":
        uploaded = st.file_uploader("📎 Upload Contract (PDF/DOCX/TXT)", type=["pdf", "txt"])
        if uploaded:
            if uploaded.name.endswith('.pdf'):
                return read_pdf(uploaded)
            return uploaded.read().decode("utf-8", errors="ignore")
        return ""
    return st.text_area("📝 Or paste contract text here:", height=300)

# PDF Report Generator
def create_pdf_report(results):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    story = []
    story.append(Paragraph("📄 Legal Contract Risk Analysis Report", styles['Title']))
    story.append(Spacer(1, 20))
    
    total_score = sum(r["score"] for r in results)
    avg_score = total_score / len(results)
    story.append(Paragraph(f"Composite Risk Score: {avg_score:.0f}/100", styles['Heading2']))
    
    for i, r in enumerate(results, 1):
        risk_color = colors.red if r["risk"] == "High" else colors.orange if r["risk"] == "Medium" else colors.green
        story.append(Paragraph(f"Clause {i} - {r['risk']} Risk ({r['score']}/100)", styles['Heading3']))
        story.append(Paragraph(r['clause'][:400] + "..." if len(r['clause']) > 400 else r['clause'], styles['Normal']))
        story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# MAIN UI
st.markdown("---")
mode = st.radio("Choose input method:", ["Upload File", "Paste Text"], horizontal=True)
raw_text = get_input_text(mode)

if st.button("🚀 ANALYZE CONTRACT", use_container_width=True, type="primary") and raw_text.strip():
    if len(raw_text) < 100:
        st.warning("⚠️ Please provide more contract text (100+ characters)")
        st.stop()
    
    # Analysis pipeline
    lang = detect_language(raw_text)
    clauses = split_clauses(raw_text, lang)
    
    if not clauses:
        st.error("❌ No valid clauses detected. Try pasting full contract sections.")
        st.stop()
    
    st.success(f"✅ Language: {'हिंदी' if lang == 'hi' else 'English'} | Clauses found: {len(clauses)}")
    
    results = []
    progress_bar = st.progress(0)
    
    for i, clause in enumerate(clauses, 1):
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"### **Clause {i}**")
                st.metric("Risk Score", f"{calculate_risk(clause)[1]}/100")
            
            with col2:
                st.write(clause[:500] + "..." if len(clause) > 500 else clause)
            
            # Entity extraction
            entities = extract_entities(clause)
            risk_level, score = calculate_risk(clause)
            
            # YOUR EXACT OUTPUT FORMAT
            st.markdown("---")
            st.markdown(f"""
**Ownership:** {'Assigned' if any(t in clause.lower() for t in ['assign', 'transfer']) else 'Retained'}  
**Exclusivity:** {'Exclusive' if 'exclusive' in clause.lower() else 'Shared'}  
**Favor:** {'One-sided' if ('buyer' in clause.lower() and 'seller' in clause.lower()) else 'Balanced'}  
**Risk score (0–100):** **{score}** ({risk_level})
            """)
            
            # **INTELLIGENT RISK EXPLANATION** (YOUR REQUEST)
            risk_explanation = []
            if entities.get('IP_TERMS'):
                risk_explanation.append(f"{len(entities['IP_TERMS'])} IP terms found: {', '.join(entities['IP_TERMS'][:3])}")
            if score >= 60:
                risk_explanation.append("🚨 HIGH RISK: Complete rights/assets transfer to Buyer")
            elif score >= 30:
                risk_explanation.append("⚠️ MEDIUM RISK: Strong obligations or exclusive terms")
            if 'buyer' in clause.lower() and 'seller' in clause.lower():
                risk_explanation.append("⚖️ One-sided: Favors Buyer over Seller")
            if entities.get('MONEY'):
                risk_explanation.append(f"💰 Financial terms: {', '.join(entities['MONEY'][:2])}")
            
            explanation = "; ".join(risk_explanation) if risk_explanation else "✅ Low risk - standard business terms"
            
            st.markdown("**Why this is risky**")
            st.warning(explanation)
            
            st.markdown("**Suggested Fix**")
            if score >= 60:
                st.success("❗ Negotiate IP retention, liability caps, mutual termination rights")
            elif score >= 30:
                st.success("💡 Add time limits to exclusivity, clarify payment terms")
            else:
                st.success("✅ Clause appears balanced - no major changes needed")
            
            results.append({
                "clause": clause, 
                "risk": risk_level, 
                "score": score,
                "entities": entities,
                "explanation": explanation
            })
        
        progress_bar.progress(i / len(clauses))
        st.divider()
    
    # SUMMARY DASHBOARD
    st.header("📊 Contract Summary")
    avg_score = sum(r["score"] for r in results) / len(results)
    high_risk_count = sum(1 for r in results if r["score"] >= 60)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Composite Risk", f"{avg_score:.0f}/100", "🔴 High" if avg_score >= 60 else "🟡 Medium" if avg_score >= 30 else "🟢 Low")
    col2.metric("Clauses Analyzed", len(results))
    col3.metric("High Risk Clauses", high_risk_count)
    col4.metric("Language", "हिंदी" if lang == "hi" else "English")
    
    # Audit trail
    os.makedirs("data", exist_ok=True)
    audit_data = {
        "timestamp": datetime.now().isoformat(),
        "language": lang,
        "clauses_analyzed": len(results),
        "avg_risk_score": avg_score,
        "high_risk_clauses": high_risk_count
    }
    with open("data/audit.json", "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2, ensure_ascii=False)
    
    # PDF Export
    pdf_bytes = create_pdf_report(results)
    st.download_button(
        "📥 Download PDF Report for Lawyer", 
        pdf_bytes, 
        "legal_risk_report.pdf", 
        "application/pdf",
        use_container_width=True
    )
    
    st.balloons()

st.markdown("---")
st.caption("⚖️ For educational use only. Always consult a qualified lawyer for legal advice.")
