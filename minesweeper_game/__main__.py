import pygame

from .game import MinesweeperGame
from .window import MinesweeperWindow

ROWS = 16
COLS = 16
MINES = 40


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
