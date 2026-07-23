# ============================================================
# INSTALADOR IRON CHAT - LUNA v2.2 PARA WINDOWS
# Ejecutar como Administrador (click derecho -> "Ejecutar como Admin")
# ============================================================

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$ErrorActionPreference = "Continue"

Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INSTALADOR IRON CHAT - LUNA v2.2   ║" -ForegroundColor Cyan
Write-Host "║   PARA WINDOWS                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n📂 Directorio: $SCRIPT_DIR" -ForegroundColor Cyan

# === 1. DETECTAR PYTHON ===
Write-Host "`n🔍 Detectando Python..." -ForegroundColor Cyan
$pythonCmd = $null
foreach ($cmd in @("py", "python")) {
    try {
        $v = & $cmd --version 2>&1
        if ($v -match 'Python 3\.(1[0-9]|[2-9][0-9])') {
            $pythonCmd = $cmd
            Write-Host "  ✅ $cmd encontrado: $($v.Trim())" -ForegroundColor Green
            break
        }
    } catch {}
}
if (-not $pythonCmd) {
    Write-Host "  ❌ Python 3.10+ no encontrado" -ForegroundColor Red
    Write-Host "  Descargalo desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  IMPORTANTE: Marca 'Add Python to PATH'" -ForegroundColor Yellow
    pause
    exit 1
}

# === 2. ENTORNO VIRTUAL ===
Write-Host "`n🔧 Creando entorno virtual..." -ForegroundColor Cyan
if (Test-Path "$SCRIPT_DIR\venv\Scripts\python.exe") {
    Write-Host "  ✅ Entorno virtual ya existe" -ForegroundColor Green
} else {
    & $pythonCmd -m venv "$SCRIPT_DIR\venv"
    if (Test-Path "$SCRIPT_DIR\venv\Scripts\python.exe") {
        Write-Host "  ✅ Entorno virtual creado" -ForegroundColor Green
    } else {
        Write-Host "  ❌ No se pudo crear el entorno virtual" -ForegroundColor Red
        pause
        exit 1
    }
}

$venvPython = "$SCRIPT_DIR\venv\Scripts\python.exe"
$venvPip = "$SCRIPT_DIR\venv\Scripts\pip.exe"

# === 3. DEPENDENCIAS ===
Write-Host "`n📦 Instalando dependencias Python..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip -q

# 3a. llama-cpp-python (solo wheels, nunca compilar)
Write-Host "  ⏳ Instalando llama-cpp-python..." -ForegroundColor Yellow
$llamaOk = $false
$methods = @(
    @("PyPI (solo binario)",     "--only-binary :all: llama-cpp-python"),
    @("abetlen.github.io",       "--only-binary :all: --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu llama-cpp-python")
)
foreach ($m in $methods) {
    Write-Host "    Intentando $($m[0])..." -ForegroundColor Gray
    $r = Start-Process -FilePath $venvPip -ArgumentList "install $($m[1])" -Wait -NoNewWindow -PassThru
    if ($r.ExitCode -eq 0) {
        $llamaOk = $true
        break
    }
}
if (-not $llamaOk) {
    Write-Host "  ⚠️ llama-cpp-python NO se instalo. Modo offline activo." -ForegroundColor Yellow
    Write-Host "    La app funciona igual con respuestas limitadas." -ForegroundColor Yellow
}

# 3b. Dependencias secundarias
Write-Host "  ⏳ Instalando dependencias secundarias..." -ForegroundColor Yellow
& $venvPip install --quiet Pillow pyttsx3 2>$null
Write-Host "  ✅ Pillow, pyttsx3 instalados" -ForegroundColor Green

# === 4. ACCESO DIRECTO ESCRITORIO ===
Write-Host "`n🖥️ Creando acceso directo en el escritorio..." -ForegroundColor Cyan
$desktop = [Environment]::GetFolderPath("Desktop")
$lnkPath = "$desktop\IRON CHAT - LUNA.lnk"

# Crear .lnk via VBS (no necesita win32com)
$vbsContent = @"
Set o = WScript.CreateObject("WScript.Shell")
Set s = o.CreateShortcut("$lnkPath")
s.TargetPath = "$venvPython"
s.Arguments = "main.py"
s.WorkingDirectory = "$SCRIPT_DIR"
s.IconLocation = "$SCRIPT_DIR\robot-icon.ico"
s.WindowStyle = 7
s.Description = "IRON CHAT - LUNA"
s.Save
"@
$vbsPath = "$env:TEMP\_create_lnk.vbs"
Set-Content -Path $vbsPath -Value $vbsContent -Encoding ASCII
try {
    $p = Start-Process -FilePath "cscript" -ArgumentList "/nologo $vbsPath" -Wait -NoNewWindow -PassThru
    if (Test-Path $lnkPath) {
        Write-Host "  ✅ Acceso directo creado: $lnkPath" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠️ No se pudo crear acceso directo" -ForegroundColor Yellow
}
Remove-Item $vbsPath -Force -ErrorAction SilentlyContinue

# === 5. MODELO DE IA ===
Write-Host "`n🤖 Modelo de IA (opcional):" -ForegroundColor Cyan
$modelDir = "$SCRIPT_DIR\models"
if (-not (Test-Path $modelDir)) { New-Item -ItemType Directory -Path $modelDir -Force | Out-Null }
$existing = Get-ChildItem "$modelDir\*.gguf" -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 1MB }
if ($existing) {
    Write-Host "  ✅ Modelo encontrado: $($existing[0].Name)" -ForegroundColor Green
} else {
    Write-Host "  ℹ️ Sin modelo. LUNA usara modo offline." -ForegroundColor Yellow
    Write-Host "     Para IA avanzada, descarga desde la app: Menu -> Descargar Modelo" -ForegroundColor Yellow
}

# === 6. CARPETA MUSICA ===
Write-Host "`n🎵 Creando carpeta de musica..." -ForegroundColor Cyan
$musicDir = "$SCRIPT_DIR\musica"
if (-not (Test-Path $musicDir)) { New-Item -ItemType Directory -Path $musicDir -Force | Out-Null }
Write-Host "  ✅ Carpeta musica/ creada (mete tus MP3 ahi)" -ForegroundColor Green

# === 7. EXCLUIR DE WINDOWS DEFENDER (opcional) ===
Write-Host "`n🛡️ Windows Defender:" -ForegroundColor Cyan
Write-Host "  ℹ️ Si Windows bloquea la aplicacion, anade una exclusion:" -ForegroundColor Yellow
Write-Host "     Windows Security -> Virus & threat protection" -ForegroundColor Yellow
Write-Host "     -> Manage settings -> Exclusions -> Add folder" -ForegroundColor Yellow
Write-Host "     -> Selecciona: $SCRIPT_DIR" -ForegroundColor Yellow

# === 8. RESUMEN ===
Write-Host "`n╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INSTALACION COMPLETADA            ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝"
Write-Host ""
Write-Host "  🚀 Ejecutar:" -ForegroundColor Green
Write-Host "     - Doble clic en 'iron-chat.bat'"
Write-Host "     - O usa el acceso directo del escritorio"
Write-Host ""
Write-Host "  ⚡ JMB ⚡"
Write-Host ""
pause
