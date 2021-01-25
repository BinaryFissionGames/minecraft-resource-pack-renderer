import json
import os
import subprocess
from collections import Set
from shutil import copyfile

from helper.model import get_model_id_from_file_path, get_path_from_model_id
from helper.options import parse_render_all_options, RENDER_OPTION_ALL
from helper.tile_entities import TILE_ENTITIY_ID_SET

options = parse_render_all_options()

if options.file_name_map is not None:
    with open(options.file_name_map, 'r') as file_map_file:
        options.file_name_map = json.load(file_map_file)


def is_in_directory(filepath, dir):
    try:
        common_path = os.path.commonpath([os.path.abspath(filepath), os.path.abspath(dir)])
        return os.path.abspath(common_path) == os.path.abspath(dir)
    except ValueError:
        return False


def get_new_file_name(filepath, suffix):
    file_name_no_suffix = os.path.splitext(os.path.basename(filepath))[0]

    if not options.collapse_tree_structure:
        if is_in_directory(filepath, options.rsp_path):
            folder_out = os.path.abspath(os.path.relpath(filepath, options.rsp_path))
        elif is_in_directory(filepath, options.mc_base_rsp_path):
            folder_out = os.path.abspath(os.path.relpath(filepath, options.mc_base_rsp_path))
        else:
            folder_out = os.path.abspath(options.output_folder)
    else:
        folder_out = os.path.abspath(options.output_folder)

    out_file = os.path.join(folder_out, file_name_no_suffix + suffix)

    return out_file


def generate_icon(filename, out_names=None):
    abs_file_name = os.path.abspath(filename)
    print('Generating icon for file ' + abs_file_name)

    main_script_output_size = options.scale_size if options.downscale_ffmpeg else options.output_size
    process_args = ['python', './main.py']

    if options.scale_to_fit:
        process_args.append('-f')

    process_args += ['-s', str(main_script_output_size), options.rsp_path, options.mc_base_rsp_path, filename,
                     './temp/out.png']

    process_result = subprocess.call(process_args, stderr=subprocess.DEVNULL)

    if process_result != 0:
        print('Failed to generate icon for file ' + abs_file_name)
        return

    if out_names is None:
        out_names = [get_new_file_name(filename, '')]

    basic_out_names = filter(lambda x: type(x) is str, out_names)
    overriden_texture_names = filter(lambda x: type(x) is not str, out_names)

    # Anything that has a texture override must be rendered on a separate pass;
    # so we should do outnames with no texture overrides,
    # then do each one with texture overrides
    #
    # Here's the structure of an entry that has texture overrides...
    # {
    #     name: '',
    #     texture_overrides: {
    #         key: val
    #     }
    # }

    if options.downscale_ffmpeg:
        subprocess.call(
            ['ffmpeg', '-loglevel', 'fatal', '-nostats', '-i', 'temp/out.png', '-vf',
             f'scale={options.output_size}:-1', '-pix_fmt', 'rgba', '-y',
             'temp/out_scaled.png'])

        file_to_copy = 'temp/out_scaled.png'
    else:
        file_to_copy = 'temp/out.png'

    for name in basic_out_names:
        output_file = os.path.join(options.output_folder, name) + '.png'
        output_folder = os.path.dirname(output_file)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        copyfile(file_to_copy, output_file)

    for obj in overriden_texture_names:
        output_file = os.path.join(options.output_folder, obj['name']) + '.png'
        output_folder = os.path.dirname(output_file)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        texture_override_args = process_args.copy()

        for orig, override in obj['texture_overrides'].items():
            texture_override_args += ['-to', f'{orig}={override}']

        process_result = subprocess.call(texture_override_args, stderr=subprocess.DEVNULL)

        if process_result != 0:
            print('Failed to generate icon for file ' + abs_file_name)
            return

        if options.downscale_ffmpeg:
            subprocess.call(
                ['ffmpeg', '-loglevel', 'fatal', '-nostats', '-i', 'temp/out.png', '-vf',
                 f'scale={options.output_size}:-1', '-pix_fmt', 'rgba', '-y',
                 'temp/out_scaled.png'])

            file_to_copy = 'temp/out_scaled.png'
        else:
            file_to_copy = 'temp/out.png'

        copyfile(file_to_copy, output_file)



def get_all_ids_from_pack(pack_path):
    # TODO: Discover namespaces other than minecraft
    models_dir = os.path.join(options.rsp_path, 'assets', 'minecraft', 'models')

    ids = []
    if os.path.exists(models_dir):
        for tup in os.walk(models_dir):
            for filename in tup[2]:
                if filename.endswith('.json'):
                    full_path = os.path.abspath(os.path.join(tup[0], filename))
                    ids.append(get_model_id_from_file_path(full_path, pack_path, []))

    return ids


def get_models_to_render() -> Set:  # Returns a Set of resource identifiers to render
    model_ids = set()
    if not options.only_render_in_map:
        model_ids |= set(get_all_ids_from_pack(options.rsp_path))

        if options.render_set == RENDER_OPTION_ALL:
            model_ids |= set(get_all_ids_from_pack(options.mc_base_rsp_path))

        if options.render_tile_entities:
            model_ids |= TILE_ENTITIY_ID_SET
    else:
        model_ids |= set(filter(lambda x: not x.startswith('_'), options.file_name_map.keys()))

    return model_ids


def main():
    models_to_render = get_models_to_render()
    for resource_id in models_to_render:
        out_file_names = options.file_name_map[
            resource_id] if options.file_name_map is not None and resource_id in options.file_name_map else None
        generate_icon(get_path_from_model_id(resource_id, options.rsp_path, options.mc_base_rsp_path, '.json'),
                      out_file_names)


main()
