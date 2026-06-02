"""Aggregated metrics for PDF reports (group join date aware)."""
from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from flatfurious.config import formatted_path, group_start_date
from flatfurious.data.activities import filter_cycling
from flatfurious.data.members import filter_rides_for_group, load_members

@dataclass
class PdfMetrics:
    month_year: str
    month_label_pt: str
    year: int
    distance_year_group_km: float
    distance_since_group_creation_km: float
    top3_month_distance: list
    ranking_month: list
    ranking_year: list
    top3_climbers_month: list
    top3_speed_month: list

MONTH_NAMES_PT = {1:"Janeiro",2:"Fevereiro",3:"Marco",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

def load_rides_filtered():
    path = formatted_path()
    if not path.exists():
        raise FileNotFoundError(f"Formatted data not found: {path}. Run sync first.")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    rides = filter_cycling(df)
    return filter_rides_for_group(rides, load_members())

def _month_label(month_year):
    y, m = map(int, month_year.split("-"))
    return f"{MONTH_NAMES_PT.get(m, month_year)}/{y}"

def _year_through_month_mask(dates: pd.Series, month_year: str) -> pd.Series:
    year, month = map(int, month_year.split("-"))
    end = pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)
    return (dates.dt.year == year) & (dates <= end)


def build_pdf_metrics(month_year: str) -> PdfMetrics:
    rides = load_rides_filtered()
    rides["month_year"] = rides["date"].dt.to_period("M").astype(str)
    year = int(month_year.split("-")[0])
    group_start = group_start_date()
    df_month = rides[rides["month_year"] == month_year]
    df_year = rides[_year_through_month_mask(rides["date"], month_year)]
    df_since = rides[rides["date"] >= group_start]
    distance_year = float(df_year["distance"].sum()) if not df_year.empty else 0.0
    distance_since = float(df_since["distance"].sum()) if not df_since.empty else 0.0
    top3_month = []
    ranking_month = []
    if not df_month.empty:
        month_totals = df_month.groupby("athlete")["distance"].sum().sort_values(ascending=False)
        for athlete, km in month_totals.head(3).items():
            top3_month.append({"athlete": athlete, "distance_km": round(float(km), 1)})
        for i, (athlete, km) in enumerate(month_totals.items(), 1):
            ranking_month.append(
                {"rank": i, "athlete": athlete, "distance_km": round(float(km), 2)}
            )
    ranking_year = []
    if not df_year.empty:
        for i, (athlete, km) in enumerate(df_year.groupby("athlete")["distance"].sum().sort_values(ascending=False).items(), 1):
            ranking_year.append({"rank": i, "athlete": athlete, "distance_km": round(float(km), 2)})
    top3_climbers = []
    if not df_month.empty and "elevation_gain_m" in df_month.columns:
        for athlete, meters in df_month.groupby("athlete")["elevation_gain_m"].sum().sort_values(ascending=False).head(3).items():
            top3_climbers.append({"athlete": athlete, "elevation_m": round(float(meters), 0)})
    top3_speed = []
    if not df_month.empty and "max_speed" in df_month.columns:
        for athlete, kmh in df_month.groupby("athlete")["max_speed"].max().sort_values(ascending=False).head(3).items():
            top3_speed.append({"athlete": athlete, "max_speed_kmh": round(float(kmh), 1)})
    return PdfMetrics(
        month_year,
        _month_label(month_year),
        year,
        round(distance_year, 0),
        round(distance_since, 0),
        top3_month,
        ranking_month,
        ranking_year,
        top3_climbers,
        top3_speed,
    )
