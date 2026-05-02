"""
renderer.py — Grid-based renderer and UI
"""
import pygame
import numpy as np
from .config import *
from .map_gen import MapData, FREE, WALL, START, GOAL
from .aco_core import ACOState

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))

class Renderer:
    def __init__(self, m: MapData):
        self.cell_w = SIM_W // m.cols
        self.cell_h = SIM_H // m.rows
        self.screen_rects = [[pygame.Rect(c * self.cell_w, r * self.cell_h, self.cell_w, self.cell_h)
                             for c in range(m.cols)] for r in range(m.rows)]

    def draw(self, surf: pygame.Surface, m: MapData, state: ACOState, lock):
        # 1. Fill background (Free cells)
        surf.fill(C_BG, (0, 0, SIM_W, SIM_H))
        
        # Lock state for copying data
        with lock:
            tau_np = state.tau.cpu().numpy()
            best_path = state.best_path[:]
            ant_heads = state.ant_heads[:]
            
        t_max = tau_np.max() if tau_np.max() > 0 else 1.0
        
        # 2. Draw walls and pheromones
        for r in range(m.rows):
            for c in range(m.cols):
                rect = self.screen_rects[r][c]
                val = m.grid[r, c]
                if val == WALL:
                    pygame.draw.rect(surf, C_WALL, rect)
                    pygame.draw.rect(surf, C_WALL_EDGE, rect, 1)
                elif val == FREE:
                    t = tau_np[r, c] / t_max
                    color = lerp_color(C_PHER_LOW, C_PHER_HIGH, t)
                    surf.fill(color, rect)
        
        # 3. Draw best path
        for r, c in best_path:
            rect = self.screen_rects[r][c].inflate(-self.cell_w//2, -self.cell_h//2)
            pygame.draw.rect(surf, C_PATH, rect)

        # 4. Draw ant heads
        for r, c in ant_heads:
            center = self.screen_rects[r][c].center
            pygame.draw.circle(surf, C_ANT, center, min(self.cell_w, self.cell_h)//3)

        # 5. Draw START and GOAL
        sr, sc = m.start
        pygame.draw.rect(surf, C_START, self.screen_rects[sr][sc])
        
        gr, gc = m.goal
        pygame.draw.rect(surf, C_GOAL, self.screen_rects[gr][gc])
        
        # Letters
        try:
            font = pygame.font.Font(None, 24)
        except:
            font = None
            
        if font:
            st = font.render("S", True, (255, 255, 255))
            surf.blit(st, st.get_rect(center=self.screen_rects[sr][sc].center))
            gt = font.render("G", True, (255, 255, 255))
            surf.blit(gt, gt.get_rect(center=self.screen_rects[gr][gc].center))

# ── UI Widgets ────────────────────────────────────────────────────

class Slider:
    def __init__(self, x, y, w, vmin, vmax, value, step, label, fmt="{:.2f}"):
        self.x, self.y, self.w = x, y, w
        self.h = 40 # Full row height for hit area
        self.vmin, self.vmax = vmin, vmax
        self.value = value
        self.step = step
        self.label = label
        self.fmt = fmt
        self.dragging = False
        self.track_h = 6
        self.thumb_r = 10

    def handle_event(self, event):
        row_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if row_rect.collidepoint(event.pos):
                self.dragging = True
                self._update_val(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_val(event.pos[0])
            return True
        return False

    def _update_val(self, mx):
        frac = (mx - self.x) / self.w
        frac = max(0.0, min(1.0, frac))
        raw = self.vmin + frac * (self.vmax - self.vmin)
        self.value = round(raw / self.step) * self.step
        self.value = max(self.vmin, min(self.vmax, self.value))

    def draw(self, surf, font):
        # Label and Value
        lbl = font.render(self.label, True, C_TEXT_DIM)
        val_str = self.fmt.format(self.value)
        val_t = font.render(val_str, True, C_TEXT)
        surf.blit(lbl, (self.x, self.y))
        surf.blit(val_t, (self.x + self.w - val_t.get_width(), self.y))
        
        # Track
        track_y = self.y + 25
        pygame.draw.rect(surf, (55, 52, 46), (self.x, track_y - self.track_h//2, self.w, self.track_h), border_radius=3)
        
        # Active portion
        frac = (self.value - self.vmin) / (self.vmax - self.vmin)
        if frac > 0:
            pygame.draw.rect(surf, C_ACCENT, (self.x, track_y - self.track_h//2, int(self.w * frac), self.track_h), border_radius=3)
            
        # Thumb
        tx = self.x + int(frac * self.w)
        pygame.draw.circle(surf, C_ACCENT, (tx, track_y), self.thumb_r)
        pygame.draw.circle(surf, (255, 255, 255), (tx, track_y), self.thumb_r, 1)

class Button:
    def __init__(self, x, y, w, h, label, color=C_BTN_NORMAL, hover_color=C_BTN_HOVER):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def draw(self, surf, font):
        c = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surf, c, self.rect, border_radius=6)
        pygame.draw.rect(surf, C_PANEL_LINE, self.rect, 1, border_radius=6)
        t = font.render(self.label, True, C_TEXT)
        surf.blit(t, t.get_rect(center=self.rect.center))

class IntText:
    def __init__(self, x, y, w, h, value, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.value = value
        self.label = label
        self.text = str(value)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            if self.active and not was_active:
                self.text = ""  # Clear on activation
            elif was_active and not self.active:
                # Commit value when losing focus by clicking elsewhere
                try:
                    self.value = int(self.text) if self.text else self.value
                except ValueError:
                    pass
                self.text = str(self.value)
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit():
                self.text += event.unicode
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.active = False
                try:
                    self.value = int(self.text) if self.text else self.value
                except:
                    pass
                self.text = str(self.value)
                return True
        return False

    def draw(self, surf, font):
        lbl = font.render(self.label, True, C_TEXT_DIM)
        surf.blit(lbl, (self.rect.x, self.rect.y - 20))
        bc = C_ACCENT if self.active else C_PANEL_LINE
        pygame.draw.rect(surf, C_BTN_NORMAL, self.rect, border_radius=5)
        pygame.draw.rect(surf, bc, self.rect, 1, border_radius=5)
        t = font.render(self.text, True, C_TEXT)
        surf.blit(t, t.get_rect(midleft=(self.rect.x + 8, self.rect.centery)))

class Panel:
    def __init__(self, params):
        px = SIM_W + 20
        sw = PANEL_W - 40
        self.sliders = [
            Slider(px, 80, sw, 5, 200, params['n_ants'], 1, "N Ants", "{:.0f}"),
            Slider(px, 140, sw, 10, 1000, params['m_iter'], 10, "M Iterations", "{:.0f}"),
            Slider(px, 200, sw, 0.1, 5.0, params['alpha'], 0.1, "Alpha (Pheromone)", "{:.1f}"),
            Slider(px, 260, sw, 0.1, 10.0, params['beta'], 0.1, "Beta (Heuristic)", "{:.1f}"),
            Slider(px, 320, sw, 0.01, 0.99, params['rho'], 0.01, "Rho (Evaporation)", "{:.2f}"),
            Slider(px, 380, sw, 1, 50, params['speed'], 1, "Speed (iter/frame)", "{:.0f}"),
        ]
        self.seed_box = IntText(px, 460, sw, 30, params['seed'], "Seed")
        self.btn_gen_map = Button(px, 502, sw, 36, "GENERATE MAP", C_BTN_ACT, C_BTN_ACT_H)
        self.btn_play = Button(px, 548, sw, 40, "START", C_BTN_GREEN, C_BTN_GREEN_H)
        self.btn_reset = Button(px, 598, sw, 40, "RESET SIM", C_BTN_NORMAL, C_BTN_HOVER)

    def draw(self, surf, fonts, state, device_str, is_paused):
        font_title, font_label, font_stats = fonts
        pygame.draw.rect(surf, C_PANEL_BG, (SIM_W, 0, PANEL_W, WIN_H))
        pygame.draw.line(surf, C_PANEL_LINE, (SIM_W, 0), (SIM_W, WIN_H))
        
        t = font_title.render("ACO GRID", True, C_ACCENT)
        surf.blit(t, (SIM_W + 20, 20))
        d_t = font_stats.render(device_str, True, C_SUCCESS)
        surf.blit(d_t, (SIM_W + 20, 50))
        
        for s in self.sliders: s.draw(surf, font_label)
        self.seed_box.draw(surf, font_label)
        self.btn_gen_map.draw(surf, font_label)

        # Update Play button label
        if state is None:
            self.btn_play.label = "START"
        elif state.iteration == 0:
            self.btn_play.label = "START"
        else:
            self.btn_play.label = "PAUSE" if not is_paused else "RESUME"

        self.btn_play.draw(surf, font_title)
        self.btn_reset.draw(surf, font_title)

        if state:
            y = 650
            it_t = font_label.render(f"Iteration: {state.iteration}", True, C_TEXT)
            surf.blit(it_t, (SIM_W + 20, y))
            bl_t = font_label.render(f"Best Length: {state.best_len:.2f}", True, C_SUCCESS)
            surf.blit(bl_t, (SIM_W + 20, y + 30))

    def handle_event(self, event):
        actions = {}
        for s in self.sliders:
            if s.handle_event(event): actions['changed'] = True
        if self.seed_box.handle_event(event): actions['changed'] = True
        if self.btn_gen_map.handle_event(event): actions['generate'] = True
        if self.btn_play.handle_event(event): actions['play'] = True
        if self.btn_reset.handle_event(event): actions['reset'] = True
        return actions

    def get_params(self):
        return {
            'n_ants': int(self.sliders[0].value),
            'm_iter': int(self.sliders[1].value),
            'alpha': self.sliders[2].value,
            'beta': self.sliders[3].value,
            'rho': self.sliders[4].value,
            'speed': int(self.sliders[5].value),
            'seed': self.seed_box.value
        }
