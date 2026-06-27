# 💪 IRON CHAT - LUNA v2.1 🏋️

**Chatbot con IA especializado en fitness, nutrición y motivación.**

![Python](https://img.shields.io/badge/Python-3.12-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey)

---

## ✨ Características

| Función | Descripción |
|---------|-------------|
| 🤖 **IA local** | Llama 3.2 3B (GGUF Q4_K_M) — sin internet necesaria |
| 🧠 **Memoria** | Recuerda los últimos 5 mensajes de la conversación |
| 🔊 **TTS real** | Piper TTS (Linux) / pyttsx3 (Windows) — voz femenina española, velocidad ajustable ⚡ |
| 🎨 **Cara animada** | Robot que se balancea al hablar |
| 🖼️ **26 dibujos ASCII** | Mancuerna, pesa, musculo, flexión, sentadilla y más |
| ⏱️ **Temporizador** | Cuenta atrás para descanso entre series (30s/60s/90s/120s/personalizado) |
| 🏋️ **Rutinas rápidas** | Push, Pull, Piernas, Full Body, Cardio, Calistenia |
| 🥗 **Dietas** | Planes de volumen, definición y alimentación saludable |
| 📊 **Progreso SQLite** | Guarda peso, medidas corporales y ve tu evolución con deltas ▲▼ |
| 🌙 **3 Temas** | Oscuro, Claro y Naturaleza — alterna con /tema o Ctrl+T |
| 🎵 **Música** | Reproduce MP3 motivacionales desde la carpeta `musica/` con volumen independiente |
| ⏰ **Recordatorios** | Programa avisos con /recordatorio |
| 📝 **Notas rápidas** | Bloc de notas para tus entrenos |
| 📤 **Exportar chat** | Guarda el historial en tu escritorio (Ctrl+D) |
| 📚 **Ejercicios** | Guía de técnica para sentadilla, press banca, peso muerto, etc. |
| 🔐 **Firma digital** | Verificación de integridad SHA256 |
| 🐉 **Sin AVX** | Compilado para CPUs antiguas (Intel Core i3 M 380) |

---

## 🖥️ Requisitos

- **CPU**: Cualquiera (compatible sin AVX)
- **RAM**: 8 GB (mínimo 4 GB)
- **Disco**: ~3 GB libres (modelo + voces)
- **SO**: Linux (Deepin, Ubuntu, Debian) o Windows 10/11
- **Python**: 3.12

---

## 🚀 Instalación

### Linux

```bash
# 1. Clonar el repositorio
git clone https://github.com/josemanueb/IRON-CHAT-LUNA.git
cd IRON-CHAT-LUNA

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install --upgrade pip
pip install llama-cpp-python pygame Pillow

# 4. Instalar Piper TTS
sudo apt install -y piper-tts

# 5. Descargar el modelo
# Colocá Llama-3.2-3B-Instruct-Q4_K_M.gguf en models/

# 6. Ejecutar
python3 main.py
```

### Windows

Ejecuta `install_windows.ps1` como administrador o manualmente:

```powershell
python -m venv venv
venv\Scripts\activate
pip install llama-cpp-python pygame Pillow pyttsx3
python main.py
```

---

## 📁 Estructura del proyecto

```
IRON-CHAT-LUNA/
├── main.py                 # Interfaz gráfica (Tkinter)
├── ai_module.py            # Módulo de IA (Llama.cpp)
├── tts_module.py           # TTS multiplataforma
├── face_animation.py       # Cara animada del robot
├── ascii_art.py            # 26 dibujos ASCII de gym
├── sounds.py               # Sonidos de notificación
├── progress_tracker.py     # Seguimiento de progreso SQLite
├── requirements.txt        # Dependencias Python
├── install_windows.ps1     # Instalador para Windows
├── crear_acceso_windows.vbs # Acceso directo Windows
├── robot-icon.ico          # Icono para Windows
├── robot-icon.png          # Icono para Linux
├── robot.jpeg              # Imagen del robot
├── gymp.jpeg / gym.jpeg    # Fondos del chat
├── iniciodesesion.wav      # Sonido de inicio
├── generar_firma.py        # Generador de hash SHA256
├── verificar_firma.py      # Verificador de integridad
├── SIGNATURE.md            # Certificado de autenticidad
├── models/                 # Modelo GGUF (no incluido)
├── voices/                 # Voces Piper (no incluidas)
├── musica/                 # Tus MP3 motivacionales
└── venv/                   # Entorno virtual
```

---

## 🎮 Cómo usar

### Botones del panel derecho

| Botón | Función |
|-------|---------|
| 🗑️ LIMPIAR | Borra el chat visible |
| 🔊 TTS ON/OFF | Activa/desactiva la voz |
| 📤 EXPORTAR | Guarda el chat en el escritorio |
| ℹ️ INFO | Muestra información del proyecto |
| 🌙 MODO OSCURO | Cambia tema claro/oscuro |
| 📝 NOTAS | Abre bloc de notas de entrenamiento |
| 🏋️ RUTINA | Rutinas rápidas (Push/Pull/Piernas/Full Body) |
| 📊 PROGRESO | Añade mediciones y ve tu historial |
| 🎵 MÚSICA OFF | Reproduce MP3 de la carpeta `musica/` |
| 📂 MP3 | Abre la carpeta de música |
| ❓ AYUDA | Muestra comandos rápidos |
| 🏆 CRÉDITOS | Muestra la firma del creador |

### Comandos rápidos (desde el chat)

```
/ayuda              - Muestra ayuda
/limpiar            - Limpia el chat
/tema               - Cambia de tema (3 disponibles)
/exportar           - Exporta historial
/notas              - Abre bloc de notas
/musica             - Activa/desactiva música
/stats              - Muestra estadísticas
/dieta <tipo>       - Plan de dieta (volumen/definicion/saludable)
/recordatorio <min> '<msg>' - Programa un aviso
/ejercicio          - Guía rápida de ejercicios
```

### Atajos de teclado

```
Enter       - Enviar mensaje
Ctrl+Enter  - Enviar mensaje
Ctrl+L      - Limpiar chat
Ctrl+D      - Exportar historial
Ctrl+T      - Cambiar tema
```

### Dibujos ASCII

Escribe algo como *"dibuja una mancuerna"* o *"muestra un músculo"* y LUNA te responderá con arte ASCII.

Dibujos disponibles: `mancuerna`, `pesa`, `musculo`, `trofeo`, `fuego`, `corazon`, `hombre`, `mujer`, `flexion`, `sentadilla`, `barra`, `reloj`, `manzana`, `agua`, `pesas`, `runner`, `yoga`, `bicicleta`, `escalera`, `peso_muerto`, `gym`, `proteina`, `cuerda`, `remo`, `abdominal`, `suplemento`.

---

## 🎨 Galería ASCII

```
  __   __
 |__| |__|
  (_)_(_)
 ==o=o==
  (_)_(_)
 |__| |__|
```
*Mancuerna*

```
 .----.
 |💪|
 '----'
 .--. .--.
 |  | |  |
 '--' '--'
```
*Músculo*

```
  ______
 / GYM \
 | 💪 |
 | 🏋️ |
 \______/
```
*Gym*

```
 .------.
 |PROTEIN|
 | SHAKE |
 '------'
    ||
    ||
```
*Proteína*

```
 .--. .--.
 |🏋️| |🏋️|
 '--' '--'
  ===O
 .--.|.--.
 |🏋️||🏋️|
 '--''--'
```
*Pesas*

```
  (@)
 (@@)
(@@@)
 (@@)
  (@)
```
*Fuego*

```
 .---.
 |🏆|
 '---'
   |
  / \
```
*Trofeo*

```
 .---.
 | O |
 '---'
  / \
 /   \
```
*Sentadilla*

```
 .----.
 |\\ //|
 | \/ |
 | /\ |
 |// \\|
 '----'
```
*Abdominal*

---

## 🧠 Modelo de IA

Descargá el modelo desde Hugging Face y ponelo en `models/`:

```
https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf
```

**Configuración actual:**
- Contexto: 2048 tokens
- Temperatura: 0.7
- Top-p: 0.9
- Hilos: 4
- GPU: deshabilitada (CPU sin AVX)

---

## 🔊 Voces TTS

### Linux (Piper)
Descargá las voces desde Hugging Face y ponelas en `voices/`:

- **Femenina (recomendada):** `es_ES-sharvard-medium.onnx`
- **Masculina:** `es_ES-carlfm-x_low.onnx`

### Windows (pyttsx3)
Usa las voces SAPI5 del sistema automáticamente.

---

## 🔐 Verificar integridad

```bash
python3 verificar_firma.py
```

Comprueba que los archivos del proyecto no hayan sido alterados mediante hash SHA256.

---

## ⚡ Rendimiento

Probado en:
- **CPU**: Intel Core i3 M 380 @ 2.53 GHz (2010, sin AVX)
- **RAM**: 8 GB
- **SO**: Deepin (Debian)
- **Modelo**: Llama 3.2 3B Q4_K_M (~2 GB en RAM)

---

## 👤 Créditos

| Rol | Nombre |
|-----|--------|
| 👨‍💻 **Creador** | ⚡ JMbirner ⚡ |
| 🤖 **Asistente** | UOS AI / OpenCode |
| 📅 **Versión** | IRON CHAT v2.0 |
| 📜 **Licencia** | Educativa y personal |

---

## 📸 Capturas

*(Añadí aquí capturas de pantalla de la interfaz)*

---

## 🤝 Contribuir

1. Hacé fork del proyecto
2. Creá una rama (`git checkout -b feature/nueva-funcion`)
3. Hacé commit (`git commit -m 'Añade nueva función'`)
4. Hacé push (`git push origin feature/nueva-funcion`)
5. Abrí un Pull Request

---

## 📬 Contacto

- GitHub: [@josemanueb](https://github.com/josemanueb)
- Repo: [IRON-CHAT-LUNA](https://github.com/josemanueb/IRON-CHAT-LUNA)

---

<p align="center">
  <strong>💪 ¡Nunca saltes el día de pierna! 🦵🔥</strong>
</p>
