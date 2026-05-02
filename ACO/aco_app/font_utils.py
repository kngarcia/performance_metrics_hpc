"""
font_utils.py — Utilidades para manejo de fuentes con fallback para fallos en pygame.font
"""
import pygame

# ── Mapa de bits 3x5 para fuente de respaldo ─────────────────────
# Cada entrada es una tupla de 5 enteros (filas), cada uno de 3 bits (columnas)
_BITMAP_3x5 = {
    '0': (7, 5, 5, 5, 7), '1': (2, 2, 2, 2, 2), '2': (7, 1, 7, 4, 7),
    '3': (7, 1, 3, 1, 7), '4': (5, 5, 7, 1, 1), '5': (7, 4, 7, 1, 7),
    '6': (7, 4, 7, 5, 7), '7': (7, 1, 1, 1, 1), '8': (7, 5, 7, 5, 7),
    '9': (7, 5, 7, 1, 1), ':': (0, 2, 0, 2, 0), '.': (0, 0, 0, 0, 2),
    '-': (0, 0, 7, 0, 0), ' ': (0, 0, 0, 0, 0), 'A': (2, 5, 7, 5, 5),
    'B': (6, 5, 6, 5, 6), 'C': (3, 4, 4, 4, 3), 'D': (6, 5, 5, 5, 6),
    'E': (7, 4, 6, 4, 7), 'F': (7, 4, 6, 4, 4), 'G': (3, 4, 5, 5, 3),
    'H': (5, 5, 7, 5, 5), 'I': (7, 2, 2, 2, 7), 'J': (1, 1, 1, 5, 2),
    'K': (5, 5, 6, 5, 5), 'L': (4, 4, 4, 4, 7), 'M': (5, 7, 5, 5, 5),
    'N': (5, 7, 7, 7, 5), 'O': (2, 5, 5, 5, 2), 'P': (6, 5, 6, 4, 4),
    'Q': (2, 5, 5, 6, 1), 'R': (6, 5, 6, 5, 5), 'S': (3, 4, 2, 1, 6),
    'T': (7, 2, 2, 2, 2), 'U': (5, 5, 5, 5, 7), 'V': (5, 5, 5, 5, 2),
    'W': (5, 5, 5, 7, 5), 'X': (5, 5, 2, 5, 5), 'Y': (5, 5, 2, 2, 2),
    'Z': (7, 1, 2, 4, 7), '/': (1, 1, 2, 4, 4), '(': (2, 4, 4, 4, 2),
    ')': (4, 2, 2, 2, 4), '|': (2, 2, 2, 2, 2), '_': (0, 0, 0, 0, 7),
    '+': (0, 2, 7, 2, 0), '=': (0, 7, 0, 7, 0), ',': (0, 0, 0, 2, 4),
    '[': (3, 2, 2, 2, 3), ']': (6, 1, 1, 1, 6), '>': (4, 2, 1, 2, 4),
    '<': (1, 2, 4, 2, 1), '?': (7, 1, 2, 0, 2), '!': (2, 2, 2, 0, 2),
}

class FallbackFont:
    """Implementacion minima de renderizado de texto mediante pixeles."""
    def __init__(self, size: int = 12):
        self.size  = size
        self.scale = max(1, size // 8)

    def render(self, text: str, antialias: bool, color: tuple,
               background: tuple | None = None) -> pygame.Surface:
        text = text.upper()  # El mapa solo tiene mayusculas para ahorrar espacio
        char_w = 3 * self.scale
        char_h = 5 * self.scale
        gap    = 1 * self.scale
        
        surf_w = max(1, len(text) * (char_w + gap))
        surf_h = char_h
        
        surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        if background:
            surf.fill(background)
            
        for i, char in enumerate(text):
            bitmap = _BITMAP_3x5.get(char, (7, 7, 7, 7, 7)) # Cuadro para desc.
            ox = i * (char_w + gap)
            for row in range(5):
                bits = bitmap[row]
                for col in range(3):
                    if bits & (1 << (2 - col)):
                        if self.scale == 1:
                            surf.set_at((ox + col, row), color)
                        else:
                            pygame.draw.rect(surf, color,
                                (ox + col * self.scale, row * self.scale,
                                 self.scale, self.scale))
        return surf

    def get_rect(self, **kwargs) -> pygame.Rect:
        # Mock para compatibilidad con Font.render().get_rect()
        # En uso real, se suele llamar despues de render
        return pygame.Rect(0, 0, 0, 0) # Sera sobrescrito por el surface real


def get_font(name: str | None, size: int, bold: bool = False):
    """
    Carga una fuente de sistema o usa el fallback si falla pygame.font.
    """
    try:
        if not pygame.font.get_init():
            pygame.font.init()
        # Intentar SysFont
        return pygame.font.SysFont(name or "Arial", size, bold=bold)
    except (ImportError, RuntimeError, AttributeError, NameError):
        # Si pygame.font falla completamente o SysFont no esta disponible
        try:
            # Intentar Font(None) como ultimo recurso de pygame
            return pygame.font.Font(None, size)
        except:
            return FallbackFont(size)
