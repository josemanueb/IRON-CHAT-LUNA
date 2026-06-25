@echo off
title IRON CHAT - LUNA Instalador
cd /d "%~dp0"

echo ╔══════════════════════════════════════╗
echo ║   INSTALADOR IRON CHAT - LUNA v2.0   ║
echo ║   PARA WINDOWS                       ║
echo ╚══════════════════════════════════════╝
echo.

REM Verificar Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado.
    echo ⬇️ Descárgalo desde: https://www.python.org/downloads/
    echo ⚠️ MARCA "Add Python to PATH" durante la instalación.
    echo.
    pause
    exit /b 1
)

python --version
echo.

python install.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Algo salió mal. Revisa los mensajes de arriba.
)

pause
