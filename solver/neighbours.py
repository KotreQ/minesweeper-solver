import numpy as np


def get_revealed_neighbours(revealed):
    padded = np.pad(revealed, 1, "constant")

    rows, cols = revealed.shape
    neighbours = np.zeros_like(revealed, np.uint8)

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue

            neighbours += padded[1 + dy : 1 + dy + rows, 1 + dx : 1 + dx + cols]

    return neighbours


def get_all_neighbours(rows, cols):
    neighbours = np.zeros((rows, cols), np.uint8)
    for y in range(rows):
        h_border = y == 0 or y == rows - 1
        for x in range(cols):
            v_border = x == 0 or x == cols - 1

            if h_border and v_border:
                val = 3
            elif h_border or v_border:
                val = 5
            else:
                val = 8

            neighbours[y][x] = val

    return neighbours
