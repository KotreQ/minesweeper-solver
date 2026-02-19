from game.tile import Tile, TileState


def get_neighbours(x, y, w, h):
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            if i < 0 or j < 0 or i >= w or j >= h or (i == x and j == y):
                continue
            yield i, j


def print_grid(grid: list[list[Tile]]):
    TILE_CHARS = {
        TileState.SAFE_0: " ",
        TileState.SAFE_1: "1",
        TileState.SAFE_2: "2",
        TileState.SAFE_3: "3",
        TileState.SAFE_4: "4",
        TileState.SAFE_5: "5",
        TileState.SAFE_6: "6",
        TileState.SAFE_7: "7",
        TileState.SAFE_8: "8",
        TileState.COVERED: ".",
        TileState.FLAGGED: "F",
        TileState.MINE: "x",
        TileState.BLOWN_MINE: "X",
        TileState.FALSE_FLAG: "f",
    }

    rows = []
    for row in grid:
        row = "".join(TILE_CHARS[tile.state] for tile in row)
        rows.append(row)

    output = "\n".join(rows)

    print("\n" + output + "\n")
