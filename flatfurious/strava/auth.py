"""Exchange Strava authorization code for tokens and persist to CSV."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd
import requests

from flatfurious.config import client_id, client_secret, strava_redirect_uri, tokens_path

TOKEN_COLUMNS = ["nome", "athlete_id", "access_token", "refresh_token", "expires_at"]


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


def normalize_tokens_df(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names to TOKEN_COLUMNS."""
    rename = {}
    if "name" in df.columns and "nome" not in df.columns:
        rename["name"] = "nome"
    df = df.rename(columns=rename)
    for col in TOKEN_COLUMNS:
        if col not in df.columns:
            df[col] = None
    return df[TOKEN_COLUMNS]


def load_tokens() -> pd.DataFrame:
    path = tokens_path()
    if not path.exists():
        return pd.DataFrame(columns=TOKEN_COLUMNS)
    df = pd.read_csv(path)
    return normalize_tokens_df(df)


def save_tokens(df: pd.DataFrame) -> Path:
    path = tokens_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    normalize_tokens_df(df).to_csv(path, index=False)
    return path


def exchange_code(auth_code: str) -> dict:
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
    data = exchange_code(auth_code)
    athlete = data["athlete"]
    full_name = f"{athlete['firstname']} {athlete['lastname']}"
    athlete_id = athlete["id"]

    df = load_tokens()
    new_row = {
        "nome": full_name,
        "athlete_id": athlete_id,
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_at": data["expires_at"],
    }

    if not df.empty and "athlete_id" in df.columns:
        mask = df["athlete_id"].astype(str) == str(athlete_id)
        if mask.any():
            for key, val in new_row.items():
                df.loc[mask, key] = val
        else:
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row])

    save_tokens(df)
    return full_name
