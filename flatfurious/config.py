"""Configuration loaded from environment variables."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parent.parent
# Repo-root .env wins over stale shell/Notebooks env (override=True).
load_dotenv(_REPO_ROOT / ".env", override=True)


def repo_root() -> Path:
    return _REPO_ROOT


def data_dir() -> Path:
    path = os.getenv("DATA_DIR", "data")
    p = Path(path)
    return p if p.is_absolute() else _REPO_ROOT / p


def reports_dir() -> Path:
    path = os.getenv("REPORTS_DIR", "reports")
    p = Path(path)
    return p if p.is_absolute() else _REPO_ROOT / p


def site_public_dir() -> Path:
    path = os.getenv("SITE_PUBLIC_DIR", "site/public")
    p = Path(path)
    return p if p.is_absolute() else _REPO_ROOT / p


def site_templates_dir() -> Path:
    return _REPO_ROOT / "site" / "templates"


def tokens_path() -> Path:
    return data_dir() / "tokens_athletes.csv"


def activities_path() -> Path:
    return data_dir() / "activities_all.csv"


def formatted_path() -> Path:
    return data_dir() / "activities_formatted.csv"


def client_id() -> str:
    value = os.getenv("CLIENT_ID")
    if not value:
        raise RuntimeError("CLIENT_ID is not set. Copy .env.example to .env")
    return value


def client_secret() -> str:
    value = os.getenv("CLIENT_SECRET")
    if not value:
        raise RuntimeError("CLIENT_SECRET is not set. Copy .env.example to .env")
    return value


def site_base_url() -> str:
    return os.getenv("SITE_BASE_URL", "").rstrip("/")


def strava_redirect_uri() -> str:
    return os.getenv(
        "STRAVA_REDIRECT_URI",
        "https://dsgaldino.github.io/Flat_and_Furious/strava/callback.html",
    )


def group_start_date() -> datetime:
    raw = os.getenv("GROUP_START_DATE", "2022-08-01")
    return datetime.strptime(raw, "%Y-%m-%d")
