import os

import pygame


def asset_path_(path: str) -> str:
    return os.path.join(os.path.dirname(__file__), "assets", path)


def get_tilemap_(tilemap_file, count, size_x, size_y):
    tilemap = pygame.image.load(asset_path_(tilemap_file))

    width, height = tilemap.get_size()
    assert width % size_x == 0
    assert height % size_y == 0

    rows = height // size_y
    cols = width // size_x
    assert count <= rows * cols

    for i in range(count):
        row = i // cols
        col = i % cols

        rect = pygame.Rect(col * size_x, row * size_y, size_x, size_y)
        tile = tilemap.subsurface(rect)
        yield tile


class TEXTURES:
    class TILES:
        V1 = None
        V2 = None
        V3 = None
        V4 = None
        V5 = None
        V6 = None
        V7 = None
        V8 = None
        PRESSED = None
        UNCOVERED = None
        FLAGGED = None
        FALSEMINE = None
        PRESSED_QUESTION = None
        QUESTION = None
        PRESSED_MINE = None
        BLOWN_MINE = None

    class FACES:
        DEAD = None
        PRESSED_HAPPY = None
        HAPPY = None
        WINNER = None
        CAUTIOUS = None

    class COUNTERBORDERS:
        TOPLEFT = None
        TOP = None
        TOPRIGHT = None
        LEFT = None
        RIGHT = None
        BOTTOMLEFT = None
        BOTTOM = None
        BOTTOMRIGHT = None

    class COUNTER:
        V0 = None
        MINUS = None
        V9 = None
        V8 = None
        V7 = None
        V6 = None
        V5 = None
        V4 = None
        V3 = None
        V2 = None
        V1 = None

    class BORDER:
        TBL = None
        TBR = None
        BR = None
        LR = None
        BL = None
        TL = None
        TR = None
        TB = None
        FILL = None


(
    TEXTURES.TILES.V1,
    TEXTURES.TILES.V2,
    TEXTURES.TILES.V3,
    TEXTURES.TILES.V4,
    TEXTURES.TILES.V5,
    TEXTURES.TILES.V6,
    TEXTURES.TILES.V7,
    TEXTURES.TILES.V8,
    TEXTURES.TILES.PRESSED,
    TEXTURES.TILES.UNCOVERED,
    TEXTURES.TILES.FLAGGED,
    TEXTURES.TILES.FALSEMINE,
    TEXTURES.TILES.PRESSED_QUESTION,
    TEXTURES.TILES.QUESTION,
    TEXTURES.TILES.PRESSED_MINE,
    TEXTURES.TILES.BLOWN_MINE,
) = get_tilemap_("tiles.bmp", 16, 16, 16)

(
    TEXTURES.FACES.DEAD,
    TEXTURES.FACES.PRESSED_HAPPY,
    TEXTURES.FACES.HAPPY,
    TEXTURES.FACES.WINNER,
    TEXTURES.FACES.CAUTIOUS,
) = get_tilemap_("faces.bmp", 5, 28, 28)

(
    TEXTURES.COUNTERBORDERS.TOPLEFT,
    TEXTURES.COUNTERBORDERS.TOP,
    TEXTURES.COUNTERBORDERS.TOPRIGHT,
    TEXTURES.COUNTERBORDERS.LEFT,
    TEXTURES.COUNTERBORDERS.RIGHT,
    TEXTURES.COUNTERBORDERS.BOTTOMLEFT,
    TEXTURES.COUNTERBORDERS.BOTTOM,
    TEXTURES.COUNTERBORDERS.BOTTOMRIGHT,
) = get_tilemap_("counter_border.bmp", 8, 16, 16)

(
    TEXTURES.COUNTER.V0,
    TEXTURES.COUNTER.MINUS,
    TEXTURES.COUNTER.V9,
    TEXTURES.COUNTER.V8,
    TEXTURES.COUNTER.V7,
    TEXTURES.COUNTER.V6,
    TEXTURES.COUNTER.V5,
    TEXTURES.COUNTER.V4,
    TEXTURES.COUNTER.V3,
    TEXTURES.COUNTER.V2,
    TEXTURES.COUNTER.V1,
) = get_tilemap_("counter.bmp", 11, 16, 32)

(
    TEXTURES.BORDER.TBL,
    TEXTURES.BORDER.TBR,
    TEXTURES.BORDER.BR,
    TEXTURES.BORDER.LR,
    TEXTURES.BORDER.BL,
    TEXTURES.BORDER.TL,
    TEXTURES.BORDER.TR,
    TEXTURES.BORDER.TB,
    TEXTURES.BORDER.FILL,
) = get_tilemap_("border.bmp", 9, 16, 16)
