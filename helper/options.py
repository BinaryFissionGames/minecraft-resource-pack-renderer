import argparse
import sys


class RenderOptions:
    def __init__(self, ns: argparse.Namespace):
        self.size = ns.size[0]
        self.view = ns.view[0]
        self.rsp_path = ns.rsp_path[0]
        self.scale_to_fit = ns.scale_to_fit
        self.mc_base_rsp_path = ns.mc_base_rsp_path[0]
        self.file_in = ns.file_in[0]
        self.file_out = ns.file_out[0]


def parse_args() -> RenderOptions:
    parser = argparse.ArgumentParser(description='Render a minecraft model json file to a PNG.')
    parser.add_argument('-s', '--size', nargs=1, default=[512], type=int, metavar='PX',
                        help='Specifies the output image size')
    parser.add_argument('-v', '--view', nargs=1, default=['gui'],
                        choices=['thirdperson_righthand', 'thirdperson_lefthand', 'firstperson_righthand',
                                 'firstperson_lefthand', 'gui', 'head', 'ground', 'fixed'], metavar='VIEW',
                        help='Specifies the view transform to use when rendering the model')
    parser.add_argument('-f', '--scale_to_fit', default=False, action='store_true',
                        help='Scale the bounds of the render space to fit the whole rendered model, instead of assuming the geometry fits within the standard 16x16 area')
    parser.add_argument('rsp_path', nargs=1, help='Base path of the resource pack')
    parser.add_argument('mc_base_rsp_path', nargs=1, help='Base path of the "default" minecraft resource pack')
    parser.add_argument('file_in', nargs=1, help='Path of the input file to render')
    parser.add_argument('file_out', nargs=1, help='Path of the output file to render to')
    return RenderOptions(parser.parse_args(sys.argv[1:]))


RENDER_OPTION_RSP = 'rsp'
RENDER_OPTION_ALL = 'all'


class RenderAllOptions:
    def __init__(self, ns: argparse.Namespace):
        self.collapse_tree_structure = ns.collapse_tree  # If true, the output will be a flat structure, instead of copying the tree structure of the input
        self.file_name_map = ns.map_file  # A JSON file that specifies a map from an input file (json) to one or more output files
        self.only_render_in_map = ns.map_only  # if true, only render items in file_name_map. Only valid if a file_name_map is specified
        self.scale_to_fit = ns.scale_to_fit  # Scale models to fit, instead of using standard 16x16 render space
        self.downscale_ffmpeg = ns.downscale_ffmpeg  # Use ffmpeg to use superscaling to introduce anti-aliasing in the final image
        self.output_size = ns.size  # final image output size
        self.scale_size = ns.superscale_size  # Output size from the render -- only used if use_ffmpeg_scaling is true
        self.render_set = ns.render_set[0]  # render rsp OR render all (base pack + rsp)
        self.render_tile_entities = ns.render_tile_entities  # if true, render tile entities (see /extra)
        self.output_folder = ns.output_path
        self.rsp_path = ns.rsp_path
        self.mc_base_rsp_path = ns.mc_base_rsp_path


def parse_render_all_options() -> RenderAllOptions:
    parser = argparse.ArgumentParser(description='Render a minecraft resource pack to PNG icons.')
    parser.add_argument('-c', '--collapse_tree', default=False, action='store_true',
                        help='Collapse file tree for output')
    parser.add_argument('-mf', '--map_file', default=None, help='Map file for input file to output file')
    parser.add_argument('-mo', '--map_only', default=False, action='store_true',
                        help='Only render files specified in the map file')
    parser.add_argument('-d', '--downscale_ffmpeg', default=False, action='store_true',
                        help='Use ffmpeg to downscale from a superscaled image, creating an aliasing effect. Requires ffmpeg installed on the PATH')
    parser.add_argument('-si', '--size', default=128, type=int, help='Output size (assumed square)')
    parser.add_argument('-ss', '--superscale_size', default=512, type=int,
                        help='Superscale size, used with --downscale_ffmpeg')
    parser.add_argument('-rs', '--render_set', default=[RENDER_OPTION_RSP],
                        choices=[RENDER_OPTION_RSP, RENDER_OPTION_ALL],
                        help='Specify whether to render just the files included in the rsp, or to extend to the base pack files as well')
    parser.add_argument('-rt', '--render_tile_entities', default=False, action='store_true',
                        help='Include tile entities from /extra to be rendered')
    parser.add_argument('-o', '--output_path', default='./rendered_rsp', help='Output folder')
    parser.add_argument('-f', '--scale_to_fit', default=False, action='store_true',
                        help='Scale the bounds of the render space to fit the whole rendered model, instead of assuming the geometry fits within the standard 16x16 area')
    parser.add_argument('rsp_path', help='Base path of the resource pack')
    parser.add_argument('mc_base_rsp_path', help='Base path of the "default" minecraft resource pack')

    return RenderAllOptions(parser.parse_args(sys.argv[1:]))


class RenderLeatherArmorsOptions:
    def __init__(self, ns: argparse.Namespace):
        self.scale = ns.scale
        self.output_path = ns.output_path
        self.rsp_path = ns.rsp_path
        self.description_file = ns.description_file


def parse_render_leather_armors_options() -> RenderLeatherArmorsOptions:
    parser = argparse.ArgumentParser(description='Render tinted leather armors based on a description file.')
    parser.add_argument('-s', '--scale', type=int, default=None, help='Scale the icon to the provided size')
    parser.add_argument('-o', '--output_path', default='./rendered_rsp', help='Output folder')
    parser.add_argument('rsp_path', help='Base path of the resource pack')
    parser.add_argument('description_file', help='JSON file describing the leather armor icons to render')

    return RenderLeatherArmorsOptions(parser.parse_args(sys.argv[1:]))


class CreateAnimatedGifOptions:
    def __init__(self, ns: argparse.Namespace):
        self.texture = ns.texture
        self.output_path = ns.output_path


def parse_create_animated_gif_options() -> CreateAnimatedGifOptions:
    parser = argparse.ArgumentParser(description='Render an animated texture as a GIF.')
    parser.add_argument('-o', '--output_path', default='./temp/out.gif', help='Output file')
    parser.add_argument('texture', help='Texture file to turn into a GIF')
    return CreateAnimatedGifOptions(parser.parse_args(sys.argv[1:]))
