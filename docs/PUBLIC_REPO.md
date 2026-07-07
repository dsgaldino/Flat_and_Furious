# Public repository checklist

This project is safe to keep **public** because athlete OAuth tokens and secrets never live in git.

## What is public vs private

| File / data | In git? | Runtime storage |
|-------------|---------|-----------------|
| Source code, workflows, site | Yes | — |
| `activities_*.csv`, reports, site output | Yes | — |
| `.env` | **No** (gitignored) | Local machine |
| `data/tokens_athletes.csv` | **No** (gitignored) | Local + Actions cache + `TOKENS_ATHLETES_B64` secret |
| `data/pending_auth_urls.txt` | **No** (gitignored) | Local only |

## One-time setup after going public

### 1. Rotate Strava credentials

If tokens or `CLIENT_SECRET` were ever committed, rotate at https://www.strava.com/settings/api and update:

- Local `.env`
- GitHub Secrets `CLIENT_ID`, `CLIENT_SECRET`

All athletes may need to re-authorise if refresh tokens were exposed.

### 2. Bootstrap `TOKENS_ATHLETES_B64` secret

From a machine with the real tokens file:

```powershell
# Windows PowerShell
$b64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes("data/tokens_athletes.csv"))
gh secret set TOKENS_ATHLETES_B64 --repo dsgaldino/Flat_and_Furious --body $b64
```

```bash
# Linux / macOS
gh secret set TOKENS_ATHLETES_B64 --repo dsgaldino/Flat_and_Furious < <(base64 -w0 data/tokens_athletes.csv)
```

CI restores from **Actions cache** first; the secret is used when cache is empty (new runner, first run, or cache eviction).

### 3. Verify workflows

Run **Daily Strava sync** manually once. Token refresh updates the cache automatically — tokens are **not** committed.

## History cleanup

If `tokens_athletes.csv` existed in older commits, purge history before or immediately after going public, then **rotate all tokens**.

```bash
git filter-repo --path data/tokens_athletes.csv --path data/pending_auth_urls.txt --invert-paths --force
git push --force origin main
```

## Local development

```bash
cp data/tokens_athletes.csv.example data/tokens_athletes.csv
cp .env.example .env
# fill credentials, register athletes via auth command
```
