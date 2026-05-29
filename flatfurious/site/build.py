"""Build static HTML site from reports and summary data."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from flatfurious.config import reports_dir, site_base_url, site_public_dir, site_templates_dir
from flatfurious.report.monthly import build_summary, previous_month


def _list_report_months() -> list[str]:
    root = reports_dir()
    if not root.exists():
        return []
    months = []
    for p in sorted(root.iterdir()):
        if p.is_dir() and (p / "summary.json").exists():
            months.append(p.name)
    return months


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

    if not months:
        print("No reports found. Run: python -m flatfurious report --month YYYY-MM")
        return public

    latest = latest_month or months[-1]
    base_url = site_base_url()

    assets_src = templates / "assets"
    assets_dst = public / "assets"
    if assets_src.exists():
        if assets_dst.exists():
            shutil.rmtree(assets_dst)
        shutil.copytree(assets_src, assets_dst)

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
            infographic_rel = f"archive/{month}/infographic.png"

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
    whatsapp_latest = reports_dir() / latest / "whatsapp.txt"
    whatsapp_text = (
        whatsapp_latest.read_text(encoding="utf-8")
        if whatsapp_latest.exists()
        else ""
    )
    infographic_rel = f"archive/{latest}/infographic.png"
    if not (public / infographic_rel).exists():
        infographic_rel = None

    index_tpl = env.get_template("index.html")
    index_html = index_tpl.render(
        summary=latest_summary,
        whatsapp_text=whatsapp_text,
        infographic_src=infographic_rel,
        base_url=base_url,
        all_months=months,
        latest_month=latest,
    )
    (public / "index.html").write_text(index_html, encoding="utf-8")

    print(f"Site built at {public}")
    return public
