import os
import sys
import re
import random
import signal
import json
from ascii_art import ASCIIArt
import knowledge

def _project_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

_PROJECT_DIR = _project_dir()
_RUTINAS_PATH = os.path.join(_PROJECT_DIR, "rutinas.json")


def _load_rutinas():
    try:
        with open(_RUTINAS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


_RUTINAS = _load_rutinas()


def _sigill_handler(signum, frame):
    raise RuntimeError("SIGILL: instrucción no soportada por la CPU (probablemente AVX/AVX2 requerido)")


try:
    signal.signal(signal.SIGILL, _sigill_handler)
except Exception:
    pass


class GPT4AllAI:
    def __init__(self):
        print("Inicializando LUNA - Entrenadora personal...")
        self._load_error = None

        self._memorias = []
        self._memorias_path = os.path.join(_PROJECT_DIR, "memorias.json")
        self._cargar_memorias()

        self.model_path = self._find_model()
        self.is_offline = False

        if not self.model_path or not os.path.exists(self.model_path):
            self._load_error = "No se encontró archivo .gguf en la carpeta models/"
            print("⚠️ " + self._load_error)
            print("⚠️ Modo OFFLINE activado — respuestas basadas en reglas")
            self.is_offline = True
            return

        print("Modelo encontrado: " + self.model_path)

        try:
            from llama_cpp import Llama
        except ImportError as e:
            self._load_error = f"llama_cpp no instalado: {e}"
            print("⚠️ " + self._load_error)
            print("⚠️ Modo OFFLINE activado — respuestas basadas en reglas")
            self.is_offline = True
            return

        print("Cargando modelo (esto puede tomar varios minutos)...")
        cfg = self._read_config()
        cpu_count = os.cpu_count() or 2
        n_threads = int(cfg.get("n_threads") or max(1, cpu_count))
        n_ctx = int(cfg.get("n_ctx") or 2048)
        n_gpu_layers = self._resolve_gpu_layers(cfg)
        self.n_ctx = n_ctx
        self.max_tokens = int(cfg.get("max_tokens") or 500)
        print(f"🔧 CPU detectada: {cpu_count} núcleos, usando {n_threads} threads")
        if n_gpu_layers:
            print(f"🎮 GPU disponible: {n_gpu_layers} capas aceleradas")
        try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_gpu_layers=n_gpu_layers,
                verbose=False
            )
            print("Modelo cargado correctamente")
        except Exception as e:
            self._load_error = str(e)
            print(f"⚠️ Error cargando modelo: {e}")
            print("⚠️ Modo OFFLINE activado")
            self.is_offline = True
            return

        print("ASCII Art cargado - disponible!")

    # --- Ajustes de carga (config.json, con defaults sensatos) ---------
    def _read_config(self):
        """Lee config.json si existe. Cualquier error => defaults."""
        try:
            path = os.path.join(_PROJECT_DIR, "config.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
        return {}

    def _resolve_gpu_layers(self, cfg):
        """Cuantas capas va a GPU.

        Antes era n_gpu_layers=0 fijo, es decir, siempre CPU aunque el usuario
        tuviera GPU con llama-cpp-python compilado con CUDA/Metal/Vulkan.

        - n_gpu_layers en config.json manda (0 = forzar CPU).
        - -1 = autodetectar todas las capas posibles.
        - llama_supports_gpu_offload() solo existe si la build trae GPU.
        """
        if "n_gpu_layers" in cfg:
            try:
                valor = int(cfg["n_gpu_layers"])
                # -1 = autodetectar todas las capas; no pasar por max(0, ...).
                if valor < 0:
                    return -1
                return valor
            except (TypeError, ValueError):
                pass
        try:
            import llama_cpp
            if getattr(llama_cpp, "llama_supports_gpu_offload", lambda: False)():
                # -1 deja que llama.cpp vuelque tantas capas como quepan.
                return -1
        except Exception:
            pass
        return 0

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
            "Qwen2.5-1.5B-Instruct.Q4_K_M.gguf": "Qwen2.5 1.5B",
            "qwen2.5-1.5b-instruct-q4_k_m.gguf": "Qwen2.5 1.5B",
            "qwen2.5-1.5b-instruct-q4_0.gguf": "Qwen2.5 1.5B",
            "TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf": "TinyLlama 1.1B",
            "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf": "TinyLlama 1.1B",
            "tinyllama-1.1b-chat-v1.0.Q4_0.gguf": "TinyLlama 1.1B",
            "Qwen2.5-3B-Instruct.Q4_K_M.gguf": "Qwen2.5 3B",
            "qwen2.5-3b-instruct-q4_k_m.gguf": "Qwen2.5 3B",
            "Qwen2.5-3B-Instruct-Q4_K_M.gguf": "Qwen2.5 3B",
            "Llama-3.2-3B-Instruct-Q4_K_M.gguf": "Llama 3.2 3B",
            "Llama-3.2-3B-Instruct-Q4_0.gguf": "Llama 3.2 3B",
            "Llama-3.2-3B-Instruct.gguf": "Llama 3.2 3B",
        }
        preferred = list(preferred_names.keys())
        models_dir = os.path.join(_PROJECT_DIR, "models")
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
        if "qwen" in name:
            return "qwen"
        if "llama-3" in name or "llama3" in name:
            return "llama3"
        return "llama"

    def _offline_response(self, user_input, history=None):
        """Respuesta sin modelo de IA.

        La base de conocimiento vive en conocimiento.json y la resuelve
        knowledge.py; aqui solo se orquesta el orden de prioridad, que es el
        mismo que tenia antes el codigo en linea:

            saludo -> agradecimiento -> rutinas (rutinas.json) -> categorias
            (conocimiento.json, con guia de ejercicios dentro) -> ascii -> generica

        Ese orden es comportamiento observable, no arbitrario: por ejemplo
        "hola, dame rutina de pecho" debe saludar, no escupir la rutina.
        """
        text = (user_input or "").lower().strip()
        if not text:
            return knowledge.respuesta_generica()

        def _ascii():
            for art_name in ASCIIArt.list_arts():
                if re.search(r'\b' + re.escape(art_name) + r'\b', text):
                    art = ASCIIArt.get_art(art_name)
                    return "🎨 Aquí tienes tu %s:\n```\n%s\n```" % (art_name, art)
            art_name = random.choice(ASCIIArt.list_arts())
            art = ASCIIArt.get_art(art_name)
            return "🎨 Aquí tienes un dibujo de %s:\n```\n%s\n```" % (art_name, art)

        # 1) Saludo y agradecimiento van primero: greeting gana a cualquier otro tema.
        for cat in ("saludo", "agradecimiento"):
            if knowledge.find_categoria_categoria(cat, user_input):
                respuesta = knowledge.get_categoria_response(cat)
                if respuesta:
                    return respuesta

        # 2) Guia tecnica de un ejercicio concreto ANTES que las rutinas.
        #    "como se hace el peso muerto" es una peticion de tecnica, aunque
        #    "peso muerto" no sea keyword de ninguna rutina.
        guia = knowledge.find_ejercicio(user_input)
        if guia and knowledge.es_peticion_ejercicio(user_input):
            return guia

        # 3) Rutinas de rutinas.json. Priorizan sobre las categorias genericas
        #    porque "piernas" o "hombros" son grupos musculares completos.
        for _key, rutina in _RUTINAS.items():
            if any(p in text for p in rutina["keywords"]):
                return rutina["response"]

        # 4) El resto de categorias.
        cat = knowledge.find_categoria(user_input)
        if cat == "ascii_art":
            return _ascii()
        if cat:
            respuesta = knowledge.get_categoria_response(cat)
            if respuesta:
                return respuesta

        # 5) Sin categoria: respuesta generica.
        return knowledge.respuesta_generica()

    def _system_prompt(self):
        memoria = self._build_memory_context()
        sys = ("Eres LUNA, una entrenadora personal y nutricionista profesional. "
               "Hablas español con energia y motivacion.\n\n"
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
               "- Si te piden un dibujo o arte ASCII, responde SOLO con el nombre del "
               "dibujo entre [ASCII:nombre], por ejemplo: [ASCII:mancuerna]\n"
               f"- Los dibujos disponibles son: {', '.join(ASCIIArt.list_arts())}\n"
               "- Recuerda lo que el usuario te ha dicho antes en la conversacion\n")
        sys += memoria

        # La base de conocimiento local tambien se inyecta aqui: sin esto, con
        # un modelo GGUF cargado LUNA perdia las rutinas y dietas que si sabe
        # cuando va en modo offline (mejora #8).
        try:
            resumen = knowledge.resumen_para_prompt(max_chars=1200)
            if resumen:
                sys += ("\nBASE DE CONOCIMIENTO LOCAL (reutiliza estos datos "
                        "textuales cuando encajen con la pregunta):\n") + resumen + "\n"
        except Exception:
            pass
        return sys

    # --- Plantilla de chat y presupuesto de contexto -------------------
    # Los GGUF de chat usan cabeceras <|im_start|>/<|im_end|> (Qwen y Llama-3
    # comparten ChatML). Antes se concatenaba "system\n...\nuser\n..." a pelo,
    # que no es un formato de chat real y degradaba la calidad del modelo.
    CHAT_TEMPLATES = {
        "chatml": "chatml",
        "llama3": "llama3",
        "plain": "plain",
    }

    def _chat_template(self):
        """Plantilla de chat segun el modelo, con override desde config.json."""
        override = None
        try:
            cfg_path = os.path.join(_PROJECT_DIR, "config.json")
            if os.path.exists(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                if isinstance(cfg, dict):
                    override = cfg.get("chat_template")
        except Exception:
            override = None
        if override in self.CHAT_TEMPLATES:
            return self.CHAT_TEMPLATES[override]
        tipo = getattr(self, "model_type", "llama")
        if tipo == "llama3":
            # Llama 3 usa cabeceras propias, no ChatML.
            return "llama3"
        # ChatML para Qwen y para los instruct GGUF genericos.
        return "chatml"

    def _stop_tokens(self):
        """Tokens de fin reales del formato de chat.

        Antes devolvia ["", ""], que en llama.cpp es un token degenerado: no
        detenia nada y la generacion se comia el max_tokens entero.
        """
        if self._chat_template() == "llama3":
            return ["<|eot_id|>", "<|end_of_text|>"]
        return ["<|im_end|>", "<|end_of_text|>"]

    @staticmethod
    def _truncate_to_budget(text, budget):
        """Recorta texto por caracteres para no desbordar el contexto.

        Aproximacion: ~3.5 caracteres por token en espanol. Mejor que dejar
        que el modelo trunque solo, porque el desborde lo produce la app.
        """
        if not text or budget <= 0:
            return ""
        if len(text) <= budget:
            return text
        return text[:budget].rsplit(" ", 1)[0]

    def _build_prompt(self, user_input, history=None):
        """Construye el prompt con la plantilla correcta y un presupuesto de
        contexto, para que historial + memoria no desborden n_ctx."""
        n_ctx = int(getattr(self, "n_ctx", 2048) or 2048)
        max_tokens = int(getattr(self, "max_tokens", 500) or 500)
        # Margen para la respuesta y para el SYSTEM prompt.
        char_budget = max(1200, (n_ctx - max_tokens - 200) * 3)

        system = self._truncate_to_budget(self._system_prompt(), char_budget // 3)

        turns = []
        if history:
            for role, text in history:
                if role in ("user", "assistant") and text:
                    turns.append((role, text))
        turns.append(("user", user_input))

        # Descartamos turnos antiguos (no el ultimo) hasta que quepa el prompt.
        while len(turns) > 1:
            total = len(system) + sum(len(t[1]) for t in turns)
            if total <= char_budget:
                break
            turns.pop(0)

        # El turno final siempre entero: es la pregunta del usuario.
        turns[-1] = (turns[-1][0], self._truncate_to_budget(turns[-1][1], char_budget // 2))
        return self._render_prompt(system, turns)

    def _render_prompt(self, system, turns):
        """Aplica la plantilla de chat con historial de N turnos."""
        tpl = self._chat_template()

        if tpl == "plain":
            usuarios = "\n\n".join(x for r, x in turns if r == "user")
            return system + "\n\nUser: " + usuarios + "\n\nAssistant:"

        if tpl == "llama3":
            out = "<|start_header_id|>system<|end_header_id|>\n\n" + system + "<|eot_id|>"
            for role, text in turns:
                if role == "user":
                    out += "<|start_header_id|>user<|end_header_id|>\n\n" + text + "<|eot_id|>"
                else:
                    out += "<|start_header_id|>assistant<|end_header_id|>\n\n" + text + "<|eot_id|>"
            return out + "<|start_header_id|>assistant<|end_header_id|>\n\n"

        # chatml (default: Qwen y Llama-3 comparten este formato)
        out = "<|im_start|>system\n" + system + "<|im_end|>\n"
        for role, text in turns:
            if role == "user":
                out += "<|im_start|>user\n" + text + "<|im_end|>\n"
            else:
                out += "<|im_start|>assistant\n" + text + "<|im_end|>\n"
        return out + "<|im_start|>assistant\n"

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
                max_tokens=self.max_tokens,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1,
                stop=self._stop_tokens()
            )
            choices = response.get('choices', [])
            if choices:
                text = choices[0].get('text', '').strip()
            else:
                text = ""
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
                max_tokens=self.max_tokens,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1,
                stop=self._stop_tokens(),
                stream=True
            ):
                choices = chunk.get('choices', [])
                if not choices:
                    continue
                token = choices[0].get('text', '')
                if not token:
                    continue
                accumulated += token
                yield accumulated

            yield self._post_process(accumulated.strip())
        except Exception as e:
            print("Error en stream_response: " + str(e))
            yield f"⚠️ Error del modelo: {e}"
