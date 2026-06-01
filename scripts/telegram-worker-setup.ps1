# Flat & Furious — deploy do Worker de notificacao Telegram
# Uso: .\scripts\telegram-worker-setup.ps1

$ErrorActionPreference = "Stop"
$WorkersDir = (Resolve-Path (Join-Path $PSScriptRoot "..\workers")).Path

Write-Host ""
Write-Host "=== Flat & Furious - Telegram Worker ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Voce ja criou o bot? Envie 'oi' para t.me/flat_and_furious_bot antes de continuar."
Write-Host ""

Push-Location $WorkersDir
try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "Instalando wrangler..." -ForegroundColor Yellow
        npm install
    }

    $wrangler = Join-Path $WorkersDir "node_modules\.bin\wrangler.cmd"
    if (-not (Test-Path $wrangler)) {
        throw "wrangler nao encontrado apos npm install"
    }

    Write-Host "Abrindo login Cloudflare (browser)..." -ForegroundColor White
    & $wrangler login

    Write-Host ""
    Write-Host "Cole o TOKEN do BotFather quando pedir TELEGRAM_BOT_TOKEN:" -ForegroundColor Yellow
    & $wrangler secret put TELEGRAM_BOT_TOKEN

    Write-Host ""
    Write-Host "Cole seu chat id (getUpdates) quando pedir TELEGRAM_CHAT_ID:" -ForegroundColor Yellow
    & $wrangler secret put TELEGRAM_CHAT_ID

    Write-Host ""
    Write-Host "Fazendo deploy..." -ForegroundColor Yellow
    & $wrangler deploy

    Write-Host ""
    Write-Host "Pronto! Copie a URL do Worker acima (termina em .workers.dev)." -ForegroundColor Green
    Write-Host "Envie essa URL no chat (sem o token) para ativar o site." -ForegroundColor Green
    Write-Host ""
}
finally {
    Pop-Location
}
