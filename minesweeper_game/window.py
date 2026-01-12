import pygame

from .game import GameState, MinesweeperGame, Tile, TileState
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


def get_tile_texture_(tile: Tile, is_pressed: bool, game_state: GameState):
    match tile.state, is_pressed, tile.is_mine, game_state:
        case TileState.COVERED, True, _, GameState.RUNNING:
            return TEXTURES.TILES.V0
        case TileState.COVERED, _, True, GameState.LOST:
            return TEXTURES.TILES.PRESSED_MINE
        case TileState.COVERED, _, True, GameState.WON:
            return TEXTURES.TILES.FLAGGED
        case TileState.COVERED, _, _, _:
            return TEXTURES.TILES.COVERED

        case TileState.FLAGGED, _, False, GameState.LOST:
            return TEXTURES.TILES.FALSEMINE
        case TileState.FLAGGED, _, _, _:
            return TEXTURES.TILES.FLAGGED

        case TileState.QUESTIONED, True, _, GameState.RUNNING:
            return TEXTURES.TILES.PRESSED_QUESTION
        case TileState.QUESTIONED, _, True, GameState.LOST:
            return TEXTURES.TILES.PRESSED_MINE
        case TileState.QUESTIONED, _, True, GameState.LOST:
            return TEXTURES.TILES.FLAGGED
        case TileState.QUESTIONED, _, _, _:
            return TEXTURES.TILES.QUESTION

        case TileState.UNCOVERED, _, False, _:
            return TILE_VALUE_TEXTURES[tile.value]
        case TileState.UNCOVERED, _, True, GameState.LOST:
            return TEXTURES.TILES.BLOWN_MINE
        case TileState.UNCOVERED, _, True, GameState.RUNNING | GameState.WON:
            return TEXTURES.ERROR


def generate_grid_graphics_(
    grid: list[list[Tile]], pressed: tuple[int, int], game_state: GameState
):
    x_offset = (1) * TILE_WIDTH
    y_offset = (1 + 3 + 1) * TILE_WIDTH

    grid_graphics = []

    for i, row in enumerate(grid):
        for j, tile in enumerate(row):
            y = i * TILE_WIDTH + y_offset
            x = j * TILE_WIDTH + x_offset
            is_pressed = (j, i) == pressed

            txt = get_tile_texture_(tile, is_pressed, game_state)

            grid_graphics.append((txt, (x, y)))

    return grid_graphics


def get_face_texture_(
    game_state: GameState, any_tile_pressed: bool, face_pressed: bool
):
    match game_state, any_tile_pressed, face_pressed:
        case GameState.RUNNING, False, False:
            return TEXTURES.FACES.HAPPY
        case GameState.RUNNING, True, _:
            return TEXTURES.FACES.CAUTIOUS
        case _, _, True:
            return TEXTURES.FACES.PRESSED_HAPPY
        case GameState.LOST, _, False:
            return TEXTURES.FACES.DEAD
        case GameState.WON, _, False:
            return TEXTURES.FACES.WINNER


class MinesweeperWindow:
    def __init__(self, game: MinesweeperGame):
        self.game_ = game

        self.board_graphics_ = generate_board_graphics_(
            self.game_.cols, self.game_.rows
        )

        window_width = (1 + self.game_.cols + 1) * TILE_WIDTH
        window_height = (1 + 3 + 1 + self.game_.rows + 1) * TILE_WIDTH

        self.surface_ = pygame.display.set_mode((window_width, window_height))

        self.face_pos_ = (
            ((1 + self.game_.cols + 1) * TILE_WIDTH - 28) // 2,
            1 * TILE_WIDTH + 10,
        )

        self.clock_ = pygame.time.Clock()
        self.window_alive_ = True

        self.mouse_event_ = ((0, 0), -1)
        self.pressed_ = None
        self.pressed_face_ = False

        pygame.display.set_caption(WINDOW_CAPTION)

    def calculate_pressed_element_(
        self, pos
    ) -> tuple[tuple[int, int] | None, bool]:  # returns (pressed_tile, is_pressed_face)
        x, y = pos
        face_dx = x - self.face_pos_[0]
        face_dy = y - self.face_pos_[1]
        if face_dx >= 0 and face_dx < 28 and face_dy >= 0 and face_dy < 28:
            face_pressed = True
        else:
            face_pressed = False

        grid_x = (1) * TILE_WIDTH
        grid_y = (1 + 3 + 1) * TILE_WIDTH
        width = self.game_.cols * TILE_WIDTH
        height = self.game_.rows * TILE_WIDTH
        if x >= grid_x and x < grid_x + width and y >= grid_y and y < grid_y + height:
            tile_x = (x - grid_x) // TILE_WIDTH
            tile_y = (y - grid_y) // TILE_WIDTH
            return (tile_x, tile_y), face_pressed

        return (None), face_pressed

    def event_handler_(self, event):
        match event.type:
            case pygame.QUIT:
                self.window_alive_ = False

            case pygame.MOUSEBUTTONDOWN:
                pressed_result = self.calculate_pressed_element_(event.pos)
                self.mouse_event_ = (
                    pressed_result,
                    event.button,
                )

                pressed_tile, pressed_face = pressed_result
                if (
                    self.game_.state == GameState.RUNNING and event.button == 1
                ):  # if finished, only face is updated, the blown mine stays marked as pressed
                    self.pressed_ = pressed_tile
                self.pressed_face_ = pressed_face

            case pygame.MOUSEBUTTONUP:
                up_event = (self.calculate_pressed_element_(event.pos), event.button)

                if self.mouse_event_ == up_event:
                    pressed_result, button = self.mouse_event_
                    pressed_tile, pressed_face = pressed_result
                    if pressed_tile is not None:
                        match button:
                            case 1:
                                self.game_.uncover(*pressed_tile)
                            case 3:
                                self.game_.cycle_covered_state(*pressed_tile)

                    elif pressed_face:
                        pass  # TODO: Restart game

                self.pressed_ = None
                self.pressed_face_ = False

    def tick(self) -> bool:  # returns true if window is alive
        self.clock_.tick(FPS)
        for event in pygame.event.get():
            self.event_handler_(event)

        grid_graphics = generate_grid_graphics_(
            self.game_.grid, self.pressed_, self.game_.state
        )

        face_texture = get_face_texture_(
            self.game_.state, self.pressed_ is not None, self.pressed_face_
        )

        self.surface_.blits(self.board_graphics_, doreturn=False)
        self.surface_.blits(grid_graphics, doreturn=False)
        self.surface_.blit(face_texture, self.face_pos_)

        pygame.display.update()

        return self.window_alive_
