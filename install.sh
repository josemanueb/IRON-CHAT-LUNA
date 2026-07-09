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
if pip install llama-cpp-python --prefer-binary -q; then
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
echo "🤖 Selecciona el modelo de IA:"
echo "     1) Qwen 2.5 3B Instruct (RECOMENDADO — Apache 2.0, mejor español)"
echo "     2) Llama 3.2 3B Instruct (Meta, requiere aceptar licencia)"
read -p "     Selecciona [1/2] (default 1): " MODEL_CHOICE

if [ "$MODEL_CHOICE" = "2" ]; then
    MODEL_NAME="Llama-3.2-3B-Instruct-Q4_K_M.gguf"
    MODEL_URL="https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
    echo "     ℹ️ Llama 3.2 requiere aceptar licencia de Meta en huggingface.co"
else
    MODEL_NAME="qwen2.5-3b-instruct-q4_k_m.gguf"
    MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
fi

MODEL_DIR="$SCRIPT_DIR/models"
MODEL_PATH="$MODEL_DIR/$MODEL_NAME"
MODEL_OK=false
mkdir -p "$MODEL_DIR"

echo "🤖 Descargando $MODEL_NAME (~2 GB)..."
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
        curl -L "$MODEL_URL" -o "$MODEL_PATH.tmp" --progress-bar 2>&1 && \
        mv "$MODEL_PATH.tmp" "$MODEL_PATH" && MODEL_OK=true

        if [ "$MODEL_OK" = false ]; then
            echo "     ⚠️ Reintentando con SSL desactivado..."
            curl -L -k "$MODEL_URL" -o "$MODEL_PATH.tmp" --progress-bar 2>&1 && \
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
        echo "     El nombre debe ser: $MODEL_NAME"
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
        curl -L "$VOICE_URL" -o "$VOICE_PATH" --progress-bar 2>&1 && \
        curl -L "$VOICE_JSON_URL" -o "$VOICES_DIR/es_ES-sharvard-medium.onnx.json" --progress-bar 2>&1 && \
        VOICE_OK=true

        if [ "$VOICE_OK" = false ]; then
            curl -L -k "$VOICE_URL" -o "$VOICE_PATH" --progress-bar 2>&1 && \
            curl -L -k "$VOICE_JSON_URL" -o "$VOICES_DIR/es_ES-sharvard-medium.onnx.json" --progress-bar 2>&1 && \
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

# === 8. RESUMEN ===
echo ""
echo "╔══════════════════════════════════════╗"
echo "║   INSTALACIÓN COMPLETADA            ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  🚀 Ejecutar:"
echo "     - En terminal:"
echo "        cd $SCRIPT_DIR"
echo "        source venv/bin/activate"
echo "        python3 main.py"
echo ""
echo "  💡 Luego abre la app y usa ☰ Menú → Acceso Escritorio"
echo ""
echo "  ⚡ JMbirner ⚡"
echo ""
