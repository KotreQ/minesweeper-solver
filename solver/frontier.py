import numpy as np


def find_edges(grid):
    rows, cols = grid.shape
    padded = np.pad(grid["is_revealed"], 1, "edge")

    max_pool = np.zeros((rows, cols), np.bool_)
    min_pool = np.ones((rows, cols), np.bool_)

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            shifted = padded[1 + dy : 1 + dy + rows, 1 + dx : 1 + dx + cols]
            max_pool = np.maximum(max_pool, shifted)
            min_pool = np.minimum(min_pool, shifted)

    border_mask = max_pool != min_pool

    edge_mask = border_mask & grid["is_revealed"]

    return edge_mask
