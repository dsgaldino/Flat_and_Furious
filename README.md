# Flat & Furious

[![Daily Strava sync](https://github.com/dsgaldino/Flat_and_Furious/actions/workflows/daily_sync.yml/badge.svg)](https://github.com/dsgaldino/Flat_and_Furious/actions/workflows/daily_sync.yml)
[![Monthly report](https://github.com/dsgaldino/Flat_and_Furious/actions/workflows/monthly_report.yml/badge.svg)](https://github.com/dsgaldino/Flat_and_Furious/actions/workflows/monthly_report.yml)
[![GitHub Pages](https://img.shields.io/badge/demo-live-8A2BE2?style=flat-square)](https://dsgaldino.github.io/Flat_and_Furious/)

**End-to-end automation for a cycling group:** Strava OAuth → daily activity sync → monthly rankings → static site → WhatsApp-ready reports.

Built as a production-style Python pipeline with **GitHub Actions**, **GitHub Pages**, and optional **Cloudflare Workers** for Telegram onboarding.

| | |
|---|---|
| **Live site** | [dsgaldino.github.io/Flat_and_Furious](https://dsgaldino.github.io/Flat_and_Furious/) |
| **Stack** | Python 3.11 · pandas · Strava API · GitHub Actions · GitHub Pages |
| **Author** | [Diego Galdino](https://github.com/dsgaldino) |

---

## What it does

1. **OAuth onboarding** — athletes authorise Strava; tokens stored securely (never in git)
2. **Daily sync** — refresh tokens, pull new rides, normalise CSV datasets
3. **Monthly report** — rankings, stats, infographic, WhatsApp text
4. **Static site** — auto-deployed to GitHub Pages after each report
5. **Telegram bot** (optional) — Cloudflare Worker triggers athlete registration

```
Strava API ──► flatfurious (Python) ──► CSV + reports ──► GitHub Pages
                     ▲
              GitHub Actions (cron)
```

---

## Quick start (local)

```bash
git clone https://github.com/dsgaldino/Flat_and_Furious.git
cd Flat_and_Furious
pip install -r requirements.txt
cp .env.example .env          # add CLIENT_ID + CLIENT_SECRET from Strava
cp data/tokens_athletes.csv.example data/tokens_athletes.csv

python -m flatfurious sync
python -m flatfurious report --month 2025-08 --build-site
python -m flatfurious site-build
```

Register a new athlete:

```bash
python -m flatfurious auth --code "STRAVA_REDIRECT_URL_WITH_CODE"
```

---

## Security model (public repo)

| Asset | Where it lives |
|-------|----------------|
| `CLIENT_ID` / `CLIENT_SECRET` | `.env` locally · GitHub Actions **Secrets** |
| Athlete OAuth tokens | `data/tokens_athletes.csv` locally · **Actions cache** + `TOKENS_ATHLETES_B64` secret |
| Activity data | Committed CSVs (no tokens) |
| Pending auth URLs | Local only (`pending_auth_urls.txt` is gitignored) |

**Never commit** `.env`, `tokens_athletes.csv`, or OAuth redirect URLs.

See [docs/PUBLIC_REPO.md](docs/PUBLIC_REPO.md) for the full public-repo checklist.

---

## GitHub Actions

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| `daily_sync.yml` | 06:00 UTC daily | Token refresh + activity collection |
| `monthly_report.yml` | 08:00 UTC, 1st of month | Report, site build, WhatsApp artifacts |
| `deploy_pages.yml` | On push to `site/public` | GitHub Pages deploy |
| `auth_athlete.yml` | Manual / repository_dispatch | Register new Strava athlete |

### Required secrets

| Secret | Description |
|--------|-------------|
| `CLIENT_ID` | Strava API client ID |
| `CLIENT_SECRET` | Strava API client secret |
| `TOKENS_ATHLETES_B64` | Base64 of `tokens_athletes.csv` (bootstrap + cache fallback) |

Optional variable: `SITE_BASE_URL` (e.g. `https://dsgaldino.github.io/Flat_and_Furious`)

---

## Project layout

```
flatfurious/           Python package (CLI, Strava, reports, site builder)
data/                  Activity CSVs (+ local tokens file, gitignored)
reports/YYYY/MM/       Monthly summary, infographic, whatsapp.txt
site/public/           Generated static site (GitHub Pages)
.github/workflows/     CI/CD automation
docs/                  Architecture, runbook, onboarding
workers/               Cloudflare Telegram bot (optional)
```

Deep dive: [docs/ESTRUTURA_DO_PROJETO.md](docs/ESTRUTURA_DO_PROJETO.md)

---

## CLI

```bash
python -m flatfurious sync                              # refresh + collect
python -m flatfurious auth --code "URL_OR_CODE"         # register athlete
python -m flatfurious report --month YYYY-MM --build-site
python -m flatfurious site-build
```

---

## Docs

- [PUBLIC_REPO.md](docs/PUBLIC_REPO.md) — making the repo public safely
- [GITHUB.md](docs/GITHUB.md) — secrets, Pages, first deploy
- [RUNBOOK.md](docs/RUNBOOK.md) — operations and troubleshooting
- [ONBOARDING.md](ONBOARDING.md) — new member flow

---

## Licence

Personal / group project. Strava API usage subject to [Strava API Agreement](https://www.strava.com/legal/api).
