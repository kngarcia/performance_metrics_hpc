"""
aco_core.py — Grid-based ACO core with PyTorch and Threading
"""
import os
import torch
import numpy as np
import threading
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from .map_gen import MapData, WALL
from .config import DEVICE

@dataclass
class ACOState:
    tau: torch.Tensor
    eta: torch.Tensor
    best_path: list[tuple[int, int]] = field(default_factory=list)
    best_len: float = float('inf')
    iteration: int = 0
    ant_heads: list[tuple[int, int]] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)

def build_state(m: MapData, alpha: float, beta: float, tau0: float = 0.1) -> ACOState:
    """Initializes tau and eta tensors on grid."""
    tau = torch.full((m.rows, m.cols), tau0, dtype=torch.float32, device=DEVICE)
    
    # Precompute eta: 1 / euclidean_distance_to_goal
    eta_np = np.zeros((m.rows, m.cols), dtype=np.float32)
    gr, gc = m.goal
    for r in range(m.rows):
        for c in range(m.cols):
            if m.grid[r, c] == WALL:
                continue
            dist = np.sqrt((r - gr)**2 + (c - gc)**2)
            eta_np[r, c] = 1.0 / max(0.5, dist)
            
    eta = torch.tensor(eta_np, device=DEVICE) ** beta
    return ACOState(tau=tau, eta=eta)

def _get_neighbors(r: int, c: int, rows: int, cols: int, grid: np.ndarray):
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr, nc] != WALL:
            yield nr, nc

def ant_walk(r: int, c: int, goal: tuple[int, int], 
             rows: int, cols: int, grid: np.ndarray,
             tau: torch.Tensor, eta: torch.Tensor, 
             alpha: float) -> list[tuple[int, int]]:
    """Single ant walk from start to goal."""
    path = [(r, c)]
    visited = {(r, c)}
    
    # Limit steps to avoid infinite loops, though visited check should handle it
    for _ in range(rows * cols):
        if (r, c) == goal:
            return path
        
        neighbors = []
        weights = []
        
        for nr, nc in _get_neighbors(r, c, rows, cols, grid):
            if (nr, nc) not in visited:
                neighbors.append((nr, nc))
                # Probability formula: P(i,j) = tau[j]^alpha * eta[j]^beta
                # Note: eta is already raised to beta in build_state for efficiency
                t = tau[nr, nc].item()
                e = eta[nr, nc].item()
                weights.append((t ** alpha) * e)
        
        if not neighbors:
            return [] # Stuck
            
        total = sum(weights)
        if total <= 0:
            idx = np.random.randint(len(neighbors))
        else:
            probs = [w / total for w in weights]
            idx = np.random.choice(len(neighbors), p=probs)
            
        r, c = neighbors[idx]
        path.append((r, c))
        visited.add((r, c))
        
    return []

def run_iteration(state: ACOState, m: MapData, 
                  n_ants: int, alpha: float, 
                  rho: float, Q: float):
    """Executes one ACO iteration using thread pool for ant walks."""
    # 1. Evaporation: tau *= (1 - rho)
    with state.lock:
        state.tau.mul_(1.0 - rho)
        state.tau.clamp_(min=1e-4)
    
    # 2. Parallel Ant Walks
    paths = []
    # Local copies for thread safety without holding lock during walks
    with state.lock:
        tau_local = state.tau.clone().cpu() # Copy to CPU for path finding logic
        eta_local = state.eta.cpu()
        
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [
            executor.submit(ant_walk, m.start[0], m.start[1], m.goal, 
                           m.rows, m.cols, m.grid, 
                           tau_local, eta_local, alpha)
            for _ in range(n_ants)
        ]
        for f in futures:
            p = f.result()
            if p:
                paths.append(p)
                
    # 3. Pheromone Deposit and Update Best Path
    with state.lock:
        new_heads = []
        for path in paths:
            new_heads.append(path[-1])
            path_len = len(path) - 1 # cell steps
            if path_len < state.best_len:
                state.best_len = path_len
                state.best_path = path[:]
            
            # Deposit Q/path_length to each cell visited
            delta = Q / max(1.0, path_len)
            for r, c in path:
                state.tau[r, c] += delta
        
        state.ant_heads = new_heads
        state.iteration += 1
