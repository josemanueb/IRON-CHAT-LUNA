# ============================================================
# INSTALADOR IRON CHAT - LUNA v2.1 (Mejorado por Grok)
# ============================================================

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INSTALADOR IRON CHAT - LUNA v2.0   ║" -ForegroundColor Cyan
Write-Host "║   PARA WINDOWS                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "📂 Directorio: $SCRIPT_DIR" -ForegroundColor Cyan

# Verificar carpetas protegidas
$protectedPaths = @(
    [Environment]::GetFolderPath("Desktop"),
    [Environment]::GetFolderPath("MyDocuments"),
    [Environment]::GetFolderPath("UserProfile") + "\Downloads"
)
$inProtected = $false
foreach ($p in $protectedPaths) {
    if ($SCRIPT_DIR.ToLower().StartsWith($p.ToLower())) { $inProtected = $true; break }
}
if ($inProtected) {
    Write-Host ""
    Write-Host "  ⚠️  ATENCIÓN: Estás instalando en una carpeta protegida" -ForegroundColor Yellow
    Write-Host "     (Desktop, Downloads, etc.). Windows Defender puede BLOQUEAR" -ForegroundColor Yellow
    Write-Host "     la descarga del modelo y el acceso directo." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  ✅ Recomendación: Mueve la carpeta a C:\IRON-CHAT-LUNA\" -ForegroundColor Green
    Write-Host "     y ejecuta este instalador desde allí." -ForegroundColor Green
    Write-Host ""
    pause
}

Write-Host "`n🔍 Detectando Python..." -ForegroundColor Cyan

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
