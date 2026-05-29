# iniciar.ps1 — Inicio automatizado del Agente Turistico Cuba
#
# Uso: doble clic en iniciar.bat
#      o desde PowerShell: .\iniciar.ps1
#
# Que hace:
#   1. Lee el proxy actual del VPN (registro de Windows)
#   2. Actualiza PROXY_URL en .env
#   3. Detecta el entorno virtual
#   4. Abre ventana de la API y espera a que responda
#   5. Abre ventana del Bot

$ErrorActionPreference = "Continue"
$Host.UI.RawUI.WindowTitle = "Iniciador — Agente Turistico Cuba"
$projectDir = $PSScriptRoot

Write-Host ""
Write-Host "==========================================" -ForegroundColor DarkCyan
Write-Host "   AGENTE TURISTICO CUBA  -  Inicio       " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor DarkCyan
Write-Host ""

# ── 1. Leer proxy del registro de Windows ─────────────────
$reg = Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' `
       -ErrorAction SilentlyContinue
$proxyActivo  = $reg.ProxyEnable
$proxyServidor = $reg.ProxyServer

if ($proxyActivo -eq 1 -and $proxyServidor) {
    # ProxyServer puede ser "10.11.0.9:8080" o ya "http://..."
    if ($proxyServidor -notmatch "^http") {
        $proxyUrl = "http://$proxyServidor"
    } else {
        $proxyUrl = $proxyServidor
    }
    Write-Host "[PROXY]  Detectado: $proxyUrl" -ForegroundColor Green
} else {
    $proxyUrl = ""
    Write-Host "[PROXY]  Sin proxy (conexion directa)" -ForegroundColor Yellow
}

# ── 2. Actualizar PROXY_URL en .env ───────────────────────
$envFile = Join-Path $projectDir ".env"
if (-not (Test-Path $envFile)) {
    Write-Host ""
    Write-Host "[ERROR]  No se encontro .env" -ForegroundColor Red
    Write-Host "         Copia .env.example como .env y rellena las credenciales." -ForegroundColor Red
    Write-Host ""
    Read-Host "Presiona Enter para cerrar"
    exit 1
}

$envLines = Get-Content $envFile
$encontrado = $false
$envLines = $envLines | ForEach-Object {
    if ($_ -match "^PROXY_URL=") {
        $encontrado = $true
        "PROXY_URL=$proxyUrl"
    } else { $_ }
}
# Si la linea PROXY_URL no existia, agregarla
if (-not $encontrado) { $envLines += "PROXY_URL=$proxyUrl" }
Set-Content $envFile $envLines -Encoding UTF8
Write-Host "[.env]   PROXY_URL -> $proxyUrl" -ForegroundColor Green

# ── 3. Verificar configuracion basica ─────────────────────
$groqLine = (Get-Content $envFile) | Where-Object { $_ -match "^GROQ_API_KEY=" }
if ($groqLine -match "your_groq_api_key_here" -or $groqLine -eq "GROQ_API_KEY=") {
    Write-Host "[AVISO]  GROQ_API_KEY no esta configurada en .env" -ForegroundColor Yellow
    Write-Host "         El chat no funcionara. Edita .env con tu clave de console.groq.com" -ForegroundColor Yellow
}

$tokenLine = (Get-Content $envFile) | Where-Object { $_ -match "^TELEGRAM_TOKEN=" }
if ($tokenLine -match "your_telegram_bot_token_here" -or $tokenLine -eq "TELEGRAM_TOKEN=") {
    Write-Host "[AVISO]  TELEGRAM_TOKEN no esta configurado en .env" -ForegroundColor Yellow
}

# ── 4. Detectar entorno virtual ───────────────────────────
$venvDir = $null
foreach ($nombre in @("venv", ".venv", "env")) {
    if (Test-Path (Join-Path $projectDir "$nombre\Scripts\Activate.ps1")) {
        $venvDir = $nombre
        break
    }
}
if (-not $venvDir) {
    Write-Host ""
    Write-Host "[ERROR]  No se encontro entorno virtual (venv / .venv / env)" -ForegroundColor Red
    Write-Host "         Crealo con: python -m venv venv" -ForegroundColor Red
    Write-Host "         Luego instala: pip install -r requirements.txt" -ForegroundColor Red
    Write-Host ""
    Read-Host "Presiona Enter para cerrar"
    exit 1
}
Write-Host "[venv]   Entorno virtual: $venvDir\" -ForegroundColor Green

# ── 5. Abrir ventana de la API ────────────────────────────
Write-Host ""
Write-Host "[API]    Abriendo ventana de la API..." -ForegroundColor Cyan

$apiCmd = @"
`$Host.UI.RawUI.WindowTitle = 'API — Agente Turistico Cuba'
Set-Location '$projectDir'
`$env:HTTP_PROXY  = '$proxyUrl'
`$env:HTTPS_PROXY = '$proxyUrl'
`$env:NO_PROXY    = 'localhost,127.0.0.1'
`$env:no_proxy    = 'localhost,127.0.0.1'
& '.\$venvDir\Scripts\Activate.ps1'
Write-Host ''
Write-Host '  API — Agente Turistico Cuba' -ForegroundColor Cyan
Write-Host '  Ctrl+C para detener' -ForegroundColor Gray
Write-Host ''
python api.py
Write-Host ''
Write-Host 'La API se detuvo.' -ForegroundColor Red
Read-Host 'Presiona Enter para cerrar esta ventana'
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiCmd

# ── 6. Esperar a que la API responda ──────────────────────
Write-Host "[API]    Esperando que responda en http://localhost:8000" -ForegroundColor Cyan
Write-Host "         (puede tardar ~15 seg la primera vez por los embeddings)" -ForegroundColor Gray

$lista    = $false
$intentos = 0
while (-not $lista -and $intentos -lt 90) {
    Start-Sleep -Seconds 2
    $intentos++
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8000/" `
                -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { $lista = $true }
    } catch {}
    if (-not $lista -and ($intentos % 10 -eq 0)) {
        Write-Host "         Aun esperando... ($($intentos * 2)s)" -ForegroundColor Gray
    }
}

if ($lista) {
    Write-Host "[API]    Lista y respondiendo!" -ForegroundColor Green
} else {
    Write-Host "[AVISO]  Tiempo de espera agotado — iniciando bot de todas formas" -ForegroundColor Yellow
}

# ── 7. Abrir ventana del Bot ──────────────────────────────
Write-Host "[Bot]    Abriendo ventana del Bot..." -ForegroundColor Cyan

$botCmd = @"
`$Host.UI.RawUI.WindowTitle = 'Bot — Agente Turistico Cuba'
Set-Location '$projectDir'
`$env:HTTP_PROXY  = '$proxyUrl'
`$env:HTTPS_PROXY = '$proxyUrl'
`$env:NO_PROXY    = 'localhost,127.0.0.1'
`$env:no_proxy    = 'localhost,127.0.0.1'
& '.\$venvDir\Scripts\Activate.ps1'
Write-Host ''
Write-Host '  Bot — Agente Turistico Cuba' -ForegroundColor Cyan
Write-Host '  Ctrl+C para detener' -ForegroundColor Gray
Write-Host ''
python bot.py
Write-Host ''
Write-Host 'El bot se detuvo.' -ForegroundColor Red
Read-Host 'Presiona Enter para cerrar esta ventana'
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $botCmd

# ── 8. Resumen ────────────────────────────────────────────
Write-Host ""
Write-Host "==========================================" -ForegroundColor DarkGreen
Write-Host "  Todo iniciado correctamente!" -ForegroundColor Green
if ($proxyUrl) {
Write-Host "  Proxy activo: $proxyUrl" -ForegroundColor Green
} else {
Write-Host "  Sin proxy (conexion directa)" -ForegroundColor Green
}
Write-Host "  API:  http://localhost:8000" -ForegroundColor Green
Write-Host "  Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor DarkGreen
Write-Host ""
Write-Host "Puedes cerrar esta ventana." -ForegroundColor Gray
Write-Host ""
Start-Sleep -Seconds 4
