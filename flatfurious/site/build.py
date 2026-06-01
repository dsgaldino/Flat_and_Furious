"""Build static HTML site from reports and summary data."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from flatfurious.config import reports_dir, site_base_url, site_public_dir, site_templates_dir
from flatfurious.report.monthly import build_summary


def _list_report_months() -> list[str]:
    root = reports_dir()
    if not root.exists():
        return []
    months = []
    for p in sorted(root.iterdir()):
        if p.is_dir() and (p / "summary.json").exists():
            months.append(p.name)
    return months


def _sync_template_assets(templates: Path, public: Path) -> None:
    """Copy template assets into public/assets without deleting extra files."""
    assets_src = templates / "assets"
    assets_dst = public / "assets"
    assets_dst.mkdir(parents=True, exist_ok=True)
    if not assets_src.exists():
        return
    for src in assets_src.rglob("*"):
        if src.is_file():
            rel = src.relative_to(assets_src)
            dst = assets_dst / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def build_site(latest_month: str | None = None) -> Path:
    """Generate site/public from templates and reports/."""
    public = site_public_dir()
    templates = site_templates_dir()
    public.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(templates)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    months = _list_report_months()
    if not months and latest_month:
        summary = build_summary(latest_month)
        from flatfurious.report.monthly import save_summary

        save_summary(latest_month, summary)
        months = [latest_month]

    _sync_template_assets(templates, public)

    if not months:
        print("No reports found. Run: python -m flatfurious report --month YYYY-MM")
        landing_tpl = env.get_template("landing.html")
        (public / "index.html").write_text(
            landing_tpl.render(latest_summary=None, latest_month=None),
            encoding="utf-8",
        )
        print(f"Site built at {public} (landing only, no reports)")
        return public

    latest = latest_month or months[-1]
    base_url = site_base_url()

    archive_dir = public / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    summaries: dict[str, dict] = {}
    for month in months:
        summary_path = reports_dir() / month / "summary.json"
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summaries[month] = summary

        month_dir = archive_dir / month
        month_dir.mkdir(parents=True, exist_ok=True)

        whatsapp_path = reports_dir() / month / "whatsapp.txt"
        whatsapp_text = ""
        if whatsapp_path.exists():
            whatsapp_text = whatsapp_path.read_text(encoding="utf-8")

        infographic_rel = None
        infographic_src = reports_dir() / month / "infographic.png"
        if infographic_src.exists():
            shutil.copy2(infographic_src, month_dir / "infographic.png")
            infographic_rel = "infographic.png"

        tpl = env.get_template("archive.html")
        html = tpl.render(
            summary=summary,
            whatsapp_text=whatsapp_text,
            infographic_src=infographic_rel,
            base_url=base_url,
            all_months=months,
        )
        (month_dir / "index.html").write_text(html, encoding="utf-8")

    latest_summary = summaries[latest]

    archive_index_tpl = env.get_template("archive-index.html")
    (archive_dir / "index.html").write_text(
        archive_index_tpl.render(
            all_months=months,
            latest_month=latest,
            latest_summary=latest_summary,
            base_url=base_url,
        ),
        encoding="utf-8",
    )

    landing_tpl = env.get_template("landing.html")
    (public / "index.html").write_text(
        landing_tpl.render(
            latest_summary=latest_summary,
            latest_month=latest,
            all_months=months,
            base_url=base_url,
        ),
        encoding="utf-8",
    )

    print(f"Site built at {public}")
    return public
