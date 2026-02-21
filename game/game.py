import random
import time
from collections import deque
from enum import Enum, auto

from .tile import Tile, TileState
from .utils import get_neighbours


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

        self.__cols = cols
        self.__rows = rows
        self.__mine_count = mine_count
        self.grid: list[list[Tile]] = [
            [Tile() for _ in range(self.__cols)] for _ in range(self.__rows)
        ]
        self.__mines_placed = False

        self.__time_started = None
        self.__time_frozen = None

        self.__game_state = GameState.RUNNING

        self.__revealed_tiles = 0
        self.__flags_placed = 0

    @property
    def state(self):
        return self.__game_state

    @property
    def revealed_tiles(self):
        return self.__revealed_tiles

    @property
    def flags_placed(self):
        return self.__flags_placed

    @property
    def cols(self):
        return self.__cols

    @property
    def rows(self):
        return self.__rows

    @property
    def mine_count(self):
        return self.__mine_count

    @property
    def elapsed_time(self):
        if self.__time_frozen is not None:
            return self.__time_frozen
        if self.__time_started is None:
            return 0
        return time.time() - self.__time_started

    def __place_mine(self, x, y):
        success = self.grid[y][x]._mark_mine()
        if not success:
            raise ValueError(f"Mine is already at ({x},{y})")

        for nx, ny in get_neighbours(x, y, self.__cols, self.__rows):
            self.grid[ny][nx]._increase_value()

        return True

    def __place_mines(self, safe_spots=[]):
        safe_spots = set(safe_spots)
        potential_spots = [
            (x, y)
            for x in range(self.__cols)
            for y in range(self.__rows)
            if (x, y) not in safe_spots
        ]
        mine_spots = random.sample(potential_spots, self.__mine_count)

        for x, y in mine_spots:
            self.__place_mine(x, y)

    def toggle_flag(self, x, y):
        if self.__game_state != GameState.RUNNING:
            return

        state = self.grid[y][x].state

        if state == TileState.COVERED:
            self.place_flag(x, y)
        elif state == TileState.FLAGGED:
            self.remove_flag(x, y)

    def place_flag(self, x, y):
        if self.__game_state != GameState.RUNNING:
            return
        
        tile = self.grid[y][x]
        if tile.place_flag():
            self.__flags_placed += 1
    
    def remove_flag(self, x, y):
        if self.__game_state != GameState.RUNNING:
            return
        
        tile = self.grid[y][x]
        if tile.remove_flag():
            self.__flags_placed -= 1

    def uncover(self, x, y):
        if self.__game_state != GameState.RUNNING:
            return

        tile = self.grid[y][x]

        if tile.state == TileState.FLAGGED:
            return

        if not self.__mines_placed:
            self.__place_mines([(x, y)])
            self.__mines_placed = True

        if self.__time_started is None:
            self.__time_started = time.time()

        to_uncover = deque()

        if tile.is_revealed:  # try making a chord
            covered_neighbours = []
            flagged_neighbours = 0
            for x, y in get_neighbours(x, y, self.__cols, self.__rows):
                if self.grid[y][x].state == TileState.FLAGGED:
                    flagged_neighbours += 1
                elif self.grid[y][x].state == TileState.COVERED:
                    covered_neighbours.append((x, y))

            if flagged_neighbours == tile.value:
                to_uncover.extend(covered_neighbours)

        else:
            to_uncover.append((x, y))

        while to_uncover:
            cur_x, cur_y = to_uncover.pop()
            cur_tile = self.grid[cur_y][cur_x]

            success = cur_tile.uncover()

            if success:
                self.__revealed_tiles += 1

            if cur_tile.state == TileState.BLOWN_MINE:
                self.__mark_game_finished(False)
                return

            if cur_tile.state == TileState.SAFE_0:
                for nx, ny in get_neighbours(cur_x, cur_y, self.__cols, self.__rows):
                    if self.grid[ny][nx].state == TileState.COVERED:
                        to_uncover.append((nx, ny))

        if self.__revealed_tiles == (self.__cols * self.__rows) - self.__mine_count:
            self.__mark_game_finished(True)
            return

    def __mark_game_finished(self, won: bool):
        self.__time_frozen = self.elapsed_time

        if won:
            self.__flags_placed = self.__mine_count
            self.__game_state = GameState.WON
        else:
            self.__game_state = GameState.LOST

        for y in range(self.__rows):
            for x in range(self.__cols):
                tile = self.grid[y][x]
                tile._mark_finished_game(won)
