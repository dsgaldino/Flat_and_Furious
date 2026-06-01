# Handoff — Flat & Furious

Documento para o próximo agente. O usuário pode referenciar: `@docs/HANDOFF.md`

**Última atualização:** 2026-06 (sessão onboarding + Pages + Telegram)

---

## O que é o projeto

Pipeline para grupo de ciclismo (Enschede): sync Strava → CSV → relatório mensal (PDF, site, WhatsApp). Repositório **privado**:

`https://github.com/dsgaldino/Flat_and_Furious`

---

## O que já foi feito

| Área | Entregue |
|------|----------|
| Fase 0 | Health check; [`RUNBOOK.md`](RUNBOOK.md) |
| Sprint PDF | `data/members.csv`, filtro `group_join_date`, `GROUP_START_DATE`, elevação no clean, `flatfurious/report/metrics.py`, `pdf.py`, CLI `monthly` / `pdf` (verificar se tudo está commitado) |
| Tokens / sync | Always-refresh em `flatfurious/strava/refresh.py`; `.env` na raiz; `load_dotenv(override=True)`; não carregar `Notebooks/.env` para secrets |
| GitHub | Remote correto: `dsgaldino/Flat_and_Furious`; GitHub Pro + Pages via Actions (`deploy_pages.yml`) |
| Onboarding web | `site/public/join.html` + `site/public/strava/callback.html` |
| Telegram (prep) | `workers/telegram-notify.js` + [`TELEGRAM_ONBOARDING.md`](TELEGRAM_ONBOARDING.md) |

### URLs públicas

- Entrada: https://dsgaldino.github.io/Flat_and_Furious/join.html
- Callback: https://dsgaldino.github.io/Flat_and_Furious/strava/callback.html
- Strava app: callback domain `dsgaldino.github.io`

---

## Atenção — logo

`site/public/assets/logo.png` **não é o logo oficial** — era mockup de **roupa/kit** só para inspiração de cores (navy + dourado). Substituir pelo logo real (moinho + FF) antes de considerar o visual final.

---

## Config (não commitar `.env`)

```env
CLIENT_ID=160663
CLIENT_SECRET=<secret atual no Strava — nunca commitar>
STRAVA_REDIRECT_URI=https://dsgaldino.github.io/Flat_and_Furious/strava/callback.html
GROUP_START_DATE=2022-08-01
```

- `data/tokens_athletes.csv` — sensível
- `data/members.csv` — datas de entrada no grupo por atleta

---

## Comandos

```bash
python -m flatfurious auth --code "URL_CALLBACK_COMPLETA"
python -m flatfurious sync --full
python -m flatfurious pdf --month YYYY-MM
python -m flatfurious monthly --month YYYY-MM --full   # se existir no __main__
```

---

## Problemas / decisões já tomadas

1. Repo remoto era `dsgal/...` — corrigido para `dsgaldino/...`
2. `Notebooks/.env` sobrescrevia `CLIENT_SECRET` — removido do fluxo de config
3. Só 3 atletas com token (Diego, Thamiris, Carlos); faltam os outros + re-auth com `activity:read_all`
4. Telegram Worker ativo: `https://flat-furious-notify.dsgaldino.workers.dev` — auto-registro opcional: [`CONFIGURACAO_AUTO_ONBOARDING.md`](CONFIGURACAO_AUTO_ONBOARDING.md)
5. Código do sprint PDF pode estar **só local** — rodar `git status` e commitar se faltar

---

## Próximos passos (prioridade)

1. **Logo** — Trocar `logo.png`, ajustar páginas, push + redeploy Pages
2. **Telegram automático** — [`TELEGRAM_ONBOARDING.md`](TELEGRAM_ONBOARDING.md)
3. **Onboarding** — Link `join.html` para membros → `auth --code` por atleta
4. **Commit** — Garantir `main` com PDF, `monthly`, `members.py`, etc.
5. **Plano CTO** — Fase 1: pytest, CI, Telegram no relatório mensal (ver plano em `.cursor/plans/`)

---

## Docs relacionados

- [`ONBOARDING.md`](../ONBOARDING.md) — link Strava, auth
- [`RUNBOOK.md`](RUNBOOK.md) — troubleshooting
- [`TELEGRAM_ONBOARDING.md`](TELEGRAM_ONBOARDING.md) — Worker + bot
- [`ESTRUTURA_DO_PROJETO.md`](ESTRUTURA_DO_PROJETO.md) — pastas
- [`PUBLICAR_GITHUB_DESKTOP.md`](PUBLICAR_GITHUB_DESKTOP.md) — Git Desktop

---

## Não usar

- `http://auth.flatandfurious/` — legado
- Commitar `.env`, tokens, ou secrets no chat
