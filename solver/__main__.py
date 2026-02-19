from game import MinesweeperGame

from . import MinesweeperSolver

COLS = 30
ROWS = 16
MINES = 99


def main() -> None:
    game = MinesweeperGame(COLS, ROWS, MINES)

    solver = MinesweeperSolver(game)


if __name__ == "__main__":
    main()
