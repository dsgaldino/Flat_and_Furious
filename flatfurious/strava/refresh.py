"""Refresh expired Strava access tokens."""

from __future__ import annotations

import time

import pandas as pd
import requests

from flatfurious.config import client_id, client_secret
from flatfurious.strava.auth import load_tokens, save_tokens


def refresh_all_tokens() -> pd.DataFrame:
    """Refresh tokens that are expired or about to expire."""
    df = load_tokens()
    if df.empty:
        print("No athletes in tokens file.")
        return df

    updated = []
    now = int(time.time())

    for _, row in df.iterrows():
        name = row["nome"]
        expires_at = int(row["expires_at"])

        if expires_at > now + 300:
            print(f"Token still valid for {name}")
            updated.append(row.to_dict())
            continue

        print(f"Refreshing token for {name}...")
        url = "https://www.strava.com/api/v3/oauth/token"
        payload = {
            "client_id": client_id(),
            "client_secret": client_secret(),
            "grant_type": "refresh_token",
            "refresh_token": row["refresh_token"],
        }
        response = requests.post(url, data=payload, timeout=30)

        if response.status_code == 200:
            new_data = response.json()
            updated.append(
                {
                    "nome": name,
                    "athlete_id": row["athlete_id"],
                    "access_token": new_data["access_token"],
                    "refresh_token": new_data["refresh_token"],
                    "expires_at": new_data["expires_at"],
                }
            )
            print(f"Token refreshed for {name}")
        else:
            print(
                f"Failed to refresh token for {name}: "
                f"{response.status_code} {response.text}"
            )
            updated.append(row.to_dict())

    df_updated = pd.DataFrame(updated)
    save_tokens(df_updated)
    return df_updated
