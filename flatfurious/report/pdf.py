"""Generate monthly PDF report."""
from __future__ import annotations
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from flatfurious.config import group_start_date
from flatfurious.data.members import new_members_in_month
from flatfurious.report.metrics import PdfMetrics, build_pdf_metrics
from flatfurious.report.monthly import report_dir_for_month

def _table(data, col_widths=None):
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5276")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    return t

def generate_pdf(month_year: str, metrics: PdfMetrics | None = None) -> Path:
    metrics = metrics or build_pdf_metrics(month_year)
    out_dir = report_dir_for_month(month_year)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "report.pdf"
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("Flat &amp; Furious", styles["Title"]))
    story.append(Paragraph(f"Relatorio - {metrics.month_label_pt}", styles["Heading2"]))
    story.append(Spacer(1, 0.4 * cm))
    welcomes = new_members_in_month(month_year)
    if welcomes:
        story.append(Paragraph("Boas-vindas", styles["Heading3"]))
        for member in welcomes:
            story.append(
                Paragraph(
                    f"<b>{member['nome']}</b>",
                    styles["Normal"],
                )
            )
        story.append(Spacer(1, 0.4 * cm))
    gs = group_start_date().strftime("%d/%m/%Y")
    story.append(Paragraph(f"<b>Total pedalado pelo grupo em {metrics.year}:</b> {metrics.distance_year_group_km:,.0f} km".replace(",", "."), styles["Normal"]))
    story.append(Paragraph(f"<b>Total desde criacao do grupo ({gs}):</b> {metrics.distance_since_group_creation_km:,.0f} km".replace(",", "."), styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Ranking do mes (km)", styles["Heading3"]))
    rows = [["#", "Atleta", "km"]]
    for row in metrics.ranking_month:
        rows.append([str(row["rank"]), row["athlete"], f"{row['distance_km']:.1f}"])
    if len(rows) == 1:
        rows.append(["-", "Sem dados", "-"])
    story.append(_table(rows, [1.2*cm, 10*cm, 3*cm]))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(f"Ranking anual {metrics.year}", styles["Heading3"]))
    rows = [["#", "Atleta", "km"]]
    for row in metrics.ranking_year:
        rows.append([str(row["rank"]), row["athlete"], f"{row['distance_km']:.1f}"])
    if len(rows) == 1:
        rows.append(["-", "Sem dados", "-"])
    story.append(_table(rows, [1.2*cm, 10*cm, 3*cm]))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Top 3 climbers (elevacao m no mes)", styles["Heading3"]))
    rows = [["#", "Atleta", "m"]]
    for i, row in enumerate(metrics.top3_climbers_month, 1):
        rows.append([str(i), row["athlete"], f"{row['elevation_m']:.0f}"])
    if len(rows) == 1:
        rows.append(["-", "Sem dados", "-"])
    story.append(_table(rows, [1.2*cm, 10*cm, 3*cm]))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Top 3 speed (max km/h no mes)", styles["Heading3"]))
    rows = [["#", "Atleta", "km/h"]]
    for i, row in enumerate(metrics.top3_speed_month, 1):
        rows.append([str(i), row["athlete"], f"{row['max_speed_kmh']:.1f}"])
    if len(rows) == 1:
        rows.append(["-", "Sem dados", "-"])
    story.append(_table(rows, [1.2*cm, 10*cm, 3*cm]))
    SimpleDocTemplate(str(path), pagesize=A4).build(story)
    print(f"PDF saved to {path}")
    return path
