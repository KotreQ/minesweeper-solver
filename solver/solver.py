import random

import numpy as np

from game.game import GameState, MinesweeperGame
from game.utils import print_grid

from .frontier import generate_frontier
from .grid import get_revealed_grid, get_value_grid
from .neighbours import (
    get_all_neighbours,
    get_key_neighbours,
    get_neighbours_coords,
)


class MinesweeperSolver:
    def __init__(self, game: MinesweeperGame):
        self.__game = game
        self.__rows = self.__game.rows
        self.__cols = self.__game.cols

        self.__revealed = np.zeros((self.__rows, self.__cols), np.bool_)
        self.__flagged = np.zeros((self.__rows, self.__cols), np.bool_)
        self.__values = np.full((self.__rows, self.__cols), -1, np.int8)

        self.__all_neighbours = get_all_neighbours(self.__rows, self.__cols)
        self.__revealed_neighbours = np.zeros((self.__rows, self.__cols), np.uint8)
        self.__flagged_neighbours = np.zeros((self.__rows, self.__cols), np.uint8)
        self.__frontier_revealed = []
        self.__frontier_covered = []

    @property
    def finished(self):
        return self.__game.state != GameState.RUNNING

    def update_data(self):
        self.__revealed = get_revealed_grid(self.__game.grid)
        self.__values = get_value_grid(self.__game.grid)

        self.__revealed_neighbours = get_key_neighbours(self.__revealed)
        self.__flagged_neighbours = get_key_neighbours(self.__flagged)

        self.__frontier_revealed, self.__frontier_covered = generate_frontier(
            self.__revealed
        )
        self.__frontier_covered = list(
            filter(lambda p: not self.__flagged[p[1]][p[0]], self.__frontier_covered)
        )

    def make_move(self):
        self.update_data()

        move_made = False

        for x, y in self.__frontier_revealed:
            covered_neighbours = (
                self.__all_neighbours[y][x] - self.__revealed_neighbours[y][x]
            )

            if covered_neighbours == self.__values[y][x]:
                for nx, ny in get_neighbours_coords(x, y, self.__rows, self.__cols):
                    if not self.__revealed[ny][nx] and not self.__flagged[ny][nx]:
                        self.__game.place_flag(nx, ny)
                        self.__flagged[ny][nx] = True
                        move_made = True

            if self.__flagged_neighbours[y][x] == self.__values[y][x]:
                for nx, ny in get_neighbours_coords(x, y, self.__rows, self.__cols):
                    if not self.__revealed[ny][nx] and not self.__flagged[ny][nx]:
                        self.__game.uncover(nx, ny)
                        move_made = True

        if move_made:
            return

        while not move_made:
            y = random.randrange(self.__rows)
            x = random.randrange(self.__cols)

            if not self.__revealed[y][x] and not self.__flagged[y][x]:
                self.__game.uncover(x, y)
                move_made = True

    def print_grid(self):
        print_grid(self.__game.grid)
