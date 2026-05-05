from dataclasses import dataclass
import numpy as np
from .frontier import find_edges
from .grid import get_neighbours_coords


@dataclass
class Constraint:
    value: int
    indices: list[tuple[int, int]]


def get_constraints(grid):
    constraints = []

    edge_mask = find_edges(grid)
    rows, cols = grid.shape

    mines_left = grid["value"] - grid["flagged_neighbours"]

    y_list, x_list = np.where(edge_mask)
    for i, (x, y) in enumerate(zip(x_list, y_list)):
        value = mines_left[y, x]
        indices = []

        for nx, ny in get_neighbours_coords(x, y, rows, cols):
            if not grid[ny, nx]["is_revealed"]:
                indices.append((ny, nx))

        c = Constraint(value, indices)
        constraints.append(c)
    
    return constraints
    