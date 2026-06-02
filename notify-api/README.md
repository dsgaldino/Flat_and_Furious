# Telegram notify API (Vercel)

Use isto se o Worker Cloudflare (`*.dsgaldino.workers.dev`) der erro SSL no browser.

## Deploy (5 min)

1. Conta grátis em https://vercel.com (login com GitHub)
2. Instale CLI: `npm install -g vercel`
3. Nesta pasta:

```powershell
cd notify-api
vercel login
vercel
```

4. No dashboard Vercel → projeto → **Settings → Environment Variables**:
   - `TELEGRAM_BOT_TOKEN` = token do BotFather
   - `TELEGRAM_CHAT_ID` = seu id (só números)
5. **Redeploy** após salvar as variáveis
6. Anote a URL: `https://SEU-PROJETO.vercel.app/api/telegram-notify`
7. Cole em `site/public/assets/join.js` → `TELEGRAM_NOTIFY_WEBHOOK`
8. Commit + push (GitHub Pages)

## Teste

Abra no browser a URL do passo 6 → `"telegram_configured": true`

Depois teste `join.html` no Strava.
