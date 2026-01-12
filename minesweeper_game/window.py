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
    def __init__(self, cols, rows, mine_count):
        self.__cols = cols
        self.__rows = rows
        self.__mine_count = mine_count

        self.__init_game()

        self.__clock = pygame.time.Clock()
        self.__window_alive = True

        self.__mouse_event = ((0, 0), -1)
        self.__pressed = None
        self.__pressed_face = False

    def __init_game(self):
        self.__game = MinesweeperGame(self.__cols, self.__rows, self.__mine_count)

        self.__board_graphics = generate_board_graphics_(
            self.__game.cols, self.__game.rows
        )

        window_width = (1 + self.__game.cols + 1) * TILE_WIDTH
        window_height = (1 + 3 + 1 + self.__game.rows + 1) * TILE_WIDTH

        self.__surface = pygame.display.set_mode((window_width, window_height))

        self.__face_pos = (
            ((1 + self.__game.cols + 1) * TILE_WIDTH - 28) // 2,
            1 * TILE_WIDTH + 10,
        )

        pygame.display.set_caption(WINDOW_CAPTION)

    def __calculate_pressed_element(
        self, pos
    ) -> tuple[tuple[int, int] | None, bool]:  # returns (pressed_tile, is_pressed_face)
        x, y = pos
        face_dx = x - self.__face_pos[0]
        face_dy = y - self.__face_pos[1]
        if face_dx >= 0 and face_dx < 28 and face_dy >= 0 and face_dy < 28:
            face_pressed = True
        else:
            face_pressed = False

        grid_x = (1) * TILE_WIDTH
        grid_y = (1 + 3 + 1) * TILE_WIDTH
        width = self.__game.cols * TILE_WIDTH
        height = self.__game.rows * TILE_WIDTH
        if x >= grid_x and x < grid_x + width and y >= grid_y and y < grid_y + height:
            tile_x = (x - grid_x) // TILE_WIDTH
            tile_y = (y - grid_y) // TILE_WIDTH
            return (tile_x, tile_y), face_pressed

        return (None), face_pressed

    def __event_handler(self, event):
        match event.type:
            case pygame.QUIT:
                self.__window_alive = False

            case pygame.MOUSEBUTTONDOWN:
                pressed_result = self.__calculate_pressed_element(event.pos)
                self.__mouse_event = (
                    pressed_result,
                    event.button,
                )

                pressed_tile, pressed_face = pressed_result
                if (
                    self.__game.state == GameState.RUNNING and event.button == 1
                ):  # if finished, only face is updated, the blown mine stays marked as pressed
                    self.__pressed = pressed_tile
                self.__pressed_face = pressed_face

            case pygame.MOUSEBUTTONUP:
                up_event = (self.__calculate_pressed_element(event.pos), event.button)

                if self.__mouse_event == up_event:
                    pressed_result, button = self.__mouse_event
                    pressed_tile, pressed_face = pressed_result
                    if pressed_tile is not None:
                        match button:
                            case 1:
                                self.__game.uncover(*pressed_tile)
                            case 3:
                                self.__game.cycle_covered_state(*pressed_tile)

                    elif pressed_face:
                        self.__init_game()

                self.__pressed = None
                self.__pressed_face = False

    def tick(self) -> bool:  # returns true if window is alive
        self.__clock.tick(FPS)
        for event in pygame.event.get():
            self.__event_handler(event)

        grid_graphics = generate_grid_graphics_(
            self.__game.grid, self.__pressed, self.__game.state
        )

        face_texture = get_face_texture_(
            self.__game.state, self.__pressed is not None, self.__pressed_face
        )

        self.__surface.blits(self.__board_graphics, doreturn=False)
        self.__surface.blits(grid_graphics, doreturn=False)
        self.__surface.blit(face_texture, self.__face_pos)

        pygame.display.update()

        return self.__window_alive
