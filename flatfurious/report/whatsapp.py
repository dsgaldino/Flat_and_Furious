"""Generate WhatsApp-ready text from monthly summary."""

from __future__ import annotations

from pathlib import Path

from flatfurious.config import site_base_url
from flatfurious.report.monthly import report_dir_for_month

_HIGHLIGHT_LABELS = {
    "maior_distancia": "Maior distancia",
    "mais_rapido": "Mais rapido",
    "escalador": "Escalador",
    "mais_tempo": "Mais tempo pedalando",
    "mais_pedaladas": "Numero de pedaladas",
    "pedal_mais_longo": "Pedal mais longo",
}


def format_whatsapp_text(summary: dict) -> str:
    """Format summary dict as plain text for WhatsApp."""
    year = summary["year"]
    lines = [
        f"Flat & Furious — {summary['month_label_pt']}",
        "",
    ]

    if summary.get("new_members"):
        lines.append("Boas-vindas ao pelotao!")
        for member in summary["new_members"]:
            lines.append(f"• {member['nome']}")
        lines.append("")

    lines.extend(
        [
            f"Distancia no mes: {summary['distance_month_km']:.0f} km",
            f"Distancia total do grupo em {year}: {summary['distance_year_km']:.0f} km",
            f"Distancia total desde a criacao do grupo: "
            f"{summary.get('distance_since_group_km', 0):.0f} km "
            f"({summary.get('earth_percent_since_group', 0):.1%} de uma volta ao mundo)",
            "",
        ]
    )

    highlights = summary.get("month_highlights") or {}
    if any(highlights.get(k) for k in _HIGHLIGHT_LABELS):
        lines.append("Destaque do Mes")
        for key, label in _HIGHLIGHT_LABELS.items():
            item = highlights.get(key)
            if item:
                lines.append(f"• {label}: {item['athlete']} — {item['value']}")
        lines.append("")

    if summary.get("ranking_month"):
        lines.append("Ranking do mes (km):")
        for row in summary["ranking_month"]:
            lines.append(
                f"{row['rank']}. {row['athlete']} — {row['distance_km']:.0f} km"
            )
        lines.append("")

    if summary.get("ranking_year"):
        lines.append(f"Ranking em {year} (km):")
        for row in summary["ranking_year"]:
            lines.append(
                f"{row['rank']}. {row['athlete']} — {row['distance_km']:.0f} km"
            )
        lines.append("")

    if summary.get("top3_rides"):
        lines.append("Top 3 pedaladas do mes:")
        for i, ride in enumerate(summary["top3_rides"], 1):
            lines.append(f"{i}. {ride['athlete']} — {ride['distance_km']:.1f} km")
        lines.append("")

    if summary.get("curiosities"):
        lines.append("Curiosidades:")
        for phrase in summary["curiosities"]:
            lines.append(f"• {phrase}")

    base = site_base_url()
    if base:
        lines.append("")
        lines.append(f"Ver mais: {base}/archive/{summary['month_year']}/")

    return "\n".join(lines).rstrip() + "\n"


def save_whatsapp_text(summary: dict, month_year: str | None = None) -> Path:
    month_year = month_year or summary["month_year"]
    out_dir = report_dir_for_month(month_year)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "whatsapp.txt"
    path.write_text(format_whatsapp_text(summary), encoding="utf-8")
    print(f"WhatsApp text saved to {path}")
    return path
