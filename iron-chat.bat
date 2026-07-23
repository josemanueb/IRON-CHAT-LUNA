@echo off
title IRON CHAT - LUNA
cd /d "%~dp0"

REM Intentar con venv primero (usando pythonw para ocultar consola)
if exist "venv\Scripts\pythonw.exe" (
    start "" /B "venv\Scripts\pythonw.exe" main.py
    exit
)
if exist "venv\Scripts\python.exe" (
    start "" /B "venv\Scripts\python.exe" main.py
    exit
)

REM Fallback a Python del sistema
where python >nul 2>&1 && (
    start "" /B python main.py
    exit
)
where py >nul 2>&1 && (
    start "" /B py main.py
    exit
)

echo [ERROR] Python no encontrado. Instala Python desde python.org y marca "Add Python to PATH".
pause
