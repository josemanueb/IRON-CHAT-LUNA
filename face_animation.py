import tkinter as tk
from PIL import Image, ImageTk
import os
import glob

class AnimatedFace:
    def __init__(self, parent, x=0, y=0, size=280, project_dir=None):
        self.parent = parent
        self.x = x
        self.y = y
        self.size = size
        self.is_speaking = False
        self.bounce = 0
        self.bounce_direction = 1
        self.running = True

        # Crear canvas
        self.canvas = tk.Canvas(
            parent,
            width=size,
            height=size,
            bg="#2C3E50",
            highlightthickness=0
        )
        self.canvas.place(x=x, y=y)

        # Buscar imagen del robot en la carpeta del proyecto
        image_path = None
        if project_dir:
            for name in ["robot.jpeg", "robot.jpg", "robot.png", "face.jpeg", "face.png"]:
                path = os.path.join(project_dir, name)
                if os.path.exists(path):
                    image_path = path
                    break
            if not image_path:
                for ext in ['*.jpeg', '*.jpg', '*.png']:
                    files = glob.glob(os.path.join(project_dir, ext))
                    if files:
                        # Usar la primera imagen que NO sea la de fondo
                        for f in files:
                            if 'gym' not in os.path.basename(f).lower() and 'fondo' not in os.path.basename(f).lower():
                                image_path = f
                                break
                        if image_path:
                            break

        self.tk_image = None
        self.image_id = None

        if image_path and os.path.exists(image_path):
            try:
                self.original_image = Image.open(image_path)
                self.original_image = self.original_image.resize((size, size), Image.LANCZOS)
                self.tk_image = ImageTk.PhotoImage(self.original_image)
                self.image_id = self.canvas.create_image(
                    size//2, size//2,
                    image=self.tk_image
                )
            except Exception as e:
                print("Error al cargar imagen del robot: " + str(e))

        # Si no hay imagen, mostrar un circulo con emoji
        if self.image_id is None:
            self.image_id = self.canvas.create_oval(
                10, 10, size-10, size-10,
                fill="#FF6B35", outline="#FFD700", width=3
            )
            self.canvas.create_text(
                size//2, size//2,
                text="🤖", font=("Helvetica", 80),
                fill="white"
            )

        # Iniciar animacion
        self.animate()

    def set_speaking(self, speaking):
        self.is_speaking = speaking

    def animate(self):
        if not self.running:
            return

        if self.is_speaking:
            self.bounce += 1 * self.bounce_direction
            if self.bounce >= 8:
                self.bounce_direction = -1
            elif self.bounce <= -8:
                self.bounce_direction = 1

            new_y = self.size // 2 + self.bounce
            self.canvas.coords(self.image_id, self.size//2, new_y)
        else:
            if self.bounce != 0:
                self.bounce = 0
                self.canvas.coords(self.image_id, self.size//2, self.size//2)

        try:
            self.parent.after(50, self.animate)
        except tk.TclError:
            self.running = False

    def destroy(self):
        self.running = False
        self.canvas.destroy()
