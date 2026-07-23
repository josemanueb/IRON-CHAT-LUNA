@echo off
title IRON CHAT - LUNA
cd /d "%~dp0"
echo Cargando IRON CHAT - LUNA...
echo.

REM Intentar con venv primero
if exist "venv\Scripts\python.exe" (
    echo Usando entorno virtual...
    "venv\Scripts\python.exe" main.py
) else (
    echo No se encontro venv. Intentando Python del sistema...
    python main.py || py main.py || echo [ERROR] Python no encontrado. Instala Python desde python.org y marca "Add Python to PATH".
)

echo.
echo IRON CHAT se ha cerrado.
pause
