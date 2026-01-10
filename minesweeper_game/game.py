import random
from collections import deque
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


def get_neighbours(x, y, w, h):
    for i in range(x - 1, x + 2):
        for j in range(y - 1, y + 2):
            if i < 0 or j < 0 or i >= w or j >= h or (i == x and j == y):
                continue
            yield i, j


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
        self.mine_count = mine_count
        self.grid = [[Tile() for _ in range(cols)] for _ in range(rows)]
        self.mines_placed_ = False

    def place_mine_(self, x, y) -> bool:  # true if succeeded
        if self.grid[y][x].is_mine:
            return False

        self.grid[y][x].is_mine = True

        for nx, ny in get_neighbours(x, y, self.cols, self.rows):
            self.grid[ny][nx].value += 1

        return True

    def place_mines(self, safe_spots=[]):
        safe_spots = set(safe_spots)
        potential_spots = [
            (x, y)
            for x in range(self.cols)
            for y in range(self.rows)
            if (x, y) not in safe_spots
        ]
        mine_spots = random.sample(potential_spots, self.mine_count)

        for x, y in mine_spots:
            self.place_mine_(x, y)

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

        if not self.mines_placed_:
            self.place_mines([(x, y)])
            self.mines_placed_ = True

        if tile.is_mine:
            print("MINE")
            tile.state = TileState.UNCOVERED
            return False

        to_uncover = deque([(x, y)])
        while to_uncover:
            cur_x, cur_y = to_uncover.pop()
            cur_tile = self.grid[cur_y][cur_x]

            cur_tile.state = TileState.UNCOVERED

            if cur_tile.value == 0:
                for nx, ny in get_neighbours(cur_x, cur_y, self.cols, self.rows):
                    if self.grid[ny][nx].state in (
                        TileState.COVERED,
                        TileState.QUESTIONED,
                    ):
                        to_uncover.append((nx, ny))

        return True
