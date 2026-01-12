import random
from collections import deque
from enum import Enum, auto


class TileState(Enum):
    COVERED = auto()
    FLAGGED = auto()
    QUESTIONED = auto()
    UNCOVERED = auto()


ENABLE_QUESTIONED = False


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


class GameState(Enum):
    RUNNING = auto()
    WON = auto()
    LOST = auto()


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
        self.__mines_placed = False

        self.__game_state = GameState.RUNNING

        self.__uncovered_tiles = 0

    @property
    def state(self):
        return self.__game_state

    @property
    def uncovered_tiles(self):
        return self.__uncovered_tiles

    def __place_mine(self, x, y):
        if self.grid[y][x].is_mine:
            raise ValueError(f"Mine is already at ({x},{y})")

        self.grid[y][x].is_mine = True

        for nx, ny in get_neighbours(x, y, self.cols, self.rows):
            self.grid[ny][nx].value += 1

        return True

    def __place_mines(self, safe_spots=[]):
        safe_spots = set(safe_spots)
        potential_spots = [
            (x, y)
            for x in range(self.cols)
            for y in range(self.rows)
            if (x, y) not in safe_spots
        ]
        mine_spots = random.sample(potential_spots, self.mine_count)

        for x, y in mine_spots:
            self.__place_mine(x, y)

    def cycle_covered_state(self, x, y):
        if self.__game_state != GameState.RUNNING:
            return

        tile = self.grid[y][x]

        match tile.state:
            case TileState.COVERED:
                new_state = TileState.FLAGGED
            case TileState.FLAGGED:
                new_state = (
                    TileState.QUESTIONED if ENABLE_QUESTIONED else TileState.COVERED
                )
            case TileState.QUESTIONED:
                new_state = TileState.COVERED
            case TileState.UNCOVERED:
                return

        tile.state = new_state

    def uncover(self, x, y):
        if self.__game_state != GameState.RUNNING:
            return

        tile = self.grid[y][x]

        if tile.state == TileState.FLAGGED:
            return

        if not self.__mines_placed:
            self.__place_mines([(x, y)])
            self.__mines_placed = True

        to_uncover = deque()

        if tile.state == TileState.UNCOVERED:
            unflagged_neighbours = []
            flagged_neighbours = 0
            for x, y in get_neighbours(x, y, self.cols, self.rows):
                if self.grid[y][x].state == TileState.FLAGGED:
                    flagged_neighbours += 1
                elif self.grid[y][x].state != TileState.UNCOVERED:
                    unflagged_neighbours.append((x, y))

            if flagged_neighbours == tile.value:
                to_uncover.extend(unflagged_neighbours)

        else:
            to_uncover.append((x, y))

        while to_uncover:
            cur_x, cur_y = to_uncover.pop()
            cur_tile = self.grid[cur_y][cur_x]

            if cur_tile.state != TileState.UNCOVERED:
                self.__uncovered_tiles += 1
                cur_tile.state = TileState.UNCOVERED

            if cur_tile.is_mine:
                self.__game_state = GameState.LOST
                return

            if cur_tile.value == 0:
                for nx, ny in get_neighbours(cur_x, cur_y, self.cols, self.rows):
                    if self.grid[ny][nx].state in (
                        TileState.COVERED,
                        TileState.QUESTIONED,
                    ):
                        to_uncover.append((nx, ny))

        if self.__uncovered_tiles == (self.cols * self.rows) - self.mine_count:
            self.__game_state = GameState.WON
