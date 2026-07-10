#!/usr/bin/env bash
# DESINSTALADOR DE IRON CHAT - LUNA v2.0 (Linux)
# Creado por: ⚡ JMbirner ⚡

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║   DESINSTALADOR IRON CHAT - LUNA    ║"
echo "╚══════════════════════════════════════╝"
echo ""

# === 1. ELIMINAR ACCESO DIRECTO ===
echo "📌 Eliminando acceso directo del escritorio..."
DESKTOP_FILE="$HOME/Desktop/IRON-CHAT-LUNA.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo "  ✅ Acceso directo eliminado"
else
    echo "  ⚠️  No se encontró acceso directo"
fi

# También buscar en ~/.local/share/applications
DESKTOP_LOCAL="$HOME/.local/share/applications/IRON-CHAT-LUNA.desktop"
if [ -f "$DESKTOP_LOCAL" ]; then
    rm "$DESKTOP_LOCAL"
    echo "  ✅ Acceso directo de aplicaciones eliminado"
fi

# === 2. ELIMINAR ENTORNO VIRTUAL ===
echo ""
echo "🔧 Eliminando entorno virtual..."
if [ -d "$SCRIPT_DIR/venv" ]; then
    rm -rf "$SCRIPT_DIR/venv"
    echo "  ✅ Entorno virtual eliminado"
else
    echo "  ⚠️  No se encontró el entorno virtual"
fi

# === 3. ELIMINAR HISTORIAL Y BASE DE DATOS ===
echo ""
echo "🗑️  Eliminando datos locales..."
for f in "$SCRIPT_DIR/historial.json" "$SCRIPT_DIR/progreso.db" "$SCRIPT_DIR/iron_chat.log"; do
    if [ -f "$f" ]; then
        rm "$f"
        echo "  ✅ $(basename "$f") eliminado"
    fi
done

# === 4. PREGUNTAR POR MODELO ===
echo ""
echo "⚠️  ¿Quieres eliminar el modelo de IA (~2 GB)?"
echo "    Si lo eliminas, tendrás que descargarlo otra vez."
read -p "   (s/N): " -r BORRAR_MODELO
if [[ "$BORRAR_MODELO" =~ ^[Ss]$ ]]; then
    if [ -d "$SCRIPT_DIR/models" ]; then
        rm -rf "$SCRIPT_DIR/models"
        echo "  ✅ Modelo eliminado"
    fi
fi

# === 5. PREGUNTAR POR CARPETA MÚSICA ===
echo ""
echo "⚠️  ¿Quieres eliminar la carpeta de música?"
read -p "   (s/N): " -r BORRAR_MUSICA
if [[ "$BORRAR_MUSICA" =~ ^[Ss]$ ]]; then
    if [ -d "$SCRIPT_DIR/musica" ]; then
        rm -rf "$SCRIPT_DIR/musica"
        echo "  ✅ Música eliminada"
    fi
fi

# === 6. LIMPIAR CACHÉ DE pygame (Linux) ===
echo ""
echo "🧹 Limpiando cachés..."
PIP_CACHE="$HOME/.cache/pip"
if [ -d "$PIP_CACHE" ]; then
    echo "  ℹ️  Caché de pip conservada en $PIP_CACHE"
fi

echo ""
echo "✅ Desinstalación completada"
echo ""
echo "  Los archivos del proyecto (main.py, etc.) se conservan."
echo "  Si quieres borrarlos completamente, elimina la carpeta:"
echo "    $SCRIPT_DIR"
echo ""
