#!/bin/bash
# ============================================================
#  INSTALADOR DE IRON CHAT - LUNA v2.0 PARA LINUX
#  Descarga automatica de modelo + voz + acceso directo
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
echo "🔊 Piper TTS se instalará como paquete Python (piper-tts) en el venv"

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
if pip install llama-cpp-python -q; then
    echo "  ✅ llama-cpp-python instalado"
else
    echo "  ❌ Error instalando llama-cpp-python"
    echo "     Prueba: pip install llama-cpp-python"
    echo "     Ver documentación si el error persiste"
    exit 1
fi

echo "  ⏳ Instalando pygame, Pillow, piper-tts..."
if pip install pygame Pillow piper-tts -q; then
    echo "  ✅ pygame, Pillow, piper-tts instalados"
else
    echo "  ⚠️ Error instalando dependencias secundarias."
    echo "     Puedes instalarlas manualmente después."
fi

# === 5. MODELO DE IA (2 GB) ===
echo ""
echo "🤖 Descargando modelo de IA (Llama 3.2 3B, ~2 GB)..."
MODEL_DIR="$SCRIPT_DIR/models"
MODEL_PATH="$MODEL_DIR/Llama-3.2-3B-Instruct-Q4_0.gguf"
MODEL_URL="https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_0.gguf"
mkdir -p "$MODEL_DIR"

if [ -f "$MODEL_PATH" ]; then
    SIZE=$(du -h "$MODEL_PATH" | cut -f1)
    echo "  ✅ Modelo ya existe: $SIZE"
else
    echo "  ⏳ Descargando modelo (puede tomar varios minutos)..."
    echo "     ⚠️  NO CIERRES ESTA VENTANA hasta que termine!"
    echo ""
    MODEL_OK=false

    # curl con fallback SSL
    if command -v curl &> /dev/null; then
        curl -L "$MODEL_URL" -o "$MODEL_PATH.tmp" --progress-bar 2>/dev/null && \
        mv "$MODEL_PATH.tmp" "$MODEL_PATH" && MODEL_OK=true

        if [ "$MODEL_OK" = false ]; then
            echo "     ⚠️ Reintentando con SSL desactivado..."
            curl -L -k "$MODEL_URL" -o "$MODEL_PATH.tmp" --progress-bar 2>/dev/null && \
            mv "$MODEL_PATH.tmp" "$MODEL_PATH" && MODEL_OK=true
        fi
    elif command -v wget &> /dev/null; then
        wget "$MODEL_URL" -O "$MODEL_PATH" 2>&1 && MODEL_OK=true
        if [ "$MODEL_OK" = false ]; then
            echo "     ⚠️ Reintentando con SSL desactivado..."
            wget --no-check-certificate "$MODEL_URL" -O "$MODEL_PATH" 2>&1 && MODEL_OK=true
        fi
    fi

    if [ "$MODEL_OK" = true ]; then
        SIZE=$(du -h "$MODEL_PATH" | cut -f1)
        echo "  ✅ Modelo descargado: $SIZE"
    else
        echo "  ❌ Error descargando el modelo."
        echo ""
        echo "  ╔══════════════════════════════════════════════╗"
        echo "  ║   DESCARGA MANUAL REQUERIDA                ║"
        echo "  ╚══════════════════════════════════════════════╝"
        echo ""
        echo "  1. Abre este enlace en tu navegador:"
        echo "     $MODEL_URL"
        echo ""
        echo "  2. Espera a que descargue (~2 GB)"
        echo ""
        echo "  3. Copia el archivo descargado AQUÍ:"
        echo "     $MODEL_DIR"
        echo "     El nombre debe ser: Llama-3.2-3B-Instruct-Q4_0.gguf"
        echo ""
        echo "  4. Una vez colocado, ejecuta install.sh otra vez"
        echo ""
        read -p "     Presiona Enter cuando hayas colocado el modelo..."

        if [ -f "$MODEL_PATH" ]; then
            SIZE=$(du -h "$MODEL_PATH" | cut -f1)
            echo "  ✅ Modelo encontrado: $SIZE"
        else
            echo "  ⚠️ Modelo no encontrado. Puedes continuar sin IA."
        fi
    fi
fi

# === 6. VOZ PIPER ===
echo ""
echo "🎤 Descargando voz Piper (femenina española)..."
VOICES_DIR="$SCRIPT_DIR/voices"
VOICE_PATH="$VOICES_DIR/es_ES-sharvard-medium.onnx"
VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"
VOICE_JSON_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json"
mkdir -p "$VOICES_DIR"

if [ -f "$VOICE_PATH" ]; then
    echo "  ✅ Voz Piper ya existe"
else
    echo "  ⏳ Descargando voz (77 MB)..."
    VOICE_OK=false

    if command -v curl &> /dev/null; then
        curl -L "$VOICE_URL" -o "$VOICE_PATH" --progress-bar 2>/dev/null && \
        curl -L "$VOICE_JSON_URL" -o "$VOICES_DIR/es_ES-sharvard-medium.onnx.json" --progress-bar 2>/dev/null && \
        VOICE_OK=true

        if [ "$VOICE_OK" = false ]; then
            curl -L -k "$VOICE_URL" -o "$VOICE_PATH" --progress-bar 2>/dev/null && \
            curl -L -k "$VOICE_JSON_URL" -o "$VOICES_DIR/es_ES-sharvard-medium.onnx.json" --progress-bar 2>/dev/null && \
            VOICE_OK=true
        fi
    elif command -v wget &> /dev/null; then
        wget "$VOICE_URL" -O "$VOICE_PATH" 2>&1 && \
        wget "$VOICE_JSON_URL" -O "$VOICES_DIR/es_ES-sharvard-medium.onnx.json" 2>&1 && \
        VOICE_OK=true

        if [ "$VOICE_OK" = false ]; then
            wget --no-check-certificate "$VOICE_URL" -O "$VOICE_PATH" 2>&1 && \
            wget --no-check-certificate "$VOICE_JSON_URL" -O "$VOICES_DIR/es_ES-sharvard-medium.onnx.json" 2>&1 && \
            VOICE_OK=true
        fi
    fi

    if [ "$VOICE_OK" = true ]; then
        echo "  ✅ Voz descargada"
    else
        echo "  ⚠️ No se pudo descargar la voz. El TTS usará la voz del sistema."
    fi
fi

# === 7. MUSICA ===
echo ""
echo "🎵 Creando carpeta de música..."
mkdir -p "$SCRIPT_DIR/musica"
echo "  ✅ Carpeta musica/ creada (mete tus MP3 ahí)"

# === 8. ACCESO DIRECTO ===
echo ""
echo "📌 Creando acceso directo..."
DESKTOP_FILE="$HOME/Desktop/IRON-CHAT-LUNA.desktop"
DESKTOP_DIR="$HOME/Desktop"

# Detectar escritorio en otros idiomas
if [ ! -d "$DESKTOP_DIR" ]; then
    if [ -d "$HOME/Escritorio" ]; then
        DESKTOP_DIR="$HOME/Escritorio"
        DESKTOP_FILE="$DESKTOP_DIR/IRON-CHAT-LUNA.desktop"
    fi
fi

# Crear si no existe
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

# También registrar en aplicaciones
APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"
cp "$DESKTOP_FILE" "$APPS_DIR/IRON-CHAT-LUNA.desktop"
echo "  ✅ Acceso directo registrado en aplicaciones"

# === 9. RESUMEN ===
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
echo "  ⚡ JMbirner ⚡"
echo ""
