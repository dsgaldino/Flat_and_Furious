# Flat & Furious

Pipeline automatizado para o grupo de ciclismo: sincroniza atividades do Strava, gera resumo mensal, site estatico e texto para WhatsApp.

**Documentacao da estrutura de pastas:** [docs/ESTRUTURA_DO_PROJETO.md](docs/ESTRUTURA_DO_PROJETO.md)  
**Conectar ao GitHub:** [docs/GITHUB.md](docs/GITHUB.md)

## Comandos

```bash
pip install -r requirements.txt
cp .env.example .env   # preencher CLIENT_ID e CLIENT_SECRET

python -m flatfurious sync
python -m flatfurious auth --code "URL_OU_CODE_STRAVA"
python -m flatfurious report --month 2025-08 --build-site
python -m flatfurious site-build
```

## Configuracao local

1. Copie [`.env.example`](.env.example) para `.env` na raiz do repo.
2. Obtenha credenciais em https://www.strava.com/settings/api
3. **Rotacione o Client Secret** se ele ja foi exposto em commits ou notebooks.

## GitHub (automacao online)

### Repositorio privado obrigatorio

O arquivo `data/tokens_athletes.csv` contem tokens de acesso. Use repositorio **privado**.

### Secrets (Settings > Secrets and variables > Actions)

| Secret | Descricao |
|--------|-----------|
| `CLIENT_ID` | Strava API client ID |
| `CLIENT_SECRET` | Strava API client secret |

### Variables (opcional)

| Variable | Descricao |
|----------|-----------|
| `SITE_BASE_URL` | Ex: `https://seuuser.github.io/Flat_and_Furious` (link no whatsapp.txt) |

### Workflows

| Workflow | Quando |
|----------|--------|
| `daily_sync.yml` | Diario 06:00 UTC — refresh tokens + atividades |
| `monthly_report.yml` | Dia 1, 08:00 UTC — relatorio + site + artefatos WhatsApp |
| `deploy_pages.yml` | Deploy do site em `site/public` |
| `auth_athlete.yml` | Manual — registrar novo membro |

### GitHub Pages

1. Settings > Pages > Source: **GitHub Actions**
2. Apos o primeiro `monthly_report` ou `site-build`, o site publica em `site/public`

## Onboarding de membros

1. Envie ao atleta o link de autorizacao Strava (mesmo `redirect_uri` do app).
2. Apos autorizar, ele envia a URL com `code=...`.
3. Rode localmente `python -m flatfurious auth --code "..."` **ou** dispare o workflow **Register Strava athlete** no GitHub Actions.

## Estrutura

```
data/
  tokens_athletes.csv
  activities_all.csv
  activities_formatted.csv
reports/YYYY-MM/
  summary.json
  whatsapp.txt
  infographic.png
site/public/          # site gerado (GitHub Pages)
flatfurious/          # codigo do pipeline
```

## WhatsApp

O arquivo `reports/YYYY-MM/whatsapp.txt` e gerado automaticamente. Copie o texto e anexe `infographic.png` no grupo. Envio via API fica para fase futura.
