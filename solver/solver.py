from pprint import pprint
import random

import numpy as np

from game.game import GameState, MinesweeperGame
from game.utils import print_grid

from .grid import update_numpy_grid, cell_dtype
from .constraints import get_constraints


class MinesweeperSolver:
    def __init__(self, game: MinesweeperGame):
        self.__game = game
        self.__rows = self.__game.rows
        self.__cols = self.__game.cols

        self.__grid = np.empty((self.__rows, self.__cols), dtype=cell_dtype)

    @property
    def finished(self):
        return self.__game.state != GameState.RUNNING

    def update_data(self):
        update_numpy_grid(self.__grid, self.__game.grid)

    def make_move(self):
        self.update_data()

        constraints = get_constraints(self.__grid)

        pprint(constraints)

        self.__game.uncover(random.randrange(self.__cols), random.randrange(self.__rows))


    def print_grid(self):
        print_grid(self.__game.grid)
