from .game.game import GameState
from .game.tile import Tile, TileState
from .textures import TEXTURES, TILE_WIDTH



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
        txt_name = str(chars[i]) if chars[i] != 10 else "minus"
        txt = TEXTURES["counter"][txt_name]
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
