"""Clean and format raw Strava activity data."""

from __future__ import annotations

import pandas as pd

from flatfurious.config import activities_path, formatted_path


def clean_and_save() -> pd.DataFrame:
    """Load raw activities, filter rides/cycles, format and save."""
    path = activities_path()
    if not path.exists():
        raise FileNotFoundError(f"Activities file not found: {path}")

    df = pd.read_csv(path, low_memory=False)
    df["start_date_local"] = pd.to_datetime(df["start_date_local"], errors="coerce")

    name_col = "nome" if "nome" in df.columns else "name"
    if name_col != "nome":
        df = df.rename(columns={name_col: "nome"})

    mask_ride = df["type"] == "Ride"
    mask_cycle = df["type"] == "Cycle"
    df_ride = df[mask_ride].copy()
    df_cycle = df[mask_cycle].copy()

    ride_out = pd.DataFrame()
    cycle_out = pd.DataFrame()

    if not df_ride.empty:
        df_ride["distance"] = (df_ride["distance"] / 1000).round(2)
        df_ride["date"] = pd.to_datetime(df_ride["start_date_local"]).dt.date
        df_ride["moving_time"] = pd.to_timedelta(df_ride["moving_time"], unit="s")
        df_ride["elapsed_time"] = pd.to_timedelta(df_ride["elapsed_time"], unit="s")
        df_ride["moving_time"] = df_ride["moving_time"].apply(
            lambda x: str(x).split()[-1]
        )
        df_ride["elapsed_time"] = df_ride["elapsed_time"].apply(
            lambda x: str(x).split()[-1]
        )
        df_ride["average_speed"] = (df_ride["average_speed"] * 3.6).round(1)
        df_ride["max_speed"] = (df_ride["max_speed"] * 3.6).round(1)
        df_ride["average_heartrate"] = pd.to_numeric(
            df_ride.get("average_heartrate"), errors="coerce"
        )
        df_ride["max_heartrate"] = pd.to_numeric(
            df_ride.get("max_heartrate"), errors="coerce"
        )
        df_ride.rename(columns={"nome": "athlete"}, inplace=True)

        cols_ride = [
            "athlete",
            "date",
            "distance",
            "moving_time",
            "elapsed_time",
            "average_speed",
            "max_speed",
            "average_heartrate",
            "max_heartrate",
        ]
        cols_ride = [c for c in cols_ride if c in df_ride.columns]
        ride_out = df_ride[cols_ride].copy()
        ride_out["activity_type"] = "Ride"

    if not df_cycle.empty:
        df_cycle["date"] = pd.to_datetime(df_cycle["start_date_local"]).dt.date
        df_cycle["moving_time"] = pd.to_timedelta(df_cycle["moving_time"], unit="s")
        df_cycle["moving_time"] = df_cycle["moving_time"].apply(
            lambda x: str(x).split()[-1]
        )
        df_cycle.rename(columns={"nome": "athlete"}, inplace=True)
        cols_cycle = ["athlete", "date", "moving_time"]
        cols_cycle = [c for c in cols_cycle if c in df_cycle.columns]
        cycle_out = df_cycle[cols_cycle].copy()
        cycle_out["activity_type"] = "Cycle"

    combined = pd.concat([ride_out, cycle_out], ignore_index=True, sort=True)
    final_cols = [
        "athlete",
        "activity_type",
        "date",
        "distance",
        "moving_time",
        "elapsed_time",
        "average_speed",
        "max_speed",
        "average_heartrate",
        "max_heartrate",
    ]
    final_cols = [c for c in final_cols if c in combined.columns]
    df_formatted = combined[final_cols].copy()

    out = formatted_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    df_formatted.to_csv(out, index=False)
    print(f"Formatted data saved to {out}")
    return df_formatted
