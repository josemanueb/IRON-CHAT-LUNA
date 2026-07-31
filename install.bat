@echo off
setlocal EnableDelayedExpansion
title IRON CHAT - LUNA Instalador (Windows)
cd /d "%~dp0"

echo ======================================
echo   INSTALADOR IRON CHAT - LUNA v2.2
echo   PARA WINDOWS
echo ======================================
echo.
echo  NOTA: Si Windows muestra advertencia,
echo  haz click en "Mas informacion" -^> "Ejecutar de todas formas".
echo  Es normal, el programa no tiene firma digital.
echo.

:: Buscar Python (py va primero, evita el alias de Microsoft Store)
set PYTHON=
where py >nul 2>nul
if !errorlevel! equ 0 set PYTHON=py
if not defined PYTHON (
    where python >nul 2>nul
    if !errorlevel! equ 0 set PYTHON=python
)
if not defined PYTHON (
    echo [ERROR] Python no encontrado.
    echo Descargalo: https://www.python.org/downloads/
    echo MARCA "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

%PYTHON% --version
echo.

:: Ejecutar instalador PowerShell
echo Ejecutando instalador...
echo Si PowerShell pregunta, escribe: S (Yes)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "install_windows.ps1"
set PS_RESULT=!errorlevel!

if !PS_RESULT! equ 0 (
    echo.
    echo OK Instalacion completada.
    echo.
    echo Ejecuta iron-chat.bat para iniciar.
) else (
    echo.
    echo [AVISO] Algo salio mal (codigo !PS_RESULT!).
    echo Puedes intentar ejecutar manualmente:
    echo   - Clic derecho sobre install_windows.ps1 -^> "Ejecutar con PowerShell"
)

echo.
endlocal
pause
