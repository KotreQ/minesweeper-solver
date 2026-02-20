import time

from game.game import GameState, MinesweeperGame

from .solver import MinesweeperSolver

COLS = 10
ROWS = 10
MINES = 10


def main() -> None:

    ### TEST

    print("TEST")
    test_results = [0, 0]
    for i in range(1000):
        test_game = MinesweeperGame(COLS, ROWS, MINES)
        test_solver = MinesweeperSolver(test_game)

        while not test_solver.finished:
            test_solver.make_move()

        if test_game.state == GameState.WON:
            test_results[1] += 1
        else:
            test_results[0] += 1

        print(f"WON {test_results[1]}:{test_results[0]} LOST", end="\r")
    print("")

    print("Waiting for demo...")
    time.sleep(3)

    ### DEMO

    game = MinesweeperGame(COLS, ROWS, MINES)

    solver = MinesweeperSolver(game)

    while not solver.finished:
        time.sleep(0.5)
        solver.make_move()
        solver.print_grid()


if __name__ == "__main__":
    main()
