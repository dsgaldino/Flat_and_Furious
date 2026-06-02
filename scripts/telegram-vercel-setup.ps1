# Deploy notify-api na Vercel (alternativa ao Worker com SSL quebrado)
$ErrorActionPreference = "Stop"
$ApiDir = (Resolve-Path (Join-Path $PSScriptRoot "..\notify-api")).Path

Write-Host "`n=== Flat & Furious — Telegram na Vercel ===`n" -ForegroundColor Cyan
Write-Host "Conta grátis: https://vercel.com`n"

Push-Location $ApiDir
try {
    if (-not (Get-Command vercel -ErrorAction SilentlyContinue)) {
        Write-Host "Instalando Vercel CLI..." -ForegroundColor Yellow
        npm install -g vercel
    }
    vercel login
    vercel --prod
    Write-Host @"

Proximo passo:
  1. Vercel Dashboard -> Settings -> Environment Variables
     TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID (Production)
  2. Deployments -> Redeploy
  3. Teste: https://SEU-PROJETO.vercel.app/api/telegram-notify
  4. Atualize site/public/assets/join.js (TELEGRAM_NOTIFY_WEBHOOK)
  5. Push para GitHub Pages

"@ -ForegroundColor Green
}
finally {
    Pop-Location
}
