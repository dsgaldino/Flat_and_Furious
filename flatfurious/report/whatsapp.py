"""Generate WhatsApp-ready text from monthly summary."""

from __future__ import annotations

from pathlib import Path

from flatfurious.config import site_base_url
from flatfurious.report.monthly import report_dir_for_month


def format_whatsapp_text(summary: dict) -> str:
    """Format summary dict as plain text for WhatsApp."""
    lines = [
        f"Flat & Furious — {summary['month_label_pt']}",
        "",
        f"Distancia total do grupo: {summary['distance_month_km']:.0f} km",
        f"Acumulado em {summary['year']}: {summary['distance_year_km']:.0f} km "
        f"({summary['earth_percent_year']:.1%} de uma volta ao mundo)",
    ]

    if summary.get("ranking_month"):
        king = summary["ranking_month"][0]
        lines.append(
            f"Rei/Rainha da distancia: {king['athlete']} ({king['distance_km']:.0f} km)"
        )

    if summary.get("fastest"):
        f = summary["fastest"]
        lines.append(
            f"Mais rapido: {f['athlete']} ({f['max_speed_kmh']:.1f} km/h)"
        )

    if summary.get("most_moving_time"):
        t = summary["most_moving_time"]
        lines.append(f"Mais tempo pedalando: {t['athlete']} ({t['duration']})")

    if summary.get("top3_rides"):
        lines.append("")
        lines.append("Top 3 pedaladas:")
        for i, ride in enumerate(summary["top3_rides"], 1):
            lines.append(f"{i}. {ride['athlete']} — {ride['distance_km']:.1f} km")

    if summary.get("curiosities"):
        lines.append("")
        lines.append("Curiosidades:")
        for phrase in summary["curiosities"]:
            lines.append(f"• {phrase}")

    base = site_base_url()
    if base:
        lines.append("")
        lines.append(f"Ver mais: {base}/archive/{summary['month_year']}/")

    return "\n".join(lines)


def save_whatsapp_text(summary: dict, month_year: str | None = None) -> Path:
    month_year = month_year or summary["month_year"]
    out_dir = report_dir_for_month(month_year)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "whatsapp.txt"
    path.write_text(format_whatsapp_text(summary), encoding="utf-8")
    print(f"WhatsApp text saved to {path}")
    return path
