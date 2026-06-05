"""CLI entry point: python -m flatfurious <command>."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from flatfurious.data.clean import clean_and_save
from flatfurious.report.charts import generate_infographic
from flatfurious.report.monthly import (
    build_summary,
    previous_month,
    save_summary,
)
from flatfurious.report.ai_prompt import save_ai_prompt
from flatfurious.report.scaffold import scaffold_all_distance_reports
from flatfurious.report.whatsapp import save_whatsapp_text
from flatfurious.site.build import build_site
from flatfurious.strava.auth import add_athlete_from_code
from flatfurious.strava.collect import collect_all
from flatfurious.strava.refresh import refresh_all_tokens


def cmd_sync(args: argparse.Namespace) -> None:
    refresh_all_tokens()
    collect_all(full_refresh=args.full)
    clean_and_save()


def cmd_auth(args: argparse.Namespace) -> None:
    name = add_athlete_from_code(args.code)
    print(f"Token saved for {name}")


def cmd_report(args: argparse.Namespace) -> None:
    month = args.month or previous_month()
    summary = build_summary(month)
    save_summary(month, summary)
    save_whatsapp_text(summary, month)
    save_ai_prompt(summary, month)
    generate_infographic(summary)
    if args.build_site:
        build_site(latest_month=month)


def cmd_site_build(args: argparse.Namespace) -> None:
    build_site(latest_month=args.month)


def cmd_scaffold(args: argparse.Namespace) -> None:
    end = args.through or datetime.today().strftime("%Y-%m")
    scaffold_all_distance_reports(
        end_month_year=end,
        migrate_legacy=not args.no_migrate,
        overwrite=not args.no_overwrite,
    )


def cmd_scaffold_parser(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "scaffold",
        help="Create reports/YEAR/MM with distance-only files for each month",
    )
    p.add_argument(
        "--through",
        help="Last month YYYY-MM (default: current month)",
    )
    p.add_argument(
        "--no-migrate",
        action="store_true",
        help="Do not move legacy reports/YYYY-MM/ folders first",
    )
    p.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Skip months that already have summary.json",
    )
    p.set_defaults(func=cmd_scaffold)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="flatfurious",
        description="Flat & Furious — Strava sync, reports and site",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_sync = sub.add_parser("sync", help="Refresh tokens, collect activities, clean data")
    p_sync.add_argument(
        "--full",
        action="store_true",
        help="Full activity refresh (ignore incremental cache)",
    )
    p_sync.set_defaults(func=cmd_sync)

    p_auth = sub.add_parser("auth", help="Add athlete from Strava OAuth code or URL")
    p_auth.add_argument("--code", required=True, help="Authorization code or redirect URL")
    p_auth.set_defaults(func=cmd_auth)

    p_report = sub.add_parser("report", help="Generate monthly report")
    p_report.add_argument("--month", help="YYYY-MM (default: previous month)")
    p_report.add_argument(
        "--build-site",
        action="store_true",
        help="Also rebuild static site",
    )
    p_report.set_defaults(func=cmd_report)

    p_site = sub.add_parser("site-build", help="Build static site from reports")
    p_site.add_argument("--month", help="Latest month to feature on index")
    p_site.set_defaults(func=cmd_site_build)

    cmd_scaffold_parser(sub)

    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
