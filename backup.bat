@echo off
title RESPALDO IRON CHAT - LUNA
cd /d "%~dp0"

echo ╔══════════════════════════════════════╗
echo ║   RESPALDO IRON CHAT - LUNA v2.0    ║
echo ╚══════════════════════════════════════╝
echo.

set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\Desktop
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmm'"') do set TS=%%i
set BACKUP_NAME=IRON-CHAT-LUNA-backup-%TS%
set BACKUP_DIR=%DESKTOP%\%BACKUP_NAME%

echo 📂 Creando carpeta de respaldo en el escritorio...
mkdir "%BACKUP_DIR%" 2>nul

echo 📦 Copiando archivos del proyecto...
REM Python
copy "%SCRIPT_DIR%main.py" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%ai_module.py" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%tts_module.py" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%face_animation.py" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%ascii_art.py" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%sounds.py" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%audio.py" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%progress_tracker.py" "%BACKUP_DIR%\" >nul

REM Instaladores
copy "%SCRIPT_DIR%install.py" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%install.bat" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%install.sh" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%install_windows.ps1" "%BACKUP_DIR%\" >nul

REM Scripts
copy "%SCRIPT_DIR%iron-chat.bat" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%uninstall.bat" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%uninstall.sh" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%crear_acceso_windows.vbs" "%BACKUP_DIR%\" >nul

REM Documentacion
copy "%SCRIPT_DIR%README.md" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%SIGNATURE.md" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%requirements.txt" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%.gitignore" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%generar_firma.py" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%verificar_firma.py" "%BACKUP_DIR%\" >nul

REM Assets (imagenes y sonidos)
copy "%SCRIPT_DIR%robot-icon.ico" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%robot-icon.png" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%robot.jpeg" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%gym.jpeg" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%gymp.jpeg" "%BACKUP_DIR%\" >nul
copy "%SCRIPT_DIR%iniciodesesion.wav" "%BACKUP_DIR%\" >nul

echo.
echo ✅ Respaldo completado en:
echo    %BACKUP_DIR%
echo.
echo Archivos: 28
echo Tamaño: ~1 MB (sin modelo ni venv)
echo.
echo ⚡ JMbirner ⚡
echo.
pause
