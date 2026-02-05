from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def export_pdf(results):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = [Paragraph("Legal Contract Risk Analysis Report", styles["Title"])]

    for i, item in enumerate(results, 1):
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Clause {i}", styles["Heading2"]))
        elements.append(Paragraph(item["clause"], styles["BodyText"]))

        table = Table([
            ["Risk Level", item["risk"]],
            ["Risk Score", item["score"]]
        ])

        table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey)
        ]))

        elements.append(table)
        elements.append(Paragraph(item["analysis"]["risk_reason"], styles["BodyText"]))
        elements.append(Paragraph(item["analysis"]["suggested_fix"], styles["BodyText"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
