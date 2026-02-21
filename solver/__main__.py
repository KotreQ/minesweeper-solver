import time

import numpy as np

from game.game import GameState, MinesweeperGame

from .solver import MinesweeperSolver
from .utils.cli import clear_console

COLS = 16
ROWS = 16
MINES = 40


def main() -> None:

    ### TEST

    clear_console()

    TEST_COUNT = 100
    test_times = np.zeros((TEST_COUNT), np.float64)
    test_results = np.zeros((TEST_COUNT), np.bool_)
    for i in range(TEST_COUNT):
        test_game = MinesweeperGame(COLS, ROWS, MINES)
        test_solver = MinesweeperSolver(test_game)

        test_start = time.time()
        while not test_solver.finished:
            test_solver.make_move()
        test_time = time.time() - test_start
        test_times[i] = test_time * 1000  # in ms
        test_results[i] = test_game.state == GameState.WON

        print(f"\rTESTING: {(i + 1) / TEST_COUNT * 100:.1f}%", end="")
    print("")

    clear_console()

    win_count = np.count_nonzero(test_results)

    print(f"Win rate: {win_count / TEST_COUNT * 100:.1f}%")
    if win_count != 0:
        print(f"Median win time: {np.median(test_times[test_results]):.1f}ms")
    else:
        print("No win data")
    if win_count != TEST_COUNT:
        print(f"Median loss time: {np.median(test_times[~test_results]):.1f}ms")
    else:
        print("No loss data")

    print("")
    print("Running demo...")
    time.sleep(5)

    ### DEMO

    game = MinesweeperGame(COLS, ROWS, MINES)

    solver = MinesweeperSolver(game)

    while not solver.finished:
        time.sleep(0.2)
        solver.make_move()
        clear_console()
        solver.print_grid()
        print(f"Game state: {game.state.name}")


if __name__ == "__main__":
    main()
