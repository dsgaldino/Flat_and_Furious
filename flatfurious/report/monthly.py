"""Build monthly summary as structured data and text report."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from flatfurious.config import formatted_path, reports_dir
from flatfurious.report.curiosidades import gerar_curiosidades

AROUND_EARTH_KM = 40075
MONTH_NAMES_PT = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Marco",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def _load_formatted() -> pd.DataFrame:
    path = formatted_path()
    if not path.exists():
        raise FileNotFoundError(f"Formatted data not found: {path}. Run sync first.")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df["month_year"] = df["date"].dt.to_period("M").astype(str)
    return df


def _format_duration(td: pd.Timedelta) -> str:
    total_seconds = int(td.total_seconds())
    horas = total_seconds // 3600
    minutos = (total_seconds % 3600) // 60
    return f"{horas}h{minutos:02d}m"


def build_summary(month_year: str) -> dict:
    """Compute monthly summary dict for month_year (YYYY-MM)."""
    df = _load_formatted()
    rides = df[df.get("activity_type", "Ride") == "Ride"].copy()
    if rides.empty:
        rides = df[df["distance"].notna()].copy()

    df_month = rides[rides["month_year"] == month_year].copy()
    year = int(month_year.split("-")[0])
    df_year = rides[rides["date"].dt.year == year].copy()

    distance_month = float(df_month["distance"].sum()) if not df_month.empty else 0.0
    dist_total_year = float(df_year["distance"].sum()) if not df_year.empty else 0.0
    percentual_earth = dist_total_year / AROUND_EARTH_KM

    fastest = None
    if not df_month.empty and "max_speed" in df_month.columns:
        row = df_month.loc[df_month["max_speed"].idxmax()]
        fastest = {"athlete": row["athlete"], "max_speed_kmh": round(float(row["max_speed"]), 1)}

    most_time = None
    if not df_month.empty:
        df_mt = df_month.copy()
        df_mt["moving_time_td"] = pd.to_timedelta(df_mt["moving_time"])
        total_time = df_mt.groupby("athlete", as_index=False)["moving_time_td"].sum()
        top = total_time.loc[total_time["moving_time_td"].idxmax()]
        most_time = {
            "athlete": top["athlete"],
            "duration": _format_duration(top["moving_time_td"]),
        }

    top3 = []
    if not df_month.empty:
        top3_df = df_month.sort_values("distance", ascending=False).head(3)
        for _, row in top3_df.iterrows():
            top3.append({"athlete": row["athlete"], "distance_km": round(float(row["distance"]), 1)})

    ranking_month = []
    if not df_month.empty:
        rm = (
            df_month.groupby("athlete")["distance"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        for i, row in rm.iterrows():
            ranking_month.append(
                {"rank": i + 1, "athlete": row["athlete"], "distance_km": round(float(row["distance"]), 2)}
            )

    ranking_year = []
    if not df_year.empty:
        ry = (
            df_year.groupby("athlete")["distance"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        for i, row in ry.iterrows():
            ranking_year.append(
                {"rank": i + 1, "athlete": row["athlete"], "distance_km": round(float(row["distance"]), 2)}
            )

    least_active = None
    if not df_month.empty:
        activity_counts = df_month["athlete"].value_counts()
        distance_sum = df_month.groupby("athlete")["distance"].sum()
        df_stats = pd.DataFrame(
            {"activities": activity_counts, "total_km": distance_sum}
        ).fillna(0)
        least = df_stats.sort_values(by=["activities", "total_km"]).head(1)
        for name, row in least.iterrows():
            least_active = {
                "athlete": name,
                "activities": int(row["activities"]),
                "total_km": round(float(row["total_km"]), 1),
            }

    least_weekend = None
    if not df_month.empty:
        df_weekend = df_month[df_month["date"].dt.dayofweek >= 5]
        weekend_counts = df_weekend["athlete"].value_counts()
        athletes = sorted(df_month["athlete"].unique().tolist())
        df_wk = pd.DataFrame({"weekend_rides": weekend_counts}).reindex(athletes).fillna(0)
        lw = df_wk.sort_values("weekend_rides").head(1)
        for name, row in lw.iterrows():
            least_weekend = {
                "athlete": name,
                "weekend_rides": int(row["weekend_rides"]),
            }

    curiosities = gerar_curiosidades(distance_month, month_year)
    y, m = map(int, month_year.split("-"))
    label_pt = f"{MONTH_NAMES_PT.get(m, month_year)}/{y}"

    return {
        "month_year": month_year,
        "month_label_pt": label_pt,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "distance_month_km": round(distance_month, 0),
        "distance_year_km": round(dist_total_year, 0),
        "earth_percent_year": round(percentual_earth, 4),
        "year": year,
        "fastest": fastest,
        "most_moving_time": most_time,
        "top3_rides": top3,
        "ranking_month": ranking_month,
        "ranking_year": ranking_year,
        "least_active": least_active,
        "least_weekend": least_weekend,
        "curiosities": curiosities,
    }


def report_dir_for_month(month_year: str) -> Path:
    return reports_dir() / month_year


def save_summary(month_year: str, summary: dict | None = None) -> Path:
    """Build and save summary.json for the month."""
    if summary is None:
        summary = build_summary(month_year)
    out_dir = report_dir_for_month(month_year)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "summary.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Summary saved to {path}")
    return path


def previous_month() -> str:
    from datetime import timedelta

    today = datetime.today()
    first = today.replace(day=1)
    prev = first - timedelta(days=1)
    return prev.strftime("%Y-%m")
