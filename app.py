import streamlit as st

# Safe imports with error handling
try:
    from core.parser import get_input_text
    from core.language import detect_language
    from core.clause_splitter import split_clauses
    from core.llm_engine import analyze_clause_with_llm
    from core.risk_engine import calculate_ip_risk
    from core.entities import extract_entities, classify_clause_type  # NOW FIXED
    from core.audit import log_audit
    from utils.helpers import export_pdf
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.stop()

st.set_page_config(page_title="Legal Contract Risk Analyzer", layout="wide")
st.title("🤖 GenAI Legal Assistant for Indian SMEs")

st.sidebar.markdown("## 📋 Features")
st.sidebar.markdown("- IP/Non-compete detection")
st.sidebar.markdown("- Hindi + English")
st.sidebar.markdown("- Risk scoring 0-100")
st.sidebar.markdown("- PDF export")

mode = st.radio("Input:", ["Upload File", "Paste Text"], horizontal=True)
raw_text = get_input_text(mode)

if st.button("🚀 Analyze Contract", use_container_width=True) and raw_text.strip():
    if len(raw_text) < 50:
        st.warning("⚠️ Need more text")
        st.stop()
    
    lang = detect_language(raw_text)
    clauses = split_clauses(raw_text, lang)
    clauses = [c for c in clauses if len(c) > 40][:12]
    
    if not clauses:
        st.error("❌ No clauses found")
        st.stop()
    
    st.success(f"✅ {lang.upper()} | {len(clauses)} clauses")
    
    results = []
    progress = st.progress(0)
    
    for i, clause in enumerate(clauses, 1):
        with st.expander(f"Clause {i}"):
            st.write(clause[:400])
            
            # NLP Analysis
            entities = extract_entities(clause)
            clause_type = classify_clause_type(clause)  # NOW WORKS
            
            # LLM Analysis
            analysis = analyze_clause_with_llm(clause, lang)
            risk_level, score = calculate_ip_risk(analysis)
            
            # EXACT OUTPUT FORMAT YOU WANTED
            st.markdown(f"""
            **Ownership:** {analysis.get('ownership', 'N/A').title()}  
            **Exclusivity:** {analysis.get('exclusivity', 'N/A').title()}  
            **Favor:** {analysis.get('favor', 'N/A').title()}  
            **Risk score (0–100):** **{score}**
            """)
            
            st.markdown("### Why this is risky")
            st.warning(analysis.get('risk_reason', 'No risk detected'))
            
            st.markdown("### Suggested Fix")
            st.success(analysis.get('suggested_fix', 'OK as is'))
            
            if entities.get('IP_TERMS'):
                st.info(f"⚠️ IP Terms: {', '.join(entities['IP_TERMS'])}")
            
            results.append({
                "clause": clause, "analysis": analysis, 
                "risk": risk_level, "score": score,
                "entities": entities, "type": clause_type
            })
        
        progress.progress(i/len(clauses))
    
    # Summary + Export
    avg_score = sum(r["score"] for r in results) / len(results)
    col1, col2 = st.columns(2)
    col1.metric("Avg Risk Score", f"{avg_score:.0f}/100")
    col2.metric("Clauses", len(results))
    
    log_audit(results, lang)
    pdf_bytes = export_pdf(results)
    st.download_button("📥 Download PDF", pdf_bytes, "contract_analysis.pdf")
