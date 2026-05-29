# Registra varios codigos Strava de uma vez.
# Uso: .\scripts\register_members.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

$urls = @(
    "http://auth.flatandfurious/?state=&code=7214cc3dbb395eb37a1ae486e39afbc7b4ae253b&scope=read,activity:read",
    "http://auth.flatandfurious/?state=&code=04b79fe01895e04610bec67e8804e14c5bdd1080&scope=read,activity:read",
    "http://auth.flatandfurious/?state=&code=b6ab961a9d09744d7c91e0a224cf152eed8e4ced&scope=read,activity:read",
    "http://auth.flatandfurious/?state=&code=a5789efb1505aef1386c4ee1c17a43c512edb2f7&scope=read,activity:read",
    "http://auth.flatandfurious/?state=&code=a6f46adac8c44999bb792c7bcf35e1c3c2104cc0&scope=read,activity:read"
)

foreach ($url in $urls) {
    Write-Host "`n--- Registrando: $url ---"
    & $Python -m flatfurious auth --code $url
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Falhou (code pode ter expirado ou ja usado). Continue com os proximos."
    }
}

Write-Host "`nAtletas em data/tokens_athletes.csv:"
Import-Csv (Join-Path $Root "data\tokens_athletes.csv") | Select-Object nome, athlete_id
