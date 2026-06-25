@echo off
title IRON CHAT - LUNA
cd /d "%~dp0"
echo Cargando IRON CHAT - LUNA...
echo.
call venv\Scripts\activate.bat
python main.py
echo.
echo IRON CHAT se ha cerrado.
pause
