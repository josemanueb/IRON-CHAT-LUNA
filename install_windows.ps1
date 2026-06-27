# ============================================================
#  INSTALADOR DE IRON CHAT - LUNA v2.0 PARA WINDOWS (PowerShell)
#  Descarga automatica de modelo + voz + acceso directo
#  Creado por: ⚡ JMbirner ⚡
# ============================================================

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   INSTALADOR IRON CHAT - LUNA v2.0   ║" -ForegroundColor Cyan
Write-Host "║   PARA WINDOWS                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "📂 Directorio: $SCRIPT_DIR" -ForegroundColor Cyan

# === 1. PYTHON ===
Write-Host "`n🔍 Verificando Python..." -ForegroundColor Cyan
$pythonCmd = $null
try {
    $v = & python --version 2>&1
    $pythonCmd = "python"
} catch {}
if (-not $pythonCmd) {
    try {
        $v = & py --version 2>&1
        $pythonCmd = "py"
    } catch {}
}
if (-not $pythonCmd) {
    Write-Host "  ❌ Python no encontrado." -ForegroundColor Red
    Write-Host "  ⬇️  Descárgalo desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  ⚠️  MARCA LA OPCIÓN 'Add Python to PATH'" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host "  ✅ $v" -ForegroundColor Green

# === 2. ENTORNO VIRTUAL ===
Write-Host "`n🔧 Creando entorno virtual..." -ForegroundColor Cyan
if (-not (Test-Path "$SCRIPT_DIR\venv")) {
    & $pythonCmd -m venv "$SCRIPT_DIR\venv"
    Write-Host "  ✅ Entorno virtual creado" -ForegroundColor Green
} else {
    Write-Host "  ✅ Entorno virtual ya existe" -ForegroundColor Green
}

$venvPython = "$SCRIPT_DIR\venv\Scripts\python.exe"
$venvPip = "$SCRIPT_DIR\venv\Scripts\pip.exe"

# === 3. DEPENDENCIAS ===
Write-Host "`n📦 Instalando dependencias Python..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip | Out-Null

Write-Host "  ⏳ Instalando llama-cpp-python..." -ForegroundColor Yellow
$llamaOk = $false

# Paso 1: verificar VC++ Redistributable
$vcredistOk = Test-Path "$env:SystemRoot\System32\vcruntime140.dll" -or (Test-Path "$SCRIPT_DIR\vcruntime140.dll")
if (-not $vcredistOk) {
    Write-Host "  ⚠️ Falta Microsoft Visual C++ Redistributable" -ForegroundColor Yellow
    Write-Host "     Descargando e instalando..." -ForegroundColor Yellow
    try {
        $vcUrl = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
        $vcTmp = "$SCRIPT_DIR\vc_redist.x64.exe"
        $wc = New-Object System.Net.WebClient
        $wc.DownloadFile($vcUrl, $vcTmp)
        # Intentar silencioso
        Write-Host "     Ejecutando instalador..." -ForegroundColor Yellow
        $proc = Start-Process -FilePath $vcTmp -ArgumentList "/install", "/quiet", "/norestart" -Wait -NoNewWindow -PassThru
        Start-Sleep -Seconds 2
        if (Test-Path "$env:SystemRoot\System32\vcruntime140.dll") {
            Remove-Item $vcTmp -Force
            Write-Host "  ✅ VC++ Redistributable instalado" -ForegroundColor Green
        } else {
            # Fallback: interfaz visible
            Write-Host "     ⚠️ Modo silencioso falló, intentando con interfaz..." -ForegroundColor Yellow
            $proc = Start-Process -FilePath $vcTmp -ArgumentList "/install", "/passive", "/norestart" -Wait -PassThru
            Start-Sleep -Seconds 2
            if (Test-Path "$env:SystemRoot\System32\vcruntime140.dll") {
                Remove-Item $vcTmp -Force
                Write-Host "  ✅ VC++ Redistributable instalado" -ForegroundColor Green
            } else {
                # Fallback: extraer DLL directo
                Write-Host "     ⚠️ Instalación falló, extrayendo vcruntime140.dll..." -ForegroundColor Yellow
                $extractDir = "$SCRIPT_DIR\vc_extract"
                New-Item -ItemType Directory -Path $extractDir -Force | Out-Null
                Start-Process -FilePath $vcTmp -ArgumentList "/extract", $extractDir -Wait -NoNewWindow -PassThru
                $dll = Get-ChildItem -Path $extractDir -Recurse -Filter "vcruntime140.dll" | Select-Object -First 1
                if ($dll) {
                    Copy-Item $dll.FullName "$SCRIPT_DIR\vcruntime140.dll" -Force
                    Write-Host "  ✅ vcruntime140.dll extraído a $SCRIPT_DIR" -ForegroundColor Green
                    $env:PATH = "$SCRIPT_DIR;$env:PATH"
                    Remove-Item $extractDir -Recurse -Force -ErrorAction SilentlyContinue
                } else {
                    Write-Host "  ⚠️ No se pudo extraer el DLL." -ForegroundColor Yellow
                    Write-Host "     Descárgalo manualmente de: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
                }
                Remove-Item $extractDir -Recurse -Force -ErrorAction SilentlyContinue
                Remove-Item $vcTmp -Force
            }
        }
    } catch {
        Write-Host "  ⚠️ Error con VC++: $_" -ForegroundColor Yellow
        Write-Host "     Descárgalo manualmente de: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
        pause
    }
}

# Paso 2: instalar solo con wheels (NUNCA compilar)
Write-Host "     Buscando wheel pre-compilado en PyPI..." -ForegroundColor Yellow
$result = & $venvPip install --only-binary :all: llama-cpp-python 2>&1
if ($LASTEXITCODE -eq 0) { $llamaOk = $true }

if (-not $llamaOk) {
    Write-Host "     Buscando en abetlen.github.io..." -ForegroundColor Yellow
    $result = & $venvPip install --only-binary :all: --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu llama-cpp-python 2>&1
    if ($LASTEXITCODE -eq 0) { $llamaOk = $true }
}

# Paso 3: descargar el .whl directamente
if (-not $llamaOk) {
    Write-Host "     Descargando wheel directamente..." -ForegroundColor Yellow
    $pyVerNum = & $venvPython -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')"
    $pyVer = "cp$pyVerNum"
    $arch = if ([Environment]::Is64BitOperatingSystem) { "win_amd64" } else { "win32" }
    $vers = @("0.3.4", "0.3.3", "0.3.2", "0.3.1", "0.3.0", "0.2.90", "0.2.89")
    foreach ($ver in $vers) {
        $url = "https://abetlen.github.io/llama-cpp-python/whl/cpu/llama_cpp_python-$ver-$pyVer-$pyVer-$arch.whl"
        $tmp = "$SCRIPT_DIR\llama_$ver.whl"
        try {
            $wc = New-Object System.Net.WebClient
            $wc.DownloadFile($url, $tmp)
            if ((Get-Item $tmp).Length -gt 100KB) {
                Write-Host "     ✅ Wheel $ver descargado" -ForegroundColor Yellow
                $result = & $venvPip install $tmp 2>&1
                if ($LASTEXITCODE -eq 0) { $llamaOk = $true }
                Remove-Item $tmp -Force
                break
            }
            Remove-Item $tmp -Force
        } catch {
            if (Test-Path $tmp) { Remove-Item $tmp -Force }
        }
    }
}

if ($llamaOk) {
    Write-Host "  ✅ llama-cpp-python instalado" -ForegroundColor Green
} else {
    $pyVerNum = & $venvPython -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')"
    $pyVer = "cp$pyVerNum"
    $arch = if ([Environment]::Is64BitOperatingSystem) { "win_amd64" } else { "win32" }
    $wheelUrl = "https://abetlen.github.io/llama-cpp-python/whl/cpu/llama_cpp_python-0.3.4-$pyVer-$pyVer-$arch.whl"

    Write-Host "  ❌ Error CRITICO instalando llama-cpp-python" -ForegroundColor Red
    Write-Host ""
    Write-Host "  🔧 Esto suele pasar por UNA de estas razones:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  1️⃣  Falta el Microsoft Visual C++ Redistributable" -ForegroundColor Yellow
    Write-Host "      Descárgalo e instálalo desde:" -ForegroundColor Yellow
    Write-Host "      https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
    Write-Host "      (solo el runtime, NO necesitas Build Tools)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  2️⃣  No hay wheel para tu Python" -ForegroundColor Yellow
    Write-Host "      Python: $pyVer, arquitectura: $arch" -ForegroundColor Yellow
    Write-Host "      Prueba: & $venvPip install $wheelUrl" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  3️⃣  Error de conexión" -ForegroundColor Yellow
    Write-Host "      Asegúrate de tener internet y vuelve a intentar." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "  ⏳ Instalando Pillow, pyttsx3, pywin32..." -ForegroundColor Yellow
$result = & $venvPip install Pillow pyttsx3 pywin32 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Pillow, pyttsx3, pywin32 instalados" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Error instalando dependencias secundarias" -ForegroundColor Yellow
}

# === 4. MODELO DE IA (2 GB) ===
Write-Host "`n🤖 Descargando modelo de IA (Llama 3.2 3B, ~2 GB)..." -ForegroundColor Cyan
$modelDir = "$SCRIPT_DIR\models"
$modelPath = "$modelDir\Llama-3.2-3B-Instruct-Q4_K_M.gguf"
if (-not (Test-Path $modelDir)) { New-Item -ItemType Directory -Path $modelDir | Out-Null }

if (Test-Path $modelPath) {
    $modelSize = (Get-Item $modelPath).Length / 1GB
    Write-Host "  ✅ Modelo ya existe: $([math]::Round($modelSize, 2)) GB" -ForegroundColor Green
} else {
    $modelUrl = "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
    Write-Host "  ⏳ Descargando modelo (puede tomar varios minutos)..." -ForegroundColor Yellow

    $downloaded = $false
    $methods = @(
        { param($u, $d) $wc = New-Object System.Net.WebClient; $wc.DownloadFile($u, $d); $true },
        { param($u, $d) [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }; $wc = New-Object System.Net.WebClient; $wc.DownloadFile($u, $d); $true },
        { param($u, $d) Start-BitsTransfer -Source $u -Destination $d -Priority High; $true }
    )

    foreach ($method in $methods) {
        if ($downloaded) { break }
        try {
            & $method $modelUrl "$modelPath.tmp"
            if ((Get-Item "$modelPath.tmp").Length -gt 1GB) {
                Move-Item "$modelPath.tmp" $modelPath -Force
                $modelSize = (Get-Item $modelPath).Length / 1GB
                Write-Host "  ✅ Modelo descargado: $([math]::Round($modelSize, 2)) GB" -ForegroundColor Green
                $downloaded = $true
            }
        } catch {
            Write-Host "     ⚠️  Método falló: $_" -ForegroundColor Yellow
        }
    }

    if (-not $downloaded) {
        Write-Host "  ❌ Error descargando el modelo." -ForegroundColor Red
        Write-Host "`n  ╔══════════════════════════════════════════════╗" -ForegroundColor Yellow
        Write-Host "  ║   DESCARGA MANUAL REQUERIDA                ║" -ForegroundColor Yellow
        Write-Host "  ╚══════════════════════════════════════════════╝" -ForegroundColor Yellow
        Write-Host "`n  1. Abre este enlace en tu navegador:" -ForegroundColor Yellow
        Write-Host "     $modelUrl" -ForegroundColor Yellow
        Write-Host "`n  2. Copia el archivo descargado AQUÍ:" -ForegroundColor Yellow
        Write-Host "     $modelDir" -ForegroundColor Yellow
        Write-Host "     El nombre debe ser: Llama-3.2-3B-Instruct-Q4_K_M.gguf" -ForegroundColor Yellow
        Write-Host "`n  3. Una vez colocado, ejecuta el instalador otra vez" -ForegroundColor Yellow
        pause
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
    $voiceUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"
    $voiceJsonUrl = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json"
    Write-Host "  ⏳ Descargando voz (77 MB)..." -ForegroundColor Yellow
    try {
        $wc = New-Object System.Net.WebClient
        $wc.DownloadFile($voiceUrl, "$voicePath.tmp")
        $wc.DownloadFile($voiceJsonUrl, "$voiceJsonPath.tmp")
        Move-Item "$voicePath.tmp" $voicePath -Force
        Move-Item "$voiceJsonPath.tmp" $voiceJsonPath -Force
        Write-Host "  ✅ Voz descargada" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️ No se pudo descargar la voz" -ForegroundColor Yellow
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
$shortcutOk = $false
$desktopPath = [Environment]::GetFolderPath("Desktop")
$linkPath = "$desktopPath\IRON CHAT - LUNA.lnk"
$targetPath = "$SCRIPT_DIR\iron-chat.bat"
$iconPath = "$SCRIPT_DIR\robot-icon.ico"
if (-not (Test-Path $iconPath)) { $iconPath = "" }

# Método 1: COM object
try {
    $ws = New-Object -ComObject WScript.Shell
    $sc = $ws.CreateShortcut($linkPath)
    $sc.TargetPath = $targetPath
    $sc.WorkingDirectory = $SCRIPT_DIR
    $sc.Description = "Chatbot Inteligente con LUNA - Entrenadora Personal"
    if ($iconPath) { $sc.IconLocation = "$iconPath, 0" }
    $sc.Save()
    Write-Host "  ✅ Acceso directo creado en el escritorio" -ForegroundColor Green
    $shortcutOk = $true
} catch {
    Write-Host "  ⚠️ COM falló: $_" -ForegroundColor Yellow
}

# Método 2: Copiar iron-chat.bat al escritorio
if (-not $shortcutOk) {
    try {
        Copy-Item "$SCRIPT_DIR\iron-chat.bat" "$desktopPath\IRON CHAT - LUNA.bat" -Force
        Write-Host "  ✅ Acceso directo creado (copia .bat)" -ForegroundColor Green
        $shortcutOk = $true
    } catch {
        Write-Host "  ⚠️ Copia falló: $_" -ForegroundColor Yellow
    }
}

# Método 3: Generar .bat
if (-not $shortcutOk) {
    try {
        $batContent = '@echo off
cd /d "' + $SCRIPT_DIR + '"
"' + $SCRIPT_DIR + '\venv\Scripts\python.exe" main.py
pause'
        Set-Content -Path "$desktopPath\IRON CHAT - LUNA.bat" -Value $batContent -Encoding ASCII
        Write-Host "  ✅ Acceso directo creado (.bat generado)" -ForegroundColor Green
        $shortcutOk = $true
    } catch {
        Write-Host "  ⚠️ Generación falló: $_" -ForegroundColor Yellow
    }
}

if (-not $shortcutOk) {
    Write-Host "  ⚠️ Crea el acceso manual: clic derecho en iron-chat.bat → Enviar a Escritorio" -ForegroundColor Yellow
}

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
Write-Host "  🚀 Ejecutar:" -ForegroundColor Green
Write-Host "     - Doble clic en 'IRON CHAT - LUNA' del escritorio" -ForegroundColor Green
Write-Host "     - O doble clic en 'run.bat'" -ForegroundColor Green
Write-Host ""
Write-Host "  ⚡ JMbirner ⚡" -ForegroundColor Cyan
Write-Host ""
pause
