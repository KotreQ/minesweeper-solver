from typing import NamedTuple

import numpy as np

from game.game import GameState, MinesweeperGame
from game.utils import print_grid

from .grid import update_numpy_grid, cell_dtype
from .constraints import get_constraints, optimize_constraints
from .solutions import find_constraints_solutions
from .probability import calculate_probabilities


class SolverAnalysis(NamedTuple):
    """Result of analyzing the board.

    Exactly one of the fields is set:

    - sure_tiles: `(is_mine, (y, x))` pairs for tiles determined with certainty by
      constraint optimization. Mines should be flagged, safe tiles uncovered.
    - probabilities: `(probability, (y, x))` pairs for all unknown tiles, sorted
      from the least to the most likely to contain a mine.
    """

    sure_tiles: list[tuple[bool, tuple[int, int]]] | None
    probabilities: list[tuple[float, tuple[int, int]]] | None


class MinesweeperSolver:
    def __init__(self, game: MinesweeperGame):
        self.__game = game
        self.__rows = self.__game.rows
        self.__cols = self.__game.cols

        self.__grid = np.empty((self.__rows, self.__cols), dtype=cell_dtype)

        self.__risk_taken = 0

    @property
    def finished(self):
        return self.__game.state != GameState.RUNNING

    def update_data(self):
        update_numpy_grid(self.__grid, self.__game.grid)

    def analyze(self) -> SolverAnalysis:
        """Analyzes the current board state.

        If constraint optimization finds tiles that are certainly mines or certainly
        safe, returns them in `SolverAnalysis.sure_tiles`. Otherwise returns
        `SolverAnalysis.probabilities` for all unknown tiles.

        Raises:
            RuntimeError: if the constraints are unsatisfiable, e.g. because of an
                incorrectly placed flag.
        """
        self.update_data()

        constraints = get_constraints(self.__grid)

        constraints, sat = optimize_constraints(constraints)
        if not sat:
            raise RuntimeError("Found constraints are unsatisfiable")

        sure_tiles = [
            (bool(c.value), next(iter(c.variables)))
            for c in constraints
            if len(c.variables) == 1
        ]
        if sure_tiles:
            return SolverAnalysis(sure_tiles, None)

        solutions = find_constraints_solutions(constraints)

        mines_left = self.__game.mine_count - self.__game.flags_placed

        probabilities = calculate_probabilities(self.__grid, solutions, mines_left)

        return SolverAnalysis(None, probabilities)

    def make_move(self):
        is_first_move = self.__game.revealed_tiles == 0

        analysis = self.analyze()

        if analysis.sure_tiles is not None:
            for is_mine, (y, x) in analysis.sure_tiles:
                if is_mine:
                    self.__game.place_flag(x, y)
                else:
                    self.__game.uncover(x, y)
            return

        prob, var = analysis.probabilities[0]
        self.__game.uncover(var[1], var[0])

        if not is_first_move:
            self.__risk_taken += (1-self.__risk_taken) * prob

    @property
    def risk_taken(self):
        return self.__risk_taken

    def print_grid(self):
        print_grid(self.__game.grid)
