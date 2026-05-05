import numpy as np


cell_dtype = np.dtype([
    ("value", np.int8),
    ("is_revealed", np.bool_),
    ("is_flagged", np.bool_),
    ("all_neighbours", np.uint8),
    ("flagged_neighbours", np.uint8),
    ("revealed_neighbours", np.uint8),
])


def update_numpy_grid(arr, grid):
    rows, cols = arr.shape

    for i in range(rows):
        h_border = i == 0 or i == rows-1
        for j in range(cols):
            v_border = j == 0 or j == cols-1

            tile = grid[i][j]
            arr[i, j]["value"] = tile.value
            arr[i, j]["is_revealed"] = tile.is_revealed
            arr[i, j]["is_flagged"] = tile.is_flagged

            if h_border and v_border:
                arr[i, j]["all_neighbours"] = 3
            elif h_border or v_border:
                arr[i, j]["all_neighbours"] = 5
            else:
                arr[i, j]["all_neighbours"] = 8
    
    arr["flagged_neighbours"] = _get_key_neighbours(arr["is_flagged"])
    arr["revealed_neighbours"] = _get_key_neighbours(arr["is_revealed"])


def _get_key_neighbours(key_arr):
    padded = np.pad(key_arr, 1, "constant", constant_values=0)

    rows, cols = key_arr.shape
    neighbours = np.zeros_like(key_arr, np.uint8)

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue

            neighbours += padded[1 + dy : 1 + dy + rows, 1 + dx : 1 + dx + cols]

    return neighbours


def get_neighbours_coords(x, y, rows, cols):
    for ny in range(y - 1, y + 2):
        if ny < 0 or ny >= rows:
            continue

        for nx in range(x - 1, x + 2):
            if nx < 0 or nx >= cols:
                continue

            if ny != y or nx != x:
                yield nx, ny
