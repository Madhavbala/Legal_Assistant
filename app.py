# app.py

import streamlit as st

from core.parser import get_input_text
from core.language import detect_language
from core.clause_splitter import split_clauses
from core.llm_engine import analyze_clause_with_llm
from utils.helpers import export_pdf

st.set_page_config(page_title="Legal Contract Risk Analyzer", layout="wide")

st.title("📄 Legal Contract Risk Analyzer")

mode = st.radio(
    "Upload Contract or Paste Text",
    ["Upload File", "Paste Text"],
    horizontal=True
)

raw_text = get_input_text(mode)

analyze_clicked = st.button("Analyze Contract", use_container_width=True)

if analyze_clicked:

    if not raw_text or len(raw_text.strip()) < 50:
        st.warning("Please upload or paste a valid contract.")
        st.stop()

    # 1. Detect language
    lang = detect_language(raw_text)
    st.success(f"Language detected: {lang}")

    # 2. Split clauses
    clauses = split_clauses(raw_text)
    clauses = [c for c in clauses if len(c.strip()) > 40]

    if not clauses:
        st.error("No clauses detected.")
        st.stop()

    st.success(f"Total clauses detected: {len(clauses)}")

    results = []

    st.header("Clause Analysis Results")

    for idx, clause in enumerate(clauses, 1):

        st.subheader(f"Clause {idx}")
        st.write(clause)

        analysis = analyze_clause_with_llm(clause, lang)

        st.markdown("### Risk Summary")
        st.markdown(f"""
- **Ownership:** {analysis["ownership"]}
- **Exclusivity:** {analysis["exclusivity"]}
- **Favor:** {analysis["favor"]}
""")

        st.markdown("**Risk Explanation**")
        st.write(analysis["risk_reason"])

        st.markdown("**Suggested Fix**")
        st.write(analysis["suggested_fix"])

        results.append({
            "clause": clause,
            "analysis": analysis
        })

        st.divider()

    pdf_bytes = export_pdf(results)

    st.download_button(
        "📥 Download PDF Report",
        pdf_bytes,
        "contract_risk_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
