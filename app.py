import streamlit as st
from core.parser import get_input_text
from core.language import detect_language
from core.clause_splitter import split_clauses
from core.llm_engine import analyze_clause_with_llm
from core.risk_engine import calculate_ip_risk
from core.entities import extract_entities
from core.audit import log_audit
from utils.helpers import export_pdf

st.set_page_config(layout="wide")
st.title("📄 Legal Contract Risk Analyzer")

mode = st.radio("Input", ["Upload File", "Paste Text"])
raw_text = get_input_text(mode)

if st.button("🚀 ANALYZE", use_container_width=True) and raw_text.strip():
    lang = detect_language(raw_text)
    clauses = split_clauses(raw_text, lang)[:10]
    
    if not clauses:
        st.error("No clauses found")
        st.stop()
    
    st.success(f"✅ {len(clauses)} clauses | {lang.upper()}")
    
    results = []
    for i, clause in enumerate(clauses, 1):
        with st.container():
            st.markdown(f"**Clause {i}**")
            st.write(clause[:500] + "..." if len(clause) > 500 else clause)
            
            # Analysis
            analysis = analyze_clause_with_llm(clause, lang)
            risk, score = calculate_ip_risk(analysis)
            
            # YOUR EXACT SPEC ✅
            st.markdown("---")
            st.markdown(f"""
**Ownership:** {analysis.get('ownership', 'N/A').title()}  
**Exclusivity:** {analysis.get('exclusivity', 'N/A').title()}  
**Favor:** {analysis.get('favor', 'N/A').title()}  
**Risk score (0–100):** **{score}**
            """)
            
            st.markdown("**Why this is risky**")
            st.warning(analysis.get('risk_reason', 'N/A'))
            
            st.markdown("**Suggested Fix**")
            st.success(analysis.get('suggested_fix', 'N/A'))
            
            results.append({"clause": clause, "analysis": analysis, "risk": risk, "score": score})
        
        st.divider()
    
    # Summary
    avg = sum(r["score"] for r in results) / len(results)
    col1, col2 = st.columns(2)
    col1.metric("Composite Risk", f"{avg:.0f}/100")
    col2.metric("Clauses", len(results))
    
    log_audit(results, lang)
    st.download_button("📥 PDF Report", export_pdf(results), "report.pdf")
