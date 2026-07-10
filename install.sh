#!/bin/bash
# ============================================================
#  INSTALADOR DE IRON CHAT - LUNA v2.2 PARA LINUX
#  Descarga automatica de modelo + acceso directo
#  Creado por: ⚡ JMbirner ⚡
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║   INSTALADOR IRON CHAT - LUNA v2.2   ║"
echo "║   PARA LINUX                          ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "📂 Directorio: $SCRIPT_DIR"
echo ""

# === 1. PYTHON ===
echo "🔍 Verificando Python..."
if command -v python3 &> /dev/null; then
    echo "  ✅ Python $(python3 --version)"
else
    echo "  ❌ Python3 no encontrado. Instálalo con:"
    echo "     sudo apt install -y python3 python3-venv python3-pip"
    exit 1
fi

# === 2. espeak-ng (TTS) ===
echo ""
echo "🔊 Instalando espeak-ng para TTS..."
if command -v espeak-ng &> /dev/null; then
    echo "  ✅ espeak-ng ya instalado"
else
    sudo apt install -y espeak-ng 2>/dev/null && echo "  ✅ espeak-ng instalado" || echo "  ⚠️ No se pudo instalar espeak-ng (TTS sin voz)"
fi

# === 3. ENTORNO VIRTUAL ===
echo ""
echo "🔧 Creando entorno virtual..."
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    python3 -m venv "$SCRIPT_DIR/venv"
    echo "  ✅ Entorno virtual creado"
else
    echo "  ✅ Entorno virtual ya existe"
fi

source "$SCRIPT_DIR/venv/bin/activate"

# === 4. PIP INSTALL (con detección de errores) ===
echo ""
echo "📦 Instalando dependencias Python..."
pip install --upgrade pip -q

echo "  ⏳ Instalando llama-cpp-python (sin AVX)..."
if pip install llama-cpp-python --prefer-binary -q; then
    echo "  ✅ llama-cpp-python instalado"
else
    echo "  ❌ Error instalando llama-cpp-python"
    echo "     Prueba: pip install llama-cpp-python"
    echo "     Ver documentación si el error persiste"
    exit 1
fi

echo "  ⏳ Instalando pygame, Pillow, ttkbootstrap..."
if pip install pygame Pillow ttkbootstrap -q; then
    echo "  ✅ pygame, Pillow, ttkbootstrap instalados"
else
    echo "  ⚠️ Error instalando dependencias secundarias."
    echo "     Puedes instalarlas manualmente después."
fi

echo "  ⏳ Verificando espeak-ng (TTS en Linux)..."
if command -v espeak-ng &> /dev/null; then
    echo "  ✅ espeak-ng encontrado"
else
    echo "  ⚠️ espeak-ng no instalado. Para TTS:"
    echo "     sudo apt install espeak-ng"
fi

# === 5. MODELO DE IA (opcional) ===
echo ""
echo "🤖 Modelo de IA (opcional):"
MODEL_DIR="$SCRIPT_DIR/models"
mkdir -p "$MODEL_DIR"
MODEL_PATH=$(find "$MODEL_DIR" -name "*.gguf" -size +1M 2>/dev/null | head -1)
if [ -n "$MODEL_PATH" ]; then
    echo "  ✅ Modelo encontrado en $MODEL_PATH"
else
    echo "  ℹ️ Sin modelo. LUNA usará su modo offline con respuestas completas."
    echo "     Para respuestas más avanzadas, coloca un .gguf en models/"
fi

# === 6. MUSICA ===
echo ""
echo "🎵 Creando carpeta de música..."
mkdir -p "$SCRIPT_DIR/musica"
echo "  ✅ Carpeta musica/ creada (mete tus MP3 ahí)"

# === 7. ACCESO DIRECTO (solo Linux) ===
echo ""
echo "📌 Creando acceso directo..."
DESKTOP_FILE="$HOME/Desktop/IRON-CHAT-LUNA.desktop"
DESKTOP_DIR="$HOME/Desktop"

if [ ! -d "$DESKTOP_DIR" ]; then
    if [ -d "$HOME/Escritorio" ]; then
        DESKTOP_DIR="$HOME/Escritorio"
        DESKTOP_FILE="$DESKTOP_DIR/IRON-CHAT-LUNA.desktop"
    fi
fi

if [ ! -d "$DESKTOP_DIR" ]; then
    mkdir -p "$DESKTOP_DIR"
fi

cat > "$DESKTOP_FILE" << DESKTOP
[Desktop Entry]
Name=IRON CHAT - LUNA
Comment=Chatbot con IA - Entrenadora personal
Exec=$SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/main.py
Icon=$SCRIPT_DIR/robot-icon.png
Path=$SCRIPT_DIR
Terminal=false
Type=Application
Categories=Utility;AI;
DESKTOP
chmod +x "$DESKTOP_FILE"
echo "  ✅ Acceso directo creado en: $DESKTOP_FILE"

APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"
cp "$DESKTOP_FILE" "$APPS_DIR/IRON-CHAT-LUNA.desktop"
echo "  ✅ Acceso directo registrado en aplicaciones"

# === 8. RESUMEN ===
echo ""
echo "╔══════════════════════════════════════╗"
echo "║   INSTALACIÓN COMPLETADA            ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  🚀 Ejecutar:"
echo "     - Menú de aplicaciones → IRON CHAT - LUNA"
echo "     - O doble clic en el icono del escritorio"
echo "     - O en terminal:"
echo "        cd $SCRIPT_DIR"
echo "        source venv/bin/activate"
echo "        python3 main.py"
echo ""
echo "  💡 También puedes crear acceso desde la app: ☰ Menú → Acceso Escritorio"
echo ""
echo "  ⚡ JMbirner ⚡"
echo ""
