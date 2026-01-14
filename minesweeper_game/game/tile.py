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
