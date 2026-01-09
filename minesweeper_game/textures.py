import os

import pygame


def asset_path_(path: str) -> str:
    return os.path.join(os.path.dirname(__file__), "assets", path)


class Tilemap:
    def __init__(self, tilemap_file, tile_size_x, tile_size_y, count=None):
        self.tilemap_ = pygame.image.load(asset_path_(tilemap_file))

        self.tile_size_x_ = tile_size_x
        self.tile_size_y_ = tile_size_y

        width, height = self.tilemap_.get_size()
        if width % tile_size_x != 0 or height % tile_size_y != 0:
            raise ValueError(
                f"Tilemap's dimensions ({width}x{height}) not divisible by tile's dimensions ({tile_size_x}x{tile_size_y})"
            )

        self.cols_ = width // tile_size_x
        self.rows_ = height // tile_size_y

        self.count_ = count or self.cols_ * self.rows_
        if self.count_ > self.cols_ * self.rows_:
            raise ValueError(
                f"Requestes tile count ({self.count_}) higher than possible in tilemap ({self.cols_}x{self.rows_})"
            )

    def __getitem__(self, index):
        if index >= self.count_:
            raise IndexError(f"Tile's index out of bounds ({index}/{self.count_})")

        row = index // self.cols_
        col = index % self.cols_

        rect = pygame.Rect(
            col * self.tile_size_x_,
            row * self.tile_size_y_,
            self.tile_size_x_,
            self.tile_size_y_,
        )
        tile = self.tilemap_.subsurface(rect)

        return tile


TILES_ = Tilemap("tiles.bmp", 16, 16)
FACES_ = Tilemap("faces.bmp", 28, 28, 5)
COUNTER_BORDER_ = Tilemap("counter_border.bmp", 16, 16, 8)
COUNTER_ = Tilemap("counter.bmp", 16, 32, 11)
BORDER_ = Tilemap("border.bmp", 16, 16)


class TEXTURES:
    class TILES:
        V1 = TILES_[0]
        V2 = TILES_[1]
        V3 = TILES_[2]
        V4 = TILES_[3]
        V5 = TILES_[4]
        V6 = TILES_[5]
        V7 = TILES_[6]
        V8 = TILES_[7]
        PRESSED = TILES_[8]
        UNCOVERED = TILES_[9]
        FLAGGED = TILES_[10]
        FALSEMINE = TILES_[11]
        PRESSED_QUESTION = TILES_[12]
        QUESTION = TILES_[13]
        PRESSED_MINE = TILES_[14]
        BLOWN_MINE = TILES_[15]

    class FACES:
        DEAD = FACES_[0]
        PRESSED_HAPPY = FACES_[1]
        HAPPY = FACES_[2]
        WINNER = FACES_[3]
        CAUTIOUS = FACES_[4]

    class COUNTER_BORDER:
        TOPLEFT = COUNTER_BORDER_[0]
        TOP = COUNTER_BORDER_[1]
        TOPRIGHT = COUNTER_BORDER_[2]
        LEFT = COUNTER_BORDER_[3]
        RIGHT = COUNTER_BORDER_[4]
        BOTTOMLEFT = COUNTER_BORDER_[5]
        BOTTOM = COUNTER_BORDER_[6]
        BOTTOMRIGHT = COUNTER_BORDER_[7]

    class COUNTER:
        V0 = COUNTER_[0]
        MINUS = COUNTER_[1]
        V9 = COUNTER_[2]
        V8 = COUNTER_[3]
        V7 = COUNTER_[4]
        V6 = COUNTER_[5]
        V5 = COUNTER_[6]
        V4 = COUNTER_[7]
        V3 = COUNTER_[8]
        V2 = COUNTER_[9]
        V1 = COUNTER_[10]

    class BORDER:
        TBL = BORDER_[0]
        TBR = BORDER_[1]
        BR = BORDER_[2]
        LR = BORDER_[3]
        BL = BORDER_[4]
        TL = BORDER_[5]
        TR = BORDER_[6]
        TB = BORDER_[7]
        FILL = BORDER_[8]
