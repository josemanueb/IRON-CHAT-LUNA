@echo off
title IRON CHAT - LUNA
cd /d "%~dp0"

REM Intentar con venv primero (usando pythonw para ocultar consola)
if exist "venv\Scripts\pythonw.exe" (
    "venv\Scripts\pythonw.exe" main.py
    exit /b 0
)
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" main.py
    exit /b 0
)

REM Fallback a Python del sistema. py/pyw van PRIMERO porque "where python"
REM puede detectar el alias de Microsoft Store que no es un Python real.
where pyw >nul 2>&1 && (
    pyw main.py
    exit /b 0
)
where py >nul 2>&1 && (
    py main.py
    exit /b 0
)
where pythonw >nul 2>&1 && (
    pythonw main.py
    exit /b 0
)
where python >nul 2>&1 && (
    python main.py
    exit /b 0
)

echo [ERROR] Python no encontrado. Instala Python desde python.org y marca "Add Python to PATH".
pause
