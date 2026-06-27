import os
from ascii_art import ASCIIArt

class GPT4AllAI:
    def __init__(self):
        print("Inicializando LUNA - Entrenadora personal...")

        self.model_name = "Llama-3.2-3B-Instruct-Q4_0.gguf"
        self.model_path = os.path.join(os.path.dirname(__file__), "models", self.model_name)

        if not os.path.exists(self.model_path):
            print("ERROR: Modelo no encontrado en: " + self.model_path)
            raise FileNotFoundError("No se encuentra el modelo en: " + self.model_path)

        print("Modelo encontrado: " + self.model_path)

        from llama_cpp import Llama
        print("Cargando modelo (esto puede tomar varios minutos)...")
        self.model = Llama(
            model_path=self.model_path,
            n_ctx=1024,
            n_threads=4,
            n_gpu_layers=0,
            verbose=False,
            chat_format="llama-3",
            use_mmap=True,
            use_mlock=False
        )
        print("Modelo cargado correctamente")

        self.ascii = ASCIIArt()
        print("ASCII Art cargado - disponible!")

    def get_response(self, user_input, history=None):
        try:
            ascii_arts_list = ", ".join(ASCIIArt.list_arts())

            system_prompt = f"""Eres LUNA, una entrenadora personal y nutricionista profesional. Hablas español con energia y motivacion.

TUS CONOCIMIENTOS:
- Creacion de rutinas de ejercicios personalizadas (pesas, cardio, calistenia)
- Nutricion deportiva y planes de alimentacion
- Consejos de suplementacion
- Anatomia y biomecanica
- Lesiones y recuperacion
- Motivacion y disciplina

INSTRUCCIONES:
- Responde SIEMPRE en español
- Se motivadora y usa emojis como 💪🔥🏋️🥗
- Da respuestas detalladas y utiles
- Si te piden una rutina, crea una completa con ejercicios, series y repeticiones
- Si te piden dieta, da opciones de comidas especificas
- Se profesional pero cercana
- Si te piden un dibujo o arte ASCII, responde SOLO con el nombre del dibujo entre [ASCII:nombre], por ejemplo: [ASCII:mancuerna]
- Los dibujos disponibles son: {ascii_arts_list}
- Recuerda lo que el usuario te ha dicho antes en la conversacion"""

            messages = [{"role": "system", "content": system_prompt}]

            if history:
                for role, text in history:
                    if role == "user":
                        messages.append({"role": "user", "content": text})
                    elif role == "assistant":
                        messages.append({"role": "assistant", "content": text})

            messages.append({"role": "user", "content": user_input})

            response = self.model.create_chat_completion(
                messages=messages,
                max_tokens=256,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1,
                stop=["<|eot_id|>"]
            )
            text = response['choices'][0]['message']['content'].strip()

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
            return "Lo siento, hubo un error al procesar tu mensaje. Intenta de nuevo."
