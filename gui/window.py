import pygame

from game.game import GameState, MinesweeperGame, TileState
from game.utils import get_neighbours
from solver.solver import MinesweeperSolver

from .graphics import (
    generate_analysis_graphics,
    generate_board_graphics,
    generate_grid_graphics,
    get_button_graphics,
    get_counter_border_graphics,
    get_counter_graphics,
    get_face_texture,
)
from .textures import TILE_WIDTH

WINDOW_CAPTION = "Minesweeper by KotreQ"
FPS = 60

SOLVE_BUTTON_LABEL = "SOLVE"
ANALYSIS_BUTTON_LABEL = "ANALYSIS"


class MinesweeperWindow:
    def __init__(self, game_spec: MinesweeperGame | tuple[int, int, int]):
        self.__game_spec = game_spec

        self.__init_game(game_spec)

        self.__clock = pygame.time.Clock()
        self.__window_alive = True

        self.__mouse_event = ((0, 0), -1)
        self.__pressed = set()
        self.__pressed_face = False
        self.__solve_button_pressed = False
        self.__analysis_button_pressed = False
        self.__show_analysis = False

    def __init_game(self, game_spec: MinesweeperGame | tuple[int, int, int]):
        if isinstance(game_spec, MinesweeperGame):
            self.__game = game_spec
        else:
            self.__game = MinesweeperGame(*game_spec)

        self.__solver = MinesweeperSolver(self.__game)
        self.__analysis_graphics = None
        self.__analysis_dirty = True

        self.__board_graphics = generate_board_graphics(
            self.__game.cols, self.__game.rows, bottom_padding_rows=2
        )

        window_width = (1 + self.__game.cols + 1) * TILE_WIDTH
        window_height = (1 + 3 + 1 + self.__game.rows + 1 + 2) * TILE_WIDTH

        self.__surface = pygame.display.set_mode((window_width, window_height))

        button_gap = TILE_WIDTH // 2
        buttons_width = min(12 * TILE_WIDTH, (self.__game.cols - 2) * TILE_WIDTH)
        button_width = (buttons_width - button_gap) // 2
        button_height = TILE_WIDTH + TILE_WIDTH // 2
        button_y = (self.__game.rows + 6) * TILE_WIDTH + (
            2 * TILE_WIDTH - button_height
        ) // 2
        solve_button_x = (window_width - buttons_width) // 2
        self.__solve_button_rect = (
            solve_button_x,
            button_y,
            button_width,
            button_height,
        )
        self.__analysis_button_rect = (
            solve_button_x + button_width + button_gap,
            button_y,
            button_width,
            button_height,
        )

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

    def __is_over_button(self, pos, rect: tuple[int, int, int, int]) -> bool:
        x, y, width, height = rect
        return x <= pos[0] < x + width and y <= pos[1] < y + height

    def __invalidate_analysis(self):
        self.__analysis_graphics = None
        self.__analysis_dirty = True

    def __update_analysis(self):
        self.__analysis_dirty = False
        self.__analysis_graphics = None

        try:
            analysis = self.__solver.analyze()
        except RuntimeError as error:
            print(f"Solver analysis error: {error}")
            return

        self.__analysis_graphics = generate_analysis_graphics(
            analysis, self.__game.cols, self.__game.rows
        )

    def __make_solver_move(self):
        if self.__game.state != GameState.RUNNING:
            return

        try:
            self.__solver.make_move()
        except RuntimeError as error:
            print(f"Solver error: {error}")
        finally:
            self.__invalidate_analysis()

    def __toggle_analysis(self):
        if self.__game.state != GameState.RUNNING:
            return

        self.__show_analysis = not self.__show_analysis
        self.__invalidate_analysis()

    def __event_handler(self, event):
        match event.type:
            case pygame.QUIT:
                self.__window_alive = False

            case pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.__is_over_button(event.pos, self.__solve_button_rect):
                        self.__solve_button_pressed = True
                    elif self.__is_over_button(
                        event.pos, self.__analysis_button_rect
                    ):
                        self.__analysis_button_pressed = True

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

                    # if pressed revealed tile, highlight neighbours as pressed
                    x, y = pressed_tile
                    if self.__game.grid[y][x].is_revealed:
                        for x, y in get_neighbours(
                            x, y, self.__game.cols, self.__game.rows
                        ):
                            self.__pressed.add((x, y))

                self.__pressed_face = pressed_face

            case pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.__solve_button_pressed and self.__is_over_button(
                        event.pos, self.__solve_button_rect
                    ):
                        self.__make_solver_move()
                    elif self.__analysis_button_pressed and self.__is_over_button(
                        event.pos, self.__analysis_button_rect
                    ):
                        self.__toggle_analysis()
                self.__solve_button_pressed = False
                self.__analysis_button_pressed = False

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
                        self.__invalidate_analysis()

                    elif pressed_face:
                        self.__init_game(self.__game_spec)

                self.__pressed.clear()
                self.__pressed_face = False

    def tick(self) -> bool:  # returns true if window is alive
        self.__clock.tick(FPS)
        for event in pygame.event.get():
            self.__event_handler(event)

        grid_graphics = generate_grid_graphics(
            self.__game.grid, self.__pressed, self.__game.state
        )

        face_texture = get_face_texture(
            self.__game.state, bool(self.__pressed), self.__pressed_face
        )

        game_running = self.__game.state == GameState.RUNNING
        mouse_pos = pygame.mouse.get_pos()

        solve_button_graphics = get_button_graphics(
            self.__solve_button_rect,
            SOLVE_BUTTON_LABEL,
            self.__solve_button_pressed and self.__is_over_button(
                mouse_pos, self.__solve_button_rect
            ),
            game_running,
        )
        analysis_button_graphics = get_button_graphics(
            self.__analysis_button_rect,
            ANALYSIS_BUTTON_LABEL,
            self.__analysis_button_pressed
            and self.__is_over_button(mouse_pos, self.__analysis_button_rect),
            game_running,
            active=self.__show_analysis,
        )

        analysis_blit = None
        if self.__show_analysis and game_running:
            if self.__analysis_dirty:
                self.__update_analysis()
            if self.__analysis_graphics is not None:
                analysis_blit = (
                    self.__analysis_graphics,
                    (TILE_WIDTH, (1 + 3 + 1) * TILE_WIDTH),
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
        if analysis_blit is not None:
            self.__surface.blit(*analysis_blit)
        self.__surface.blit(*solve_button_graphics)
        self.__surface.blit(*analysis_button_graphics)
        self.__surface.blits(mine_counter_border_graphics, doreturn=False)
        self.__surface.blits(mine_counter_graphics, doreturn=False)
        self.__surface.blits(time_counter_border_graphics, doreturn=False)
        self.__surface.blits(time_counter_graphics, doreturn=False)
        self.__surface.blit(face_texture, self.__face_pos)

        pygame.display.update()

        return self.__window_alive
