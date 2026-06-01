"""Exchange Strava authorization code for tokens and persist to CSV."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import pandas as pd
import requests

from flatfurious.config import client_id, client_secret, strava_redirect_uri, tokens_path

REQUIRED_TOKEN_COLUMNS = [
    "nome",
    "athlete_id",
    "access_token",
    "refresh_token",
    "expires_at",
]

PROFILE_COLUMNS = [
    "username",
    "scope",
    "token_type",
    "expires_in",
    "firstname",
    "lastname",
    "city",
    "state",
    "country",
    "sex",
    "premium",
    "summit",
    "strava_created_at",
    "strava_updated_at",
    "profile_url",
    "profile_medium_url",
]

CSV_COLUMN_ORDER = REQUIRED_TOKEN_COLUMNS + PROFILE_COLUMNS

# Backward compatibility
TOKEN_COLUMNS = REQUIRED_TOKEN_COLUMNS


def extract_code_from_input(raw: str) -> str:
    """Accept raw code or full redirect URL."""
    raw = raw.strip()
    if "code=" in raw:
        parsed = urlparse(raw)
        params = parse_qs(parsed.query)
        if "code" in params:
            return params["code"][0]
        match = re.search(r"code=([^&\s]+)", raw)
        if match:
            return match.group(1)
    return raw


def token_response_to_row(data: dict[str, Any]) -> dict[str, Any]:
    """Flatten Strava OAuth token JSON into a CSV row."""
    athlete = data.get("athlete") or {}
    first = athlete.get("firstname", "")
    last = athlete.get("lastname", "")

    return {
        "nome": f"{first} {last}".strip(),
        "athlete_id": int(athlete["id"]),
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_at": int(data["expires_at"]),
        "username": athlete.get("username"),
        "scope": data.get("scope"),
        "token_type": data.get("token_type"),
        "expires_in": data.get("expires_in"),
        "firstname": first,
        "lastname": last,
        "city": athlete.get("city"),
        "state": athlete.get("state"),
        "country": athlete.get("country"),
        "sex": athlete.get("sex"),
        "premium": athlete.get("premium"),
        "summit": athlete.get("summit"),
        "strava_created_at": athlete.get("created_at"),
        "strava_updated_at": athlete.get("updated_at"),
        "profile_url": athlete.get("profile"),
        "profile_medium_url": athlete.get("profile_medium"),
    }


def normalize_tokens_df(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure required columns exist; keep extra columns; order known columns first."""
    if df.empty:
        return pd.DataFrame(columns=CSV_COLUMN_ORDER)

    rename = {}
    if "name" in df.columns and "nome" not in df.columns:
        rename["name"] = "nome"
    df = df.rename(columns=rename)

    for col in REQUIRED_TOKEN_COLUMNS:
        if col not in df.columns:
            df[col] = None

    if "athlete_id" in df.columns:
        df["athlete_id"] = pd.to_numeric(df["athlete_id"], errors="coerce").astype("Int64")

    extra = [c for c in df.columns if c not in CSV_COLUMN_ORDER]
    ordered = [c for c in CSV_COLUMN_ORDER if c in df.columns] + extra
    return df[ordered]


def load_tokens() -> pd.DataFrame:
    path = tokens_path()
    if not path.exists():
        return pd.DataFrame(columns=CSV_COLUMN_ORDER)
    df = pd.read_csv(path)
    return normalize_tokens_df(df)


def save_tokens(df: pd.DataFrame) -> Path:
    path = tokens_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    _dedupe_by_athlete_id(normalize_tokens_df(df)).to_csv(path, index=False)
    return path


def _athlete_id_key(value: Any) -> str:
    """Normalize athlete_id for comparisons (20232024.0 == 20232024)."""
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        return str(value)


def _dedupe_by_athlete_id(df: pd.DataFrame) -> pd.DataFrame:
    """Keep the latest token row per athlete (highest expires_at)."""
    if df.empty or "athlete_id" not in df.columns:
        return df

    out = df.copy()
    out["_athlete_key"] = out["athlete_id"].map(_athlete_id_key)
    if "expires_at" in out.columns:
        out["_expires_at"] = pd.to_numeric(out["expires_at"], errors="coerce").fillna(0)
        out = out.sort_values("_expires_at").drop_duplicates("_athlete_key", keep="last")
    else:
        out = out.drop_duplicates("_athlete_key", keep="last")
    return out.drop(columns=["_athlete_key", "_expires_at"], errors="ignore").reset_index(drop=True)


def _upsert_row(df: pd.DataFrame, new_row: dict[str, Any]) -> pd.DataFrame:
    athlete_id = _athlete_id_key(new_row["athlete_id"])

    if not df.empty and "athlete_id" in df.columns:
        mask = df["athlete_id"].map(_athlete_id_key) == athlete_id
        if mask.any():
            idx = df.index[mask][0]
            for key, val in new_row.items():
                df.at[idx, key] = val
            return _dedupe_by_athlete_id(df)

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return _dedupe_by_athlete_id(df)


def add_athlete_from_token_response(data: dict[str, Any]) -> str:
    """Register or update athlete from full Strava OAuth token response."""
    new_row = token_response_to_row(data)
    df = load_tokens()
    df = _upsert_row(df, new_row)
    save_tokens(df)
    return new_row["nome"]


def parse_token_response_text(text: str) -> dict[str, Any]:
    """Parse JSON or Python dict literal (as pasted from Strava)."""
    text = text.strip()
    if not text:
        raise ValueError("Empty token response")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    return ast.literal_eval(text)


def exchange_code(auth_code: str) -> dict[str, Any]:
    """Exchange authorization code for access and refresh tokens."""
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": client_id(),
        "client_secret": client_secret(),
        "code": extract_code_from_input(auth_code),
        "grant_type": "authorization_code",
        "redirect_uri": strava_redirect_uri(),
    }
    response = requests.post(url, data=payload, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to exchange code: {response.status_code} {response.text}"
        )
    return response.json()


def add_athlete_from_code(auth_code: str) -> str:
    """Register or update athlete tokens from OAuth code. Returns athlete name."""
    return add_athlete_from_token_response(exchange_code(auth_code))
