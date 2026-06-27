class ASCIIArt:
    @staticmethod
    def get_art(name):
        arts = {
            "mancuerna": "  __   __\n |__| |__|\n  (_)_(_)\n ==o=o==\n  (_)_(_)\n |__| |__|",
            "pesa": " +=====+\n | ### |\n | ### |\n +=====+",
            "musculo": " .----.\n |💪|\n '----'\n .--. .--.\n |  | |  |\n '--' '--'",
            "trofeo": " .---.\n |🏆|\n '---'\n   |\n  / \\",
            "fuego": "  (@)\n (@@)\n(@@@)\n (@@)\n  (@)",
            "corazon": " *****\n*******\n *****\n   *",
            "hombre": " .---.\n | O |\n '---'\n  /|\\\n  / \\",
            "mujer": " .---.\n | O |\n '---'\n  /|\\\n  / \\",
            "flexion": " .---.\n | O |\n '---'\n  /|\\\n  / \\",
            "sentadilla": " .---.\n | O |\n '---'\n  / \\\n /   \\",
            "barra": " ===O===\n  ##|##\n  ##|##",
            "reloj": " .---.\n |@  |\n '---'",
            "manzana": " .---.\n |🍎|\n '---'\n   |\n  / \\",
            "agua": " .---.\n |💧|\n |💧|\n '---'",
            "pesas": " .--. .--.\n |🏋️| |🏋️|\n '--' '--'\n  ===O\n .--.|.--.\n |🏋️||🏋️|\n '--''--'",
            "runner": " .---.\n | O |\n '---' 🏃\n  /|\\\n  / \\",
            "yoga": " .---.\n | O |\n '---'\n  / \\\n /   \\\n/     \\",
            "bicicleta": " .---.\n | O |\n '---' 🚲\n  / \\\n /   \\",
            "escalera": " ##\n ## ##\n ## ## ##\n ## ## ## ##\n 🏃^^^^",
            "peso_muerto": " .---.\n | O |\n '---'\n  / \\\n / 🏋️ \\",
            "gym": "  ______\n / GYM \\\n | 💪 |\n | 🏋️ |\n \\______/",
            "proteina": " .------.\n |PROTEIN|\n | SHAKE |\n '------'\n    ||\n    ||",
            "cuerda": "  ~~~~~\n  ~ ~ ~\n  ~~~~~\n  ~ ~ ~\n  ~~~~~",
            "remo": "  ____\n | __ |\n ||  ||\n ||__||\n |____|\n   /\\",
            "abdominal": " .----.\n |\\\\ //|\n | \\/ |\n | /\\ |\n |// \\\\|\n '----'",
            "suplemento": " .------.\n | 💊💊 |\n | SUP  |\n '------'\n    ||\n   /  \\",
        }
        return arts.get(name.lower(), arts.get("musculo"))

    @staticmethod
    def list_arts():
        return ["mancuerna","pesa","musculo","trofeo","fuego","corazon","hombre","mujer","flexion","sentadilla","barra","reloj","manzana","agua","pesas","runner","yoga","bicicleta","escalera","peso_muerto","gym","proteina","cuerda","remo","abdominal","suplemento"]
