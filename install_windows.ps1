# ============================================================
# INSTALADOR IRON CHAT - LUNA v2.2 PARA WINDOWS
# Descarga Python portable si no está instalado
# ============================================================

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$ErrorActionPreference = "Continue"
$PYTHON_VERSION = "3.12.5"
$PYTHON_URL = "https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-embed-amd64.zip"

Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INSTALADOR IRON CHAT - LUNA v2.2   ║" -ForegroundColor Cyan
Write-Host "║   PARA WINDOWS                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n📂 Directorio: $SCRIPT_DIR" -ForegroundColor Cyan

# === 1. DETECTAR O DESCARGAR PYTHON ===
Write-Host "`n🔍 Detectando Python..." -ForegroundColor Cyan
$pythonExe = $null

# Buscar Python del sistema
foreach ($cmd in @("py", "python", "python3")) {
    try {
        $v = & $cmd --version 2>&1
        if ($v -match 'Python 3\.(1[0-9]|[2-9][0-9])') {
            $pythonExe = (Get-Command $cmd).Source
            Write-Host "  ✅ Python del sistema: $($v.Trim())" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pythonExe) {
    # Buscar Python portable ya descargado
    $portablePython = "$SCRIPT_DIR\portable_python\python.exe"
    if (Test-Path $portablePython) {
        $pythonExe = $portablePython
        Write-Host "  ✅ Python portable encontrado" -ForegroundColor Green
    } else {
        Write-Host "  ⬇️ Descargando Python portable ($PYTHON_VERSION)..." -ForegroundColor Yellow
        $zipPath = "$env:TEMP\python-embed.zip"
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $wc = New-Object System.Net.WebClient
            $wc.DownloadFile($PYTHON_URL, $zipPath)
            Write-Host "  ✅ Descargado. Extrayendo..." -ForegroundColor Green

            Expand-Archive -Path $zipPath -DestinationPath "$SCRIPT_DIR\portable_python" -Force

            # Habilitar imports en el Python portable (modificar ._pth)
            $pthFile = Get-ChildItem "$SCRIPT_DIR\portable_python\*._pth" | Select-Object -First 1
            if ($pthFile) {
                $content = Get-Content $pthFile.FullName
                $content = $content -replace '^#import site', 'import site'
                Set-Content -Path $pthFile.FullName -Value $content
            }

            # Instalar pip via get-pip.py
            $pipUrl = "https://bootstrap.pypa.io/get-pip.py"
            $getPip = "$env:TEMP\get-pip.py"
            $wc.DownloadFile($pipUrl, $getPip)
            & "$SCRIPT_DIR\portable_python\python.exe" $getPip --quiet 2>$null

            $pythonExe = "$SCRIPT_DIR\portable_python\python.exe"
            Write-Host "  ✅ Python portable listo" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ No se pudo descargar Python portable" -ForegroundColor Red
            Write-Host "  Descarga Python manual desde: https://www.python.org/downloads/" -ForegroundColor Yellow
            Write-Host "  y vuelve a ejecutar este instalador." -ForegroundColor Yellow
            pause
            exit 1
        }
        Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    }
}

# === 2. ENTORNO VIRTUAL ===
Write-Host "`n🔧 Creando entorno virtual..." -ForegroundColor Cyan
if (Test-Path "$SCRIPT_DIR\venv\Scripts\python.exe") {
    Write-Host "  ✅ Entorno virtual ya existe" -ForegroundColor Green
} else {
    & $pythonExe -m venv "$SCRIPT_DIR\venv"
    if (Test-Path "$SCRIPT_DIR\venv\Scripts\python.exe") {
        Write-Host "  ✅ Entorno virtual creado" -ForegroundColor Green
    } else {
        Write-Host "  ❌ No se pudo crear el entorno virtual" -ForegroundColor Red
        pause
        exit 1
    }
}

$venvPython = "$SCRIPT_DIR\venv\Scripts\python.exe"

# === 3. DEPENDENCIAS ===
Write-Host "`n📦 Instalando dependencias Python..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip -q

# 3a. llama-cpp-python (usar .whl local si existe)
Write-Host "  ⏳ Instalando llama-cpp-python..." -ForegroundColor Yellow
$llamaOk = $false

# Buscar .whl en el directorio del proyecto
$whlFile = Get-ChildItem "$SCRIPT_DIR\llama_cpp_python_win-*.whl" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($whlFile) {
    Write-Host "    Wheel local encontrado: $($whlFile.Name)" -ForegroundColor Gray
    $r = & $venvPython -m pip install "$($whlFile.FullName)" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $llamaOk = $true
        Write-Host "  ✅ llama-cpp-python instalado desde .whl local" -ForegroundColor Green
    }
}

if (-not $llamaOk) {
    # Intentar desde internet
    $methods = @(
        @("PyPI (solo binario)",     "--only-binary :all: llama-cpp-python"),
        @("abetlen.github.io",       "--only-binary :all: --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu llama-cpp-python")
    )
    foreach ($m in $methods) {
        Write-Host "    Intentando $($m[0])..." -ForegroundColor Gray
        $r = & $venvPython -m pip install $($m[1]) 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $llamaOk = $true
            Write-Host "  ✅ llama-cpp-python instalado" -ForegroundColor Green
            break
        }
    }
}

if (-not $llamaOk) {
    Write-Host "  ⚠️ llama-cpp-python NO se instalo. Modo offline activo." -ForegroundColor Yellow
    Write-Host "    La app funciona igual con respuestas limitadas." -ForegroundColor Yellow
}

# 3b. Dependencias secundarias
Write-Host "  ⏳ Instalando Pillow, pyttsx3..." -ForegroundColor Yellow
& $venvPython -m pip install --quiet Pillow pyttsx3 2>$null
Write-Host "  ✅ Pillow, pyttsx3 instalados" -ForegroundColor Green

# === 4. ACCESO DIRECTO ESCRITORIO ===
Write-Host "`n🖥️ Creando acceso directo..." -ForegroundColor Cyan
$desktop = [Environment]::GetFolderPath("Desktop")
$lnkPath = "$desktop\IRON CHAT - LUNA.lnk"

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
    Start-Process -FilePath "cscript" -ArgumentList "/nologo $vbsPath" -Wait -NoNewWindow -PassThru | Out-Null
    if (Test-Path $lnkPath) {
        Write-Host "  ✅ Acceso directo creado en el escritorio" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠️ No se pudo crear el acceso directo" -ForegroundColor Yellow
}
Remove-Item $vbsPath -Force -ErrorAction SilentlyContinue

# === 5. MODELO DE IA ===
Write-Host "`n🤖 Modelo de IA:" -ForegroundColor Cyan
$modelDir = "$SCRIPT_DIR\models"
if (-not (Test-Path $modelDir)) { New-Item -ItemType Directory -Path $modelDir -Force | Out-Null }
$existing = Get-ChildItem "$modelDir\*.gguf" -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 1MB }
if ($existing) {
    Write-Host "  ✅ Modelo encontrado: $($existing[0].Name)" -ForegroundColor Green
} else {
    Write-Host "  ℹ️ Sin modelo. LUNA usara modo offline." -ForegroundColor Yellow
    Write-Host "     Para IA avanzada: Menu -> Descargar Modelo" -ForegroundColor Yellow
}

# === 6. CARPETA MUSICA ===
Write-Host "`n🎵 Musica:" -ForegroundColor Cyan
$musicDir = "$SCRIPT_DIR\musica"
if (-not (Test-Path $musicDir)) { New-Item -ItemType Directory -Path $musicDir -Force | Out-Null }
Write-Host "  ✅ Carpeta musica/ creada" -ForegroundColor Green

# === 7. RESUMEN ===
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
