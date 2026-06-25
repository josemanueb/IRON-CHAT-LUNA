#!/bin/bash
# ============================================================
#  INSTALADOR DE IRON CHAT - LUNA v2.0 PARA LINUX
#  Descarga automatica de modelo + voz + Piper
#  Creado por: ⚡ JMbirner ⚡
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║   INSTALADOR IRON CHAT - LUNA v2.0   ║"
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

# === 2. PIPER TTS ===
echo ""
echo "🔊 Instalando Piper TTS..."
if command -v piper-tts &> /dev/null; then
    echo "  ✅ Piper TTS ya instalado"
else
    echo "  ⏳ Instalando Piper TTS..."
    sudo apt install -y piper-tts 2>/dev/null && echo "  ✅ Piper instalado" || echo "  ⚠️ No se pudo instalar Piper. TTS no disponible"
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

# === 4. DEPENDENCIAS ===
echo ""
echo "📦 Instalando dependencias Python..."
pip install --upgrade pip -q
echo "  ⏳ Instalando llama-cpp-python (sin AVX)..."
pip install llama-cpp-python -q
echo "  ✅ llama-cpp-python instalado"
echo "  ⏳ Instalando pygame, Pillow..."
pip install pygame Pillow -q
echo "  ✅ pygame, Pillow instalados"

# === 5. MODELO DE IA (2 GB) ===
echo ""
echo "🤖 Descargando modelo de IA (Llama 3.2 3B, ~2 GB)..."
MODEL_DIR="$SCRIPT_DIR/models"
MODEL_PATH="$MODEL_DIR/Llama-3.2-3B-Instruct-Q4_0.gguf"
mkdir -p "$MODEL_DIR"

if [ -f "$MODEL_PATH" ]; then
    SIZE=$(du -h "$MODEL_PATH" | cut -f1)
    echo "  ✅ Modelo ya existe: $SIZE"
else
    echo "  ⏳ Descargando modelo (puede tomar varios minutos)..."
    MODEL_URL="https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_0.gguf"
    if command -v curl &> /dev/null; then
        curl -L "$MODEL_URL" -o "$MODEL_PATH" --progress-bar && echo "  ✅ Modelo descargado" || echo "  ❌ Error descargando modelo"
    elif command -v wget &> /dev/null; then
        wget "$MODEL_URL" -O "$MODEL_PATH" 2>&1 && echo "  ✅ Modelo descargado" || echo "  ❌ Error descargando modelo"
    else
        echo "  ❌ No hay curl ni wget. Instálalos: sudo apt install -y curl"
        echo "  ⚠️ Descárgalo manualmente desde:"
        echo "     $MODEL_URL"
        echo "  ⚠️ Y colócalo en: $MODEL_DIR"
    fi
fi

# === 6. VOZ PIPER ===
echo ""
echo "🎤 Descargando voz Piper (femenina española)..."
VOICES_DIR="$SCRIPT_DIR/voices"
VOICE_PATH="$VOICES_DIR/es_ES-sharvard-medium.onnx"
mkdir -p "$VOICES_DIR"

if [ -f "$VOICE_PATH" ]; then
    echo "  ✅ Voz Piper ya existe"
else
    echo "  ⏳ Descargando voz (77 MB)..."
    VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"
    VOICE_JSON_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json"
    if command -v curl &> /dev/null; then
        curl -L "$VOICE_URL" -o "$VOICE_PATH" --progress-bar && \
        curl -L "$VOICE_JSON_URL" -o "$VOICES_DIR/es_ES-sharvard-medium.onnx.json" --progress-bar && \
        echo "  ✅ Voz descargada" || echo "  ⚠️ No se pudo descargar la voz"
    elif command -v wget &> /dev/null; then
        wget "$VOICE_URL" -O "$VOICE_PATH" 2>&1 && \
        wget "$VOICE_JSON_URL" -O "$VOICES_DIR/es_ES-sharvard-medium.onnx.json" 2>&1 && \
        echo "  ✅ Voz descargada" || echo "  ⚠️ No se pudo descargar la voz"
    fi
fi

# === 7. MUSICA ===
echo ""
echo "🎵 Creando carpeta de música..."
mkdir -p "$SCRIPT_DIR/musica"
echo "  ✅ Carpeta musica/ creada (mete tus MP3 ahí)"

# === 8. ACCESO DIRECTO ===
echo ""
echo "📌 Creando acceso directo en el escritorio..."
DESKTOP_FILE="$HOME/Desktop/IRON-CHAT-LUNA.desktop"
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
echo "  ✅ Acceso directo creado en el escritorio"

# === 9. RESUMEN ===
echo ""
echo "╔══════════════════════════════════════╗"
echo "║   INSTALACIÓN COMPLETADA            ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  🚀 Ejecutar: Doble clic en 'IRON CHAT - LUNA' del escritorio"
echo "  🚀 O en terminal:"
echo "      cd $SCRIPT_DIR"
echo "      source venv/bin/activate"
echo "      python3 main.py"
echo ""
echo "  ⚡ JMbirner ⚡"
echo ""
