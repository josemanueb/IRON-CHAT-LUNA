# ============================================================
# INSTALADOR IRON CHAT - LUNA v2.1 (Mejorado por Grok)
# ============================================================

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INSTALADOR IRON CHAT - LUNA v2.1   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "\n🔍 Detectando Python..." -ForegroundColor Cyan

$pythonCmd = $null
try {
    $v = & py --version 2>&1
    if ($v -match 'Python') { $pythonCmd = 'py' }
} catch {}

if (-not $pythonCmd) {
    try {
        $v = & python --version 2>&1
        if ($v -match 'Python') { $pythonCmd = 'python' }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "❌ Python no encontrado" -ForegroundColor Red
    Write-Host "Descarga Python desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Importante: Marca 'Add Python to PATH'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✅ Python detectado" -ForegroundColor Green

# Crear venv
Write-Host "\n🔧 Creando venv..." -ForegroundColor Cyan
& $pythonCmd -m venv venv

$venvPython = "$SCRIPT_DIR\venv\Scripts\python.exe"

Write-Host "\n📦 Instalando dependencias..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install --only-binary :all: llama-cpp-python Pillow pyttsx3 pywin32

Write-Host "\n✅ Instalacion completada!" -ForegroundColor Green
Write-Host "Ejecuta iron-chat.bat para iniciar el programa." -ForegroundColor Green
pause
