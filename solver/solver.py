import random

from game.game import GameState, MinesweeperGame
from game.utils import print_grid
from solver.uncovered import get_uncovered_grid

from .frontier import generate_frontier
from .neighbours import get_all_neighbours, get_uncovered_neighbours


class MinesweeperSolver:
    def __init__(self, game: MinesweeperGame):
        self.__game = game
        self.__rows = self.__game.rows
        self.__cols = self.__game.cols

        self.__unknown = set(
            (x, y) for y in range(self.__rows) for x in range(self.__cols)
        )
        self.__frontier_revealed = []
        self.__frontier_covered = []
        self.__all_neighbours = get_all_neighbours(self.__rows, self.__cols)
        self.__uncovered_neighbours = self.__all_neighbours.copy()

    @property
    def finished(self):
        return self.__game.state != GameState.RUNNING

    def update_data(self):
        self.__uncovered = get_uncovered_grid(self.__game.grid)

        self.__frontier_revealed, self.__frontier_covered = generate_frontier(
            self.__uncovered
        )

        revealed = set()
        for x, y in self.__unknown:
            if self.__uncovered[y][x]:
                revealed.add((x, y))

        self.__unknown -= revealed

        self.__uncovered_neighbours = get_uncovered_neighbours(self.__uncovered)

    def make_move(self):
        self.update_data()

        if self.__frontier_covered:
            x, y = random.choice(self.__frontier_covered)
            self.__unknown.remove((x, y))
        else:
            x, y = self.__unknown.pop()

        self.__game.uncover(x, y)

    def print_grid(self):
        print_grid(self.__game.grid)
