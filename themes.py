COLORES = [
    {
        "nombre": "🌙 Oscuro",
        "bg": "#1a1a2e", "fg": "#ECF0F1", "chat_bg": "#0d0d1a",
        "btn_bg": "#2C3E50", "acento": "#FFD700", "naranja": "#FF6B35",
        "input_bg": "#1a1a2e", "scroll": "#34495E", "face_bg": "#2C3E50"
    },
    {
        "nombre": "☀️ Claro",
        "bg": "#F5F5F5", "fg": "#2C3E50", "chat_bg": "#FFFFFF",
        "btn_bg": "#2980B9", "acento": "#E67E22", "naranja": "#E74C3C",
        "input_bg": "#FFFFFF", "scroll": "#BDC3C7", "face_bg": "#2980B9"
    },
    {
        "nombre": "🌿 Naturaleza",
        "bg": "#1a2e1a", "fg": "#E8F5E9", "chat_bg": "#0d1a0d",
        "btn_bg": "#2E7D32", "acento": "#A5D6A7", "naranja": "#FF8A65",
        "input_bg": "#1a2e1a", "scroll": "#388E3C", "face_bg": "#2E7D32"
    },
]


def get_theme(index):
    return COLORES[index % len(COLORES)]


def theme_count():
    return len(COLORES)
