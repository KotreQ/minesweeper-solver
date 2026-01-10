from enum import Enum, auto


class TileState(Enum):
    COVERED = auto()
    FLAGGED = auto()
    QUESTIONED = auto()
    UNCOVERED = auto()


class Tile:
    def __init__(self):
        self.is_mine = False
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

    def cycle_covered_state(self, x, y) -> bool:  # true if succeeded
        tile = self.grid[y][x]

        match tile.state:
            case TileState.COVERED:
                new_state = TileState.FLAGGED
            case TileState.FLAGGED:
                new_state = TileState.QUESTIONED
            case TileState.QUESTIONED:
                new_state = TileState.COVERED
            case TileState.UNCOVERED:
                return False

        tile.state = new_state
        return True

    def uncover(self, x, y) -> bool:  # true if the game continues
        tile = self.grid[y][x]

        if tile.state == TileState.FLAGGED:
            return True

        tile.state = TileState.UNCOVERED
        return not tile.is_mine
