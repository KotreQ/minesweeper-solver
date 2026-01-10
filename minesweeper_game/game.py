from enum import Enum, auto


class TileState(Enum):
    COVERED = auto()
    FLAGGED = auto()
    QUESTIONED = auto()
    UNCOVERED = auto()


class Tile:
    def __init__(self):
        self.is_bomb = False
        self.value = 0
        self.state = TileState.COVERED


class MinesweeperGame:
    def __init__(self, cols, rows, mine_count):
        assert cols >= 9
        assert rows >= 9
        assert mine_count >= 10
        assert cols <= 30
        assert rows <= 24
        assert mine_count <= (cols - 1) * (rows - 1)

        self.cols = cols
        self.rows = rows
        self.grid = [[Tile() for _ in range(cols)] for _ in range(rows)]
