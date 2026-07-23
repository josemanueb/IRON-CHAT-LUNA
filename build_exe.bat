@echo off
title IRON CHAT - LUNA Builder (EXE)
cd /d "%~dp0"

echo ╔══════════════════════════════════════╗
echo ║   CONSTRUIR EJECUTABLE (.exe)        ║
echo ║   IRON CHAT - LUNA v2.2              ║
echo ╚══════════════════════════════════════╝
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
    pause
    exit /b 1
)

:: Instalar PyInstaller si no está
%PYTHON% -m pip install pyinstaller --quiet 2>nul

:: Construir el .exe
echo ⏳ Construyendo ejecutable (puede tardar varios minutos)...
echo.
%PYTHON% -m PyInstaller --onefile --windowed --icon=robot-icon.ico --name "IRON-CHAT-LUNA" --add-data "robot-icon.png;." --add-data "robot.jpeg;." --add-data "gymp.jpeg;." --add-data "iniciodesesion.wav;." --add-data "icon-jmb.png;." --add-data "lang.py;." --add-data "themes.py;." --add-data "hash_utils.py;." --add-data "ascii_art.py;." --add-data "sounds.py;." --add-data "audio.py;." --add-data "tts_module.py;." --add-data "face_animation.py;." --add-data "ai_module.py;." --add-data "progress_tracker.py;." --add-data "rutinas.json;." --add-data "SIGNATURE.md;." main.py

if exist "dist\IRON-CHAT-LUNA.exe" (
    echo.
    echo ✅ Ejecutable creado: dist\IRON-CHAT-LUNA.exe
    echo.
    echo NOTA: Windows mostrara la misma advertencia de seguridad
    echo porque el .exe no tiene firma digital.
    echo Para quitarla, necesitas un certificado de codigo ($).
    echo.
) else (
    echo.
    echo ❌ Error al construir el ejecutable.
)

pause
