"""Collect activities from Strava API for all authorized athletes."""

from __future__ import annotations

import time

import pandas as pd
import requests

from flatfurious.config import activities_path
from flatfurious.strava.auth import load_tokens


def _fetch_activities(token: str, after: int | None = None) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    all_activities: list[dict] = []
    page = 1
    per_page = 200

    while True:
        params: dict = {"per_page": per_page, "page": page}
        if after is not None:
            params["after"] = after

        resp = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers=headers,
            params=params,
            timeout=60,
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Strava API error {resp.status_code}: {resp.text[:500]}"
            )

        batch = resp.json()
        if not batch:
            break

        all_activities.extend(batch)
        if len(batch) < per_page:
            break
        page += 1
        time.sleep(0.2)

    return all_activities


def _after_timestamp_for_athlete(
    existing: pd.DataFrame, athlete_name: str
) -> int | None:
    if existing.empty or "nome" not in existing.columns:
        return None

    subset = existing[existing["nome"] == athlete_name]
    if subset.empty or "start_date" not in subset.columns:
        return None

    dates = pd.to_datetime(subset["start_date"], utc=True, errors="coerce")
    latest = dates.max()
    if pd.isna(latest):
        return None
    return int(latest.timestamp())


def collect_all(full_refresh: bool = False) -> pd.DataFrame:
    """Collect activities for all athletes and save to activities_all.csv."""
    df_tokens = load_tokens()
    if df_tokens.empty:
        raise RuntimeError("No tokens found. Run: python -m flatfurious auth --code ...")

    path = activities_path()
    existing = pd.DataFrame()
    if path.exists() and not full_refresh:
        existing = pd.read_csv(path, low_memory=False)

    new_parts: list[pd.DataFrame] = []
    processed_names: set[str] = set()

    for _, row in df_tokens.iterrows():
        name = row["nome"]
        token = row["access_token"]
        processed_names.add(name)
        print(f"Collecting activities for {name}...")

        after = None if full_refresh else _after_timestamp_for_athlete(existing, name)

        try:
            raw = _fetch_activities(token, after=after)
        except RuntimeError as exc:
            print(f"Warning: {exc}")
            if not existing.empty:
                prev = existing[existing["nome"] == name]
                if not prev.empty:
                    new_parts.append(prev)
            continue

        if not raw:
            print(f"No new activities for {name}")
            if not existing.empty:
                prev = existing[existing["nome"] == name]
                if not prev.empty:
                    new_parts.append(prev)
            continue

        df_new = pd.json_normalize(raw)
        df_new["nome"] = name
        print(f"Fetched {len(raw)} activities for {name}")

        if not full_refresh and not existing.empty:
            prev = existing[existing["nome"] == name]
            if (
                not prev.empty
                and "id" in df_new.columns
                and "id" in prev.columns
            ):
                prev_ids = set(prev["id"].astype(str))
                df_new = df_new[~df_new["id"].astype(str).isin(prev_ids)]
                combined = pd.concat([prev, df_new], ignore_index=True)
            elif not prev.empty:
                combined = pd.concat([prev, df_new], ignore_index=True)
            else:
                combined = df_new
        else:
            combined = df_new

        new_parts.append(combined)

    if not existing.empty:
        for name in existing["nome"].unique():
            if name not in processed_names:
                new_parts.append(existing[existing["nome"] == name])

    if not new_parts:
        raise RuntimeError("No activities collected.")

    df_all = pd.concat(new_parts, ignore_index=True)
    if "id" in df_all.columns:
        df_all = df_all.drop_duplicates(subset=["id"], keep="last")

    path.parent.mkdir(parents=True, exist_ok=True)
    df_all.to_csv(path, index=False)
    print(f"Saved {len(df_all)} activities to {path}")
    return df_all
