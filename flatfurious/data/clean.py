"""Clean and format raw Strava activity data."""

from __future__ import annotations

import pandas as pd

from flatfurious.config import activities_path, formatted_path
from flatfurious.data.activities import CYCLING_STRAVA_TYPES
from flatfurious.data.members import canonical_athlete_name, load_members


def _format_cycling(df: pd.DataFrame) -> pd.DataFrame:
    """Format Ride and VirtualRide rows for reports."""
    out = df.copy()
    out["distance"] = (out["distance"] / 1000).round(2)
    out["date"] = pd.to_datetime(out["start_date_local"]).dt.date
    out["moving_time"] = pd.to_timedelta(out["moving_time"], unit="s")
    out["elapsed_time"] = pd.to_timedelta(out["elapsed_time"], unit="s")
    out["moving_time"] = out["moving_time"].apply(lambda x: str(x).split()[-1])
    out["elapsed_time"] = out["elapsed_time"].apply(lambda x: str(x).split()[-1])
    out["average_speed"] = (out["average_speed"] * 3.6).round(1)
    out["max_speed"] = (out["max_speed"] * 3.6).round(1)
    out["average_heartrate"] = pd.to_numeric(out.get("average_heartrate"), errors="coerce")
    out["max_heartrate"] = pd.to_numeric(out.get("max_heartrate"), errors="coerce")
    if "total_elevation_gain" in out.columns:
        out["elevation_gain_m"] = pd.to_numeric(
            out["total_elevation_gain"], errors="coerce"
        ).round(0)
    out.rename(columns={"nome": "athlete"}, inplace=True)
    out["activity_type"] = out["type"]

    cols = [
        "athlete",
        "activity_type",
        "date",
        "distance",
        "moving_time",
        "elapsed_time",
        "average_speed",
        "max_speed",
        "elevation_gain_m",
        "average_heartrate",
        "max_heartrate",
    ]
    cols = [c for c in cols if c in out.columns]
    return out[cols].copy()


def clean_and_save() -> pd.DataFrame:
    """Load raw activities, keep Ride + VirtualRide, format and save."""
    path = activities_path()
    if not path.exists():
        raise FileNotFoundError(f"Activities file not found: {path}")

    df = pd.read_csv(path, low_memory=False)
    df["start_date_local"] = pd.to_datetime(df["start_date_local"], errors="coerce")

    name_col = "nome" if "nome" in df.columns else "name"
    if name_col != "nome":
        df = df.rename(columns={name_col: "nome"})

    df_cycling = df[df["type"].isin(CYCLING_STRAVA_TYPES)].copy()
    ride_out = _format_cycling(df_cycling) if not df_cycling.empty else pd.DataFrame()

    members = load_members()
    if not ride_out.empty:
        ride_out["athlete"] = ride_out["athlete"].map(
            lambda n: canonical_athlete_name(n, members)
        )

    out = formatted_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    ride_out.to_csv(out, index=False)
    print(f"Formatted data saved to {out} ({len(ride_out)} cycling activities)")
    return ride_out
