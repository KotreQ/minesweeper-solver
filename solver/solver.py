from game.game import GameState, MinesweeperGame
from game.utils import print_grid

from .frontier import generate_frontier


class MinesweeperSolver:
    def __init__(self, game: MinesweeperGame):
        self.__game = game
        self.__rows = self.__game.rows
        self.__cols = self.__game.cols

        self.__done = set()
        self.__unknown = set(
            (x, y) for y in range(self.__rows) for x in range(self.__cols)
        )
        self.__frontier_revealed = []
        self.__frontier_covered = []

    @property
    def finished(self):
        return self.__game.state != GameState.RUNNING

    def update_data(self):
        self.__frontier_revealed, self.__frontier_covered = generate_frontier(
            self.__game.grid, self.__rows, self.__cols
        )

    def make_move(self):
        self.update_data()
        x, y = self.__unknown.pop()

        self.__game.uncover(x, y)

        self.__done.add((x, y))

    def print_grid(self):
        print_grid(self.__game.grid)
