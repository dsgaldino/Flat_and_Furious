"""Generate AI infographic prompt text from monthly summary."""

from __future__ import annotations

from pathlib import Path

from flatfurious.report.monthly import report_dir_for_month, report_relative_path

_HIGHLIGHT_LABELS = {
    "maior_distancia": "Maior distancia",
    "mais_rapido": "Mais rapido",
    "escalador": "Escalador",
    "mais_tempo": "Mais tempo pedalando",
    "mais_pedaladas": "Numero de pedaladas",
    "pedal_mais_longo": "Pedal mais longo",
}


def _month_title_upper(summary: dict) -> str:
    label = summary.get("month_label_pt", summary["month_year"])
    if "/" in label:
        month, year = label.split("/", 1)
        return f"{month.upper()} {year}"
    return label.upper()


def format_data_block(summary: dict) -> str:
    """Portuguese data block — paste into any image AI."""
    year = summary["year"]
    lines = [
        f"TITULO: FLAT & FURIOUS — ANALISE DE CICLISMO — {_month_title_upper(summary)}",
        "",
    ]

    if summary.get("new_members"):
        lines.append("BOAS-VINDAS AO PELOTAO:")
        for member in summary["new_members"]:
            lines.append(f"• {member['nome']}")
        lines.append("")

    earth_pct = (summary.get("earth_percent_since_group") or 0) * 100
    lines.extend(
        [
            "DISTANCIAS DO GRUPO:",
            f"• Distancia no mes: {summary['distance_month_km']:.0f} km",
            f"• Total em {year}: {summary['distance_year_km']:.0f} km",
            f"• Desde criacao do grupo: {summary.get('distance_since_group_km', 0):.0f} km "
            f"({earth_pct:.1f}% de uma volta ao mundo)",
            "",
        ]
    )

    highlights = summary.get("month_highlights") or {}
    if any(highlights.get(k) for k in _HIGHLIGHT_LABELS):
        lines.append("DESTAQUE DO MES:")
        for key, label in _HIGHLIGHT_LABELS.items():
            item = highlights.get(key)
            if item:
                lines.append(f"• {label}: {item['athlete']} — {item['value']}")
        lines.append("")

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

    if summary.get("top3_rides"):
        lines.append("TOP 3 PEDALADAS MAIS LONGAS:")
        for i, ride in enumerate(summary["top3_rides"], 1):
            lines.append(f"{i}. {ride['athlete']} — {ride['distance_km']:.1f} km")
        lines.append("")

    if summary.get("curiosities"):
        lines.append("CURIOSIDADES:")
        for i, phrase in enumerate(summary["curiosities"], 1):
            lines.append(f"{i}. {phrase}")
        lines.append("")

    lines.append("RODAPE: Pelotao Enschede | NL + BR | Ride + VirtualRide")
    lines.append("")
    lines.append("NAO INCLUIR: destaques nem tanto, rankings negativos, menor atividade.")
    return "\n".join(lines)


def _highlights_lines_en(summary: dict) -> list[str]:
    lines = []
    for key, label in _HIGHLIGHT_LABELS.items():
        item = (summary.get("month_highlights") or {}).get(key)
        if item:
            lines.append(f"   {label}: {item['athlete']} — {item['value']}")
    return lines


def _ranking_lines(rows: list[dict]) -> list[str]:
    return [f"   {r['rank']}. {r['athlete']} — {r['distance_km']:.0f} km" for r in rows]


def _podium_lines(top3: list[dict]) -> list[str]:
    medals = ("gold", "silver", "bronze")
    labels = ("1", "2", "3")
    lines = []
    for i, ride in enumerate(top3[:3]):
        medal = medals[i] if i < len(medals) else "bronze"
        label = labels[i] if i < len(labels) else str(i + 1)
        lines.append(
            f"   {label} ({medal}): {ride['athlete']} — {ride['distance_km']:.1f} km"
        )
    return lines


def format_ai_prompt(summary: dict) -> str:
    """Full prompt for DALL-E, Midjourney, Ideogram, etc."""
    title = _month_title_upper(summary)
    year = summary["year"]
    earth_pct = (summary.get("earth_percent_since_group") or 0) * 100
    month_km = summary["distance_month_km"]
    year_km = summary["distance_year_km"]
    since_km = summary.get("distance_since_group_km", 0)

    sections: list[str] = []
    n = 0

    if summary.get("new_members"):
        names = ", ".join(m["nome"] for m in summary["new_members"])
        n += 1
        sections.append(
            f'{n}) Green welcome card: "BOAS-VINDAS AO PELOTAO" — {names}'
        )

    n += 1
    sections.append(
        f"""{n}) Row of 3 distance cards:
   - "Distancia no mes" → {month_km:.0f} km (green)
   - "Total em {year}" → {year_km:.0f} km (blue)
   - "Desde criacao do grupo" → {since_km:.0f} km, subtitle "{earth_pct:.0f}% volta ao mundo" with thin progress bar (purple)"""
    )

    hl_lines = _highlights_lines_en(summary)
    highlights_block = "\n".join(hl_lines) if hl_lines else "   (sem destaques)"
    n += 1
    sections.append(
        f'{n}) "DESTAQUE DO MES" white panel:\n{highlights_block}'
    )

    rank_month = "\n".join(_ranking_lines(summary.get("ranking_month") or []))
    rank_year = "\n".join(_ranking_lines(summary.get("ranking_year") or []))
    podium = "\n".join(_podium_lines(summary.get("top3_rides") or []))

    curios = summary.get("curiosities") or []
    cur_lines = []
    for i, phrase in enumerate(curios[:2], 1):
        cur_lines.append(f"   ({i}) {phrase}")
    curios_block = "\n".join(cur_lines) if cur_lines else "   (sem curiosidades)"

    n += 1
    sections.append(
        f"""{n}) Two columns:
   LEFT: podium "TOP 3 PEDALADAS MAIS LONGAS":
{podium}
   RIGHT: gold-bordered "CURIOSIDADES DO MES":
{curios_block}"""
    )

    n += 1
    layout_sections = "\n\n".join(sections)

    main_prompt = f"""Infographic dashboard poster, tall vertical layout, clean modern sports analytics UI.
Reference: light cream background #E8EEF4, white rounded cards with soft shadows, Dutch orange #D35400, navy #1A3A52, gold accent #C9A227.
Header band navy with gold text "FLAT & FURIOUS" and orange title "ANALISE DE CICLISMO" and subtitle "{title}".

ALL SECTIONS IN PORTUGUESE (legible typography):

{layout_sections}

{n + 1}) "RANKINGS" — two tables side by side:
   "RANKING MENSAL":
{rank_month}
   "RANKING ANUAL {year}":
{rank_year}

Footer small text: "Pelotao Enschede | NL + BR | Ride + VirtualRide"

Decorative (subtle margins): Dutch windmills on flat green polder, canal with bicycles, orange tulips; Brazilian touches — coffee cup, pastel/brigadeiro, green beer bottle (Grolsch style), soft green-yellow accents (no literal flag). Cycling peloton silhouette in header. Flat Twente terrain, no mountains.

Style: flat vector + UI mockup hybrid, professional Strava club monthly report, high contrast, 4K, sharp text areas.

DO NOT include: "destaques nem tanto", shame cards, negative rankings, least active.

Negative prompt: blurry illegible text, dark theme, mountains, motorcycles, watermark, cluttered collage, photorealistic faces.
"""

    data_block = format_data_block(summary)
    return (
        f"# AI Infographic Prompt — {summary.get('month_label_pt', summary['month_year'])}\n"
        f"# Gerado automaticamente pelo Flat & Furious\n\n"
        f"=== PROMPT PRINCIPAL (copiar para a IA de imagem) ===\n\n"
        f"{main_prompt.strip()}\n\n"
        f"=== BLOCO DE DADOS (PT — conferencia de numeros) ===\n\n"
        f"{data_block}\n\n"
        f"=== DICA ===\n"
        f"Anexe reports/{report_relative_path(summary['month_year'])}/infographic.png como referencia de layout. "
        f"Para texto 100% correto, sobreponha numeros no Canva/Figma usando o bloco de dados acima.\n"
    )


def save_ai_prompt(summary: dict, month_year: str | None = None) -> Path:
    """Write ai_prompt.txt next to whatsapp.txt and infographic.png."""
    month_year = month_year or summary["month_year"]
    out_dir = report_dir_for_month(month_year)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "ai_prompt.txt"
    path.write_text(format_ai_prompt(summary), encoding="utf-8")
    print(f"AI prompt saved to {path}")
    return path
