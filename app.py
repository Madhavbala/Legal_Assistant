import streamlit as st

from core.parser import get_input_text
from core.language import detect_language
from core.clause_splitter import split_clauses
from core.llm_engine import analyze_clause_with_llm
from core.risk_engine import calculate_ip_risk
from utils.helpers import export_pdf

st.set_page_config(page_title="Legal Contract Risk Analyzer", layout="wide")
st.title("Legal Contract Risk Analyzer")

mode = st.radio("Input Mode", ["Upload File", "Paste Text"], horizontal=True)
raw_text = get_input_text(mode)

if st.button("Analyze Contract", use_container_width=True):

    if not raw_text or len(raw_text.strip()) < 50:
        st.warning("Please provide a valid contract.")
        st.stop()

    lang = detect_language(raw_text)
    st.success(f"Detected language: {lang}")

    clauses = split_clauses(raw_text, lang)

    if not clauses:
        st.error("No clauses detected.")
        st.stop()

    results = []

    for i, clause in enumerate(clauses, 1):
        st.subheader(f"Clause {i}")
        st.write(clause)

        analysis = analyze_clause_with_llm(clause, lang)
        risk_level, risk_score = calculate_ip_risk(analysis)

        st.markdown(f"""
**Ownership:** {analysis["ownership"].title()}  
**Exclusivity:** {analysis["exclusivity"].title()}  
**Favor:** {analysis["favor"].title()}  
**Risk score (0–100):** {risk_score}
""")

        st.markdown("### Why this is risky")
        st.write(analysis["risk_reason"])

        st.markdown("### Suggested Fix")
        st.write(analysis["suggested_fix"])

        results.append({
            "clause": clause,
            "analysis": analysis,
            "risk": risk_level,
            "score": risk_score
        })

        st.divider()

    pdf = export_pdf(results)
    st.download_button(
        "Download PDF Report",
        pdf,
        "contract_risk_report.pdf",
        mime="application/pdf"
    )
