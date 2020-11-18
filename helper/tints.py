import os

from PIL import Image

from helper.filepaths import get_texture_path
from helper.model import get_namespaced_json_id

GRASS_BLOCK_TINT = [124, 189, 107]
OAK_LEAVES_TINT = [72, 181, 24]
BIRCH_LEAVES_TINT = [128, 167, 85]
SPRUCE_LEAVES_TINT = [97, 153, 97]
JUNGLE_LEAVES_TINT = [72, 181, 24]
ACACIA_LEAVES_TINT = [72, 181, 24]
DARK_OAK_LEAVES_TINT = [72, 181, 24]

filename_to_tint = {
    'block/oak_leaves': OAK_LEAVES_TINT,
    'block/acacia_leaves': ACACIA_LEAVES_TINT,
    'block/birch_leaves': BIRCH_LEAVES_TINT,
    'block/dark_oak_leaves': DARK_OAK_LEAVES_TINT,
    'block/jungle_leaves': JUNGLE_LEAVES_TINT,
    'block/spruce_leaves': SPRUCE_LEAVES_TINT,
}


def find_leaf_tint(json_ids):
    ids_copy = json_ids
    ids_copy.reverse()

    for json_id in ids_copy:
        full_id = get_namespaced_json_id(json_id)
        for tint_json_id in filename_to_tint.keys():
            full_tint_json_id = get_namespaced_json_id(tint_json_id)
            if full_tint_json_id == full_id:
                return filename_to_tint[tint_json_id]

    return [255, 255, 255]  # No tint found, just use plain white
