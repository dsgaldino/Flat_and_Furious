"""Generate infographic PNG for monthly report."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

from flatfurious.config import formatted_path
from flatfurious.report.monthly import report_dir_for_month

AROUND_EARTH_KM = 40075


def _faixa_distancia(km: float) -> str:
    return f"{int(round(km / 10) * 10)} km"


def generate_infographic(summary: dict) -> Path:
    """Create infographic.png in reports/YYYY-MM/."""
    month_year = summary["month_year"]
    out_dir = report_dir_for_month(month_year)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "infographic.png"

    df = pd.read_csv(formatted_path())
    df["date"] = pd.to_datetime(df["date"])
    df["month_year"] = df["date"].dt.to_period("M").astype(str)
    rides = df[df.get("activity_type", "Ride") == "Ride"].copy()
    if rides.empty:
        rides = df[df["distance"].notna()].copy()
    df_month = rides[rides["month_year"] == month_year].copy()

    fig = plt.figure(figsize=(12, 10), facecolor="#1a1a2e")
    fig.suptitle(
        f"Flat & Furious — {summary['month_label_pt']}",
        fontsize=20,
        fontweight="bold",
        color="white",
        y=0.98,
    )

    ax_main = fig.add_axes([0.08, 0.55, 0.84, 0.35])
    ax_main.set_facecolor("#16213e")
    ax_main.axis("off")

    highlights = [
        f"Grupo no mes: {summary['distance_month_km']:.0f} km",
        f"Ano {summary['year']}: {summary['distance_year_km']:.0f} km "
        f"({summary['earth_percent_year']:.1%} volta ao mundo)",
    ]
    if summary.get("fastest"):
        f = summary["fastest"]
        highlights.append(f"Mais rapido: {f['athlete']} — {f['max_speed_kmh']} km/h")
    if summary.get("ranking_month") and summary["ranking_month"]:
        k = summary["ranking_month"][0]
        highlights.append(f"Lider do mes: {k['athlete']} — {k['distance_km']:.0f} km")

    ax_main.text(
        0.05,
        0.85,
        "\n".join(highlights),
        fontsize=14,
        color="#e94560",
        va="top",
        family="sans-serif",
    )

    if summary.get("top3_rides"):
        top_lines = ["Top 3 pedaladas:"] + [
            f"  {i}. {r['athlete']} — {r['distance_km']} km"
            for i, r in enumerate(summary["top3_rides"], 1)
        ]
        ax_main.text(
            0.05,
            0.35,
            "\n".join(top_lines),
            fontsize=12,
            color="white",
            va="top",
            family="sans-serif",
        )

    ax_rank = fig.add_axes([0.08, 0.08, 0.45, 0.42])
    ax_rank.set_facecolor("#16213e")
    if summary.get("ranking_month"):
        names = [r["athlete"].split()[0] for r in summary["ranking_month"][:8]]
        dists = [r["distance_km"] for r in summary["ranking_month"][:8]]
        colors = ["#e94560" if i == 0 else "#0f3460" for i in range(len(names))]
        ax_rank.barh(names[::-1], dists[::-1], color=colors[::-1])
        ax_rank.set_xlabel("km", color="white")
        ax_rank.tick_params(colors="white")
        ax_rank.set_title("Ranking mensal", color="white", fontsize=12)
        for spine in ax_rank.spines.values():
            spine.set_color("#333")
    else:
        ax_rank.axis("off")
        ax_rank.text(0.5, 0.5, "Sem dados", ha="center", color="white")

    ax_wc = fig.add_axes([0.58, 0.08, 0.36, 0.42])
    ax_wc.axis("off")
    if not df_month.empty:
        df_month = df_month.copy()
        df_month["faixa"] = df_month["distance"].apply(_faixa_distancia)
        freq = df_month["faixa"].value_counts().to_dict()
        if freq:
            wc = WordCloud(
                width=400,
                height=300,
                background_color="#16213e",
                colormap="plasma",
            ).generate_from_frequencies(freq)
            ax_wc.imshow(wc, interpolation="bilinear")
            ax_wc.set_title("Distancias comuns", color="white", fontsize=10)

    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Infographic saved to {out_path}")
    return out_path
