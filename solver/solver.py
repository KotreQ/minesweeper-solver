import numpy as np

from game.game import GameState, MinesweeperGame
from game.utils import print_grid

from .grid import update_numpy_grid, cell_dtype
from .constraints import get_constraints, optimize_constraints
from .solutions import find_constraints_solutions
from .probability import calculate_probabilities


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
            if len(c.variables) == 1:
                y, x = list(c.variables)[0]
                if c.value:
                    self.__game.place_flag(x, y)
                else:
                    self.__game.uncover(x, y)
                move_made = True

        if move_made:
            return

        solutions = find_constraints_solutions(constraints)

        mines_left = self.__game.mine_count - self.__game.flags_placed

        probabilities = calculate_probabilities(self.__grid, solutions, mines_left)

        prob, var = probabilities[0]
        self.__game.uncover(var[1], var[0])

    def print_grid(self):
        print_grid(self.__game.grid)
