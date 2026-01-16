import pygame

from .game.game import GameState, MinesweeperGame
from .game.tile import Tile, TileState
from .game.utils import get_neighbours
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
            txt = TEXTURES["border"]["fill"]

            if row in horizontal_rows and col in vertical_cols:
                corner_x = vertical_cols.index(col)
                corner_y = horizontal_rows.index(row)

                match corner_x, corner_y:
                    case 0, 0:
                        txt = TEXTURES["border"]["br"]
                    case 0, 1:
                        txt = TEXTURES["border"]["tbr"]
                    case 0, 2:
                        txt = TEXTURES["border"]["tr"]
                    case 1, 0:
                        txt = TEXTURES["border"]["bl"]
                    case 1, 1:
                        txt = TEXTURES["border"]["tbl"]
                    case 1, 2:
                        txt = TEXTURES["border"]["tl"]

            elif row in horizontal_rows:
                txt = TEXTURES["border"]["lr"]
            elif col in vertical_cols:
                txt = TEXTURES["border"]["tb"]
            else:
                txt = TEXTURES["border"]["fill"]

            board_graphics.append((txt, (col * TILE_WIDTH, row * TILE_WIDTH)))

    return board_graphics


def get_tile_texture_(tile: Tile, is_pressed: bool, game_state: GameState) -> str:
    match tile.state, is_pressed, tile.is_mine, game_state:
        case TileState.COVERED, True, _, GameState.RUNNING:
            return TEXTURES["tiles"]["0"]
        case TileState.COVERED, _, True, GameState.LOST:
            return TEXTURES["tiles"]["mine"]
        case TileState.COVERED, _, True, GameState.WON:
            return TEXTURES["tiles"]["flagged"]
        case TileState.COVERED, _, _, _:
            return TEXTURES["tiles"]["covered"]

        case TileState.FLAGGED, _, False, GameState.LOST:
            return TEXTURES["tiles"]["false_mine"]
        case TileState.FLAGGED, _, _, _:
            return TEXTURES["tiles"]["flagged"]

        case TileState.UNCOVERED, _, False, _:
            return TEXTURES["tiles"][str(tile.value)]
        case TileState.UNCOVERED, _, True, GameState.LOST:
            return TEXTURES["tiles"]["blown_mine"]


def generate_grid_graphics_(
    grid: list[list[Tile]], pressed: set[tuple[int, int]], game_state: GameState
):
    x_offset = (1) * TILE_WIDTH
    y_offset = (1 + 3 + 1) * TILE_WIDTH

    grid_graphics = []

    for i, row in enumerate(grid):
        for j, tile in enumerate(row):
            y = i * TILE_WIDTH + y_offset
            x = j * TILE_WIDTH + x_offset
            is_pressed = (j, i) in pressed

            txt = get_tile_texture_(tile, is_pressed, game_state)

            grid_graphics.append((txt, (x, y)))

    return grid_graphics


def get_face_texture_(
    game_state: GameState, any_tile_pressed: bool, face_pressed: bool
):
    match game_state, any_tile_pressed, face_pressed:
        case GameState.RUNNING, False, False:
            return TEXTURES["faces"]["happy"]
        case GameState.RUNNING, True, _:
            return TEXTURES["faces"]["cautious"]
        case _, _, True:
            return TEXTURES["faces"]["pressed"]
        case GameState.LOST, _, False:
            return TEXTURES["faces"]["dead"]
        case GameState.WON, _, False:
            return TEXTURES["faces"]["winner"]


COUNTER_TEXTURES = [
    TEXTURES["counter"]["0"],
    TEXTURES["counter"]["1"],
    TEXTURES["counter"]["2"],
    TEXTURES["counter"]["3"],
    TEXTURES["counter"]["4"],
    TEXTURES["counter"]["5"],
    TEXTURES["counter"]["6"],
    TEXTURES["counter"]["7"],
    TEXTURES["counter"]["8"],
    TEXTURES["counter"]["9"],
    TEXTURES["counter"]["minus"],
]


def get_counter_graphics(offset: tuple[int, int], value: int):
    assert -99 <= value <= 999

    x_offset, y_offset = offset
    chars = [0, 0, 0]

    if value < 0:
        value = -value
        chars[0] = 10  # minus

    pos = 2
    while value:
        chars[pos] = value % 10
        value //= 10
        pos -= 1

    counter_graphics = []

    for i in range(3):
        pos = x_offset + i * TILE_WIDTH, y_offset
        txt = COUNTER_TEXTURES[chars[i]]
        counter_graphics.append((txt, pos))

    return counter_graphics


def get_counter_border_graphics(counter_offset: tuple[int, int]):
    x_offset, y_offset = counter_offset

    border_width = TILE_WIDTH // 2

    counter_border_graphics = []

    counter_border_graphics.append(
        (
            TEXTURES["counter_border"]["left"],
            (x_offset - border_width, y_offset + border_width),
        )
    )
    counter_border_graphics.append(
        (
            TEXTURES["counter_border"]["right"],
            (x_offset - border_width + 3 * TILE_WIDTH, y_offset + border_width),
        )
    )

    for col in range(2):
        counter_border_graphics.append(
            (
                TEXTURES["counter_border"]["top"],
                (x_offset + border_width + col * TILE_WIDTH, y_offset - border_width),
            )
        )
        counter_border_graphics.append(
            (
                TEXTURES["counter_border"]["bottom"],
                (
                    x_offset + border_width + col * TILE_WIDTH,
                    y_offset - border_width + 2 * TILE_WIDTH,
                ),
            )
        )

    counter_border_graphics.append(
        (
            TEXTURES["counter_border"]["top_left"],
            (
                x_offset - border_width,
                y_offset - border_width,
            ),
        )
    )
    counter_border_graphics.append(
        (
            TEXTURES["counter_border"]["top_right"],
            (
                x_offset - border_width + 3 * TILE_WIDTH,
                y_offset - border_width,
            ),
        )
    )
    counter_border_graphics.append(
        (
            TEXTURES["counter_border"]["bottom_left"],
            (
                x_offset - border_width,
                y_offset - border_width + 2 * TILE_WIDTH,
            ),
        )
    )
    counter_border_graphics.append(
        (
            TEXTURES["counter_border"]["bottom_right"],
            (
                x_offset - border_width + 3 * TILE_WIDTH,
                y_offset - border_width + 2 * TILE_WIDTH,
            ),
        )
    )

    return counter_border_graphics


class MinesweeperWindow:
    def __init__(self, cols, rows, mine_count):
        self.__cols = cols
        self.__rows = rows
        self.__mine_count = mine_count

        self.__init_game()

        self.__clock = pygame.time.Clock()
        self.__window_alive = True

        self.__mouse_event = ((0, 0), -1)
        self.__pressed = set()
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

        self.__mine_counter_pos = (TILE_WIDTH * 3 // 2, TILE_WIDTH * 3 // 2)
        self.__time_counter_pos = (
            window_width - TILE_WIDTH * 3 // 2 - TILE_WIDTH * 3,
            TILE_WIDTH * 3 // 2,
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
                    self.__game.state == GameState.RUNNING
                    and event.button == 1
                    and pressed_tile is not None
                ):  # if finished, only face is updated, the blown mine stays marked as pressed
                    self.__pressed.add(pressed_tile)

                    # if pressed uncovered tile, highlight neighbours as pressed
                    x, y = pressed_tile
                    if self.__game.grid[y][x].state == TileState.UNCOVERED:
                        for x, y in get_neighbours(x, y, self.__cols, self.__rows):
                            self.__pressed.add((x, y))

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
                                self.__game.toggle_flag(*pressed_tile)

                    elif pressed_face:
                        self.__init_game()

                self.__pressed.clear()
                self.__pressed_face = False

    def tick(self) -> bool:  # returns true if window is alive
        self.__clock.tick(FPS)
        for event in pygame.event.get():
            self.__event_handler(event)

        grid_graphics = generate_grid_graphics_(
            self.__game.grid, self.__pressed, self.__game.state
        )

        face_texture = get_face_texture_(
            self.__game.state, bool(self.__pressed), self.__pressed_face
        )

        unplaced_flags = self.__game.mine_count - self.__game.flags_placed
        mine_counter_graphics = get_counter_graphics(
            self.__mine_counter_pos, unplaced_flags
        )
        time_counter_graphics = get_counter_graphics(
            self.__time_counter_pos, int(min(self.__game.elapsed_time, 999))
        )

        mine_counter_border_graphics = get_counter_border_graphics(
            self.__mine_counter_pos
        )
        time_counter_border_graphics = get_counter_border_graphics(
            self.__time_counter_pos
        )

        self.__surface.blits(self.__board_graphics, doreturn=False)
        self.__surface.blits(grid_graphics, doreturn=False)
        self.__surface.blits(mine_counter_border_graphics, doreturn=False)
        self.__surface.blits(mine_counter_graphics, doreturn=False)
        self.__surface.blits(time_counter_border_graphics, doreturn=False)
        self.__surface.blits(time_counter_graphics, doreturn=False)
        self.__surface.blit(face_texture, self.__face_pos)

        pygame.display.update()

        return self.__window_alive
