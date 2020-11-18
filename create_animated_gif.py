import PIL

from helper.options import parse_create_animated_gif_options
from PIL import Image

options = parse_create_animated_gif_options()

with Image.open(options.texture) as full_texture:
    full_texture = full_texture.convert("RGBA")
    texture_size = full_texture.width
    if texture_size >= full_texture.height:
        raise Exception("Textures width should be smaller than it's height!")

    images = []
    for i in range(0, full_texture.height // texture_size):
        images.append(full_texture.crop((0, i * texture_size, texture_size, (i + 1) * texture_size)))

    # TODO: Extract frame times/order from mcmeta file
    images[0].save(options.output_path, save_all=True, append_images=images[1:], duration=1000 // 20, loop=0,
                   transparency=0, disposal=2)
