from game import GameState, Tile, TileState
from .textures import TEXTURES, TILE_WIDTH


def generate_board_graphics(cols: int, rows: int):
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


TILE_TEXTURES = {
    TileState.SAFE_0: TEXTURES["tiles"]["0"],
    TileState.SAFE_1: TEXTURES["tiles"]["1"],
    TileState.SAFE_2: TEXTURES["tiles"]["2"],
    TileState.SAFE_3: TEXTURES["tiles"]["3"],
    TileState.SAFE_4: TEXTURES["tiles"]["4"],
    TileState.SAFE_5: TEXTURES["tiles"]["5"],
    TileState.SAFE_6: TEXTURES["tiles"]["6"],
    TileState.SAFE_7: TEXTURES["tiles"]["7"],
    TileState.SAFE_8: TEXTURES["tiles"]["8"],
    TileState.COVERED: TEXTURES["tiles"]["covered"],
    TileState.FLAGGED: TEXTURES["tiles"]["flagged"],
    TileState.MINE: TEXTURES["tiles"]["mine"],
    TileState.BLOWN_MINE: TEXTURES["tiles"]["blown_mine"],
    TileState.FALSE_FLAG: TEXTURES["tiles"]["false_mine"],
}


def __get_tile_texture(
    tile_state: TileState, is_pressed: bool, game_state: GameState
) -> str:
    if (
        tile_state == TileState.COVERED
        and is_pressed
        and game_state == GameState.RUNNING
    ):
        return TILE_TEXTURES[TileState.SAFE_0]

    return TILE_TEXTURES[tile_state]


def generate_grid_graphics(
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

            txt = __get_tile_texture(tile, is_pressed, game_state)

            grid_graphics.append((txt, (x, y)))

    return grid_graphics


def get_face_texture(game_state: GameState, any_tile_pressed: bool, face_pressed: bool):
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
