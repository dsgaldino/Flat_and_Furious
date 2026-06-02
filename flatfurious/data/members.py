"""Group membership dates for activity filtering."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from flatfurious.config import data_dir, group_start_date


def members_path() -> Path:
    return data_dir() / "members.csv"


def canonical_athlete_name(name: str, members: pd.DataFrame | None = None) -> str:
    """Match members.csv spelling; otherwise title-case each word."""
    if not name or not str(name).strip():
        return name
    members = members if members is not None else load_members()
    key = str(name).strip().lower()
    for official in members["nome"]:
        if official.lower() == key:
            return official
    return " ".join(part.capitalize() for part in str(name).split())


def load_members() -> pd.DataFrame:
    path = members_path()
    if not path.exists():
        raise FileNotFoundError(
            f"Members file not found: {path}. Create data/members.csv with nome, group_join_date."
        )
    df = pd.read_csv(path)
    if "nome" not in df.columns or "group_join_date" not in df.columns:
        raise ValueError("members.csv must have columns: nome, group_join_date")
    df["group_join_date"] = pd.to_datetime(df["group_join_date"]).dt.normalize()
    return df


def filter_rides_for_group(df: pd.DataFrame, members: pd.DataFrame | None = None) -> pd.DataFrame:
    """Keep only rides on or after each athlete group_join_date."""
    if df.empty:
        return df

    members = members if members is not None else load_members()
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"]).dt.normalize()
    join_map = dict(zip(members["nome"], members["group_join_date"]))

    def keep_row(row: pd.Series) -> bool:
        athlete = row["athlete"]
        cutoff = join_map.get(athlete, pd.Timestamp(group_start_date()))
        return row["date"] >= cutoff

    mask = out.apply(keep_row, axis=1)
    return out.loc[mask].copy()


def members_eligible_through_month(
    month_year: str, members: pd.DataFrame | None = None
) -> list[str]:
    """Members with group_join_date on or before the last day of month_year."""
    members = members if members is not None else load_members()
    year, month = map(int, month_year.split("-"))
    end = pd.Timestamp(year=year, month=month, day=1) + pd.offsets.MonthEnd(0)
    eligible = members[members["group_join_date"] <= end].sort_values("nome")
    return eligible["nome"].tolist()


def new_members_in_month(
    month_year: str, members: pd.DataFrame | None = None
) -> list[dict[str, str]]:
    """Members whose group_join_date falls in month_year (YYYY-MM)."""
    members = members if members is not None else load_members()
    year, month = map(int, month_year.split("-"))
    in_month = (members["group_join_date"].dt.year == year) & (
        members["group_join_date"].dt.month == month
    )
    rows = []
    for _, row in members.loc[in_month].iterrows():
        rows.append(
            {
                "nome": row["nome"],
                "group_join_date": row["group_join_date"].strftime("%d/%m/%Y"),
            }
        )
    return rows
