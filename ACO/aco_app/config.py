"""
config.py — Configuracion global y deteccion de dispositivo
"""
import torch

# ── Deteccion automatica de dispositivo ──────────────────────────
def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")

DEVICE = get_device()

# ── Ventana ───────────────────────────────────────────────────────
WIN_W        = 1280
WIN_H        = 760
PANEL_W      = 300          # ancho del panel lateral
SIM_W        = WIN_W - PANEL_W
SIM_H        = WIN_H
FPS          = 60

# ── Canvas normalizado del mapa ───────────────────────────────────
CANVAS_W     = 1.0
CANVAS_H     = 1.0

# ── Colores (R, G, B) ─────────────────────────────────────────────
C_BG         = (18,  18,  16)
C_PANEL_BG   = (26,  25,  22)
C_PANEL_LINE = (50,  48,  44)
C_WALL       = (45,  42,  38)
C_WALL_EDGE  = (75,  72,  65)
C_PHER_LOW   = (30,  30,  35)
C_PHER_HIGH  = (29,  158, 117)   # teal
C_PATH       = (127, 119, 221)   # purpura
C_ANT        = (239, 159,  39)   # ambar
C_START      = (83,  74,  183)   # purpura oscuro
C_GOAL       = (183,  60,  60)   # teal oscuro
C_TEXT       = (194, 192, 182)
C_TEXT_DIM   = (110, 107, 100)
C_ACCENT     = (127, 119, 221)
C_SUCCESS    = (29,  158, 117)
C_BTN_NORMAL = (45,  42,  38)
C_BTN_HOVER  = (62,  58,  52)
C_BTN_ACT    = (83,  74,  183)
C_BTN_GREEN  = (22,  90,  68)
C_BTN_GREEN_H= (29, 120,  90)
C_BTN_ACT_H  = (103, 95, 205)

# ── Parametros ACO por defecto ────────────────────────────────────
ROWS         = 40
COLS         = 60

DEFAULT_PARAMS = dict(
    seed    = 42,
    n_ants  = 25,       # N hormigas
    m_iter  = 100,      # M iteraciones
    alpha   = 1.5,      # peso feromona
    beta    = 4.0,      # peso heuristica
    rho     = 0.25,     # evaporacion
    q_dep   = 1.0,      # deposito Q
    tau0    = 0.1,      # feromona inicial
    speed   = 4,        # iteraciones por frame
)
