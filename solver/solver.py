import random

import numpy as np

from game.game import GameState, MinesweeperGame
from game.utils import print_grid

from .grid import update_numpy_grid, cell_dtype
from .constraints import get_constraints, optimize_constraints
from .solutions import find_constraints_solutions


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

        move_made = False

        constraints = get_constraints(self.__grid)

        constraints = optimize_constraints(constraints)

        for c in constraints:
            if len(c.indices) == 1:
                y, x = list(c.indices)[0]
                if c.value:
                    self.__game.place_flag(x, y)
                else:
                    self.__game.uncover(x, y)
                move_made = True

        if move_made:
            return

        solutions = find_constraints_solutions(constraints)

        while True:
            y = random.randrange(self.__rows)
            x = random.randrange(self.__cols)
            if not self.__grid[y, x]["is_revealed"] and not self.__grid[y, x]["is_flagged"]:
                self.__game.uncover(x, y)
                break

    def print_grid(self):
        print_grid(self.__game.grid)
