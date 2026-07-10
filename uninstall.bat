@echo off
title DESINSTALAR IRON CHAT - LUNA
echo ╔══════════════════════════════════════╗
echo ║   DESINSTALADOR IRON CHAT - LUNA    ║
echo ╚══════════════════════════════════════╝
echo.

set SCRIPT_DIR=%~dp0

REM === 1. ELIMINAR ACCESO DIRECTO ===
echo 📌 Eliminando acceso directo del escritorio...
if exist "%USERPROFILE%\Desktop\IRON CHAT - LUNA.lnk" (
    del "%USERPROFILE%\Desktop\IRON CHAT - LUNA.lnk"
    echo   ✅ Acceso directo eliminado
) else (
    echo   ⚠️ No se encontró acceso directo
)

REM === 2. ELIMINAR ENTORNO VIRTUAL ===
echo.
echo 🔧 Eliminando entorno virtual...
if exist "%SCRIPT_DIR%venv" (
    rmdir /s /q "%SCRIPT_DIR%venv"
    echo   ✅ Entorno virtual eliminado
) else (
    echo   ⚠️ No se encontró el entorno virtual
)

REM === 3. ELIMINAR HISTORIAL Y BASE DE DATOS ===
echo.
echo 🗑️ Eliminando datos locales...
if exist "%SCRIPT_DIR%historial.json" (
    del "%SCRIPT_DIR%historial.json"
    echo   ✅ Historial eliminado
)
if exist "%SCRIPT_DIR%progreso.db" (
    del "%SCRIPT_DIR%progreso.db"
    echo   ✅ Base de datos eliminada
)
if exist "%SCRIPT_DIR%iron_chat.log" (
    del "%SCRIPT_DIR%iron_chat.log"
    echo   ✅ Logs eliminados
)

REM === 4. PREGUNTAR POR MODELO ===
echo.
echo ⚠️ ¿Quieres eliminar el modelo de IA (~2 GB)?
echo    Si lo eliminas, tendrás que descargarlo otra vez.
set /p BORRAR_MODELO="   (S/N): "
if /i "%BORRAR_MODELO%"=="S" (
    if exist "%SCRIPT_DIR%models" (
        rmdir /s /q "%SCRIPT_DIR%models"
        echo   ✅ Modelo eliminado
    )
)

REM === 5. PREGUNTAR POR CARPETA MÚSICA ===
echo.
echo ⚠️ ¿Quieres eliminar la carpeta de música?
set /p BORRAR_MUSICA="   (S/N): "
if /i "%BORRAR_MUSICA%"=="S" (
    if exist "%SCRIPT_DIR%musica" (
        rmdir /s /q "%SCRIPT_DIR%musica"
        echo   ✅ Música eliminada
    )
)

echo.
echo ✅ Desinstalación completada
echo.
echo   Los archivos del proyecto (main.py, etc.) se conservan.
echo   Si quieres borrarlos completamente, elimina la carpeta:
echo     %SCRIPT_DIR%
echo.
pause
