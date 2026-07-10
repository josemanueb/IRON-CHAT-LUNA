import os
import random
import signal
import json
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
            return

        self._memorias = []
        self._memorias_path = os.path.join(os.path.dirname(__file__), "memorias.json")
        self._cargar_memorias()
        print("ASCII Art cargado - disponible!")

    def _cargar_memorias(self):
        if os.path.exists(self._memorias_path):
            try:
                with open(self._memorias_path, "r", encoding="utf-8") as f:
                    self._memorias = json.load(f)
                print(f"🧠 Memorias cargadas: {len(self._memorias)} sesiones")
            except Exception:
                self._memorias = []

    def _guardar_memorias(self):
        try:
            with open(self._memorias_path, "w", encoding="utf-8") as f:
                json.dump(self._memorias[-20:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def recordar(self, resumen):
        self._memorias.append({"rol": "usuario", "resumen": resumen})
        self._guardar_memorias()

    def _build_memory_context(self):
        if not self._memorias:
            return ""
        ctx = "\nMEMORIA DE CONVERSACIONES ANTERIORES:\n"
        for m in self._memorias[-5:]:
            ctx += f"- {m['resumen']}\n"
        ctx += "\n"
        return ctx

    def _find_model(self):
        preferred_names = {
            "qwen2.5-1.5b-instruct-q4_k_m.gguf": "Qwen2.5 1.5B",
            "qwen2.5-1.5b-instruct-q4_0.gguf": "Qwen2.5 1.5B",
            "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf": "TinyLlama 1.1B",
            "tinyllama-1.1b-chat-v1.0.Q4_0.gguf": "TinyLlama 1.1B",
            "qwen2.5-3b-instruct-q4_k_m.gguf": "Qwen2.5 3B",
            "Qwen2.5-3B-Instruct-Q4_K_M.gguf": "Qwen2.5 3B",
            "Llama-3.2-3B-Instruct-Q4_K_M.gguf": "Llama 3.2 3B",
            "Llama-3.2-3B-Instruct-Q4_0.gguf": "Llama 3.2 3B",
            "Llama-3.2-3B-Instruct.gguf": "Llama 3.2 3B",
        }
        preferred = list(preferred_names.keys())
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        if not os.path.isdir(models_dir):
            return None
        for name in preferred:
            path = os.path.join(models_dir, name)
            if os.path.exists(path) and os.path.getsize(path) > 1000000:
                self.model_type = self._detect_model_type(name)
                self.model_name = preferred_names.get(name, name)
                print(f"📦 Modelo detectado: {self.model_type.upper()} ({name})")
                return path
        for f in os.listdir(models_dir):
            if f.endswith(".gguf") and f.lower() not in ("readme.md", "readme.txt"):
                path = os.path.join(models_dir, f)
                if os.path.getsize(path) > 1000000:
                    self.model_type = self._detect_model_type(f)
                    self.model_name = f
                    print(f"📦 Modelo detectado: {self.model_type.upper()} ({f})")
                    return path
        self.model_type = self._detect_model_type("")
        self.model_name = "—"
        return None

    @staticmethod
    def _detect_model_type(filename: str) -> str:
        name = filename.lower()
        if "tinyllama" in name:
            return "qwen"
        if "qwen" in name:
            return "qwen"
        return "llama"

    def _offline_response(self, user_input, history=None):
        text = user_input.lower().strip()

        # === SALUDOS ===
        if any(p in text for p in ["hola", "buenos días", "buenas", "hey", "que tal", "saludos", "buenas tardes", "buenas noches"]):
            return ("¡Hola! 👋 Soy LUNA, tu entrenadora personal. ¿En qué puedo ayudarte hoy?\n\n"
                    "Puedes pedirme:\n"
                    "🏋️ Rutinas: Push, Pull, Piernas, Full Body, Cardio, Calistenia\n"
                    "🥗 Dietas: Volumen, Definición o Saludable\n"
                    "🎨 Dibujos ASCII (ej: 'dibuja una mancuerna')\n"
                    "📊 Seguimiento de progreso\n"
                    "⏱️ Temporizador de descanso\n"
                    "📝 Ver ejercicios (ej: 'cómo se hace sentadilla')\n"
                    "💧 Consejos de hidratación y descanso\n\n"
                    "¿Por dónde empezamos? 💪🔥")

        # === AGRADECIMIENTOS ===
        if any(p in text for p in ["gracias", "thanks", "vale", "ok", "perfecto", "de acuerdo", "entendido"]):
            return random.choice([
                "¡De nada! 💪 Estoy aquí para ayudarte a conseguir tus metas. ¡Sigue así! 🔥",
                "¡A mandar! Cuando quieras otra cosa, aquí estoy. 💪",
                "Para eso estoy. ¿Necesitas algo más? 🔥",
                "¡Dale duro! Cualquier cosa, me dices. 💪🔥",
            ])

        # === RUTINA PUSH ===
        if any(p in text for p in ["push", "empuje", "pecho", "hombro", "triceps", "tríceps"]):
            return ("🔥 RUTINA PUSH (Empuje):\n\n"
                    "1️⃣ Press de banca con barra — 4x8-10\n"
                    "2️⃣ Press militar con mancuernas — 4x10-12\n"
                    "3️⃣ Aperturas con mancuernas en banco plano — 3x12\n"
                    "4️⃣ Elevaciones laterales — 3x15\n"
                    "5️⃣ Fondos en paralelas — 3x10-12\n"
                    "6️⃣ Extensiones de tríceps en polea — 3x15\n\n"
                    "💪 Descansa 60-90s entre series. ¡A darle!")

        # === RUTINA PULL ===
        if any(p in text for p in ["pull", "traccion", "tracción", "espalda", "biceps", "bíceps"]):
            return ("🔥 RUTINA PULL (Tracción):\n\n"
                    "1️⃣ Dominadas (o jalón al pecho) — 4x8-10\n"
                    "2️⃣ Remo con barra — 4x10-12\n"
                    "3️⃣ Jalón al pecho en polea alta — 3x12\n"
                    "4️⃣ Remo con mancuerna a una mano — 3x12 por brazo\n"
                    "5️⃣ Curl con barra — 3x12\n"
                    "6️⃣ Curl martillo — 3x15\n\n"
                    "🔥 Concéntrate en la contracción. ¡Tira fuerte!")

        # === RUTINA PIERNAS ===
        if any(p in text for p in ["pierna", "piernas", "leg", "quad", "cuadriceps", "gluteo", "glúteo", "femoral", "isquiotibial"]):
            return ("🦵 RUTINA DE PIERNAS:\n\n"
                    "1️⃣ Sentadilla con barra — 4x8-10\n"
                    "2️⃣ Prensa de piernas — 4x12\n"
                    "3️⃣ Curl femoral acostado — 3x15\n"
                    "4️⃣ Extensiones de cuádriceps — 3x15\n"
                    "5️⃣ Elevaciones de gemelos de pie — 4x20\n"
                    "6️⃣ Zancadas con mancuernas — 3x10 por pierna\n\n"
                    "🦵 ¡Las piernas son la base de todo! Dale duro.")

        # === FULL BODY ===
        if any(p in text for p in ["full body", "cuerpo completo", "cuerpo entero", "dia completo", "día completo"]):
            return ("💪 RUTINA FULL BODY:\n\n"
                    "1️⃣ Sentadilla con barra — 4x8-10\n"
                    "2️⃣ Press de banca — 4x8-10\n"
                    "3️⃣ Remo con barra — 4x10-12\n"
                    "4️⃣ Press militar — 3x10\n"
                    "5️⃣ Peso muerto rumano — 3x12\n"
                    "6️⃣ Curl de bíceps + extensiones tríceps — 3x15\n\n"
                    "🔥 Cuerpo completo en una sesión. ¡Intensidad total!")

        # === CARDIO ===
        if any(p in text for p in ["cardio", "cardiovascular", "correr", "bicicleta", "elíptica", "eliptica", "trote"]):
            return ("🏃 RUTINA DE CARDIO:\n\n"
                    "1️⃣ Calentamiento: 5 min caminata rápida\n"
                    "2️⃣ Trote suave — 10 min a ritmo constante\n"
                    "3️⃣ HIIT: 30s sprint / 30s recuperación x 8 rondas\n"
                    "4️⃣ Bicicleta estática — 10 min ritmo moderado\n"
                    "5️⃣ Cuerda para saltar — 3x1 min\n"
                    "6️⃣ Enfriamiento: 5 min estiramientos\n\n"
                    "🔥 Quema grasa y mejora tu resistencia cardiovascular!")

        # === CALISTENIA ===
        if any(p in text for p in ["calistenia", "calisthenics", "peso corporal", "bodyweight", "sin pesas", "casa"]):
            return ("💪 RUTINA DE CALISTENIA (sin pesas):\n\n"
                    "1️⃣ Flexiones (push-ups) — 4x15\n"
                    "2️⃣ Dominadas (o negativas) — 4x8\n"
                    "3️⃣ Sentadillas con peso corporal — 4x20\n"
                    "4️⃣ Fondos en silla — 3x12\n"
                    "5️⃣ Plancha — 3x45s\n"
                    "6️⃣ Burpees — 3x10\n\n"
                    "🔥 Controla tu propio peso corporal. ¡Sin excusas!")

        # === RUTINA HOMBROS ===
        if any(p in text for p in ["hombro", "hombros", "deltoides", "press militar", "elevaciones"]):
            return ("🔥 RUTINA DE HOMBROS:\n\n"
                    "1️⃣ Press militar con barra — 4x8-10\n"
                    "2️⃣ Elevaciones laterales con mancuerna — 4x12-15\n"
                    "3️⃣ Elevaciones frontales — 3x12\n"
                    "4️⃣ Pájaros (vuelos invertidos) — 3x15\n"
                    "5️⃣ Encogimientos de hombros — 4x12\n"
                    "6️⃣ Face pull en polea — 3x15\n\n"
                    "🔥 Hombros redondos y fuertes. ¡A darle!")

        # === RUTINA BRAZOS ===
        if any(p in text for p in ["brazo", "brazos", "bíceps", "biceps", "tríceps", "triceps", "curl", "antebrazo"]):
            return ("💪 RUTINA DE BRAZOS:\n\n"
                    "🔥 BÍCEPS:\n"
                    "1️⃣ Curl con barra — 4x10-12\n"
                    "2️⃣ Curl martillo — 3x12-15\n"
                    "3️⃣ Curl concentrado — 3x12\n\n"
                    "🔥 TRÍCEPS:\n"
                    "4️⃣ Extensiones en polea — 4x12\n"
                    "5️⃣ Fondos en banco — 3x12\n"
                    "6️⃣ Patada de tríceps — 3x15\n\n"
                    "🔥 Brazos marcados. ¡A explotarlos!")

        # === RUTINA ABDOMINALES ===
        if any(p in text for p in ["abdominal", "abdominales", "core", "abs", "six pack", "abdomen", "vientre"]):
            return ("🔥 RUTINA ABDOMINALES:\n\n"
                    "1️⃣ Plancha frontal — 4x45s\n"
                    "2️⃣ Crunch clásico — 3x20\n"
                    "3️⃣ Elevación de piernas — 3x15\n"
                    "4️⃣ Russian twists — 3x20 (10 cada lado)\n"
                    "5️⃣ Plancha lateral — 3x30s cada lado\n"
                    "6️⃣ Bicicleta (crunches) — 3x20\n\n"
                    "🔥 El core es tu centro de poder. ¡Dale duro!")

        # === GLÚTEOS ===
        if any(p in text for p in ["gluteo", "glúteo", "gluteos", "glúteos", "culo", "cadera", "hip thrust"]):
            return ("🍑 RUTINA DE GLÚTEOS:\n\n"
                    "1️⃣ Hip thrust con barra — 4x10-12\n"
                    "2️⃣ Sentadilla búlgara — 3x10 por pierna\n"
                    "3️⃣ Patada de glúteo en polea — 3x15 cada pierna\n"
                    "4️⃣ Peso muerto rumano — 4x12\n"
                    "5️⃣ Elevación de cadera a una pierna — 3x12\n"
                    "6️⃣ Zancada lateral — 3x10 por pierna\n\n"
                    "🍑 ¡Glúteos fuertes, espalda sana!")

        # === TIPS / CONSEJOS ===
        if any(p in text for p in ["consejo", "tip", "recomendación", "recomendacion", "sugerencia", "ayuda"]):
            return ("💡 CONSEJOS DE LUNA:\n\n"
                    "🏋️ Entrenamiento:\n"
                    "• Siempre calienta 5-10 min antes de entrenar\n"
                    "• Progresa el peso gradualmente (sobrecarga progresiva)\n"
                    "• Descansa 48h entre grupos musculares grandes\n"
                    "• La técnica es más importante que el peso\n\n"
                    "🥗 Nutrición:\n"
                    "• 2g de proteína por kg de peso corporal\n"
                    "• Bebe 2-3L de agua al día\n"
                    "• No entrenes en ayunas\n\n"
                    "😴 Descanso:\n"
                    "• Duerme 7-9 horas\n"
                    "• El músculo crece cuando descansas, no cuando entrenas\n\n"
                    "🔥 La disciplina supera a la motivación. ¡Sigue así!")

        # === CALENTAMIENTO ===
        if any(p in text for p in ["calentar", "calentamiento", "warm up", "warmup", "pre calentamiento"]):
            return ("🔥 CALENTAMIENTO GENERAL (5-10 min):\n\n"
                    "1️⃣ Rotación de cuello — 30s\n"
                    "2️⃣ Círculos de hombros — 30s\n"
                    "3️⃣ Rotación de brazos — 30s\n"
                    "4️⃣ Torsión de tronco — 30s\n"
                    "5️⃣ Rotación de cadera — 30s\n"
                    "6️⃣ Sentadillas con peso corporal — 15 reps\n"
                    "7️⃣ Zancadas dinámicas — 10 por pierna\n"
                    "8️⃣ Saltos de tijera — 30s\n"
                    "9️⃣ Trote suave en el sitio — 1 min\n\n"
                    "🔥 ¡Prepara el cuerpo para la batalla!")

        # === ESTIRAMIENTOS ===
        if any(p in text for p in ["estirar", "estiramiento", "stretch", "flexibilidad", "elasticidad"]):
            return ("🧘 ESTIRAMIENTOS POST-ENTRENO:\n\n"
                    "🔥 Parte superior:\n"
                    "• Estiramiento de pecho en marco de puerta — 30s\n"
                    "• Estiramiento de tríceps — 30s cada brazo\n"
                    "• Estiramiento de hombro cruzado — 30s\n\n"
                    "🔥 Parte inferior:\n"
                    "• Estiramiento de cuádriceps de pie — 30s cada pierna\n"
                    "• Estiramiento de isquiotibiales — 30s cada pierna\n"
                    "• Estiramiento de gemelos — 30s cada pierna\n"
                    "• Estiramiento de glúteos — 30s cada lado\n\n"
                    "🧘 Respira profundamente mientras estiras. ¡No rebotes!")

        # === DESCANSO / RECUPERACIÓN ===
        if any(p in text for p in ["descanso", "recuperacion", "recuperación", "recovery", "descansar"]):
            return ("😴 RECUPERACIÓN Y DESCANSO:\n\n"
                    "💤 Sueño:\n"
                    "• 7-9 horas de sueño de calidad\n"
                    "• Sin pantallas 30 min antes de dormir\n"
                    "• Habitación oscura y fresca\n\n"
                    "🛁 Recuperación activa:\n"
                    "• Caminata ligera — 20-30 min\n"
                    "• Estiramientos suaves\n"
                    "• Rodillo de espuma (foam roller)\n\n"
                    "🥗 Nutrición post-entreno:\n"
                    "• Proteína + carbohidratos en los 30 min posteriores\n"
                    "• Batido de proteína con plátano\n\n"
                    "🔥 Recuerda: el músculo crece cuando descansas.")

        # === HIDRATACIÓN ===
        if any(p in text for p in ["agua", "hidratacion", "hidratación", "beber", "hidratarse"]):
            return ("💧 HIDRATACIÓN:\n\n"
                    "• Bebe 2-3 litros de agua al día\n"
                    "• Durante el entrenamiento: 200ml cada 15-20 min\n"
                    "• Si sudas mucho, añade electrolitos\n"
                    "• El agua con gas NO deshidrata (mito)\n"
                    "• Orina clara = bien hidratado\n\n"
                    "🔥 La hidratación es el 70% del rendimiento.")

        # === SUPLEMENTOS ===
        if any(p in text for p in ["suplemento", "suplementos", "proteina en polvo", "whey", "creatina", "bcaa", "pre entreno"]):
            return ("💊 SUPLEMENTOS RECOMENDADOS:\n\n"
                    "🥛 Proteína Whey:\n"
                    "• 1-2 dosis al día (post-entreno y/o desayuno)\n"
                    "• Ayuda a alcanzar los requerimientos de proteína\n\n"
                    "💪 Creatina Monohidrato:\n"
                    "• 5g al día (todos los días, sin descanso)\n"
                    "• Mejora fuerza y rendimiento\n"
                    "• El suplemento más estudiado y seguro\n\n"
                    "☕ Cafeína / Pre-entreno:\n"
                    "• 30-60 min antes de entrenar\n"
                    "• No usar después de las 6pm\n\n"
                    "⚠️ Los suplementos son COMPLEMENTOS, no reemplazos.\n"
                    "🔥 La base siempre será: buena alimentación + entrenamiento.")

        # === LESIONES ===
        if any(p in text for p in ["lesion", "lesión", "dolor", "molestia", "lastimado", "dañado"]):
            return ("⚠️ CONSEJOS SOBRE LESIONES:\n\n"
                    "🔥 Inmediato:\n"
                    "• Para el ejercicio que causa dolor\n"
                    "• Aplica hielo (15 min cada 2h) si hay inflamación\n"
                    "• No entrenes la zona lesionada\n\n"
                    "🏥 Cuándo ir al médico:\n"
                    "• Dolor intenso o punzante\n"
                    "• Hinchazón excesiva\n"
                    "• No puedes apoyar peso\n"
                    "• El dolor no mejora tras 3-4 días\n\n"
                    "🔄 Prevención:\n"
                    "• Calienta siempre\n"
                    "• No aumentes el peso más del 10% semanal\n"
                    "• Escucha a tu cuerpo\n\n"
                    "⚠️ Esto es solo orientativo. Consulta siempre a un profesional.")

        # === DIETA VOLUMEN ===
        if any(p in text for p in ["dieta", "comer", "comida", "nutricion", "nutrición", "almuerzo", "cena", "desayuno"]):
            if any(p in text for p in ["volumen", "masa", "crecer", "ganar peso", "bulking", "aumentar"]):
                return ("🥗 DIETA DE VOLUMEN (Ganar masa muscular):\n\n"
                        "🍳 Desayuno: 4 huevos revueltos, avena con leche, plátano\n"
                        "🥪 Media mañana: Batido de proteína + 2 rebanadas pan integral con crema de cacahuete\n"
                        "🥗 Comida: 200g arroz, 250g pechuga pollo, aguacate\n"
                        "🥤 Post-entreno: Batido proteína + dextrosa\n"
                        "🥩 Cena: 250g carne roja magra, patata asada, espárragos\n"
                        "🌙 Antes de dormir: Caseína o requesón\n\n"
                        "🔥 Superávit calórico de ~300-500 kcal. ¡A crecer!")
            elif any(p in text for p in ["definicion", "definición", "perder", "bajar", "perder peso", "cortar", "definir"]):
                return ("🥗 DIETA DE DEFINICIÓN (Perder grasa):\n\n"
                        "🍳 Desayuno: Clara de huevo, avena ligera, té verde\n"
                        "🥪 Media mañana: Manzana + 10 almendras\n"
                        "🥗 Comida: 150g pollo, ensalada verde, quinoa\n"
                        "🥤 Post-entreno: Batido proteína con agua\n"
                        "🥩 Cena: Pescado blanco o pollo, verduras al vapor\n\n"
                        "🔥 Déficit calórico de ~300-500 kcal. Mucha proteína!")
            elif any(p in text for p in ["vegano", "vegana", "vegetariano", "vegetariana", "plant based"]):
                return ("🥗 DIETA VEGANA / VEGETARIANA:\n\n"
                        "🍳 Desayuno: Batido de proteína vegetal, avena, fruta\n"
                        "🥪 Almuerzo: Tofu salteado, quinoa, verduras\n"
                        "🥗 Comida: Lentejas, arroz integral, aguacate\n"
                        "🥤 Post-entreno: Bebida de soja + proteína vegetal\n"
                        "🥩 Cena: Seitán o garbanzos, batata, brócoli\n\n"
                        "🔥 Asegúrate de cubrir: B12, hierro, zinc y proteína completa.")
            else:
                return ("🥗 PLAN DE ALIMENTACIÓN SALUDABLE:\n\n"
                        "🍳 Desayuno: Avena con proteína en polvo, plátano y almendras\n"
                        "🥪 Almuerzo: Pechuga de pollo, arroz integral y brócoli\n"
                        "🥗 Comida: Salmón, quinoa y espárragos\n"
                        "🥤 Merienda: Batido de proteína con fruta\n"
                        "🥩 Cena: Carne magra, batata y ensalada\n\n"
                        "💧 Bebe 2-3L de agua al día. ¡La nutrición es el 70%!")

        # === EJERCICIOS (guía técnica) ===
        if any(p in text for p in ["ejercicio", "ejercicios", "como se hace", "técnica", "tecnica", "como hacer"]):
            exercise_db = {
                "sentadilla": "🏋️ SENTADILLA (Squat):\n• Pies al ancho de hombros\n• Barra en trampa cervical\n• Baja hasta paralela (muslo paralelo al suelo)\n• Rodillas hacia afuera, pecho arriba\n• Series: 4x8-10",
                "press banca": "🏋️ PRESS DE BANCA (Bench Press):\n• Acuéstate en banco plano\n• Barra a la altura del pecho\n• Baja controlado hasta tocar el pecho\n• Sube explosivamente\n• Series: 4x8-10",
                "peso muerto": "🏋️ PESO MUERTO (Deadlift):\n• Pies al ancho de hombros\n• Barra sobre el empeine\n• Espalda recta, cadera atrás\n• Levanta con fuerza de piernas\n• Series: 3x5-8",
                "dominada": "🏋️ DOMINADA (Pull-up):\n• Agarre prono, manos al ancho de hombros\n• Activa escápulas\n• Sube hasta que la barbilla pase la barra\n• Baja controlado\n• Series: 4x8-12",
                "flexion": "🏋️ FLEXIÓN (Push-up):\n• Cuerpo recto, manos al ancho de hombros\n• Baja el pecho hasta rozar el suelo\n• Sube explosivamente\n• Variante: inclinada, declinada, diamante\n• Series: 3x15-20",
                "curl": "🏋️ CURL DE BÍCEPS:\n• Mancuernas o barra\n• Codos pegados al cuerpo\n• Sube contrayendo el bíceps\n• Baja controlado (3s)\n• Series: 3x12-15",
                "hip thrust": "🍑 HIP THRUST:\n• Barra sobre la cadera\n• Espalda apoyada en un banco\n• Sube la cadera contrayendo glúteos\n• Aguarda 1s arriba\n• Series: 4x10-12",
                "press militar": "🏋️ PRESS MILITAR:\n• Barra al frente, a la altura de los hombros\n• Empuja hacia arriba sin arquear la espalda\n• Baja controlado\n• Series: 4x8-10",
                "remo": "🏋️ REMO CON BARRA:\n• Inclina el torso a 45°\n• Barra al pecho contrayendo la espalda\n• Codos pegados al cuerpo\n• Series: 4x10-12",
                "fondos": "🏋️ FONDOS EN PARALELAS:\n• Cuerpo recto, mira al frente\n• Baja hasta que los hombros estén a la altura de los codos\n• Sube explosivamente\n• Series: 3x10-12",
            }
            for ex_name, ex_desc in exercise_db.items():
                if ex_name in text:
                    return ex_desc
            return ("📚 EJERCICIOS DISPONIBLES:\n"
                    "• Sentadilla\n• Press banca\n• Peso muerto\n"
                    "• Dominada\n• Flexión\n• Curl de bíceps\n"
                    "• Hip thrust\n• Press militar\n• Remo\n• Fondos\n\n"
                    "Escribe 'cómo se hace [ejercicio]' para ver la técnica.")

        # === MOTIVACIÓN ===
        if any(p in text for p in ["motivacion", "motivación", "ánimo", "animo", "no puedo", "difícil", "duro", "cuesta"]):
            return random.choice([
                "🔥 Escucha: el camino no es fácil, pero TÚ eres más fuerte. Un día a la vez. ¡Tú puedes! 💪",
                "💪 La incomodidad es temporal, pero el orgullo de haberlo hecho es para siempre. ¡Dale!",
                "🔥 El único fracaso es rendirse. Si sigues adelante, ya estás ganando. ¡Vamos!",
                "🏋️ Cada gota de sudor es un paso más cerca de tu meta. No pares. ¡Tú vales!",
                "💪 El dolor que sientes hoy es la fuerza que tendrás mañana. ¡Sigue así!",
                "🔥 No se trata de ser el mejor, sino de ser mejor que ayer. Y eso ya lo estás logrando.",
                "🌟 Cree en ti. Ya has superado todo lo que la vida te ha puesto. Esto no será diferente.",
            ])

        # === RUTINA SEMANAL ===
        if any(p in text for p in ["rutina semanal", "semana", "plan semanal", "organización", "organizacion", "planificar"]):
            return ("📅 RUTINA SEMANAL RECOMENDADA:\n\n"
                    "LUNES:  🏋️ Push (Pecho, Hombro, Tríceps)\n"
                    "MARTES: 🦵 Piernas (Cuádriceps, Glúteos)\n"
                    "MIÉRCOLES: 🏃 Cardio + Abdominales\n"
                    "JUEVES:  🔥 Pull (Espalda, Bíceps)\n"
                    "VIERNES: 🍑 Glúteos + Hombros\n"
                    "SÁBADO:  💪 Full Body o Descanso\n"
                    "DOMINGO: 😴 Descanso total\n\n"
                    "🔥 Ajusta según tu nivel y disponibilidad. ¡Constancia!")

        # === PROGRESIÓN / SOBRECARGA ===
        if any(p in text for p in ["progresion", "progresión", "progresar", "mejorar", "avanzar", "sobrecarga"]):
            return ("📈 PRINCIPIOS DE PROGRESIÓN:\n\n"
                    "🔥 Sobrecarga progresiva:\n"
                    "• Aumenta el peso ~2.5-5kg cada semana\n"
                    "• O aumenta repeticiones (ej: 8→10→12)\n"
                    "• O reduce descanso entre series\n\n"
                    "📊 Mide tu progreso:\n"
                    "• Lleva un registro de pesos y repeticiones\n"
                    "• Toma fotos cada 2-4 semanas\n"
                    "• Mide perímetros corporales\n\n"
                    "⚠️ REGLA DEL 10%:\n"
                    "• No aumentes peso/semana más del 10%\n"
                    "• La técnica siempre primero\n\n"
                    "🔥 Pequeñas mejoras cada día = grandes resultados.")

        # === COMANDOS / FUNCIONES DE LA APP ===
        if any(p in text for p in ["comando", "comandos", "funciones", "que puedes hacer", "ayuda", "/ayuda", "/help"]):
            return ("❓ COMANDOS DISPONIBLES:\n\n"
                    "  /ayuda       - Muestra esta ayuda\n"
                    "  /limpiar     - Limpia el chat\n"
                    "  /tema        - Cambia el tema visual\n"
                    "  /exportar    - Exporta el historial\n"
                    "  /musica      - Abrir carpeta de música\n"
                    "  /notas       - Abrir bloc de notas\n"
                    "  /progreso    - Registrar medidas\n"
                    "  /recordatorio - Programa un aviso\n\n"
                    "También puedes pedirme:\n"
                    "🏋️ Rutinas de entrenamiento\n"
                    "🥗 Planes de alimentación\n"
                    "🎨 Dibujos ASCII\n"
                    "💪 Consejos y motivación")

        # === RECORDATORIO ===
        if any(p in text for p in ["recordatorio", "recuerda", "recordar", "avísame", "alarma"]):
            return ("⏰ FUNCIÓN RECORDATORIO:\n\n"
                    "Usa el comando /recordatorio para programar un aviso.\n"
                    "Ejemplo: /recordatorio 30 'Beber agua'\n"
                    "(30 = minutos, 'Beber agua' = el mensaje)\n\n"
                    "También puedes usar el temporizador del panel derecho ⏱️")

        # === MÚSICA ===
        if any(p in text for p in ["musica", "música", "cancion", "canción", "playlist", "motivacional"]):
            return ("🎵 MÚSICA PARA ENTRENAR:\n\n"
                    "🔥 Recomendaciones:\n"
                    "• Pon música en la carpeta 'musica/' del proyecto\n"
                    "• Usa los controles de volumen en el panel derecho\n"
                    "• El volumen de música y TTS son independientes\n\n"
                    "🎧 Canciones motivacionales:\n"
                    "• Eye of the Tiger - Survivor\n"
                    "• Stronger - Kanye West\n"
                    "• Till I Collapse - Eminem\n"
                    "• Lose Yourself - Eminem\n"
                    "• We Will Rock You - Queen\n\n"
                    "🔥 ¡Música alta, mente fuerte!")

        # === FRASE/DICHOS ===
        if any(p in text for p in ["frase", "dicho", "cita", "filosofía", "reflexion", "reflexión"]):
            return random.choice([
                "💪 \"El dolor es temporal, la gloria es para siempre.\"",
                "🔥 \"No cuentes los días, haz que los días cuenten.\"",
                "🏋️ \"El único que puede decir que no puedes eres tú.\"",
                "🌟 \"Los sueños no funcionan a menos que tú lo hagas.\"",
                "💪 \"La disciplina es hacer lo que hay que hacer, aunque no tengas ganas.\"",
                "🔥 \"Si quieres algo que nunca tuviste, haz algo que nunca hiciste.\"",
                "🏆 \"El éxito no es definitivo, el fracaso no es fatal: es el coraje de continuar lo que cuenta.\"",
            ])

        # === SALIR/DESPEDIDA ===
        if any(p in text for p in ["adiós", "adios", "chao", "nos vemos", "hasta luego", "bye", "nos vemos"]):
            return random.choice([
                "¡Hasta luego! 💪 Sigue entrenando duro. ¡Vuelve cuando quieras! 🔥",
                "Nos vemos pronto. Recuerda: la constancia es la clave. ¡A darle! 💪",
                "¡Cuídate mucho! Si necesitas algo, aquí estoy. 💪🔥",
            ])

        # === MODO OFFLINE ===
        if any(p in text for p in ["offline", "sin conexion", "sin conexión", "modo offline", "sin modelo"]):
            return ("📡 MODO OFFLINE ACTIVO:\n\n"
                    "Actualmente estoy funcionando sin modelo de IA. Usando mi base de conocimiento local.\n\n"
                    "Puedo ayudarte con:\n"
                    "✅ Rutinas de entrenamiento\n"
                    "✅ Planes de alimentación\n"
                    "✅ Consejos y motivación\n"
                    "✅ Guía de ejercicios\n"
                    "✅ Dibujos ASCII\n"
                    "✅ Temporizador y recordatorios\n\n"
                    "Si quieres respuestas más avanzadas, descarga un modelo GGUF en la carpeta 'models/'.\n\n"
                    "💪 Pero mientras tanto, ¡aquí estoy para ti!")

        # === ASCII ART ===
        if any(p in text for p in ["dibuja", "ascii", "dibujo", "arte", "pinta"]):
            for art_name in ASCIIArt.list_arts():
                if art_name in text:
                    art = ASCIIArt.get_art(art_name)
                    return f"🎨 Aquí tienes tu {art_name}:\n```\n{art}\n```"
            art_name = random.choice(ASCIIArt.list_arts())
            art = ASCIIArt.get_art(art_name)
            return f"🎨 Aquí tienes un dibujo de {art_name}:\n```\n{art}\n```"

        # === RESPUESTA POR DEFECTO ===
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
            "💪 Escucha a tu cuerpo, pero no le des siempre la razón. ¿Necesitas algo?",
            "🔥 Cada repetición te acerca a tu mejor versión. ¿En qué te ayudo hoy?",
            "🏋️ El hierro no miente. ¿Preparado para la siguiente serie?",
        ]
        return random.choice(responses)

    def _system_prompt(self):
        memoria = self._build_memory_context()
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
               "- Recuerda lo que el usuario te ha dicho antes en la conversacion\n") + memoria
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

    def _build_prompt(self, user_input, history=None):
        history_block = ""
        if history:
            for role, text in history:
                if role == "user":
                    history_block += self._user_turn(text)
                elif role == "assistant":
                    history_block += self._assistant_turn(text)
        return self._system_prompt() + history_block + self._user_turn(user_input) + self._assistant_turn("")

    def _post_process(self, text):
        if "[ASCII:" in text:
            import re
            match = re.search(r'\[ASCII:(\w+)\]', text)
            if match:
                art_name = match.group(1)
                art = ASCIIArt.get_art(art_name)
                text = text.replace(f"[ASCII:{art_name}]", f"\n```\n{art}\n```\n")
        return text

    def get_response(self, user_input, history=None):
        try:
            if self.is_offline:
                return self._offline_response(user_input, history)

            prompt = self._build_prompt(user_input, history)
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
            return self._post_process(text)
        except Exception as e:
            print("Error al generar respuesta: " + str(e))
            return f"⚠️ Error del modelo: {e}"

    def stream_response(self, user_input, history=None):
        try:
            if self.is_offline:
                yield self._offline_response(user_input, history)
                return

            prompt = self._build_prompt(user_input, history)
            accumulated = ""
            for chunk in self.model(
                prompt,
                max_tokens=500,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1,
                stop=self._stop_tokens(),
                stream=True
            ):
                token = chunk['choices'][0]['text']
                if not token:
                    continue
                accumulated += token
                yield accumulated

            yield self._post_process(accumulated.strip())
        except Exception as e:
            print("Error en stream_response: " + str(e))
            yield f"⚠️ Error del modelo: {e}"
