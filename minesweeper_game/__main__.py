import pygame

from .window import MinesweeperWindow

COLS = 30
ROWS = 16
MINES = 99


def main() -> None:
    pygame.init()

    window = MinesweeperWindow((COLS, ROWS, MINES))

    running = True
    while running:
        running = window.tick()

    pygame.quit()


if __name__ == "__main__":
    main()
