"""
main.py — Entry point for Grid-based ACO
"""
import sys
import os
import threading
import time
import pygame
import torch

from aco_app.config import *
from aco_app.map_gen import generate_map, MapData
from aco_app.aco_core import build_state, run_iteration, ACOState
from aco_app.renderer import Panel, Renderer
from aco_app.font_utils import get_font

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("ACO Grid Optimization")
        self.clock = pygame.time.Clock()
        
        self.font_title = get_font("Arial", 22, bold=True)
        self.font_label = get_font("Arial", 16, bold=False)
        self.font_stats = get_font("Arial", 14, bold=False)
        self.fonts = (self.font_title, self.font_label, self.font_stats)
        
        self.params = DEFAULT_PARAMS.copy()
        self.panel = Panel(self.params)
        
        self.map_data = None
        self.aco_state = None
        self.renderer = None

        self.aco_thread = None
        self._stop_event = threading.Event()
        self.is_paused = True

        self.device_str = self._get_device_label()

    def _get_device_label(self) -> str:
        d = DEVICE.type.upper()
        if d == "CUDA":
            return f"GPU: {torch.cuda.get_device_name(0)} (CUDA)"
        if d == "MPS":
            return "GPU: Apple Silicon (MPS)"
        return "CPU (no GPU)"

    def _stop_thread(self):
        self._stop_event.set()
        if self.aco_thread and self.aco_thread.is_alive():
            self.aco_thread.join()
        self._stop_event.clear()

    def _start_thread(self):
        self.aco_thread = threading.Thread(target=self.aco_loop, daemon=True)
        self.aco_thread.start()

    def generate_map_and_reset(self):
        """Generate a new map from the current seed and reset the ACO state."""
        self._stop_thread()
        self.params = self.panel.get_params()
        self.map_data = generate_map(self.params['seed'], ROWS, COLS)
        self.renderer = Renderer(self.map_data)
        self.aco_state = build_state(self.map_data, self.params['alpha'], self.params['beta'], self.params.get('tau0', 0.1))
        self.is_paused = True
        self._start_thread()

    def reset_sim(self):
        """Reset the ACO state on the current map (map stays the same)."""
        if self.map_data is None:
            return
        self._stop_thread()
        self.params = self.panel.get_params()
        self.aco_state = build_state(self.map_data, self.params['alpha'], self.params['beta'], self.params.get('tau0', 0.1))
        self._start_thread()

    def aco_loop(self):
        while not self._stop_event.is_set():
            if not self.is_paused and self.aco_state.iteration < self.params['m_iter']:
                # Run speed iterations per "step"
                for _ in range(self.params['speed']):
                    if self._stop_event.is_set() or self.is_paused: break
                    run_iteration(self.aco_state, self.map_data, 
                                  self.params['n_ants'], self.params['alpha'], 
                                  self.params['rho'], self.params.get('q_dep', 1.0))
                
                # Small sleep to yield
                time.sleep(0.01)
            else:
                time.sleep(0.1)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._stop_event.set()
                    pygame.quit()
                    sys.exit()
                
                actions = self.panel.handle_event(event)
                if actions.get('generate'):
                    self.generate_map_and_reset()
                if actions.get('play') and self.map_data is not None:
                    self.is_paused = not self.is_paused
                if actions.get('reset'):
                    self.is_paused = True
                    self.reset_sim()
                if actions.get('changed'):
                    if self.aco_state and self.aco_state.iteration == 0:
                        self.params = self.panel.get_params()
                
            # Render
            self.screen.fill(C_BG)
            if self.renderer:
                self.renderer.draw(self.screen, self.map_data, self.aco_state, self.aco_state.lock)
            else:
                line1 = self.font_label.render("Enter a seed and click GENERATE MAP", True, (110, 107, 100))
                line2 = self.font_label.render("to start the simulation", True, (110, 107, 100))
                self.screen.blit(line1, line1.get_rect(center=(SIM_W // 2, SIM_H // 2 - 16)))
                self.screen.blit(line2, line2.get_rect(center=(SIM_W // 2, SIM_H // 2 + 16)))
            
            self.panel.draw(self.screen, self.fonts, self.aco_state, self.device_str, self.is_paused)
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    app = App()
    app.run()
