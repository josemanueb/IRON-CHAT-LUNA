@echo off
title IRON CHAT - LUNA Instalador
cd /d "%~dp0"

echo ╔══════════════════════════════════════╗
echo ║   INSTALADOR IRON CHAT - LUNA v2.2   ║
echo ║   PARA WINDOWS                       ║
echo ╚══════════════════════════════════════╝
echo.
echo 🔍 NOTA: Si ves una advertencia de Windows,
echo    haz click en "Mas informacion" -^> "Ejecutar de todas formas"
echo    Es normal, el programa no tiene firma digital.
echo.

:: Buscar Python
set PYTHON=
where py >nul 2>nul
if %errorlevel% equ 0 set PYTHON=py
if not defined PYTHON (
    where python >nul 2>nul
    if %errorlevel% equ 0 set PYTHON=python
)
if not defined PYTHON (
    echo ❌ Python no encontrado.
    echo ⬇️ Descargalo: https://www.python.org/downloads/
    echo ⚠️ MARCA "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

%PYTHON% --version
echo.

:: Ejecutar instalador PowerShell
echo ⏳ Ejecutando instalador...
echo    Si PowerShell pregunta, escribe: S (Yes)
echo.
powershell -ExecutionPolicy Bypass -File "install_windows.ps1"

if %errorlevel% equ 0 (
    echo.
    echo ✅ Instalacion completada.
    echo.
    echo Ejecuta iron-chat.bat para iniciar.
) else (
    echo.
    echo ⚠️ Algo salio mal. Revisa los mensajes de arriba.
    echo    Puedes intentar ejecutar manualmente:
    echo    install_windows.ps1 (click derecho -^> Ejecutar con PowerShell)
)

echo.
pause
