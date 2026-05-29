"""Register Strava athletes from a file with one URL or code per line."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flatfurious.strava.auth import add_athlete_from_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Register athletes from URL file")
    parser.add_argument(
        "file",
        nargs="?",
        default="data/pending_auth_urls.txt",
        help="Text file with one auth URL per line",
    )
    args = parser.parse_args()
    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    ok, fail = 0, 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            name = add_athlete_from_code(line)
            print(f"OK: {name}")
            ok += 1
        except Exception as exc:
            print(f"FAIL: {line[:60]}... -> {exc}")
            fail += 1

    print(f"\nDone: {ok} registered, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
