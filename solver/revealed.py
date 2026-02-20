import numpy as np


def get_revealed_grid(grid):
    revealed = [[cell.is_revealed for cell in row] for row in grid]
    revealed = np.array(revealed, np.bool_)

    return revealed