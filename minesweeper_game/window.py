import pygame

from .game import MinesweeperGame
from .textures import TEXTURES

WINDOW_CAPTION = "Minesweeper by KotreQ"
FPS = 60
TILE_WIDTH = 16


def generate_board_textures_(cols, rows):
    texture_rows = 1 + 3 + 1 + rows + 1
    texture_cols = 1 + cols + 1
    horizontal_rows = [0, 4, texture_rows - 1]
    vertical_cols = [0, texture_cols - 1]

    board_textures = []

    for row in range(texture_rows):
        for col in range(texture_cols):
            txt = TEXTURES.BORDER.FILL

            if row in horizontal_rows and col in vertical_cols:
                corner_x = vertical_cols.index(col)
                corner_y = horizontal_rows.index(row)

                match corner_x, corner_y:
                    case 0, 0:
                        txt = TEXTURES.BORDER.BR
                    case 0, 1:
                        txt = TEXTURES.BORDER.TBR
                    case 0, 2:
                        txt = TEXTURES.BORDER.TR
                    case 1, 0:
                        txt = TEXTURES.BORDER.BL
                    case 1, 1:
                        txt = TEXTURES.BORDER.TBL
                    case 1, 2:
                        txt = TEXTURES.BORDER.TL

            elif row in horizontal_rows:
                txt = TEXTURES.BORDER.LR
            elif col in vertical_cols:
                txt = TEXTURES.BORDER.TB
            else:
                txt = TEXTURES.BORDER.FILL

            board_textures.append((txt, (col * TILE_WIDTH, row * TILE_WIDTH)))

    return board_textures


class MinesweeperWindow:
    def __init__(self, game: MinesweeperGame):
        self.game_ = game

        self.board_texture_ = generate_board_textures_(self.game_.cols, self.game_.rows)

        window_width = (1 + self.game_.cols + 1) * TILE_WIDTH
        window_height = (1 + 3 + 1 + self.game_.rows + 1) * TILE_WIDTH

        self.surface_ = pygame.display.set_mode((window_width, window_height))

        self.clock_ = pygame.time.Clock()
        self.running_ = True

        pygame.display.set_caption(WINDOW_CAPTION)

    def event_handler_(self, event):
        if event.type == pygame.QUIT:
            self.running_ = False
            return

        # press_event: (pressing a button cancels previous unpressed event if there was one -> just replace variables)
        # 	pressed = event.x, event.y
        # 	press_button = event.btn (if right -> no animation)

        # release_event:
        # 	unpressed = event.x, event.y
        # 	unpress_button = event.btn

        # 	if pressed == unpressed and press_button == unpress_button:
        # 		pressed.action(press_button)

    def tick(self) -> bool:  # returns true if window is alive
        self.clock_.tick(FPS)
        for event in pygame.event.get():
            self.event_handler_(event)

        self.surface_.blits(self.board_texture_, doreturn=False)

        pygame.display.update()

        return self.running_
