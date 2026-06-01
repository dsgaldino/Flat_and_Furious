# Telegram — notificacao automatica no onboarding

Quando um amigo autoriza o Strava, voce recebe uma mensagem no Telegram com o link para registrar (`auth --code`).

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
3. No Telegram voce recebe o link → rode:

```bash
python -m flatfurious auth --code "URL_DA_MENSAGEM"
```

## Sem Worker

Se `TELEGRAM_NOTIFY_WEBHOOK` estiver vazio, o atleta ve botoes **Copiar link** e **Enviar no Telegram** (manual).
