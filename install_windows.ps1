# ============================================================
# INSTALADOR IRON CHAT - LUNA v2.2 PARA WINDOWS
# Descarga Python portable (instalador completo) si no está instalado
# ============================================================

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$ErrorActionPreference = "Continue"
$PYTHON_VERSION = "3.12.5"
$PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-amd64.exe"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  INSTALADOR IRON CHAT - LUNA v2.2" -ForegroundColor Cyan
Write-Host "  PARA WINDOWS" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Directorio: $SCRIPT_DIR" -ForegroundColor Cyan

# === 1. DETECTAR O DESCARGAR PYTHON ===
Write-Host ""
Write-Host "Detectando Python..." -ForegroundColor Cyan
$portableDir = "$SCRIPT_DIR\portable_python"
$pythonExe = $null

# Si ya hay venv, usarlo directamente
if (Test-Path "$SCRIPT_DIR\venv\Scripts\python.exe") {
    $pythonExe = "$SCRIPT_DIR\venv\Scripts\python.exe"
    Write-Host "  OK Entorno virtual ya existe" -ForegroundColor Green
} else {
    # Buscar Python del sistema
    foreach ($cmd in @("py", "python", "python3")) {
        try {
            $v = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -and $v -match 'Python 3\.(1[0-9]|[2-9][0-9])') {
                $pythonExe = (Get-Command $cmd).Source
                Write-Host "  OK Python del sistema: $($v.Trim())" -ForegroundColor Green
                break
            }
        } catch {}
    }

    # Buscar Python portable ya instalado
    if (-not $pythonExe -and (Test-Path "$portableDir\python.exe")) {
        $pythonExe = "$portableDir\python.exe"
        Write-Host "  OK Python portable encontrado" -ForegroundColor Green
    }

    # Descargar instalador completo de Python (tiene venv, pip y tkinter)
    if (-not $pythonExe) {
        Write-Host "  Bajando instalador completo de Python $PYTHON_VERSION..." -ForegroundColor Yellow
        $installer = "$env:TEMP\python-installer.exe"
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $wc = New-Object System.Net.WebClient
            $wc.DownloadFile($PYTHON_INSTALLER_URL, $installer)

            Write-Host "  Instalando Python en $portableDir (sin admin)..." -ForegroundColor Yellow
            $p = Start-Process -FilePath $installer -ArgumentList "/quiet","InstallAllUsers=0","PrependPath=0","Include_test=0","Include_tcltk=1","Include_launcher=0","Include_pip=1","TargetDir=$portableDir" -Wait -PassThru
            if ($p.ExitCode -eq 0 -and (Test-Path "$portableDir\python.exe")) {
                $pythonExe = "$portableDir\python.exe"
                Write-Host "  OK Python portable listo" -ForegroundColor Green
            } else {
                Write-Host "  ERROR No se pudo instalar Python portable (codigo: $($p.ExitCode))" -ForegroundColor Red
                Write-Host "  Descarga Python manual desde: https://www.python.org/downloads/" -ForegroundColor Yellow
                Write-Host "  y vuelve a ejecutar este instalador." -ForegroundColor Yellow
                pause
                exit 1
            }
        } catch {
            Write-Host "  ERROR No se pudo descargar Python portable" -ForegroundColor Red
            Write-Host "  Descarga Python manual desde: https://www.python.org/downloads/" -ForegroundColor Yellow
            Write-Host "  y vuelve a ejecutar este instalador." -ForegroundColor Yellow
            pause
            exit 1
        }
        Remove-Item $installer -Force -ErrorAction SilentlyContinue
    }
}

# === 2. ENTORNO VIRTUAL ===
Write-Host ""
Write-Host "Creando entorno virtual..." -ForegroundColor Cyan
if (-not (Test-Path "$SCRIPT_DIR\venv\Scripts\python.exe")) {
    & $pythonExe -m venv "$SCRIPT_DIR\venv"
    if (-not (Test-Path "$SCRIPT_DIR\venv\Scripts\python.exe")) {
        Write-Host "  ERROR No se pudo crear el entorno virtual" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "  OK Entorno virtual creado" -ForegroundColor Green
}

$venvPython = "$SCRIPT_DIR\venv\Scripts\python.exe"
$venvPythonw = "$SCRIPT_DIR\venv\Scripts\pythonw.exe"

# === 3. DEPENDENCIAS ===
Write-Host ""
Write-Host "Instalando dependencias Python..." -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip -q

# 3a. Verificar Visual C++ Redistributable (necesario para llama-cpp-python)
Write-Host "  Verificando Visual C++ Redistributable..." -ForegroundColor Yellow
$vcMissing = $true
$vcPaths = @("$env:SystemRoot\System32\vcruntime140.dll", "$env:WINDIR\System32\vcruntime140.dll", "$env:SystemRoot\System32\vcruntime140_1.dll")
foreach ($p in $vcPaths) { if (Test-Path $p) { $vcMissing = $false; break } }
if ($vcMissing) {
    Write-Host "    AVISO No se encuentra vcruntime140.dll" -ForegroundColor Yellow
    Write-Host "    Descargando e instalando VC++ Redistributable..." -ForegroundColor Gray
    $vcUrl = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
    $vcTmp = "$env:TEMP\vc_redist.x64.exe"
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $wc = New-Object System.Net.WebClient
        $wc.DownloadFile($vcUrl, $vcTmp)
        Write-Host "    Instalando..." -ForegroundColor Gray
        $p = Start-Process -FilePath $vcTmp -ArgumentList "/install", "/quiet", "/norestart" -Wait -PassThru
        if ($p.ExitCode -in @(0, 3010, 1638)) {
            Write-Host "  OK VC++ Redistributable instalado" -ForegroundColor Green
        } else {
            Write-Host "    AVISO VC++ fallo (codigo: $($p.ExitCode))." -ForegroundColor Yellow
            Write-Host "    Descargalo manualmente: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "    AVISO No se pudo instalar automaticamente." -ForegroundColor Yellow
        Write-Host "    Descargalo manualmente: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
    }
    Remove-Item $vcTmp -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "  OK VC++ Redistributable presente" -ForegroundColor Green
}

# 3b. llama-cpp-python (usar .whl local si existe)
Write-Host "  Instalando llama-cpp-python..." -ForegroundColor Yellow
$llamaOk = $false

# Detectar soporte AVX de la CPU (los wheels precompilados lo requieren)
function Test-CpuHasAvx {
    try {
        $src = @"
using System;
using System.Runtime.InteropServices;
public static class CpuInfo {
    [DllImport("kernel32.dll")]
    public static extern bool GetIsProcessorFeaturePresent(int feature);
    public static bool HasAvx() { return GetIsProcessorFeaturePresent(39); }
    public static bool HasAvx2() { return GetIsProcessorFeaturePresent(40); }
}
"@
        Add-Type -TypeDefinition $src -ErrorAction Stop
        return ([CpuInfo]::HasAvx() -and [CpuInfo]::HasAvx2())
    } catch {
        return $false  # si no podemos detectarlo, asumimos que NO tiene AVX2
    }
}
$hasAvx = Test-CpuHasAvx
if ($hasAvx) {
    Write-Host "    CPU compatible con AVX2: se usan wheels precompilados" -ForegroundColor Gray
} else {
    Write-Host "    CPU SIN AVX2: se compilara llama-cpp-python sin AVX" -ForegroundColor Yellow
}

# Buscar cualquier .whl local de llama_cpp en el directorio del proyecto
$whlFile = Get-ChildItem "$SCRIPT_DIR\*.whl" -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'llama' } | Select-Object -First 1
if ($whlFile) {
    Write-Host "    Wheel local encontrado: $($whlFile.Name)" -ForegroundColor Gray
    & $venvPython -m pip install "$($whlFile.FullName)"
    if ($LASTEXITCODE -eq 0) {
        $llamaOk = $true
        Write-Host "  OK llama-cpp-python instalado desde .whl local" -ForegroundColor Green
    } else {
        Write-Host "    AVISO Error instalando .whl local, probando alternativas..." -ForegroundColor Yellow
    }
}

# Comprobar que el wheel instalado realmente funcione (sin SIGILL)
function Test-LlamaCppImport {
    & $venvPython -c "import llama_cpp" 2>&1 | Out-Null
    return $LASTEXITCODE -eq 0
}

# Compilar desde fuente SIN AVX (para CPUs antiguas) usando w64devkit
function Install-LlamaNoAvx {
    Write-Host "    Compilando llama-cpp-python SIN AVX (puede tardar varios minutos)..." -ForegroundColor Yellow
    $toolVer = "2.8.0"
    $toolDir = "$env:LOCALAPPDATA\w64devkit"
    # El archivo extrae dentro de una subcarpeta w64devkit\w64devkit\bin; buscar recursivo
    $gccPath = Get-ChildItem "$toolDir" -Recurse -Filter "gcc.exe" -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match '\\bin\\gcc\.exe$' } | Select-Object -First 1
    if (-not $gccPath) {
        $url = "https://github.com/skeeto/w64devkit/releases/download/v$toolVer/w64devkit-x64-$toolVer.7z.exe"
        $tmp = "$env:TEMP\w64devkit-$toolVer.7z.exe"
        Write-Host "      Descargando w64devkit $toolVer (compilador portable)..." -ForegroundColor Gray
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            $wc = New-Object System.Net.WebClient
            $wc.DownloadFile($url, $tmp)
            Write-Host "      Extrayendo..." -ForegroundColor Gray
            if (Test-Path $toolDir) { Remove-Item $toolDir -Recurse -Force -ErrorAction SilentlyContinue }
            New-Item -ItemType Directory -Path $toolDir -Force | Out-Null
            & $tmp -y "-o$toolDir" | Out-Null
            Remove-Item $tmp -Force -ErrorAction SilentlyContinue
        } catch {
            Write-Host "      ERROR descargando w64devkit: $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    }
    $gccPath = Get-ChildItem "$toolDir" -Recurse -Filter "gcc.exe" -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match '\\bin\\gcc\.exe$' } | Select-Object -First 1
    if (-not $gccPath) {
        Write-Host "      ERROR no se encontro gcc.exe en w64devkit" -ForegroundColor Red
        return $false
    }
    $w64bin = Split-Path -Parent $gccPath.FullName
    $env:PATH = "$w64bin;$env:PATH"
    $env:CMAKE_ARGS = "-DGGML_NATIVE=OFF -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_BMI2=OFF -DGGML_FMA=OFF -DGGML_F16C=OFF"
    Write-Host "      Instalando cmake y ninja..." -ForegroundColor Gray
    & $venvPython -m pip install --quiet cmake ninja
    if ($LASTEXITCODE -ne 0) { Write-Host "      ERROR instalando cmake/ninja" -ForegroundColor Red; return $false }
    Write-Host "      Compilando (sin AVX)... esto puede tardar 5-15 minutos" -ForegroundColor Gray
    # NOTA: --no-binary llama-cpp-python (NO :all:) para no forzar a compilar cmake/ninja desde fuente
    & $venvPython -m pip install --no-cache-dir llama-cpp-python --no-binary llama-cpp-python
    if ($LASTEXITCODE -ne 0) { return $false }
    Remove-Item Env:CMAKE_ARGS -ErrorAction SilentlyContinue
    return (Test-LlamaCppImport)
}

if (-not $llamaOk) {
    if (-not $hasAvx) {
        # CPU sin AVX2: compilar directamente SIN AVX (los wheels precompilados crashearian con SIGILL)
        if (Install-LlamaNoAvx) {
            $llamaOk = $true
            Write-Host "  OK llama-cpp-python compilado SIN AVX" -ForegroundColor Green
        }
    } else {
        # CPU con AVX2: intentar wheels precompilados desde internet
        $methods = @(
            @("PyPI (solo binario)", @("--only-binary", ":all:", "llama-cpp-python")),
            @("abetlen.github.io", @("--only-binary", ":all:", "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cpu", "llama-cpp-python"))
        )
        foreach ($m in $methods) {
            Write-Host "    Intentando $($m[0])..." -ForegroundColor Gray
            & $venvPython -m pip install @($m[1])
            if ($LASTEXITCODE -eq 0) {
                $llamaOk = $true
                Write-Host "  OK llama-cpp-python instalado" -ForegroundColor Green
                break
            }
        }
        if (-not $llamaOk -and -not (Test-LlamaCppImport)) {
            # El wheel precompilado pudo instalarse pero requerir AVX2; compilar sin AVX como respaldo
            Write-Host "    Wheel precompilado no compatible, compilando SIN AVX..." -ForegroundColor Yellow
            if (Install-LlamaNoAvx) {
                $llamaOk = $true
                Write-Host "  OK llama-cpp-python compilado SIN AVX (respaldo)" -ForegroundColor Green
            }
        }
    }
}

if (-not $llamaOk) {
    Write-Host "  AVISO llama-cpp-python NO se instalo. Modo offline activo." -ForegroundColor Yellow
    Write-Host "    La app funciona igual con respuestas limitadas." -ForegroundColor Yellow
}

# 3c. Dependencias secundarias
Write-Host "  Instalando Pillow, pyttsx3, pywin32..." -ForegroundColor Yellow
& $venvPython -m pip install --quiet Pillow pyttsx3 pywin32
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK Pillow, pyttsx3, pywin32 instalados" -ForegroundColor Green
} else {
    Write-Host "  AVISO Algunas dependencias secundarias fallaron" -ForegroundColor Yellow
}

# === 4. ACCESO DIRECTO ESCRITORIO ===
Write-Host ""
Write-Host "Creando acceso directo..." -ForegroundColor Cyan
$desktop = [Environment]::GetFolderPath("Desktop")
$lnkPath = "$desktop\IRON CHAT - LUNA.lnk"

# Usar pythonw.exe (sin consola) y WindowStyle=1 (normal)
$vbsContent = @"
Set o = WScript.CreateObject("WScript.Shell")
Set s = o.CreateShortcut("$lnkPath")
s.TargetPath = "$venvPythonw"
s.Arguments = "main.py"
s.WorkingDirectory = "$SCRIPT_DIR"
s.IconLocation = "$SCRIPT_DIR\robot-icon.ico"
s.WindowStyle = 1
s.Description = "IRON CHAT - LUNA"
s.Save
"@
$vbsPath = "$env:TEMP\_create_lnk.vbs"
Set-Content -Path $vbsPath -Value $vbsContent -Encoding Unicode
try {
    Start-Process -FilePath "cscript" -ArgumentList "/nologo", "`"$vbsPath`"" -Wait -NoNewWindow -PassThru | Out-Null
    if (Test-Path $lnkPath) {
        Write-Host "  OK Acceso directo creado en el escritorio" -ForegroundColor Green
    }
} catch {
    Write-Host "  AVISO No se pudo crear el acceso directo" -ForegroundColor Yellow
}
Remove-Item $vbsPath -Force -ErrorAction SilentlyContinue

# === 5. MODELO DE IA ===
Write-Host ""
Write-Host "Modelo de IA:" -ForegroundColor Cyan
$modelDir = "$SCRIPT_DIR\models"
if (-not (Test-Path $modelDir)) { New-Item -ItemType Directory -Path $modelDir -Force | Out-Null }
$existing = Get-ChildItem "$modelDir\*.gguf" -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 1MB }
if ($existing) {
    Write-Host "  OK Modelo encontrado: $($existing[0].Name)" -ForegroundColor Green
} else {
    Write-Host "  Info Sin modelo. LUNA usara modo offline." -ForegroundColor Yellow
    Write-Host "     Para IA avanzada: Menu -> Descargar Modelo" -ForegroundColor Yellow
}

# === 6. CARPETA MUSICA ===
Write-Host ""
Write-Host "Musica:" -ForegroundColor Cyan
$musicDir = "$SCRIPT_DIR\musica"
if (-not (Test-Path $musicDir)) { New-Item -ItemType Directory -Path $musicDir -Force | Out-Null }
Write-Host "  OK Carpeta musica/ creada" -ForegroundColor Green

# === 7. RESUMEN ===
Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  INSTALACION COMPLETADA" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Ejecutar:" -ForegroundColor Green
Write-Host "     - Doble clic en 'iron-chat.bat'"
Write-Host "     - O usa el acceso directo del escritorio"
Write-Host ""
Write-Host "  JMB"
Write-Host ""
pause
