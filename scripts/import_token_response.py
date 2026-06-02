"""Import Strava OAuth token response (JSON or Python dict) into tokens_athletes.csv."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as scripts/import_token_response.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flatfurious.strava.auth import (  # noqa: E402
    add_athlete_from_token_response,
    load_tokens,
    parse_token_response_text,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import Strava OAuth token response into data/tokens_athletes.csv"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="File with token response (.json or .txt with Python dict). Reads stdin if omitted.",
    )
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        print("Paste token response, then Ctrl+Z Enter (Windows) or Ctrl+D (Unix):")
        text = sys.stdin.read()

    try:
        data = parse_token_response_text(text)
        name = add_athlete_from_token_response(data)
        print(f"Registered: {name}")
        df = load_tokens()
        print(f"Total athletes in CSV: {len(df)}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
