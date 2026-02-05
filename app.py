import streamlit as st
from core.parser import get_input_text, preprocess_text
from core.language import detect_language, get_nlp_pipeline
from core.clause_splitter import split_clauses
from core.llm_engine import analyze_clause_with_llm  # unchanged
from core.risk_engine import calculate_risk
from core.entities import extract_entities, classify_clause_type
from core.audit import log_audit
from utils.helpers import export_pdf  # unchanged

st.set_page_config(page_title="Legal Contract Risk Analyzer", layout="wide")
st.title("🤖 GenAI Legal Assistant for Indian SMEs")

# Sidebar: Contract types & features
st.sidebar.markdown("## 📋 Supported")
st.sidebar.markdown("- Employment, Vendor, Lease, Partnership")
st.sidebar.markdown("- IP/Non-compete/Termination detection")
st.sidebar.markdown("- Hindi + English")
st.sidebar.markdown("- Risk scoring + Fixes")

mode = st.radio("Input Method:", ["Upload File", "Paste Text"])
raw_text = get_input_text(mode)

if st.button("🔍 Analyze Full Contract", use_container_width=True):
    lang = detect_language(raw_text)
    clean_text = preprocess_text(raw_text, lang)
    
    clauses = split_clauses(clean_text, lang)
    if not clauses:
        st.stop()
    
    st.success(f"✅ {len(clauses)} clauses | Language: {'Hindi' if lang=='hi' else 'English'}")
    
    results = []
    progress = st.progress(0)
    
    composite_score = 0
    for i, clause in enumerate(clauses[:12], 1):  # Limit for speed
        with st.expander(f"Clause {i} ({len(clause)} chars)"):
            st.write(clause)
            
            # spaCy processing
            nlp = get_nlp_pipeline(lang)
            doc = nlp(clause)
            
            entities = extract_entities(doc)
            clause_type = classify_clause_type(doc)
            
            # LLM analysis
            analysis = analyze_clause_with_llm(clause, lang)
            risk, score = calculate_risk(analysis, entities, clause_type)
            
            # Problem statement OUTPUT FORMAT
            st.markdown(f"""
            **Ownership:** {analysis.get('ownership', 'N/A').title()}  
            **Exclusivity:** {analysis.get('exclusivity', 'N/A').title()}  
            **Favor:** {analysis.get('favor', 'N/A').title()}  
            **Risk score (0–100):** **{score}** ({risk})
            **Clause Type:** {clause_type.title()}
            **Entities:** Parties: {entities.get('PERSON',[])} | Money: {entities.get('MONEY',[])}
            """)
            
            st.markdown("### Why this is risky")
            st.warning(analysis.get('risk_reason', 'No issues detected'))
            
            st.markdown("### Suggested Fix")
            st.success(analysis.get('suggested_fix', 'Clause appears balanced'))
            
            if entities.get('IP_TERMS'):
                st.info("⚠️ **IP Terms Found**")
            
            results.append({"clause": clause, "analysis": analysis, "risk": risk, "score": score, 
                          "entities": entities, "type": clause_type})
        
        progress.progress(i / len(clauses))
        composite_score += score
    
    # Summary Report
    avg_score = composite_score / len(results)
    st.header("📊 Contract Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Composite Risk", f"{avg_score:.0f}/100", f"{calculate_risk({}, {}, '')[0]}")
    col2.metric("Clauses Analyzed", len(results))
    col3.metric("High Risk Clauses", sum(1 for r in results if r['score'] >= 60))
    
    # Export & Audit
    log_audit(results, lang)
    pdf_bytes = export_pdf(results)
    st.download_button("📥 PDF Report for Lawyer", pdf_bytes, "legal_risk_report.pdf")
    
    st.balloons()
