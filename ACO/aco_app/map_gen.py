"""
map_gen.py — Grid-based map generation
"""
import numpy as np
from dataclasses import dataclass
from collections import deque

# Cell types
FREE  = 0
WALL  = 1
START = 2
GOAL  = 3

@dataclass
class MapData:
    grid: np.ndarray
    rows: int
    cols: int
    start: tuple[int, int]
    goal: tuple[int, int]

def _has_path(grid: np.ndarray, start: tuple[int, int], goal: tuple[int, int]) -> bool:
    """BFS to check if a path exists from start to goal."""
    rows, cols = grid.shape
    q = deque([start])
    visited = {start}
    
    while q:
        r, c = q.popleft()
        if (r, c) == goal:
            return True
        
        # 8-directional movement
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr, nc] != WALL and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append((nr, nc))
    return False

def generate_map(seed: int, rows: int, cols: int) -> MapData:
    """
    Generates a 2D grid map with rectangular walls.
    Guarantees a valid path from START to GOAL.
    """
    current_seed = seed
    while True:
        rng = np.random.default_rng(current_seed)
        grid = np.zeros((rows, cols), dtype=np.int8)
        
        # Fixed START and GOAL positions
        start = (rows // 2, 2)
        goal  = (rows // 2, cols - 3)
        
        grid[start] = START
        grid[goal]  = GOAL
        
        # Generate rectangular walls
        n_rects = rng.integers(10, 20)
        for _ in range(n_rects):
            w = rng.integers(3, 8)
            h = rng.integers(3, 8)
            r = rng.integers(0, rows - h)
            c = rng.integers(5, cols - 5 - w) # Avoid start/goal areas
            
            # Slicing to set walls
            grid[r:r+h, c:c+w] = WALL
            
        # Ensure START and GOAL are not overwritten and are FREE around them
        grid[start] = START
        grid[goal]  = GOAL
        
        if _has_path(grid, start, goal):
            return MapData(grid=grid, rows=rows, cols=cols, start=start, goal=goal)
        
        current_seed += 1
