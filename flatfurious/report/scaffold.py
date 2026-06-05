"""Scaffold report folders with distance-only data (investigation / validation)."""

from __future__ import annotations

import base64
import json
import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd

from flatfurious.config import group_start_date, reports_dir
from flatfurious.report.monthly import (
    build_distance_only_summary,
    report_dir_for_month,
    report_relative_path,
)

# 1×1 transparent PNG placeholder until full infographic is generated
_PLACEHOLDER_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


_PARTIAL_HIGHLIGHT_LABELS = (
    ("mais_rapido", "Mais rapido"),
    ("escalador", "Escalador"),
    ("mais_tempo", "Mais tempo pedalando"),
    ("mais_pedaladas", "Numero de pedaladas"),
    ("pedal_mais_longo", "Pedal mais longo"),
)


def _format_welcome_lines(summary: dict) -> list[str]:
    """Boas-vindas block when new members joined in the report month."""
    members = summary.get("new_members") or []
    if not members:
        return []
    lines = ["Boas-vindas ao pelotao!"]
    for member in members:
        lines.append(f"• {member['nome']}")
    lines.append("")
    return lines


def _format_ranking_lines(summary: dict) -> list[str]:
    """Monthly and year-to-date ranking blocks."""
    year = summary["year"]
    lines: list[str] = []
    if summary.get("ranking_month"):
        lines.append("Ranking do mes (km):")
        for row in summary["ranking_month"]:
            lines.append(f"{row['rank']}. {row['athlete']} — {row['distance_km']:.0f} km")
        lines.append("")
    if summary.get("ranking_year"):
        lines.append(f"Ranking em {year} (km):")
        for row in summary["ranking_year"]:
            lines.append(f"{row['rank']}. {row['athlete']} — {row['distance_km']:.0f} km")
        lines.append("")
    return lines


def _format_curiosity_lines(summary: dict) -> list[str]:
    phrases = summary.get("curiosities") or []
    if not phrases:
        return []
    lines = ["Curiosidades"]
    for phrase in phrases:
        lines.append(f"• {phrase}")
    lines.append("")
    return lines


def _format_highlight_lines(summary: dict) -> list[str]:
    """Destaque do mes lines present in partial summaries."""
    highlights = summary.get("month_highlights") or {}
    lines: list[str] = []
    for key, label in _PARTIAL_HIGHLIGHT_LABELS:
        item = highlights.get(key)
        if item:
            if not lines:
                lines.append("Destaque do Mes")
            lines.append(f"• {label}: {item['athlete']} — {item['value']}")
    if lines:
        lines.append("")
    return lines


def _all_months_through(end_month_year: str) -> list[str]:
    gs = pd.Timestamp(group_start_date())
    end = pd.Period(end_month_year, freq="M")
    start = pd.Period(gs.strftime("%Y-%m"), freq="M")
    return [str(p) for p in pd.period_range(start, end, freq="M")]


def format_distance_only_whatsapp(summary: dict) -> str:
    label = summary.get("month_label_pt", summary["month_year"])
    year = summary["year"]
    dist_month = summary["distance_month_km"]
    dist_year = summary["distance_year_km"]
    dist_since = summary["distance_since_group_km"]
    earth_pct = summary.get("earth_percent_since_group", 0)
    parts = [
        f"Flat & Furious — {label}",
        "",
    ]
    parts.extend(_format_welcome_lines(summary))
    parts.extend([
        f"Distancia no mes: {dist_month:.0f} km",
        f"Distancia total do grupo em {year}: {dist_year:.0f} km",
        f"Distancia total desde a criacao do grupo: {dist_since:.0f} km "
        f"({earth_pct:.1%} de uma volta ao mundo)",
        "",
    ])
    parts.extend(_format_highlight_lines(summary))
    parts.extend(_format_curiosity_lines(summary))
    parts.extend(_format_ranking_lines(summary))
    pending = "infografico completo"
    if not summary.get("curiosities"):
        pending = "curiosidades (aguardando km do mes) e " + pending
    parts.append(f"(Relatorio parcial — falta {pending}.)")
    return "\n".join(parts) + "\n"


def _format_curiosity_block_ai(summary: dict) -> str:
    phrases = summary.get("curiosities") or []
    if not phrases:
        return ""
    lines = ["CURIOSIDADES:"]
    for i, phrase in enumerate(phrases, 1):
        lines.append(f"{i}. {phrase}")
    lines.append("")
    return "\n".join(lines) + "\n"


def _format_pending_block_ai(summary: dict) -> str:
    if summary.get("curiosities"):
        return "Infografico completo ainda nao preenchido nesta fase de validacao."
    return (
        "Curiosidades aguardam km do mes (Ride/VirtualRide). "
        "Infografico completo ainda nao preenchido nesta fase de validacao."
    )


def _format_ranking_block_ai(summary: dict) -> str:
    lines: list[str] = []
    year = summary["year"]
    if summary.get("ranking_month"):
        lines.append("RANKING DO MES (km):")
        for row in summary["ranking_month"]:
            lines.append(f"{row['rank']}. {row['athlete']} — {row['distance_km']:.0f} km")
        lines.append("")
    if summary.get("ranking_year"):
        lines.append(f"RANKING EM {year} (km):")
        for row in summary["ranking_year"]:
            lines.append(f"{row['rank']}. {row['athlete']} — {row['distance_km']:.0f} km")
        lines.append("")
    return ("\n".join(lines) + "\n") if lines else ""


def format_distance_only_ai_prompt(summary: dict) -> str:
    rel = report_relative_path(summary["month_year"])
    label = summary.get("month_label_pt", summary["month_year"])
    year = summary["year"]
    dist_month = summary["distance_month_km"]
    dist_year = summary["distance_year_km"]
    dist_since = summary["distance_since_group_km"]
    earth_pct = (summary.get("earth_percent_since_group") or 0) * 100
    welcome_block = ""
    welcome_lines = _format_welcome_lines(summary)
    if welcome_lines:
        welcome_block = (
            "BOAS-VINDAS AO PELOTAO:\n"
            + "\n".join(line for line in welcome_lines if line != "Boas-vindas ao pelotao!")
            + "\n\n"
        )

    highlight_block = ""
    hl_lines = _format_highlight_lines(summary)
    if hl_lines:
        highlight_block = "DESTAQUE DO MES:\n" + "\n".join(
            line for line in hl_lines if line and line != "Destaque do Mes"
        )
        if highlight_block and not highlight_block.endswith("\n"):
            highlight_block += "\n"
        highlight_block += "\n"

    return (
        f"# AI Infographic Prompt — {label}\n"
        f"# Relatorio parcial (distance_only)\n\n"
        f"=== DADOS DISPONIVEIS ===\n\n"
        f"{welcome_block}"
        f"DISTANCIAS DO GRUPO:\n"
        f"• Distancia no mes: {dist_month:.0f} km\n"
        f"• Total em {year}: {dist_year:.0f} km\n"
        f"• Desde criacao do grupo: {dist_since:.0f} km "
        f"({earth_pct:.1f}% de uma volta ao mundo)\n\n"
        f"{highlight_block}"
        f"{_format_curiosity_block_ai(summary)}"
        f"{_format_ranking_block_ai(summary)}"
        f"=== PENDENTE ===\n\n"
        f"{_format_pending_block_ai(summary)}\n\n"
        f"=== DICA ===\n"
        f"Quando o relatorio completo existir: reports/{rel}/infographic.png\n"
    )


def save_distance_only_month(month_year: str, *, overwrite: bool = True) -> Path:
    """Write summary.json, whatsapp.txt, ai_prompt.txt, placeholder infographic.png."""
    summary = build_distance_only_summary(month_year)
    out_dir = report_dir_for_month(month_year)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = out_dir / "summary.json"
    if summary_path.exists() and not overwrite:
        return out_dir

    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "whatsapp.txt").write_text(
        format_distance_only_whatsapp(summary), encoding="utf-8"
    )
    (out_dir / "ai_prompt.txt").write_text(
        format_distance_only_ai_prompt(summary), encoding="utf-8"
    )
    (out_dir / "infographic.png").write_bytes(_PLACEHOLDER_PNG)
    return out_dir


def migrate_legacy_report_dirs() -> list[str]:
    """Move reports/YYYY-MM/ to reports/YYYY/MM/. Returns moved month keys."""
    root = reports_dir()
    moved: list[str] = []
    if not root.exists():
        return moved
    for entry in sorted(root.iterdir()):
        if not entry.is_dir() or "-" not in entry.name or len(entry.name) != 7:
            continue
        try:
            year, month = entry.name.split("-")
            int(year)
            int(month)
        except ValueError:
            continue
        dest = root / year / f"{int(month):02d}"
        if dest.resolve() == entry.resolve():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            for child in entry.iterdir():
                target = dest / child.name
                if child.is_file() and not target.exists():
                    shutil.move(str(child), str(target))
            if not any(entry.iterdir()):
                entry.rmdir()
        else:
            shutil.move(str(entry), str(dest))
        moved.append(entry.name)
    return moved


def scaffold_all_distance_reports(
    end_month_year: str | None = None,
    *,
    migrate_legacy: bool = True,
    overwrite: bool = True,
) -> int:
    """
    Create reports/YEAR/MM for every month since group start through end_month_year.
    Each folder gets distance-only content plus placeholder infographic.
    """
    if migrate_legacy:
        migrate_legacy_report_dirs()

    end = end_month_year or datetime.today().strftime("%Y-%m")
    count = 0
    for month_year in _all_months_through(end):
        save_distance_only_month(month_year, overwrite=overwrite)
        count += 1
    print(f"Scaffolded {count} months under {reports_dir()} (through {end})")
    return count
