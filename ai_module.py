import os
import re
from ascii_art import ASCIIArt

class GPT4AllAI:
    def __init__(self):
        print("Inicializando LUNA - Entrenadora personal...")
        from llama_cpp import Llama

        self.model_name = "Llama-3.2-3B-Instruct-Q4_0.gguf"
        self.model_path = os.path.join(os.path.dirname(__file__), "models", self.model_name)

        if not os.path.exists(self.model_path):
            print("ERROR: Modelo no encontrado en: " + self.model_path)
            raise FileNotFoundError("No se encuentra el modelo en: " + self.model_path)

        print("Modelo encontrado: " + self.model_path)

        print("Cargando modelo (esto puede tomar varios minutos)...")
        self.model = Llama(
            model_path=self.model_path,
            n_ctx=2048,
            n_threads=4,
            n_gpu_layers=0,
            verbose=False,
            chat_format="llama-3",
            use_mmap=True,
            use_mlock=False
        )
        print("Modelo cargado correctamente")

    def get_response(self, user_input, history=None):
        try:
            ascii_arts_list = ", ".join(ASCIIArt.list_arts())

            system_prompt = f"""Eres LUNA, una entrenadora personal certificada y nutricionista deportiva. Hablas español con un tono profesional, motivador y basado en ciencia.

PERFIL PROFESIONAL:
- Entrenadora personal con especializacion en fuerza, hipertrofia y calistenia
- Nutricionista deportiva especializada en composicion corporal
- Experta en biomecanica y prevencion de lesiones
- Coach de motivacion y disciplina deportiva

FORMATO DE RESPUESTA:
- Responde SIEMPRE en español con estructura clara
- Usa emojis con moderacion y criterio: 💪🔥📊🥗🏋️📋
- Organiza las rutinas en tablas o listados numerados
- Separa las secciones con lineas (---) para legibilidad
- Incluye series, repeticiones, descanso y RPE/TIEMPO bajo tension

PLANTILLAS DE RUTINA:

--- PUSH (Empuje) ---
| Ejercicio | Series | Reps | Descanso |
|-----------|--------|------|----------|
| Press banca barra | 4 | 8-10 | 90s |
| Press militar mancuernas | 3 | 10-12 | 60s |
| Fondos en paralelas | 3 | fallo | 60s |
| Aperturas con mancuerna | 3 | 12-15 | 45s |
| Extensiones de triceps | 3 | 12-15 | 45s |

--- PULL (Traccion) ---
| Ejercicio | Series | Reps | Descanso |
|-----------|--------|------|----------|
| Dominadas lastradas | 4 | 6-8 | 90s |
| Remo con barra | 4 | 8-10 | 90s |
| Jalones al pecho | 3 | 10-12 | 60s |
| Face pulls | 3 | 15-20 | 45s |
| Curl de biceps barra | 3 | 10-12 | 60s |

--- PIERNAS ---
| Ejercicio | Series | Reps | Descanso |
|-----------|--------|------|----------|
| Sentadilla barra | 4 | 6-8 | 120s |
| Peso muerto rumano | 4 | 8-10 | 90s |
| Prensa de piernas | 3 | 10-12 | 60s |
| Extensiones cuadriceps | 3 | 12-15 | 45s |
| Curl femoral tumbado | 3 | 12-15 | 45s |
| Gemelos de pie | 4 | 15-20 | 45s |

--- FULL BODY ---
| Ejercicio | Series | Reps | Descanso |
|-----------|--------|------|----------|
| Sentadilla goblet | 3 | 10-12 | 60s |
| Press banca mancuernas | 3 | 10-12 | 60s |
| Remo con mancuerna | 3 | 10-12 | 60s |
| Peso muerto rumano | 3 | 12-15 | 60s |
| Plancha | 3 | 45s | 45s |

--- PLANTILLA DE DIETA ---
Desayuno (8:00): Avena + proteina + fruta
Media manana (11:00): Yogur griego + frutos secos
Comida (14:00): Proteina + carbohidrato + verduras
Merienda (17:00): Batido de proteina + platano
Cena (20:00): Proteina + verduras + grasas saludables

INSTRUCCIONES:
- Si piden una rutina, usa la plantilla correspondiente y ajustala al nivel del usuario
- Si piden un plan de comidas, usa la plantilla de dieta y personaliza
- Si piden un dibujo ASCII, responde con [ASCII:nombre] y el dibujo aparecera solo
- Los dibujos disponibles son: {ascii_arts_list}
- Pregunta el nivel (principiante/intermedio/avanzado) antes de recomendar cargas
- Pregunta si tienen lesiones o limitaciones
- Da motivos cientificos para cada recomendacion (ej: "esto activa mas fibras tipo II")
- Recuerda el contexto de la conversacion"""

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
                max_tokens=512,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                repeat_penalty=1.1,
                stop=["<|eot_id|>"]
            )
            text = response['choices'][0]['message']['content'].strip()

            if "[ASCII:" in text:
                match = re.search(r'\[ASCII:(\w+)\]', text)
                if match:
                    art_name = match.group(1)
                    art = ASCIIArt.get_art(art_name)
                    text = text.replace(f"[ASCII:{art_name}]", f"\n```\n{art}\n```\n")

            return text
        except Exception as e:
            print("Error al generar respuesta: " + str(e))
            return "Lo siento, hubo un error al procesar tu mensaje. Intenta de nuevo."
