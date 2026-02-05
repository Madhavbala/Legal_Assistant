from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def export_pdf(results):
    """
    Generate PDF report from analysis results.
    Defensive against missing keys.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ClauseHeader",
            fontSize=12,
            spaceAfter=6,
            textColor=colors.darkblue,
            bold=True
        )
    )

    styles.add(
        ParagraphStyle(
            name="ClauseBody",
            fontSize=10,
            spaceAfter=10
        )
    )

    styles.add(
        ParagraphStyle(
            name="AnalysisBody",
            fontSize=9,
            spaceAfter=14,
            textColor=colors.black
        )
    )

    elements = []

    elements.append(Paragraph("Legal Contract Risk Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    if not results:
        elements.append(Paragraph("No clauses were analyzed.", styles["Normal"]))
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    for idx, item in enumerate(results, start=1):

        # 🔒 SAFE CLAUSE EXTRACTION
        clause_text = (
            item.get("clause")
            or item.get("text")
            or item.get("content")
            or "Clause text not available."
        )

        risk = item.get("risk", "Unknown")
        analysis = item.get("analysis", "No analysis available.")

        elements.append(
            Paragraph(f"Clause {idx}", styles["ClauseHeader"])
        )

        elements.append(
            Paragraph(clause_text, styles["ClauseBody"])
        )

        table_data = [
            ["Risk Level", risk],
        ]

        table = Table(table_data, colWidths=[100, 350])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONT", (0, 0), (-1, -1), "Helvetica"),
                ]
            )
        )

        elements.append(table)
        elements.append(Spacer(1, 6))

        elements.append(
            Paragraph(f"<b>Explanation:</b> {analysis}", styles["AnalysisBody"])
        )

        elements.append(Spacer(1, 12))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
