# ============================================================
#  INSTALADOR DE IRON CHAT - LUNA v2.0 PARA WINDOWS
#  Creado por: ⚡ JMbirner ⚡ con UOS AI
# ============================================================

Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INSTALADOR IRON CHAT - LUNA v2.0   ║" -ForegroundColor Cyan
Write-Host "║   PARA WINDOWS                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# === DETECTAR DIRECTORIO ===
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "📂 Directorio: $SCRIPT_DIR" -ForegroundColor Cyan

# === 1. VERIFICAR PYTHON ===
Write-Host "`n🔍 Verificando Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python no encontrado." -ForegroundColor Red
    Write-Host "  ⬇️  Descárgalo desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  ⚠️  MARCA LA OPCIÓN 'Add Python to PATH' durante la instalación" -ForegroundColor Yellow
    pause
    exit 1
}

# === 2. CREAR ENTORNO VIRTUAL ===
Write-Host "`n🔧 Creando entorno virtual..." -ForegroundColor Cyan
if (-not (Test-Path "$SCRIPT_DIR\venv")) {
    python -m venv "$SCRIPT_DIR\venv"
    Write-Host "  ✅ Entorno virtual creado" -ForegroundColor Green
} else {
    Write-Host "  ✅ Entorno virtual ya existe" -ForegroundColor Green
}

# === 3. ACTIVAR ENTORNO E INSTALAR DEPENDENCIAS ===
Write-Host "`n📦 Instalando dependencias Python..." -ForegroundColor Cyan
$venvPython = "$SCRIPT_DIR\venv\Scripts\python.exe"
$venvPip = "$SCRIPT_DIR\venv\Scripts\pip.exe"

# Actualizar pip
& $venvPython -m pip install --upgrade pip 2>&1 | Out-Null

# Instalar dependencias (en Windows NO se necesita compilar sin AVX)
Write-Host "  ⏳ Instalando llama-cpp-python..." -ForegroundColor Yellow
& $venvPip install llama-cpp-python 2>&1 | Out-Null
Write-Host "  ✅ llama-cpp-python instalado" -ForegroundColor Green

Write-Host "  ⏳ Instalando pygame, Pillow, pyttsx3..." -ForegroundColor Yellow
& $venvPip install pygame Pillow pyttsx3 2>&1 | Out-Null
Write-Host "  ✅ pygame, Pillow, pyttsx3 instalados" -ForegroundColor Green

# === 4. CREAR CARPETA DE MÚSICA ===
Write-Host "`n🎵 Creando carpeta de música..." -ForegroundColor Cyan
if (-not (Test-Path "$SCRIPT_DIR\musica")) {
    New-Item -ItemType Directory -Path "$SCRIPT_DIR\musica" | Out-Null
    Write-Host "  ✅ Carpeta musica/ creada (mete tus MP3 ahí)" -ForegroundColor Green
} else {
    Write-Host "  ✅ Carpeta musica/ ya existe" -ForegroundColor Green
}

# === 5. CREAR ACCESO DIRECTO EN EL ESCRITORIO ===
Write-Host "`n📌 Creando acceso directo en el escritorio..." -ForegroundColor Cyan
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = "$DesktopPath\IRON CHAT - LUNA.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = "$SCRIPT_DIR\venv\Scripts\python.exe"
    $Shortcut.Arguments = "$SCRIPT_DIR\main.py"
    $Shortcut.WorkingDirectory = "$SCRIPT_DIR"
    $Shortcut.Description = "Chatbot Inteligente con LUNA - Entrenadora Personal"
    # Buscar icono del robot
    $iconPath = "$SCRIPT_DIR\robot-icon.ico"
    if (Test-Path $iconPath) {
        $Shortcut.IconLocation = "$iconPath, 0"
    }
    $Shortcut.Save()
Write-Host "  ✅ Acceso directo creado en el escritorio" -ForegroundColor Green

# === 6. CREAR SCRIPT DE EJECUCIÓN RÁPIDA (run.bat) ===
Write-Host "`n📝 Creando run.bat para ejecución rápida..." -ForegroundColor Cyan
$batContent = @"
@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py
pause
"@
Set-Content -Path "$SCRIPT_DIR\run.bat" -Value $batContent -Encoding ASCII
Write-Host "  ✅ run.bat creado (doble clic para ejecutar)" -ForegroundColor Green

# === 7. VERIFICAR MODELO ===
Write-Host "`n🔍 Verificando modelo de IA..." -ForegroundColor Cyan
$modelPath = "$SCRIPT_DIR\models\Llama-3.2-3B-Instruct-Q4_0.gguf"
if (Test-Path $modelPath) {
    $modelSize = (Get-Item $modelPath).Length / 1GB
    Write-Host "  ✅ Modelo encontrado: $([math]::Round($modelSize, 2)) GB" -ForegroundColor Green
} else {
    Write-Host "  ❌ Modelo NO encontrado en:" -ForegroundColor Red
    Write-Host "     $modelPath" -ForegroundColor Red
    Write-Host "  ⚠️  Descárgalo desde:" -ForegroundColor Yellow
    Write-Host "     https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_0.gguf" -ForegroundColor Yellow
    Write-Host "  ⚠️  Y colócalo en: $SCRIPT_DIR\models\" -ForegroundColor Yellow
}

# === 8. VERIFICAR ARCHIVOS DEL PROYECTO ===
Write-Host "`n📋 Verificando archivos del proyecto..." -ForegroundColor Cyan
$archivos = @("main.py", "tts_module.py", "ai_module.py", "face_animation.py", "ascii_art.py", "sounds.py", "robot.jpeg")
$faltan = 0
foreach ($archivo in $archivos) {
    if (Test-Path "$SCRIPT_DIR\$archivo") {
        Write-Host "  ✅ $archivo" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $archivo FALTANTE" -ForegroundColor Red
        $faltan++
    }
}

# === 9. VERIFICAR VOCES ===
Write-Host "`n🎤 Verificando voces Piper..." -ForegroundColor Cyan
$voicesDir = "$SCRIPT_DIR\voices"
if (Test-Path $voicesDir) {
    $voices = Get-ChildItem "$voicesDir\*.onnx"
    if ($voices.Count -gt 0) {
        foreach ($voz in $voices) {
            Write-Host "  ✅ $($voz.Name)" -ForegroundColor Green
        }
    } else {
        Write-Host "  ⚠️  No hay voces Piper. El TTS usará pyttsx3 (voz del sistema)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️  No hay carpeta voices/. El TTS usará pyttsx3 (voz del sistema)" -ForegroundColor Yellow
}

# === 10. RESUMEN FINAL ===
Write-Host "`n╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INSTALACIÓN COMPLETADA            ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan

if ($faltan -eq 0) {
    Write-Host "`n  ✅ Todos los archivos OK" -ForegroundColor Green
} else {
    Write-Host "`n  ❌ Faltan $faltan archivos" -ForegroundColor Red
}

Write-Host "`n  🚀 Para ejecutar IRON CHAT:" -ForegroundColor Green
Write-Host "     1. Doble clic en el acceso directo del escritorio" -ForegroundColor Yellow
Write-Host "     2. O doble clic en 'run.bat'" -ForegroundColor Yellow
Write-Host "     3. O en terminal:" -ForegroundColor Yellow
Write-Host "        cd $SCRIPT_DIR" -ForegroundColor Yellow
Write-Host "        venv\Scripts\activate" -ForegroundColor Yellow
Write-Host "        python main.py" -ForegroundColor Yellow

Write-Host "`n  🎵 Para música: mete MP3s en:" -ForegroundColor Green
Write-Host "     $SCRIPT_DIR\musica\" -ForegroundColor Yellow

Write-Host "`n  🔊 TTS: Usa la voz natural de Windows (pyttsx3)" -ForegroundColor Green
Write-Host "     Si tienes voces Piper, las usará automáticamente" -ForegroundColor Yellow

Write-Host "`n  ⚡ JMbirner ⚡ - sin AVX 🐉🔥" -ForegroundColor Cyan
Write-Host ""

pause
