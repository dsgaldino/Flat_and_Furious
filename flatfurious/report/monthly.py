"""Build monthly summary as structured data and text report."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from flatfurious.config import formatted_path, group_start_date, reports_dir
from flatfurious.data.activities import filter_cycling
from flatfurious.data.members import (
    filter_rides_for_group,
    load_members,
    members_eligible_through_month,
    new_members_in_month,
)
from flatfurious.report.curiosidades_auto import gerar_curiosidades_auto

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


def _load_rides() -> pd.DataFrame:
    """Rides from formatted CSV, respecting group_join_date per athlete."""
    path = formatted_path()
    if not path.exists():
        raise FileNotFoundError(f"Formatted data not found: {path}. Run sync first.")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    rides = filter_cycling(df)
    rides = filter_rides_for_group(rides, load_members())
    rides["month_year"] = rides["date"].dt.to_period("M").astype(str)
    return rides


def _through_month_end(month_year: str) -> pd.Timestamp:
    """Last calendar day of month_year (YYYY-MM)."""
    year, month = map(int, month_year.split("-"))
    return pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)


def _year_through_month_mask(dates: pd.Series, month_year: str) -> pd.Series:
    """True for rides from 1 Jan of that year through the last day of month_year."""
    year, month = map(int, month_year.split("-"))
    end = _through_month_end(month_year)
    return (dates.dt.year == year) & (dates <= end)


def _since_group_through_month_mask(dates: pd.Series, month_year: str) -> pd.Series:
    """Rides from group creation through the last day of the report month."""
    group_start = pd.Timestamp(group_start_date())
    end = _through_month_end(month_year)
    return (dates >= group_start) & (dates <= end)


def _format_duration(td: pd.Timedelta) -> str:
    total_seconds = int(td.total_seconds())
    horas = total_seconds // 3600
    minutos = (total_seconds % 3600) // 60
    return f"{horas}h{minutos:02d}m"


def _athlete_stat(
    athlete: str, value: str, *, metric: str | None = None
) -> dict[str, str]:
    return {"athlete": athlete, "value": value, "metric": metric or ""}


def _build_month_highlights(df_month: pd.DataFrame) -> dict[str, dict | None]:
    """Per-category leader for the Destaque do Mes section."""
    if df_month.empty:
        return {
            "maior_distancia": None,
            "mais_rapido": None,
            "escalador": None,
            "mais_tempo": None,
            "mais_pedaladas": None,
            "pedal_mais_longo": None,
        }

    out: dict[str, dict | None] = {}

    by_dist = df_month.groupby("athlete")["distance"].sum().sort_values(ascending=False)
    if not by_dist.empty:
        out["maior_distancia"] = _athlete_stat(
            by_dist.index[0], f"{by_dist.iloc[0]:.0f} km"
        )

    # Maior velocidade registrada (pico max_speed Strava); rides >= 10 km evitam spike em trecho curto
    if "max_speed" in df_month.columns:
        df_sp = df_month[df_month["distance"] >= 10]
        if df_sp.empty:
            df_sp = df_month[df_month["distance"] > 0]
        if not df_sp.empty:
            peak = df_sp.groupby("athlete")["max_speed"].max().sort_values(ascending=False)
            out["mais_rapido"] = _athlete_stat(
                peak.index[0],
                f"{peak.iloc[0]:.1f} km/h",
            )

    if "elevation_gain_m" in df_month.columns:
        elev = (
            df_month.groupby("athlete")["elevation_gain_m"]
            .sum()
            .sort_values(ascending=False)
        )
        if elev.iloc[0] > 0:
            out["escalador"] = _athlete_stat(
                elev.index[0], f"{elev.iloc[0]:.0f} m"
            )

    df_mt = df_month.copy()
    df_mt["moving_time_td"] = pd.to_timedelta(df_mt["moving_time"])
    time_sum = df_mt.groupby("athlete")["moving_time_td"].sum().sort_values(ascending=False)
    if not time_sum.empty:
        out["mais_tempo"] = _athlete_stat(
            time_sum.index[0], _format_duration(time_sum.iloc[0])
        )

    ride_counts = df_month["athlete"].value_counts().sort_values(ascending=False)
    if not ride_counts.empty:
        out["mais_pedaladas"] = _athlete_stat(
            ride_counts.index[0], f"{int(ride_counts.iloc[0])} pedaladas"
        )

    longest = df_month[df_month["distance"] > 0].sort_values("distance", ascending=False)
    if not longest.empty:
        row = longest.iloc[0]
        out["pedal_mais_longo"] = _athlete_stat(
            row["athlete"], f"{float(row['distance']):.1f} km"
        )

    return out


def _build_ranking(
    df: pd.DataFrame, month_year: str, members: pd.DataFrame
) -> list[dict]:
    """Ranking with every group member eligible through month_year; missing data = 0 km."""
    eligible = members_eligible_through_month(month_year, members)
    if not eligible:
        return []

    if df.empty:
        totals = {name: 0.0 for name in eligible}
    else:
        summed = df.groupby("athlete")["distance"].sum()
        totals = {name: float(summed.get(name, 0.0)) for name in eligible}

    ordered = sorted(totals.keys(), key=lambda name: (-totals[name], name.lower()))
    return [
        {
            "rank": i + 1,
            "athlete": name,
            "distance_km": round(totals[name], 2),
        }
        for i, name in enumerate(ordered)
    ]


def build_summary(month_year: str) -> dict:
    """Compute monthly summary dict for month_year (YYYY-MM)."""
    rides = _load_rides()
    members = load_members()
    df_month = rides[rides["month_year"] == month_year].copy()
    year = int(month_year.split("-")[0])
    df_year = rides[_year_through_month_mask(rides["date"], month_year)].copy()

    distance_month = float(df_month["distance"].sum()) if not df_month.empty else 0.0
    dist_total_year = float(df_year["distance"].sum()) if not df_year.empty else 0.0

    df_since = rides[_since_group_through_month_mask(rides["date"], month_year)]
    distance_since = float(df_since["distance"].sum()) if not df_since.empty else 0.0
    earth_percent_since = distance_since / AROUND_EARTH_KM

    month_highlights = _build_month_highlights(df_month)

    top3 = []
    if not df_month.empty:
        top3_df = (
            df_month[df_month["distance"] > 0]
            .sort_values("distance", ascending=False)
            .head(3)
        )
        for _, row in top3_df.iterrows():
            top3.append({"athlete": row["athlete"], "distance_km": round(float(row["distance"]), 1)})

    ranking_month = _build_ranking(df_month, month_year, members)
    ranking_year = _build_ranking(df_year, month_year, members)

    eligible_count = len(members_eligible_through_month(month_year, members))
    ride_count = len(df_month) if not df_month.empty else 0
    athlete_count = df_month["athlete"].nunique() if not df_month.empty else 0
    elevation_m = (
        float(df_month["elevation_gain_m"].sum())
        if not df_month.empty and "elevation_gain_m" in df_month.columns
        else 0.0
    )
    moving_hours = 0.0
    if not df_month.empty:
        moving_hours = (
            pd.to_timedelta(df_month["moving_time"]).sum().total_seconds() / 3600
        )
    longest_km = (
        float(df_month["distance"].max()) if not df_month.empty else 0.0
    )
    weekend_rides = (
        len(df_month[df_month["date"].dt.dayofweek >= 5]) if not df_month.empty else 0
    )

    curiosities = gerar_curiosidades_auto(
        month_year,
        distance_month,
        ride_count=ride_count,
        athlete_count=athlete_count,
        eligible_athlete_count=eligible_count,
        elevation_m=elevation_m,
        moving_hours=moving_hours,
        longest_ride_km=longest_km,
        weekend_rides=weekend_rides,
    )

    new_members = new_members_in_month(month_year)
    y, m = map(int, month_year.split("-"))
    label_pt = f"{MONTH_NAMES_PT.get(m, month_year)}/{y}"
    year_label_pt = (
        f"ate {MONTH_NAMES_PT.get(m, month_year).lower()}/{y}"
        if m < 12
        else str(year)
    )
    gs_label = pd.Timestamp(group_start_date()).strftime("%d/%m/%Y")

    return {
        "month_year": month_year,
        "month_label_pt": label_pt,
        "year_label_pt": year_label_pt,
        "group_start_label": gs_label,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "distance_month_km": round(distance_month, 0),
        "distance_year_km": round(dist_total_year, 0),
        "distance_since_group_km": round(distance_since, 0),
        "earth_percent_since_group": round(earth_percent_since, 4),
        "year": year,
        "month_highlights": month_highlights,
        "top3_rides": top3,
        "ranking_month": ranking_month,
        "ranking_year": ranking_year,
        "new_members": new_members,
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
