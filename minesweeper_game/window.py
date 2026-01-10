import pygame

from .game import MinesweeperGame, Tile, TileState
from .textures import TEXTURES

WINDOW_CAPTION = "Minesweeper by KotreQ"
FPS = 60
TILE_WIDTH = 16


def generate_board_graphics_(cols: int, rows: int):
    tile_rows = 1 + 3 + 1 + rows + 1
    tile_cols = 1 + cols + 1
    horizontal_rows = [0, 4, tile_rows - 1]
    vertical_cols = [0, tile_cols - 1]

    board_graphics = []

    for row in range(tile_rows):
        for col in range(tile_cols):
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

            board_graphics.append((txt, (col * TILE_WIDTH, row * TILE_WIDTH)))

    return board_graphics


TILE_VALUE_TEXTURES = [
    TEXTURES.TILES.V0,
    TEXTURES.TILES.V1,
    TEXTURES.TILES.V2,
    TEXTURES.TILES.V3,
    TEXTURES.TILES.V4,
    TEXTURES.TILES.V5,
    TEXTURES.TILES.V6,
    TEXTURES.TILES.V7,
    TEXTURES.TILES.V8,
]


def get_tile_texture_(tile: Tile, is_pressed: bool):
    match tile.state, is_pressed:
        case TileState.COVERED, False:
            return TEXTURES.TILES.COVERED
        case TileState.COVERED, True:
            return TEXTURES.TILES.V0
        case TileState.FLAGGED, _:
            return TEXTURES.TILES.FLAGGED
        case TileState.QUESTIONED, False:
            return TEXTURES.TILES.QUESTION
        case TileState.QUESTIONED, True:
            return TEXTURES.TILES.PRESSED_QUESTION
        case (
            TileState.UNCOVERED,
            False,
        ) if tile.is_mine:
            return TEXTURES.TILES.PRESSED_MINE
        case (
            TileState.UNCOVERED,
            True,
        ) if tile.is_mine:
            return TEXTURES.TILES.BLOWN_MINE
        case TileState.UNCOVERED, _ if not tile.is_mine:
            return TILE_VALUE_TEXTURES[tile.value]


def generate_grid_graphics_(
    grid: list[list[Tile]], pressed: tuple[int, int] | None = None
):
    x_offset = (1) * TILE_WIDTH
    y_offset = (1 + 3 + 1) * TILE_WIDTH

    grid_graphics = []

    for i, row in enumerate(grid):
        for j, tile in enumerate(row):
            y = i * TILE_WIDTH + y_offset
            x = j * TILE_WIDTH + x_offset
            is_pressed = (i, j) == pressed

            txt = get_tile_texture_(tile, is_pressed)

            grid_graphics.append((txt, (x, y)))

    return grid_graphics


class MinesweeperWindow:
    def __init__(self, game: MinesweeperGame):
        self.game_ = game

        self.board_graphics_ = generate_board_graphics_(
            self.game_.cols, self.game_.rows
        )

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

        grid_graphics = generate_grid_graphics_(self.game_.grid)

        self.surface_.blits(self.board_graphics_, doreturn=False)
        self.surface_.blits(grid_graphics, doreturn=False)

        pygame.display.update()

        return self.running_
