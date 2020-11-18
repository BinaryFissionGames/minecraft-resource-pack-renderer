import json
import os

import PIL
from PIL import Image

from helper.options import parse_render_leather_armors_options

options = parse_render_leather_armors_options()


def color_tuple_from_hexcode(hexcode):
    return int(hexcode[1:3], 16), int(hexcode[3:5], 16), int(hexcode[5:7], 16)


def generate_outputs_for_definition(definition):
    color_tuple = color_tuple_from_hexcode(definition["color"])

    if "icon_relative_path" in definition and definition["icon_relative_path"] != "":
        piece_colormap = os.path.join(options.rsp_path, definition["icon_relative_path"])
    else:
        piece_colormap = None

    if "overlay_relative_path" in definition and definition["overlay_relative_path"] != "":
        piece_overlay = os.path.join(options.rsp_path, definition["overlay_relative_path"])
    else:
        piece_overlay = None

    output_name = os.path.join(options.output_path, definition["name"]) + '.png'

    generate_image(color_tuple, piece_colormap, piece_overlay, output_name)


def generate_image(color_tuple, input_image_path, overlay_image_path, output_image_path):
    if input_image_path is not None and overlay_image_path is not None:
        with Image.open(input_image_path) as input_image:
            with Image.open(overlay_image_path) as overlay_image:
                bands = input_image.convert('RGBA').split()
                R, G, B, A = 0, 1, 2, 3
                r_band = bands[R].point(lambda x: round((x / 255) * color_tuple[0]))
                g_band = bands[G].point(lambda x: round((x / 255) * color_tuple[1]))
                b_band = bands[B].point(lambda x: round((x / 255) * color_tuple[2]))

                image_out = Image.merge('RGBA', [r_band, g_band, b_band, bands[A]])

                if image_out.width != overlay_image.width or image_out.height != overlay_image.height:
                    image_out = image_out.resize((overlay_image.width, overlay_image.height), resample=PIL.Image.BICUBIC)

                image_out = Image.alpha_composite(image_out, overlay_image.convert('RGBA'))

                if options.scale is not None:
                    resample_method = PIL.Image.NEAREST if image_out.width <= options.scale else PIL.Image.BICUBIC
                    image_out = image_out.resize((options.scale, options.scale), resample=resample_method)

                image_out.save(output_image_path)
    elif input_image_path is not None:
        with Image.open(input_image_path) as input_image:
            bands = input_image.convert('RGBA').split()
            R, G, B, A = 0, 1, 2, 3
            r_band = bands[R].point(lambda x: round((x / 255) * color_tuple[0]))
            g_band = bands[G].point(lambda x: round((x / 255) * color_tuple[1]))
            b_band = bands[B].point(lambda x: round((x / 255) * color_tuple[2]))

            image_out = Image.merge('RGBA', [r_band, g_band, b_band, bands[A]])

            if options.scale is not None:
                resample_method = PIL.Image.NEAREST if image_out.width <= options.scale else PIL.Image.BICUBIC
                image_out = image_out.resize((options.scale, options.scale), resample=resample_method)

            image_out.save(output_image_path)
        pass
    elif overlay_image_path is not None:
        with Image.open(overlay_image_path) as overlay_image:
            image_out = overlay_image
            if options.scale is not None:
                resample_method = PIL.Image.NEAREST if image_out.width <= options.scale else PIL.Image.BICUBIC
                image_out = image_out.resize((options.scale, options.scale), resample=resample_method)

            image_out.save(output_image_path)
        pass


def main():
    with open(options.description_file, 'r') as desc_file:
        armor_descriptions = json.load(desc_file)

    for desc in armor_descriptions:
        print("Generating icon for " + desc["name"])
        generate_outputs_for_definition(desc)


main()
