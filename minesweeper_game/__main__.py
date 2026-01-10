import pygame

from .window import MinesweeperWindow
from .game import MinesweeperGame

ROWS = 16
COLS = 16
MINES = 40

SAFE_START_NEIGHBOURS = False  # make all neighbours of starting tile safe?


def main() -> None:
    pygame.init()

    game = MinesweeperGame(30, 16, 99)
    window = MinesweeperWindow(game)

    running = True
    while running:
        running = window.tick()

    pygame.quit()


if __name__ == "__main__":
    main()
