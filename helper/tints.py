import os

from PIL import Image

from helper.filepaths import get_texture_path

GRASS_BLOCK_TINT = [124, 189, 107]
OAK_LEAVES_TINT = [72, 181, 24]
BIRCH_LEAVES_TINT = [128, 167, 85]
SPRUCE_LEAVES_TINT = [97, 153, 97]
JUNGLE_LEAVES_TINT = [72, 181, 24]
ACACIA_LEAVES_TINT = [72, 181, 24]
DARK_OAK_LEAVES_TINT = [72, 181, 24]

filename_to_tint = {
    'leaves.json': OAK_LEAVES_TINT,
    'leaves_1.json': OAK_LEAVES_TINT,
    'leaves_2.json': OAK_LEAVES_TINT,
    'leaves_acacia.json': ACACIA_LEAVES_TINT,
    'leaves_acacia1.json': ACACIA_LEAVES_TINT,
    'leaves_acacia2.json': ACACIA_LEAVES_TINT,
    'leaves_birch.json': BIRCH_LEAVES_TINT,
    'leaves_birch1.json': BIRCH_LEAVES_TINT,
    'leaves_birch2.json': BIRCH_LEAVES_TINT,
    'leaves_dark_oak.json': DARK_OAK_LEAVES_TINT,
    'leaves_dark_oak1.json': DARK_OAK_LEAVES_TINT,
    'leaves_dark_oak2.json': DARK_OAK_LEAVES_TINT,
    'leaves_jungle.json': JUNGLE_LEAVES_TINT,
    'leaves_jungle1.json': JUNGLE_LEAVES_TINT,
    'leaves_jungle2.json': JUNGLE_LEAVES_TINT,
    'spruce_leaves.json': SPRUCE_LEAVES_TINT,
    'spruce_leaves_2.json': SPRUCE_LEAVES_TINT,
}


def generate_tint_png(base_path, filename, tint_map_file_path):
    tint = filename_to_tint[filename]
    with Image.open(tint_map_file_path) as image:
        bands = image.convert('RGBA').split()
        R, G, B, A = 0, 1, 2, 3
        r_band = bands[R].point(lambda x: round((x / 255) * tint[0]))
        g_band = bands[G].point(lambda x: round((x / 255) * tint[1]))
        b_band = bands[B].point(lambda x: round((x / 255) * tint[2]))

        imageOut = Image.merge('RGBA', [r_band, g_band, b_band, bands[A]])
        original_filename = os.path.splitext(os.path.split(tint_map_file_path)[1])[0]
        texture_path = 'block/' + original_filename + '_tint'
        filename_out = get_texture_path(base_path, texture_path)
        imageOut.save(filename_out)
        return texture_path
