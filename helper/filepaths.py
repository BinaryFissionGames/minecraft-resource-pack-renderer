import os


def get_texture_path(base_path, texture_string):
    return os.path.abspath(os.path.normpath(
        os.path.join(base_path, "assets", "minecraft", "textures", texture_string) + ".png"))