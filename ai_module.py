import os
import random
import signal
from ascii_art import ASCIIArt


def _sigill_handler(signum, frame):
    raise RuntimeError("SIGILL: instrucción no soportada por la CPU (probablemente AVX/AVX2 requerido)")


try:
    signal.signal(signal.SIGILL, _sigill_handler)
except Exception:
    pass


class GPT4AllAI:
    def __init__(self):
        print("Inicializando LUNA - Entrenadora personal...")

        self.model_path = self._find_model()
        self.is_offline = False

        if not self.model_path or not os.path.exists(self.model_path):
            print("⚠️ Modelo no encontrado.")
            print("⚠️ Modo OFFLINE activado — respuestas basadas en reglas")
            self.is_offline = True
            self.ascii = ASCIIArt()
            return

        print("Modelo encontrado: " + self.model_path)

        from llama_cpp import Llama

        print("Cargando modelo (esto puede tomar varios minutos)...")
        try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=0,
                verbose=False
            )
            print("Modelo cargado correctamente")
        except Exception as e:
            print(f"⚠️ Error cargando modelo: {e}")
            print("⚠️ Modo OFFLINE activado")
            self.is_offline = True
            self.ascii = ASCIIArt()
            return

        self.ascii = ASCIIArt()
        print("ASCII Art cargado - disponible!")

    def _find_model(self):
        preferred = [
            "qwen2.5-3b-instruct-q4_k_m.gguf",
            "Qwen2.5-3B-Instruct-Q4_K_M.gguf",
            "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
            "Llama-3.2-3B-Instruct-Q4_0.gguf",
            "Llama-3.2-3B-Instruct.gguf"
        ]
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        if not os.path.isdir(models_dir):
            return None
        for name in preferred:
            path = os.path.join(models_dir, name)
            if os.path.exists(path) and os.path.getsize(path) > 1000000:
                self.model_type = "qwen" if "qwen" in name.lower() else "llama"
                print(f"📦 Modelo detectado: {self.model_type.upper()} ({name})")
                return path
        for f in os.listdir(models_dir):
            if f.endswith(".gguf") and f.lower() not in ("readme.md", "readme.txt"):
                path = os.path.join(models_dir, f)
                if os.path.getsize(path) > 1000000:
                    self.model_type = "qwen" if "qwen" in f.lower() else "llama"
                    print(f"📦 Modelo detectado: {self.model_type.upper()} ({f})")
                    return path
        self.model_type = "llama"
        return None

    def _offline_response(self, user_input, history=None):
        text = user_input.lower().strip()

        if any(p in text for p in ["push", "empuje", "pecho", "hombro", "triceps", "tríceps"]):
            return ("🔥 RUTINA PUSH (Empuje):\n\n"
                    "1️⃣ Press de banca con barra — 4x8-10\n"
                    "2️⃣ Press militar con mancuernas — 4x10-12\n"
                    "3️⃣ Aperturas con mancuernas en banco plano — 3x12\n"
                    "4️⃣ Elevaciones laterales — 3x15\n"
                    "5️⃣ Fondos en paralelas — 3x10-12\n"
                    "6️⃣ Extensiones de tríceps en polea — 3x15\n\n"
                    "💪 Descansa 60-90s entre series. ¡A darle!")

        if any(p in text for p in ["pull", "traccion", "tracción", "espalda", "biceps", "bíceps"]):
            return ("🔥 RUTINA PULL (Tracción):\n\n"
                    "1️⃣ Dominadas (o jalón al pecho) — 4x8-10\n"
                    "2️⃣ Remo con barra — 4x10-12\n"
                    "3️⃣ Jalón al pecho en polea alta — 3x12\n"
                    "4️⃣ Remo con mancuerna a una mano — 3x12 por brazo\n"
                    "5️⃣ Curl con barra — 3x12\n"
                    "6️⃣ Curl martillo — 3x15\n\n"
                    "🔥 Concéntrate en la contracción. ¡Tira fuerte!")

        if any(p in text for p in ["pierna", "piernas", "leg", "quad", "cuadriceps", "gluteo", "glúteo"]):
            return ("🦵 RUTINA DE PIERNAS:\n\n"
                    "1️⃣ Sentadilla con barra — 4x8-10\n"
                    "2️⃣ Prensa de piernas — 4x12\n"
                    "3️⃣ Curl femoral acostado — 3x15\n"
                    "4️⃣ Extensiones de cuádriceps — 3x15\n"
                    "5️⃣ Elevaciones de gemelos de pie — 4x20\n"
                    "6️⃣ Zancadas con mancuernas — 3x10 por pierna\n\n"
                    "🦵 ¡Las piernas son la base de todo! Dale duro.")

        if any(p in text for p in ["full body", "cuerpo completo", "cuerpo entero"]):
            return ("💪 RUTINA FULL BODY:\n\n"
                    "1️⃣ Sentadilla con barra — 4x8-10\n"
                    "2️⃣ Press de banca — 4x8-10\n"
                    "3️⃣ Remo con barra — 4x10-12\n"
                    "4️⃣ Press militar — 3x10\n"
                    "5️⃣ Peso muerto rumano — 3x12\n"
                    "6️⃣ Curl de bíceps + extensiones tríceps — 3x15\n\n"
                    "🔥 Cuerpo completo en una sesión. ¡Intensidad total!")

        if any(p in text for p in ["cardio", "cardiovascular", "correr", "bicicleta", "elíptica", "eliptica"]):
            return ("🏃 RUTINA DE CARDIO:\n\n"
                    "1️⃣ Calentamiento: 5 min caminata rápida\n"
                    "2️⃣ Trote suave — 10 min a ritmo constante\n"
                    "3️⃣ HIIT: 30s sprint / 30s recuperación x 8 rondas\n"
                    "4️⃣ Bicicleta estática — 10 min ritmo moderado\n"
                    "5️⃣ Cuerda para saltar — 3x1 min\n"
                    "6️⃣ Enfriamiento: 5 min estiramientos\n\n"
                    "🔥 Quema grasa y mejora tu resistencia cardiovascular!")

        if any(p in text for p in ["calistenia", "calisthenics", "peso corporal", "bodyweight", "sin pesas"]):
            return ("💪 RUTINA DE CALISTENIA (sin pesas):\n\n"
                    "1️⃣ Flexiones (push-ups) — 4x15\n"
                    "2️⃣ Dominadas (o negativas) — 4x8\n"
                    "3️⃣ Sentadillas con peso corporal — 4x20\n"
                    "4️⃣ Fondos en silla — 3x12\n"
                    "5️⃣ Plancha — 3x45s\n"
                    "6️⃣ Burpees — 3x10\n\n"
                    "🔥 Controla tu propio peso corporal. ¡Sin excusas!")

        if any(p in text for p in ["dibuja", "ascii", "dibujo", "arte"]):
            for art_name in ASCIIArt.list_arts():
                if art_name in text:
                    art = ASCIIArt.get_art(art_name)
                    return f"🎨 Aquí tienes tu {art_name}:\n```\n{art}\n```"
            art_name = random.choice(ASCIIArt.list_arts())
            art = ASCIIArt.get_art(art_name)
            return f"🎨 Aquí tienes un dibujo de {art_name}:\n```\n{art}\n```"

        if any(p in text for p in ["dieta", "comer", "comida", "nutricion", "nutrición", "almuerzo", "cena", "desayuno"]):
            if any(p in text for p in ["volumen", "masa", "crecer", "ganar peso", "bulking"]):
                return ("🥗 DIETA DE VOLUMEN (Ganar masa muscular):\n\n"
                        "🍳 Desayuno: 4 huevos revueltos, avena con leche, plátano\n"
                        "🥪 Media mañana: Batido de proteína + 2 rebanadas pan integral con crema de cacahuete\n"
                        "🥗 Comida: 200g arroz, 250g pechuga pollo, aguacate\n"
                        "🥤 Post-entreno: Batido proteína + dextrosa\n"
                        "🥩 Cena: 250g carne roja magra, patata asada, espárragos\n"
                        "🌙 Antes de dormir: Caseína o requesón\n\n"
                        "🔥 Superávit calórico de ~300-500 kcal. ¡A crecer!")
            elif any(p in text for p in ["definicion", "definición", "perder", "bajar", "perder peso", "cortar"]):
                return ("🥗 DIETA DE DEFINICIÓN (Perder grasa):\n\n"
                        "🍳 Desayuno: Clara de huevo, avena ligera, té verde\n"
                        "🥪 Media mañana: Manzana + 10 almendras\n"
                        "🥗 Comida: 150g pollo, ensalada verde, quinoa\n"
                        "🥤 Post-entreno: Batido proteína con agua\n"
                        "🥩 Cena: Pescado blanco o pollo, verduras al vapor\n\n"
                        "🔥 Déficit calórico de ~300-500 kcal. Mucha proteína!")
            else:
                return ("🥗 PLAN DE ALIMENTACIÓN SALUDABLE:\n\n"
                        "🍳 Desayuno: Avena con proteína en polvo, plátano y almendras\n"
                        "🥪 Almuerzo: Pechuga de pollo, arroz integral y brócoli\n"
                        "🥗 Comida: Salmón, quinoa y espárragos\n"
                        "🥤 Merienda: Batido de proteína con fruta\n"
                        "🥩 Cena: Carne magra, batata y ensalada\n\n"
                        "💧 Bebe 2-3L de agua al día. ¡La nutrición es el 70%!")

        if any(p in text for p in ["ejercicio", "ejercicios", "ejecutar", "como se hace"]):
            exercise_db = {
                "sentadilla": "🏋️ SENTADILLA (Squat):\n• Pies al ancho de hombros\n• Barra en trampa cervical\n• Baja hasta paralela (muslo paralelo al suelo)\n• Rodillas hacia afuera, pecho arriba\n• Series: 4x8-10",
                "press banca": "🏋️ PRESS DE BANCA (Bench Press):\n• Acuéstate en banco plano\n• Barra a la altura del pecho\n• Baja controlado hasta tocar el pecho\n• Sube explosivamente\n• Series: 4x8-10",
                "peso muerto": "🏋️ PESO MUERTO (Deadlift):\n• Pies al ancho de hombros\n• Barra sobre el empeine\n• Espalda recta, cadera atrás\n• Levanta con fuerza de piernas\n• Series: 3x5-8",
                "dominada": "🏋️ DOMINADA (Pull-up):\n• Agarre prono, manos al ancho de hombros\n• Activa escápulas\n• Sube hasta que la barbilla pase la barra\n• Baja controlado\n• Series: 4x8-12",
                "flexion": "🏋️ FLEXIÓN (Push-up):\n• Cuerpo recto, manos al ancho de hombros\n• Baja el pecho hasta rozar el suelo\n• Sube explosivamente\n• Variante: inclinada, declinada, diamante\n• Series: 3x15-20",
                "curl": "🏋️ CURL DE BÍCEPS:\n• Mancuernas o barra\n• Codos pegados al cuerpo\n• Sube contrayendo el bíceps\n• Baja controlado (3s)\n• Series: 3x12-15",
            }
            for ex_name, ex_desc in exercise_db.items():
                if ex_name in text:
                    return ex_desc
            return ("📚 EJERCICIOS DISPONIBLES:\n"
                    "• Sentadilla\n• Press banca\n• Peso muerto\n"
                    "• Dominada\n• Flexión\n• Curl de bíceps\n\n"
                    "Escribe 'cómo se hace [ejercicio]' para ver la técnica.")

        if any(p in text for p in ["recordatorio", "recuerda", "recordar", "avísame"]):
            return ("⏰ FUNCIÓN RECORDATORIO:\n\n"
                    "Usa el comando /recordatorio para programar un aviso.\n"
                    "Ejemplo: /recordatorio 30 'Beber agua'\n\n"
                    "También puedes usar el temporizador del panel derecho ⏱️")

        if any(p in text for p in ["gracias", "thanks", "vale", "ok", "perfecto"]):
            return "¡De nada! 💪 Estoy aquí para ayudarte a conseguir tus metas. ¡Sigue así! 🔥"

        if any(p in text for p in ["hola", "buenos días", "buenas", "hey", "que tal", "saludos"]):
            return ("¡Hola! 👋 Soy LUNA, tu entrenadora personal. ¿En qué puedo ayudarte hoy?\n\n"
                    "Puedes pedirme:\n"
                    "🏋️ Rutinas: Push, Pull, Piernas, Full Body, Cardio, Calistenia\n"
                    "🥗 Dietas: Volumen, Definición o Saludable\n"
                    "🎨 Dibujos ASCII (ej: 'dibuja una mancuerna')\n"
                    "📊 Seguimiento de progreso\n"
                    "⏱️ Temporizador de descanso\n"
                    "📝 Ver ejercicios (ej: 'cómo se hace sentadilla')\n\n"
                    "¿Por dónde empezamos? 💪🔥")

        responses = [
            "¡Sigue así! 💪 Cada repetición cuenta. ¿Quieres que te sugiera una rutina?",
            "El esfuerzo de hoy es el resultado de mañana. 🏋️ ¿Necesitas algo específico?",
            "Recuerda: la disciplina supera a la motivación. 🔥 ¿En qué te ayudo?",
            "💪 ¡A darle! Puedo ayudarte con rutinas, nutrición o lo que necesites.",
            "El gym es tu templo. 🏛️ ¿Preparado para la siguiente serie?",
            "No hay atajos. Solo trabajo duro. 🏋️ ¿Qué ejercicios quieres hacer hoy?",
            "Vamos allá! 🔥 Puedo crearte una rutina personalizada si quieres.",
            "Duerme bien, entrena duro, come limpio. 🔁 ¡Así de simple!",
            "La motivación te hace empezar, la disciplina te hace continuar. 🔥",
        ]
        return random.choice(responses)

    def _system_prompt(self):
        sys = ("Eres LUNA, una entrenadora personal y nutricionista profesional. Hablas español con energia y motivacion.\n\n"
               "TUS CONOCIMIENTOS:\n"
               "- Creacion de rutinas de ejercicios personalizadas (pesas, cardio, calistenia)\n"
               "- Nutricion deportiva y planes de alimentacion\n"
               "- Consejos de suplementacion\n"
               "- Anatomia y biomecanica\n"
               "- Lesiones y recuperacion\n"
               "- Motivacion y disciplina\n\n"
               "INSTRUCCIONES:\n"
               "- Responde SIEMPRE en español\n"
               "- Se motivadora y usa emojis como 💪🔥🏋️🥗\n"
               "- Da respuestas detalladas y utiles\n"
               "- Si te piden una rutina, crea una completa con ejercicios, series y repeticiones\n"
               "- Si te piden dieta, da opciones de comidas especificas\n"
               "- Se profesional pero cercana\n"
               "- Si te piden un dibujo o arte ASCII, responde SOLO con el nombre del dibujo entre [ASCII:nombre], por ejemplo: [ASCII:mancuerna]\n"
               f"- Los dibujos disponibles son: {', '.join(ASCIIArt.list_arts())}\n"
               "- Recuerda lo que el usuario te ha dicho antes en la conversacion\n")
        if getattr(self, 'model_type', 'llama') == "qwen":
            return f"<|im_start|>system\n{sys}<|im_end|>\n"
        return f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{sys}<|eot_id|>\n"

    def _user_turn(self, text):
        if getattr(self, 'model_type', 'llama') == "qwen":
            return f"<|im_start|>user\n{text}<|im_end|>\n"
        return f"<|start_header_id|>user<|end_header_id|>\n\n{text}<|eot_id|>\n"

    def _assistant_turn(self, text=""):
        if getattr(self, 'model_type', 'llama') == "qwen":
            return f"<|im_start|>assistant\n{text}"
        return f"<|start_header_id|>assistant<|end_header_id|>\n\n{text}"

    def _stop_tokens(self):
        if getattr(self, 'model_type', 'llama') == "qwen":
            return ["<|im_end|>", "<|im_start|>"]
        return ["<|eot_id|>", "<|end_header_id|>"]

    def get_response(self, user_input, history=None):
        try:
            if self.is_offline:
                return self._offline_response(user_input, history)

            ascii_arts_list = ", ".join(ASCIIArt.list_arts())

            history_block = ""
            if history:
                for role, text in history:
                    if role == "user":
                        history_block += self._user_turn(text)
                    elif role == "assistant":
                        history_block += self._assistant_turn(text)

            prompt = self._system_prompt() + history_block + self._user_turn(user_input) + self._assistant_turn("")

            response = self.model(
                prompt,
                max_tokens=500,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1,
                stop=self._stop_tokens()
            )
            text = response['choices'][0]['text'].strip()

            if "[ASCII:" in text:
                import re
                match = re.search(r'\[ASCII:(\w+)\]', text)
                if match:
                    art_name = match.group(1)
                    art = ASCIIArt.get_art(art_name)
                    text = text.replace(f"[ASCII:{art_name}]", f"\n```\n{art}\n```\n")

            return text
        except Exception as e:
            print("Error al generar respuesta: " + str(e))
            return self._offline_response(user_input, history)
