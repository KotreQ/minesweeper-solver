import numpy as np


def get_uncovered_grid(grid):
    uncovered = [[cell.is_uncovered for cell in row] for row in grid]
    uncovered = np.array(uncovered, np.bool_)

    return uncovered