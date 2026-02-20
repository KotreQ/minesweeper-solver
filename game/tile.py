from enum import Enum


class TileState(Enum):
    SAFE_0 = 0
    SAFE_1 = 1
    SAFE_2 = 2
    SAFE_3 = 3
    SAFE_4 = 4
    SAFE_5 = 5
    SAFE_6 = 6
    SAFE_7 = 7
    SAFE_8 = 8
    COVERED = 9
    FLAGGED = 10
    MINE = 11
    BLOWN_MINE = 12
    FALSE_FLAG = 13


class Tile:
    def __init__(self):
        self.__is_mine = False
        self.__value = 0
        self.__game_finished = False

        self.__state = TileState.COVERED

    @property
    def state(self) -> TileState:
        return self.__state
    
    @property
    def is_revealed(self) -> bool:
        return self.__state.value <= 8

    @property
    def value(self) -> int | None:
        if self.is_revealed:
            return self.__value
        else:
            return None

    def uncover(self) -> tuple[bool, bool]:
        """Uncovers the tile

        Returns:
            bool: True if succeeded, False if it's a mine or failed
        """

        if self.__game_finished:
            return False

        if self.__state == TileState.COVERED:
            if self.__is_mine:
                self.__state = TileState.BLOWN_MINE
                return False

            self.__state = TileState(self.__value)
            return True

        return False

    def toggle_flag(self) -> bool:
        """Toggles the flag on the tile

        Returns:
            bool: True if succeeded, False otherwise
        """

        if self.__game_finished:
            return False

        if self.__state == TileState.COVERED:
            self.__state = TileState.FLAGGED
            return True
        elif self.__state == TileState.FLAGGED:
            self.__state = TileState.COVERED
            return True

        return False

    def _mark_mine(self) -> bool:
        """Marks the tile as a mine

        Returns:
            bool: True if succeeded, False if it was already a mine
        """

        if self.__is_mine:
            return False

        self.__is_mine = True
        return True

    def _increase_value(self):
        if self.__value >= 8:
            raise ValueError("Tile's value is already at max level")

        self.__value += 1

    def _mark_finished_game(self, won: bool):
        self.__game_finished = True

        if self.__state == TileState.COVERED and self.__is_mine:
            if won:
                self.__state = TileState.FLAGGED
            else:
                self.__state = TileState.MINE

        elif self.__state == TileState.FLAGGED and not self.__is_mine:
            self.__state = TileState.FALSE_FLAG
