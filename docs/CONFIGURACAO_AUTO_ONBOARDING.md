# Configuração — Telegram + registro automático de atletas

Checklist para não precisar rodar `python -m flatfurious auth` no PC quando alguém autoriza o Strava.

---

## Visão geral

```text
Atleta (join.html) → Cloudflare Worker → Telegram (você)
                              ↓
                    GitHub Actions (auth_athlete.yml)
                              ↓
                    commit em data/tokens_athletes.csv
```

---

## Parte 1 — Já feito (Telegram)

| Item | Status |
|------|--------|
| Bot @flat_and_furious_bot | Criado |
| Worker `flat-furious-notify.dsgaldino.workers.dev` | Deploy |
| `TELEGRAM_BOT_TOKEN` no Wrangler | Configurado |
| `TELEGRAM_CHAT_ID` no Wrangler | Numérico (ex. via @userinfobot) |
| `join.js` / `site.js` → `TELEGRAM_NOTIFY_WEBHOOK` | URL do Worker |

**Teste:** abra a URL do Worker no browser → `"telegram_configured": true`.

---

## Parte 2 — GitHub Actions (secrets do repo)

Repo: `dsgaldino/Flat_and_Furious` → **Settings → Secrets and variables → Actions**

| Secret | Valor |
|--------|--------|
| `CLIENT_ID` | Id do app Strava (ex. `160663`) |
| `CLIENT_SECRET` | Secret do app Strava (mesmo do `.env` local) |

Estes já são usados pelo workflow **Monthly report**.

---

## Parte 3 — Personal Access Token (PAT) para o Worker disparar o Actions

1. GitHub → **Settings** (da sua conta) → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. **Generate new token (classic)**
3. Nome: `flat-furious-worker-dispatch`
4. Expiration: 90 dias ou No expiration (sua escolha)
5. Scopes: marque **`repo`** (repositório privado) e **`workflow`**
6. **Generate token** → copie o token (só aparece uma vez)

Guarde em arquivo temporário se for colar no Wrangler com o método do Notepad (ver abaixo).

---

## Parte 4 — Secrets extras no Cloudflare Worker

No PowerShell:

```powershell
cd c:\Users\dsgal\Documents\GitHub\Flat_and_Furious\workers
```

### STRAVA_CLIENT_SECRET

Mesmo valor de `CLIENT_SECRET` do `.env` / GitHub.

```powershell
npx wrangler secret put STRAVA_CLIENT_SECRET
```

(Método Notepad: salve só o secret em `C:\Users\dsgal\Documents\strava-secret.txt`, depois:)

```powershell
Get-Content "C:\Users\dsgal\Documents\strava-secret.txt" -Raw | npx wrangler secret put STRAVA_CLIENT_SECRET
Remove-Item "C:\Users\dsgal\Documents\strava-secret.txt"
```

### GITHUB_DISPATCH_TOKEN

O PAT da Parte 3.

```powershell
Get-Content "C:\Users\dsgal\Documents\gh-pat.txt" -Raw | npx wrangler secret put GITHUB_DISPATCH_TOKEN
Remove-Item "C:\Users\dsgal\Documents\gh-pat.txt"
```

### Opcional

```powershell
npx wrangler secret put GITHUB_REPO
```

Valor: `dsgaldino/Flat_and_Furious` (já é o padrão se omitir).

Redeploy (opcional após secrets; secrets aplicam sem redeploy):

```powershell
npx wrangler deploy
```

---

## Parte 5 — Push do código (workflow atualizado)

O arquivo `.github/workflows/auth_athlete.yml` precisa estar no GitHub com `repository_dispatch` (evento `strava_auth`).

Faça **push** da branch `main` após o commit.

---

## Parte 6 — Verificar

### Health check do Worker

https://flat-furious-notify.dsgaldino.workers.dev

Esperado:

```json
{
  "ok": true,
  "telegram_configured": true,
  "strava_auto": true,
  "github_auto": true
}
```

Se `github_auto` ou `strava_auto` for `false`, falta o secret correspondente no Wrangler.

### Teste real

1. https://dsgaldino.github.io/Flat_and_Furious/join.html  
2. Autorizar Strava (conta teste)  
3. Telegram: mensagem com nome do atleta + “Registro automático iniciado no GitHub”  
4. GitHub → **Actions** → workflow **Register Strava athlete** (run verde)  
5. Repo: `data/tokens_athletes.csv` atualizado com commit `chore(ci): register Strava athlete token`

---

## Mensagem no Telegram (exemplo)

```text
🚴 Flat & Furious — novo atleta

👤 Nome Sobrenome

✅ Registro automático iniciado no GitHub.
Em ~1–2 min o token entra em data/tokens_athletes.csv (commit no repo).

Acompanhe: GitHub → Actions → Register Strava athlete

🔗 URL:
https://dsgaldino.github.io/Flat_and_Furious/strava/callback.html?...
```

---

## Se o automático falhar

1. **Actions vermelho** → abra o log; code expirado é comum (válido ~10 min). Peça ao atleta autorizar de novo.
2. **Telegram sem “automático”** → configure `GITHUB_DISPATCH_TOKEN` e `STRAVA_CLIENT_SECRET`.
3. **Fallback manual:**

```bash
python -m flatfurious auth --code "URL_COMPLETA_DO_TELEGRAM"
```

Ou: Actions → **Register Strava athlete** → Run workflow → cole a URL.

---

## Segurança

- Nunca commitar `.env`, tokens ou PAT no GitHub.
- Apagar arquivos `.txt` usados para colar secrets no Wrangler.
- PAT com escopo mínimo (`repo` + `workflow`).

---

## Referências

- [`TELEGRAM_ONBOARDING.md`](TELEGRAM_ONBOARDING.md) — bot e Worker
- [`.github/workflows/auth_athlete.yml`](../.github/workflows/auth_athlete.yml) — registro no CI
