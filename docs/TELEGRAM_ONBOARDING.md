# Telegram — notificacao automatica no onboarding

Quando um amigo autoriza o Strava, voce recebe uma mensagem no Telegram com o link para registrar (`auth --code`).

## Problema conhecido: SSL no workers.dev

Se `https://flat-furious-notify.dsgaldino.workers.dev` der **ERR_SSL_VERSION_OR_CIPHER_MISMATCH** no browser, o certificado do subdominio `workers.dev` ainda nao esta ativo (ou falhou). O Worker pode aparecer no painel Cloudflare com invocacoes, mas o browser nao conecta.

**Solucao recomendada:** deploy na **Vercel** (pasta `notify-api/`, ver [`notify-api/README.md`](../notify-api/README.md) ou `.\scripts\telegram-vercel-setup.ps1`).

## 1. Criar o bot (5 min)

1. No Telegram, fale com [@BotFather](https://t.me/BotFather)
2. `/newbot` → nome: `Flat Furious Admin` → username: ex. `flat_furious_admin_bot`
3. Guarde o **token** (ex. `123456:ABC...`)

## 2. Obter seu chat_id

1. Envie qualquer mensagem para o seu bot
2. Abra no browser (substitua TOKEN):

   `https://api.telegram.org/botTOKEN/getUpdates`

3. Copie `"chat":{"id": 123456789` → esse numero e o **TELEGRAM_CHAT_ID**

## 3. Deploy do Worker (gratis — Cloudflare)

1. Conta em https://dash.cloudflare.com (gratis)
2. **Windows (recomendado)** — na raiz do repo:

```powershell
.\scripts\telegram-worker-setup.ps1
```

O script instala o Wrangler localmente, abre login no browser, pede os secrets e faz deploy.

3. **Manual** — na pasta `workers/`:

```powershell
cd workers
npm install
npx wrangler login
npx wrangler secret put TELEGRAM_BOT_TOKEN
npx wrangler secret put TELEGRAM_CHAT_ID
npx wrangler deploy
```

4. Anote a URL exibida no deploy, ex.: `https://flat-furious-notify.SEU_SUBDOMINIO.workers.dev`

5. **Health check:** abra essa URL no browser. Deve aparecer JSON com `"telegram_configured": true`.

## 4. Ativar no site

Em `site/public/assets/join.js`:

```javascript
TELEGRAM_NOTIFY_WEBHOOK: "https://flat-furious-notify.SEU_SUBDOMINIO.workers.dev",
```

Commit + push (ou redeploy GitHub Pages).

## 5. Testar

1. Abra `join.html` → autorize com Strava (conta teste)
2. Na pagina de sucesso deve aparecer: *"O administrador foi notificado no Telegram"*
3. No Telegram voce recebe a mensagem com nome do atleta e status do registro

## 6. Registro automatico (sem `python` no PC)

O Worker pode disparar o workflow **Register Strava athlete** no GitHub. O token vai para `data/tokens_athletes.csv` via commit (~1–2 min).

### Secrets extras no Worker

```powershell
cd workers
npx wrangler secret put STRAVA_CLIENT_SECRET
npx wrangler secret put GITHUB_DISPATCH_TOKEN
npx wrangler deploy
```

| Secret | O que e |
|--------|---------|
| `STRAVA_CLIENT_SECRET` | Mesmo valor do `.env` / GitHub `CLIENT_SECRET` |
| `GITHUB_DISPATCH_TOKEN` | Personal Access Token (classic) com `repo` + `workflow` |

Opcional: `GITHUB_REPO` = `dsgaldino/Flat_and_Furious` (padrao ja e este).

### GitHub

1. Repo → **Settings → Secrets → Actions**: `CLIENT_ID` e `CLIENT_SECRET` (ja usados no monthly report)
2. Criar PAT: GitHub → **Settings → Developer settings → PAT (classic)** → scopes `repo`, `workflow`
3. Health check do Worker deve mostrar `"github_auto": true` e `"strava_auto": true`

### Mensagem no Telegram (com auto ativo)

- Nome do atleta
- "Registro automatico iniciado no GitHub"
- URL completa (fallback se o Actions falhar)

Sem `GITHUB_DISPATCH_TOKEN`, a mensagem ainda traz o comando `python -m flatfurious auth --code "URL"`.

## Sem Worker

Se `TELEGRAM_NOTIFY_WEBHOOK` estiver vazio, o atleta ve botoes **Copiar link** e **Enviar no Telegram** (manual).

## Erro: "Nao foi possivel notificar o Telegram automaticamente"

1. Abra https://flat-furious-notify.dsgaldino.workers.dev — precisa `"telegram_configured": true`.
2. Na pagina de callback, abra **Detalhes tecnicos** e leia o JSON de erro.
3. Regrave os secrets (so numeros no chat id, sem aspas):

```powershell
cd workers
npx wrangler secret put TELEGRAM_BOT_TOKEN
npx wrangler secret put TELEGRAM_CHAT_ID
npx wrangler deploy
```

4. **chat_id:** mande `oi` para @flat_and_furious_bot, depois `getUpdates` — use so o numero de `"id"` dentro de `"chat"`.
5. **token:** copie de novo do BotFather (/token), sem espacos no inicio/fim.
