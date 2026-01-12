import os

import pygame


def asset_path(path: str) -> str:
    return os.path.join(os.path.dirname(__file__), "assets", path)


class Tilemap:
    def __init__(self, tilemap_file, tile_size_x, tile_size_y, count=None):
        self.__tilemap = pygame.image.load(asset_path(tilemap_file))

        self.__tile_size_x = tile_size_x
        self.__tile_size_y = tile_size_y

        width, height = self.__tilemap.get_size()
        if width % tile_size_x != 0 or height % tile_size_y != 0:
            raise ValueError(
                f"Tilemap's dimensions ({width}x{height}) not divisible by tile's dimensions ({tile_size_x}x{tile_size_y})"
            )

        self.__cols = width // tile_size_x
        self.__rows = height // tile_size_y

        self.__count = count or self.__cols * self.__rows
        if self.__count > self.__cols * self.__rows:
            raise ValueError(
                f"Requestes tile count ({self.__count}) higher than possible in tilemap ({self.__cols}x{self.__rows})"
            )

    def __getitem__(self, index):
        if index >= self.__count:
            raise IndexError(f"Tile's index out of bounds ({index}/{self.__count})")

        row = index // self.__cols
        col = index % self.__cols

        rect = pygame.Rect(
            col * self.__tile_size_x,
            row * self.__tile_size_y,
            self.__tile_size_x,
            self.__tile_size_y,
        )
        tile = self.__tilemap.subsurface(rect)

        return tile


TILES = Tilemap("tiles.bmp", 16, 16)
FACES = Tilemap("faces.bmp", 28, 28, 5)
COUNTER_BORDER = Tilemap("counter_border.bmp", 16, 16, 8)
COUNTER = Tilemap("counter.bmp", 16, 32, 11)
BORDER = Tilemap("border.bmp", 16, 16)
ERROR = Tilemap("error.bmp", 16, 16)


class TEXTURES:
    ERROR = ERROR[0]

    class TILES:
        V1 = TILES[0]
        V2 = TILES[1]
        V3 = TILES[2]
        V4 = TILES[3]
        V5 = TILES[4]
        V6 = TILES[5]
        V7 = TILES[6]
        V8 = TILES[7]
        V0 = TILES[8]
        COVERED = TILES[9]
        FLAGGED = TILES[10]
        FALSEMINE = TILES[11]
        PRESSED_QUESTION = TILES[12]
        QUESTION = TILES[13]
        PRESSED_MINE = TILES[14]
        BLOWN_MINE = TILES[15]

    class FACES:
        DEAD = FACES[0]
        PRESSED_HAPPY = FACES[1]
        HAPPY = FACES[2]
        WINNER = FACES[3]
        CAUTIOUS = FACES[4]

    class COUNTER_BORDER:
        TOPLEFT = COUNTER_BORDER[0]
        TOP = COUNTER_BORDER[1]
        TOPRIGHT = COUNTER_BORDER[2]
        LEFT = COUNTER_BORDER[3]
        RIGHT = COUNTER_BORDER[4]
        BOTTOMLEFT = COUNTER_BORDER[5]
        BOTTOM = COUNTER_BORDER[6]
        BOTTOMRIGHT = COUNTER_BORDER[7]

    class COUNTER:
        V0 = COUNTER[0]
        MINUS = COUNTER[1]
        V9 = COUNTER[2]
        V8 = COUNTER[3]
        V7 = COUNTER[4]
        V6 = COUNTER[5]
        V5 = COUNTER[6]
        V4 = COUNTER[7]
        V3 = COUNTER[8]
        V2 = COUNTER[9]
        V1 = COUNTER[10]

    class BORDER:
        TBL = BORDER[0]
        TBR = BORDER[1]
        BR = BORDER[2]
        LR = BORDER[3]
        BL = BORDER[4]
        TL = BORDER[5]
        TR = BORDER[6]
        TB = BORDER[7]
        FILL = BORDER[8]
