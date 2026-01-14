import os

import pygame

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

TEXTURES_PATH = os.path.join(ASSETS_PATH, "textures")

TEXTURES = {}


def load_textures():
    global TEXTURES

    for dir_name in os.listdir(TEXTURES_PATH):
        dir_path = os.path.join(TEXTURES_PATH, dir_name)
        if not os.path.isdir(dir_path):
            continue

        TEXTURES[dir_name] = {}

        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            txt = pygame.image.load(file_path)

            txt_name = os.path.splitext(file_name)[0]

            TEXTURES[dir_name][txt_name] = txt

load_textures()