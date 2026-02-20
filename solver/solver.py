import random

import numpy as np

from game.game import GameState, MinesweeperGame
from game.utils import print_grid

from .frontier import generate_frontier
from .grid import get_revealed_grid, get_value_grid
from .neighbours import get_all_neighbours, get_revealed_neighbours


class MinesweeperSolver:
    def __init__(self, game: MinesweeperGame):
        self.__game = game
        self.__rows = self.__game.rows
        self.__cols = self.__game.cols

        self.__revealed = np.zeros((self.__rows, self.__cols), np.bool_)
        self.__values = np.full((self.__rows, self.__cols), -1, np.int8)

        self.__all_neighbours = get_all_neighbours(self.__rows, self.__cols)
        self.__revealed_neighbours = self.__all_neighbours.copy()
        self.__frontier_revealed = []
        self.__frontier_covered = []

    @property
    def finished(self):
        return self.__game.state != GameState.RUNNING

    def update_data(self):
        self.__revealed = get_revealed_grid(self.__game.grid)
        self.__values = get_value_grid(self.__game.grid)

        self.__revealed_neighbours = get_revealed_neighbours(self.__revealed)

        self.__frontier_revealed, self.__frontier_covered = generate_frontier(
            self.__revealed
        )

    def make_move(self):
        self.update_data()

    def print_grid(self):
        print_grid(self.__game.grid)
