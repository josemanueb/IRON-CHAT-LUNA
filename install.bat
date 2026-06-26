@echo off
title IRON CHAT - LUNA Instalador
cd /d "%~dp0"

echo ╔══════════════════════════════════════╗
echo ║   INSTALADOR IRON CHAT - LUNA v2.0   ║
echo ║   PARA WINDOWS                       ║
echo ╚══════════════════════════════════════╝
echo.

REM Intentar con py (Windows Launcher) o python
where py >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON=py
) else (
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        echo ❌ Python no encontrado.
        echo ⬇️ Descárgalo desde: https://www.python.org/downloads/
        echo ⚠️ MARCA "Add Python to PATH" durante la instalación.
        echo.
        pause
        exit /b 1
    )
    set PYTHON=python
)

%PYTHON% --version
echo.
echo Instalando IRON CHAT - LUNA...
echo.

%PYTHON% install.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Instalación completada correctamente.
    echo.
    echo Ejecuta iron-chat.bat para iniciar.
) else (
    echo.
    echo ❌ Algo salió mal. Revisa los mensajes de arriba.
    echo.
    echo Si el error es llama-cpp-python, asegúrate de tener instalado:
    echo   Microsoft Visual C++ Redistributable
    echo   https://aka.ms/vs/17/release/vc_redist.x64.exe
)

echo.
pause
