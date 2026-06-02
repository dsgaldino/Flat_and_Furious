# Runbook — Flat & Furious

Guia operacional: health check, falhas comuns e fluxo mensal.

**Último health check (Fase 0):** 2026-06-01

---

## Resultado do último health check

| Verificação | Status | Detalhe |
|-------------|--------|---------|
| `.env` local | OK | Arquivo presente na raiz |
| `tokens_athletes.csv` | **CRÍTICO** | 2 atletas; tokens **expirados** em 2026-05-29 |
| Scope OAuth | **ATENÇÃO** | `activity:read` — o onboarding pede `activity:read_all` |
| `activities_formatted.csv` | **CRÍTICO** | Só **1 atleta** (Diego); última atividade **2025-08-31** |
| Relatório `2025-08` | Desatualizado | `summary.json` ainda lista 6 atletas (dados antigos) |
| `infographic.png` | **Falta** | Pasta `reports/2025-08/` sem imagem |
| `site/public` | OK | `index.html` + arquivo `2025-08` existem |
| GitHub Actions (`gh`) | Não verificado | CLI `gh` não instalada nesta máquina |
| Repo remoto | OK | `origin` → `https://github.com/dsgaldino/Flat_and_Furious.git` |

### Causa provável do “parou de funcionar”

1. **Tokens expirados** → `daily_sync` no GitHub falha no refresh/collect.
2. **Grupo encolheu no CSV** → faltam 4+ membros em `tokens_athletes.csv` (só Diego e Thamiris; dados formatados só Diego).
3. **Dados congelados em ago/2025** → relatórios mensais recentes não refletem pedaladas novas.
4. **URLs em `pending_auth_urls.txt`** → codes de uso único, provavelmente **já expirados**; membros precisam autorizar de novo com scope correto.

---

## Ações imediatas (ordem recomendada)

### 1. Renovar tokens (local)

```bash
pip install -r requirements.txt
python -m flatfurious sync
```

Se falhar com erro 401/400 no refresh: o `refresh_token` pode ter sido revogado → re-auth (passo 2).

### 2. Re-registrar membros com scope correto

Link (substitua `CLIENT_ID`):

```
https://www.strava.com/oauth/authorize?client_id=CLIENT_ID&response_type=code&redirect_uri=http://auth.flatandfurious/&approval_prompt=force&scope=activity:read_all,profile:read_all
```

Por membro, após autorizar:

```bash
python -m flatfurious auth --code "http://auth.flatandfurious/?code=..."
```

Ou vários de uma vez (URLs novas, uma por linha):

```bash
python scripts/register_from_file.py data/pending_auth_urls.txt
```

**Importante:** cada `code` vale uma vez e expira em poucos minutos.

### 3. Sync completo após todos os tokens

```bash
python -m flatfurious sync --full
```

Confirme em `data/activities_formatted.csv` que aparecem **todos** os atletas e datas recentes.

### 4. Gerar relatório de teste

```bash
python -m flatfurious report --month 2025-08 --build-site
```

Verifique:

- `reports/YYYY-MM/whatsapp.txt`
- `reports/YYYY-MM/infographic.png`
- `reports/YYYY-MM/summary.json`

### 5. GitHub (uma vez)

- Repo **privado**
- Secrets: `CLIENT_ID`, `CLIENT_SECRET`
- Variable (opcional): `SITE_BASE_URL`
- Settings → Pages → Source: **GitHub Actions**
- Actions → conferir runs de **Daily Strava sync** e **Monthly report**

Sem `gh` CLI: abra https://github.com/dsgaldino/Flat_and_Furious/actions no browser.

---

## Fluxo mensal (dia 1)

1. Workflow **Monthly report** roda às 08:00 UTC (ou dispare manualmente com mês `YYYY-MM`).
2. Baixe artefato `whatsapp-YYYY-MM` em Actions (ou use arquivos em `reports/` após commit).
3. Copie `whatsapp.txt` + anexe `infographic.png` no grupo WhatsApp.
4. Site atualiza em GitHub Pages (`site/public`).

*(Fase 2 do plano: notificação Telegram semi-automática.)*

---

## Se X falhar, faça Y

| Sintoma | Causa provável | Correção |
|---------|----------------|----------|
| `CLIENT_ID is not set` | `.env` ou secrets GitHub vazios | Preencher `.env` / Secrets no repo |
| `Strava API error 401` no refresh | `CLIENT_ID` / `CLIENT_SECRET` errados no `.env` | Usar o mesmo app Strava dos tokens; nunca commitar secret |
| `Strava API error 401` no collect | Refresh falhou ou `.env` incorreto | Corrigir `.env`; `sync` sempre renova todos os tokens antes do collect |
| `Strava API error 403` | Scope insuficiente (`activity:read` vs `read_all`) | Re-autorizar com `activity:read_all` |
| Só 1 atleta no CSV | Tokens faltando ou collect falhou para outros | Registrar todos; `sync --full` |
| Relatório com atletas “fantasma” | `summary.json` antigo / CSV desatualizado | `sync --full` + `report` de novo |
| `infographic.png` ausente | Erro em `report` (matplotlib/font) | Rodar `report` local e ver stderr |
| CI não commita | Branch protegida sem bypass para Actions | Ajustar protection rules ou commit manual |
| Pages 404 | Pages não habilitado ou `site/public` vazio | Habilitar Actions Pages; rodar `--build-site` |
| Code em `pending_auth_urls` não funciona | Code já usado ou expirado | Novo link de autorização Strava |

---

## Comandos rápidos

```bash
python -m flatfurious sync
python -m flatfurious sync --full
python -m flatfurious auth --code "URL_OU_CODE"
python -m flatfurious report --month YYYY-MM --build-site
python -m flatfurious site-build
```

---

## Health check manual

```bash
python scripts/health_check_phase0.py
```

*(Script a ser adicionado na Fase 1; até lá use os passos da seção “Ações imediatas”.)*

## Sprint PDF (manual)

**Grupo criado:** 2022-08-01 (`GROUP_START_DATE` no `.env`)

**Membros:** `data/members.csv` — pedaladas contam apenas apos `group_join_date`.

### Comandos

```bash
pip install -r requirements.txt
python -m flatfurious auth --code "URL_STRAVA"
python -m flatfurious monthly --month 2025-08 --full
# ou separado:
python -m flatfurious sync --full
python -m flatfurious pdf --month 2025-08
```

**Saida:** `reports/YYYY-MM/report.pdf`

### Se sync falhar com 401

1. Confirme `CLIENT_ID` e `CLIENT_SECRET` no `.env` (iguais ao app Strava).
2. Rotacione o secret no Strava se necessario.
3. Cada membro re-autoriza com scope `activity:read_all,profile:read_all`.
