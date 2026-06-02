"""Generate monthly infographic PNG (light dashboard poster style)."""

from __future__ import annotations

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle, Wedge

from flatfurious.report.monthly import report_dir_for_month

# Prefer a Windows font with Latin-1 extended glyphs when available
for _font in ("Segoe UI", "Arial", "DejaVu Sans"):
    if any(_font in f.name for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = _font
        break

COLORS = {
    "bg": "#E8EEF4",
    "card": "#ffffff",
    "card_edge": "#c8d4e0",
    "shadow": "#8899aa",
    "title_orange": "#D35400",
    "title_blue": "#1A3A52",
    "brand_gold": "#C9A227",
    "section": "#2874a6",
    "blue": "#3498db",
    "green": "#27ae60",
    "green_welcome": "#e8f8f5",
    "purple": "#8e44ad",
    "gold": "#f4c430",
    "silver": "#bfc9d1",
    "bronze": "#cd7f32",
    "text": "#2c3e50",
    "muted": "#5d6d7e",
    "polder": "#a8d5a2",
    "canal": "#7eb8da",
    "tulip": "#D35400",
    "br_soft": "#f5c6d0",
    "coffee": "#6f4e37",
    "beer": "#7cb342",
}

OUTPUT_DPI = 200
FIG_WIDTH = 10.8


def _month_title(summary: dict) -> str:
    """e.g. Janeiro/2026 -> JANEIRO 2026"""
    label = summary.get("month_label_pt", summary["month_year"])
    if "/" in label:
        month, year = label.split("/", 1)
        return f"{month.upper()} {year}"
    return label.upper()


def _first_name(full_name: str) -> str:
    return full_name.split()[0] if full_name else full_name


def _format_highlight_value(key: str, value: str) -> str:
    if key == "mais_rapido" and "km/h" in value:
        num = value.replace(" km/h", "").strip()
        try:
            return f"{float(num):.1f}".replace(".", ",") + " km/h"
        except ValueError:
            return value
    if key == "mais_pedaladas":
        return value.replace(" pedaladas", "").strip()
    if key == "pedal_mais_longo" and "km" in value:
        num = value.replace(" km", "").strip()
        try:
            return f"{float(num):.1f}".replace(".", ",") + " km"
        except ValueError:
            return value
    return value


def _rounded_box(
    ax,
    xy: tuple[float, float],
    width: float,
    height: float,
    *,
    facecolor: str,
    edgecolor: str,
    linewidth: float = 1.2,
    rounding: float = 0.05,
    shadow: bool = True,
) -> FancyBboxPatch:
    x, y = xy
    if shadow:
        sh = FancyBboxPatch(
            (x + 0.004, y - 0.004),
            width,
            height,
            boxstyle=f"round,pad=0.01,rounding_size={rounding}",
            facecolor=COLORS["shadow"],
            edgecolor="none",
            alpha=0.18,
            zorder=1,
        )
        ax.add_patch(sh)
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle=f"round,pad=0.01,rounding_size={rounding}",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        zorder=2,
    )
    ax.add_patch(box)
    return box


def _draw_card(
    ax,
    *,
    icon: str,
    label: str,
    name: str | None,
    value: str,
    value_color: str,
    sub: str | None = None,
) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    _rounded_box(ax, (0.02, 0.02), 0.96, 0.96, facecolor=COLORS["card"], edgecolor=COLORS["card_edge"])
    ax.text(
        0.1,
        0.78,
        icon,
        fontsize=13,
        fontweight="bold",
        ha="center",
        va="center",
        color=value_color,
        zorder=3,
        bbox=dict(boxstyle="circle,pad=0.32", facecolor="#f4f6f8", edgecolor=value_color),
    )
    ax.text(0.22, 0.82, label, fontsize=10.5, color=COLORS["muted"], ha="left", va="top", zorder=3)
    y = 0.58
    if name:
        ax.text(0.5, y, name, fontsize=12, fontweight="bold", color=COLORS["text"], ha="center", zorder=3)
        y = 0.32
    ax.text(0.5, y, value, fontsize=19, fontweight="bold", color=value_color, ha="center", zorder=3)
    if sub:
        ax.text(0.5, 0.1, sub, fontsize=8.5, color=COLORS["muted"], ha="center", zorder=3)


def _section_title(fig, y: float, text: str) -> None:
    ax = fig.add_axes([0.05, y, 0.9, 0.022])
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        text,
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color=COLORS["section"],
    )


def _draw_ranking_table(ax, title: str, rows: list[dict]) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    _rounded_box(ax, (0.01, 0.01), 0.98, 0.98, facecolor=COLORS["card"], edgecolor=COLORS["card_edge"])
    ax.text(0.5, 0.94, title, ha="center", fontsize=11, fontweight="bold", color=COLORS["title_blue"], zorder=3)

    if not rows:
        ax.text(0.5, 0.5, "Sem dados", ha="center", color=COLORS["muted"], zorder=3)
        return

    medals = {1: "1º", 2: "2º", 3: "3º"}
    y = 0.86
    ax.text(0.08, y, "#", fontsize=9, fontweight="bold", color=COLORS["title_blue"], zorder=3)
    ax.text(0.16, y, "ATLETA", fontsize=9, fontweight="bold", color=COLORS["title_blue"], zorder=3)
    ax.text(0.88, y, "KM", fontsize=9, fontweight="bold", color=COLORS["title_blue"], ha="right", zorder=3)
    y -= 0.08
    for row in rows[:5]:
        rank = medals.get(row["rank"], str(row["rank"]))
        name = row["athlete"]
        if len(name) > 22:
            name = name[:20] + "..."
        km = int(round(row["distance_km"]))
        ax.text(0.08, y, rank, fontsize=9, color=COLORS["text"], zorder=3)
        ax.text(0.16, y, name, fontsize=9, color=COLORS["text"], zorder=3)
        ax.text(0.88, y, str(km), fontsize=9, color=COLORS["text"], ha="right", zorder=3)
        y -= 0.075


def _draw_podium(ax, top3: list[dict]) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    _rounded_box(ax, (0.01, 0.01), 0.98, 0.98, facecolor=COLORS["card"], edgecolor=COLORS["card_edge"])
    ax.text(
        0.5,
        0.92,
        "TOP 3 PEDALADAS MAIS LONGAS",
        ha="center",
        fontsize=10,
        fontweight="bold",
        color=COLORS["title_blue"],
        zorder=3,
    )

    if not top3:
        ax.text(0.5, 0.5, "Sem dados", ha="center", color=COLORS["muted"], zorder=3)
        return

    slots = [
        (0.5, 0.55, 0.14, COLORS["gold"], "1"),
        (0.22, 0.42, 0.11, COLORS["silver"], "2"),
        (0.78, 0.42, 0.11, COLORS["bronze"], "3"),
    ]
    for i, (cx, cy, radius, color, label) in enumerate(slots):
        if i >= len(top3):
            break
        ride = top3[i]
        circle = Circle(
            (cx, cy), radius, facecolor=color, edgecolor=COLORS["card_edge"], linewidth=1.5, zorder=3
        )
        ax.add_patch(circle)
        dist = f"{ride['distance_km']:.1f}".replace(".", ",")
        ax.text(cx, cy + 0.04, f"{label}º", ha="center", fontsize=10, fontweight="bold", color=COLORS["text"], zorder=4)
        ax.text(
            cx,
            cy - 0.02,
            _first_name(ride["athlete"]),
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=COLORS["text"],
            zorder=4,
        )
        ax.text(cx, cy - radius - 0.06, f"{dist} km", ha="center", fontsize=9, color=COLORS["muted"], zorder=4)


def _draw_curiosities(ax, phrases: list[str]) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    _rounded_box(
        ax,
        (0.01, 0.01),
        0.98,
        0.98,
        facecolor=COLORS["card"],
        edgecolor=COLORS["brand_gold"],
        linewidth=2.0,
    )
    ax.text(
        0.5,
        0.92,
        "CURIOSIDADES DO MÊS",
        ha="center",
        fontsize=11,
        fontweight="bold",
        color=COLORS["title_blue"],
        zorder=3,
    )
    labels = ["(1)", "(2)"]
    y = 0.78
    for i, phrase in enumerate(phrases[:2]):
        label = labels[i] if i < len(labels) else "•"
        color = COLORS["section"] if i == 0 else COLORS["title_orange"]
        wrapped = textwrap.fill(phrase, width=38)
        ax.text(0.06, y, label, fontsize=10, fontweight="bold", ha="left", va="top", color=color, zorder=3)
        ax.text(
            0.13,
            y,
            wrapped,
            fontsize=9.5,
            color=COLORS["text"],
            ha="left",
            va="top",
            linespacing=1.35,
            zorder=3,
        )
        y -= 0.16 * max(1, wrapped.count("\n") + 1)
    if not phrases:
        ax.text(0.5, 0.5, "Sem curiosidades", ha="center", color=COLORS["muted"], zorder=3)


def _draw_welcome(ax, members: list[dict]) -> None:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    _rounded_box(
        ax,
        (0.01, 0.01),
        0.98,
        0.98,
        facecolor=COLORS["green_welcome"],
        edgecolor=COLORS["green"],
        linewidth=1.8,
    )
    ax.text(
        0.5,
        0.72,
        "BOAS-VINDAS AO PELOTÃO",
        ha="center",
        fontsize=12,
        fontweight="bold",
        color=COLORS["green"],
        zorder=3,
    )
    y = 0.42
    for member in members:
        ax.text(0.5, y, f"• {member['nome']}", fontsize=11, color=COLORS["text"], ha="center", va="top", zorder=3)
        y -= 0.22


def _draw_windmill(ax, cx: float, cy: float, scale: float = 1.0, alpha: float = 0.35) -> None:
    s = scale
    ax.add_patch(Rectangle((cx - 0.02 * s, cy - 0.12 * s), 0.04 * s, 0.12 * s, facecolor="#8d6e63", alpha=alpha, zorder=0))
    for angle in (0, 90, 180, 270):
        wedge = Wedge((cx, cy), 0.09 * s, angle, angle + 25, width=0.018 * s, facecolor="#5d6d7e", alpha=alpha, zorder=0)
        ax.add_patch(wedge)
    ax.add_patch(Circle((cx, cy), 0.012 * s, facecolor="#5d6d7e", alpha=alpha, zorder=0))


def _draw_bicycle(ax, cx: float, cy: float, scale: float = 1.0, alpha: float = 0.3) -> None:
    s = scale
    r = 0.025 * s
    for dx in (-0.04, 0.04):
        ax.add_patch(Circle((cx + dx * s, cy), r, fill=False, edgecolor=COLORS["title_blue"], linewidth=1.2, alpha=alpha, zorder=0))
    ax.plot([cx - 0.04 * s, cx, cx + 0.04 * s], [cy, cy + 0.05 * s, cy], color=COLORS["title_blue"], alpha=alpha, linewidth=1.2, zorder=0)


def _draw_tulip(ax, cx: float, cy: float, scale: float = 1.0, alpha: float = 0.4) -> None:
    s = scale
    ax.plot([cx, cx], [cy, cy + 0.06 * s], color=COLORS["green"], alpha=alpha, linewidth=1.5, zorder=0)
    ax.add_patch(Circle((cx, cy + 0.065 * s), 0.018 * s, facecolor=COLORS["tulip"], alpha=alpha, zorder=0))


def _draw_coffee_cup(ax, cx: float, cy: float, scale: float = 1.0, alpha: float = 0.35) -> None:
    s = scale
    ax.add_patch(Rectangle((cx - 0.025 * s, cy), 0.05 * s, 0.05 * s, facecolor=COLORS["coffee"], alpha=alpha, zorder=0))
    ax.add_patch(
        FancyBboxPatch(
            (cx + 0.025 * s, cy + 0.01 * s),
            0.018 * s,
            0.03 * s,
            boxstyle="round,pad=0",
            facecolor="none",
            edgecolor=COLORS["coffee"],
            linewidth=1,
            alpha=alpha,
            zorder=0,
        )
    )


def _draw_beer_bottle(ax, cx: float, cy: float, scale: float = 1.0, alpha: float = 0.35) -> None:
    s = scale
    ax.add_patch(Rectangle((cx - 0.012 * s, cy), 0.024 * s, 0.08 * s, facecolor=COLORS["beer"], alpha=alpha, zorder=0))
    ax.add_patch(Rectangle((cx - 0.008 * s, cy + 0.08 * s), 0.016 * s, 0.02 * s, facecolor="#455a64", alpha=alpha, zorder=0))


def _draw_brigadeiro(ax, cx: float, cy: float, scale: float = 1.0, alpha: float = 0.35) -> None:
    s = scale
    ax.add_patch(Circle((cx, cy), 0.022 * s, facecolor="#5d4037", alpha=alpha, zorder=0))
    ax.add_patch(Circle((cx, cy + 0.012 * s), 0.006 * s, facecolor=COLORS["br_soft"], alpha=alpha * 0.8, zorder=0))


def _draw_peloton(ax, x0: float, y0: float, width: float, alpha: float = 0.22) -> None:
    n = 6
    for i in range(n):
        cx = x0 + (i / max(n - 1, 1)) * width
        cy = y0 + (0.01 if i % 2 else 0)
        _draw_bicycle(ax, cx, cy, scale=0.7, alpha=alpha)


def _draw_margin_decorations(fig) -> None:
    """Subtle NL + BR flat vector accents in side margins."""
    ax_l = fig.add_axes([0.0, 0.08, 0.06, 0.82])
    ax_l.set_xlim(0, 1)
    ax_l.set_ylim(0, 1)
    ax_l.axis("off")
    ax_l.add_patch(Rectangle((0.1, 0.0), 0.8, 0.35, facecolor=COLORS["polder"], alpha=0.25, zorder=0))
    ax_l.add_patch(Rectangle((0.05, 0.08), 0.9, 0.06, facecolor=COLORS["canal"], alpha=0.2, zorder=0))
    _draw_windmill(ax_l, 0.5, 0.55, scale=1.2, alpha=0.32)
    _draw_windmill(ax_l, 0.25, 0.42, scale=0.7, alpha=0.22)
    _draw_bicycle(ax_l, 0.72, 0.12, scale=0.9, alpha=0.28)

    ax_r = fig.add_axes([0.94, 0.08, 0.06, 0.82])
    ax_r.set_xlim(0, 1)
    ax_r.set_ylim(0, 1)
    ax_r.axis("off")
    for i, tx in enumerate((0.25, 0.5, 0.75)):
        _draw_tulip(ax_r, tx, 0.15 + i * 0.04, scale=1.0, alpha=0.38)
    _draw_coffee_cup(ax_r, 0.3, 0.55, scale=1.1, alpha=0.32)
    _draw_brigadeiro(ax_r, 0.65, 0.58, scale=1.0, alpha=0.32)
    _draw_beer_bottle(ax_r, 0.5, 0.72, scale=1.0, alpha=0.32)

    ax_bot = fig.add_axes([0.08, 0.03, 0.84, 0.04])
    ax_bot.set_xlim(0, 1)
    ax_bot.set_ylim(0, 1)
    ax_bot.axis("off")
    ax_bot.add_patch(Polygon([[0.0, 0.3], [1.0, 0.35], [1.0, 0.0], [0.0, 0.05]], closed=True, facecolor=COLORS["polder"], alpha=0.18, zorder=0))
    _draw_peloton(ax_bot, 0.08, 0.35, 0.84, alpha=0.2)


def generate_infographic(summary: dict) -> Path:
    """Create infographic.png in reports/YYYY-MM/ (vertical dashboard poster)."""
    month_year = summary["month_year"]
    out_dir = report_dir_for_month(month_year)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "infographic.png"

    new_members = summary.get("new_members") or []
    has_welcome = bool(new_members)
    fig_h = 19.2 if has_welcome else 17.6
    fig = plt.figure(figsize=(FIG_WIDTH, fig_h), facecolor=COLORS["bg"])
    _draw_margin_decorations(fig)

    # --- Header ---
    ax_band = fig.add_axes([0, 0.968, 1, 0.032])
    ax_band.axis("off")
    ax_band.add_patch(
        FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0", facecolor=COLORS["title_blue"], edgecolor="none")
    )

    ax_head = fig.add_axes([0.07, 0.918, 0.86, 0.055])
    ax_head.axis("off")
    ax_head.text(0.5, 0.72, "FLAT & FURIOUS", ha="center", fontsize=13, fontweight="bold", color=COLORS["brand_gold"])
    ax_head.text(
        0.5,
        0.38,
        "ANÁLISE DE CICLISMO",
        ha="center",
        fontsize=24,
        fontweight="bold",
        color=COLORS["title_orange"],
    )
    ax_head.text(
        0.5,
        0.02,
        _month_title(summary),
        ha="center",
        fontsize=16,
        fontweight="bold",
        color=COLORS["title_blue"],
    )

    y = 0.905

    # --- 1) Boas-vindas ---
    if has_welcome:
        welcome_h = 0.065
        ax_w = fig.add_axes([0.07, y - welcome_h, 0.86, welcome_h])
        _draw_welcome(ax_w, new_members)
        y -= welcome_h + 0.018

    # --- 2) Distance cards ---
    card_h = 0.105
    card_w = 0.27
    gap = 0.035
    x0 = 0.07
    year = summary.get("year", "")
    earth_pct = summary.get("earth_percent_since_group", 0) or 0
    earth_label = f"{earth_pct * 100:.0f}% volta ao mundo"

    dist_cards = [
        ("M", "Distância no mês", None, f"{summary.get('distance_month_km', 0):.0f} km", COLORS["green"], None),
        ("A", f"Total em {year}", None, f"{summary.get('distance_year_km', 0):.0f} km", COLORS["blue"], None),
        (
            "G",
            "Desde criação do grupo",
            None,
            f"{summary.get('distance_since_group_km', 0):.0f} km",
            COLORS["purple"],
            earth_label,
        ),
    ]
    for i, (icon, label, name, value, color, sub) in enumerate(dist_cards):
        ax = fig.add_axes([x0 + i * (card_w + gap), y - card_h, card_w, card_h])
        _draw_card(ax, icon=icon, label=label, name=name, value=value, value_color=color, sub=sub)
        if i == 2 and earth_pct > 0:
            bar_ax = ax.inset_axes([0.12, 0.05, 0.76, 0.055])
            bar_ax.set_xlim(0, 1)
            bar_ax.set_ylim(0, 1)
            bar_ax.axis("off")
            bar_ax.add_patch(
                FancyBboxPatch((0, 0.15), 1, 0.7, boxstyle="round,pad=0", facecolor="#ecf0f1", edgecolor="none")
            )
            bar_ax.add_patch(
                FancyBboxPatch(
                    (0, 0.15),
                    min(earth_pct / 0.5, 1.0),
                    0.7,
                    boxstyle="round,pad=0",
                    facecolor=COLORS["purple"],
                    edgecolor="none",
                )
            )

    y -= card_h + 0.022

    # --- 3) Destaques ---
    mh = summary.get("month_highlights") or {}
    highlight_labels = {
        "maior_distancia": "Maior distância",
        "mais_rapido": "Mais rápido",
        "escalador": "Escalador",
        "mais_tempo": "Mais tempo",
        "mais_pedaladas": "Pedaladas",
        "pedal_mais_longo": "Pedal + longo",
    }
    highlight_lines = []
    for key, lbl in highlight_labels.items():
        item = mh.get(key)
        if item:
            val = _format_highlight_value(key, item["value"])
            highlight_lines.append(f"{lbl}: {_first_name(item['athlete'])} — {val}")

    if highlight_lines:
        _section_title(fig, y, "DESTAQUE DO MÊS")
        y -= 0.028
        box_h = min(0.155, 0.028 + 0.021 * len(highlight_lines))
        ax_hl = fig.add_axes([0.07, y - box_h, 0.86, box_h])
        ax_hl.set_xlim(0, 1)
        ax_hl.set_ylim(0, 1)
        ax_hl.axis("off")
        _rounded_box(ax_hl, (0.01, 0.02), 0.98, 0.96, facecolor=COLORS["card"], edgecolor=COLORS["card_edge"], linewidth=1)
        ty = 0.9
        for line in highlight_lines[:6]:
            ax_hl.text(0.04, ty, line, fontsize=9.5, color=COLORS["text"], ha="left", va="top", zorder=3)
            ty -= 0.145
        y -= box_h + 0.018

    # --- 4) Podium + Curiosities ---
    row_h = 0.21
    ax_podium = fig.add_axes([0.07, y - row_h, 0.42, row_h])
    _draw_podium(ax_podium, summary.get("top3_rides") or [])

    ax_cur = fig.add_axes([0.52, y - row_h, 0.41, row_h])
    _draw_curiosities(ax_cur, summary.get("curiosities") or [])

    y -= row_h + 0.028

    # --- 5) Rankings ---
    _section_title(fig, y, "RANKINGS")
    y -= 0.028

    table_h = 0.26
    ax_month = fig.add_axes([0.07, y - table_h, 0.42, table_h])
    _draw_ranking_table(ax_month, "RANKING MENSAL", summary.get("ranking_month") or [])

    ax_year = fig.add_axes([0.52, y - table_h, 0.41, table_h])
    _draw_ranking_table(ax_year, f"RANKING ANUAL {summary.get('year', '')}", summary.get("ranking_year") or [])

    ax_foot = fig.add_axes([0.07, 0.012, 0.86, 0.018])
    ax_foot.axis("off")
    ax_foot.text(
        0.5,
        0.5,
        "Pelotão Enschede  |  NL + BR  |  Ride + VirtualRide",
        ha="center",
        fontsize=7.5,
        color=COLORS["muted"],
    )

    fig.savefig(out_path, dpi=OUTPUT_DPI, bbox_inches="tight", facecolor=COLORS["bg"], pad_inches=0.25)
    plt.close(fig)
    print(f"Infographic saved to {out_path}")
    return out_path
