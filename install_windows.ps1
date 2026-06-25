# ============================================================
#  INSTALADOR DE IRON CHAT - LUNA v2.0 PARA WINDOWS
#  Descarga automatica de modelo + voz
#  Creado por: ⚡ JMbirner ⚡
# ============================================================

Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INSTALADOR IRON CHAT - LUNA v2.0   ║" -ForegroundColor Cyan
Write-Host "║   PARA WINDOWS                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "📂 Directorio: $SCRIPT_DIR" -ForegroundColor Cyan

# === 1. PYTHON ===
Write-Host "`n🔍 Verificando Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python no encontrado." -ForegroundColor Red
    Write-Host "  ⬇️  Descárgalo desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  ⚠️  MARCA LA OPCIÓN 'Add Python to PATH'" -ForegroundColor Yellow
    pause
    exit 1
}

# === 2. ENTORNO VIRTUAL ===
Write-Host "`n🔧 Creando entorno virtual..." -ForegroundColor Cyan
if (-not (Test-Path "$SCRIPT_DIR\venv")) {
    python -m venv "$SCRIPT_DIR\venv"
    Write-Host "  ✅ Entorno virtual creado" -ForegroundColor Green
} else {
    Write-Host "  ✅ Entorno virtual ya existe" -ForegroundColor Green
}

# === 3. DEPENDENCIAS ===
Write-Host "`n📦 Instalando dependencias Python..." -ForegroundColor Cyan
$venvPython = "$SCRIPT_DIR\venv\Scripts\python.exe"
$venvPip = "$SCRIPT_DIR\venv\Scripts\pip.exe"

& $venvPython -m pip install --upgrade pip 2>&1 | Out-Null

Write-Host "  ⏳ Instalando llama-cpp-python..." -ForegroundColor Yellow
& $venvPip install llama-cpp-python 2>&1 | Out-Null
Write-Host "  ✅ llama-cpp-python instalado" -ForegroundColor Green

Write-Host "  ⏳ Instalando pygame, Pillow, pyttsx3..." -ForegroundColor Yellow
& $venvPip install pygame Pillow pyttsx3 2>&1 | Out-Null
Write-Host "  ✅ pygame, Pillow, pyttsx3 instalados" -ForegroundColor Green

# === 4. MODELO DE IA (2 GB) ===
Write-Host "`n🤖 Descargando modelo de IA (Llama 3.2 3B, ~2 GB)..." -ForegroundColor Cyan
$modelDir = "$SCRIPT_DIR\models"
$modelPath = "$modelDir\Llama-3.2-3B-Instruct-Q4_0.gguf"
if (-not (Test-Path $modelDir)) { New-Item -ItemType Directory -Path $modelDir | Out-Null }

if (Test-Path $modelPath) {
    $modelSize = (Get-Item $modelPath).Length / 1GB
    Write-Host "  ✅ Modelo ya existe: $([math]::Round($modelSize, 2)) GB" -ForegroundColor Green
} else {
    Write-Host "  ⏳ Descargando modelo (esto puede tomar varios minutos)..." -ForegroundColor Yellow
    $modelUrl = "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_0.gguf"
    try {
        $wc = New-Object System.Net.WebClient
        $wc.DownloadFile($modelUrl, "$modelPath.tmp")
        Move-Item "$modelPath.tmp" $modelPath -Force
        $modelSize = (Get-Item $modelPath).Length / 1GB
        Write-Host "  ✅ Modelo descargado: $([math]::Round($modelSize, 2)) GB" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Error descargando modelo: $_" -ForegroundColor Red
        Write-Host "  ⚠️  Descárgalo manualmente desde:" -ForegroundColor Yellow
        Write-Host "     $modelUrl" -ForegroundColor Yellow
        Write-Host "  ⚠️  Y colócalo en: $modelDir" -ForegroundColor Yellow
    }
}

# === 5. VOZ PIPER ===
Write-Host "`n🎤 Descargando voz Piper (femenina española)..." -ForegroundColor Cyan
$voicesDir = "$SCRIPT_DIR\voices"
$voicePath = "$voicesDir\es_ES-sharvard-medium.onnx"
$voiceJsonPath = "$voicesDir\es_ES-sharvard-medium.onnx.json"
if (-not (Test-Path $voicesDir)) { New-Item -ItemType Directory -Path $voicesDir | Out-Null }

if (Test-Path $voicePath) {
    Write-Host "  ✅ Voz Piper ya existe" -ForegroundColor Green
} else {
    Write-Host "  ⏳ Descargando voz (77 MB)..." -ForegroundColor Yellow
    $voiceUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"
    $voiceJsonUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json"
    try {
        $wc = New-Object System.Net.WebClient
        $wc.DownloadFile($voiceUrl, $voicePath)
        $wc.DownloadFile($voiceJsonUrl, $voiceJsonPath)
        Write-Host "  ✅ Voz descargada: es_ES-sharvard-medium.onnx" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️ No se pudo descargar la voz. El TTS usará pyttsx3 (voz del sistema)" -ForegroundColor Yellow
    }
}

# === 6. MUSICA ===
Write-Host "`n🎵 Creando carpeta de música..." -ForegroundColor Cyan
if (-not (Test-Path "$SCRIPT_DIR\musica")) {
    New-Item -ItemType Directory -Path "$SCRIPT_DIR\musica" | Out-Null
    Write-Host "  ✅ Carpeta musica/ creada (mete tus MP3 ahí)" -ForegroundColor Green
} else {
    Write-Host "  ✅ Carpeta musica/ ya existe" -ForegroundColor Green
}

# === 7. ACCESO DIRECTO ===
Write-Host "`n📌 Creando acceso directo en el escritorio..." -ForegroundColor Cyan
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = "$DesktopPath\IRON CHAT - LUNA.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "$SCRIPT_DIR\venv\Scripts\python.exe"
$Shortcut.Arguments = '"{0}\main.py"' -f $SCRIPT_DIR
$Shortcut.WorkingDirectory = "$SCRIPT_DIR"
$Shortcut.Description = "Chatbot Inteligente con LUNA - Entrenadora Personal"
$iconPath = "$SCRIPT_DIR\robot-icon.ico"
if (Test-Path $iconPath) { $Shortcut.IconLocation = "$iconPath, 0" }
$Shortcut.Save()
Write-Host "  ✅ Acceso directo creado en el escritorio" -ForegroundColor Green

# === 8. RUN.BAT ===
Write-Host "`n📝 Creando run.bat..." -ForegroundColor Cyan
$batContent = @"
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py
pause
"@
Set-Content -Path "$SCRIPT_DIR\run.bat" -Value $batContent -Encoding ASCII
Write-Host "  ✅ run.bat creado" -ForegroundColor Green

# === 9. RESUMEN ===
Write-Host "`n╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INSTALACIÓN COMPLETADA            ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  🚀 Ejecutar: Doble clic en 'IRON CHAT - LUNA' del escritorio" -ForegroundColor Green
Write-Host "  🚀 O: doble clic en 'run.bat'" -ForegroundColor Green
Write-Host ""
Write-Host "  ⚡ JMbirner ⚡" -ForegroundColor Cyan
Write-Host ""
pause
