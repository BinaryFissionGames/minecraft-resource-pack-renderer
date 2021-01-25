import json
import os

from helper.model import ModelJSON, load_model_json, get_path_from_model_id

# This script is for creating mappings from a scraped format;
# Unless you're doing minescape related stuff, you probably don't need this script.

RSP_BASE_PATH = './rsp'
MC_ASSETS_BASE_PATH = './temp/minecraft-assets'

SPECIAL_ITEM_MAPPINGS = [
    # [lambda x: x == 'block.minecraft.player_head', lambda x: 'builtin/entity/player_head'],
    # [lambda x: x == 'block.minecraft.chest', lambda x: 'builtin/entity/chest'],
]


def get_model_id_from_translation_key(trans_key: str):
    for mapping in SPECIAL_ITEM_MAPPINGS:
        if mapping[0](trans_key):
            return mapping[1](trans_key)

    parts = trans_key.split('.')
    return 'item/' + parts[2]


def name_to_file_name(ingame_name: str):
    return ingame_name.strip().replace(' ', '_').replace('\'', '')


def texture_path_to_relative_path(id):
    mc_file_path = os.path.abspath(MC_ASSETS_BASE_PATH)
    file_path = get_path_from_model_id(id, RSP_BASE_PATH, MC_ASSETS_BASE_PATH, '.png',
                                       type='textures')

    if os.path.abspath(file_path).startswith(mc_file_path):
        rel_path = os.path.relpath(os.path.abspath(file_path), mc_file_path)
    else:
        rel_path = os.path.relpath(os.path.abspath(file_path), os.path.abspath(RSP_BASE_PATH))

    return rel_path


def get_leather_armor_desc(item_info):
    model = load_model_json(get_model_id_from_translation_key(item_info['mcItemName']), RSP_BASE_PATH,
                            MC_ASSETS_BASE_PATH)
    new_model = get_model_override(model, item_info)
    if new_model is not None:
        model = new_model

    textures = {}
    for tex in model.textures:
        textures[tex.name] = tex.texture_ref

    layer0 = texture_path_to_relative_path(textures['layer0']) if "layer0" in textures else ''
    layer1 = texture_path_to_relative_path(textures['layer1']) if "layer1" in textures else ''

    return {
        'name': name_to_file_name(item_info['itemName']),
        'color': item_info['colorString'],
        "icon_relative_path": layer0,
        "overlay_relative_path": layer1
    }


def get_item_model_mapping(item_info):
    model = load_model_json(get_model_id_from_translation_key(item_info['mcItemName']), RSP_BASE_PATH,
                            MC_ASSETS_BASE_PATH)
    new_model = get_model_override(model, item_info)
    if new_model is not None:
        model = new_model

    return model.full_id_path[-1], name_to_file_name(item_info['itemName'])


def get_model_override(model: ModelJSON, item_info):
    for predicate in model.predicates:
        if predicate.matches(item_info['itemDamage'], item_info['maxDamage']):
            return load_model_json(predicate.model, RSP_BASE_PATH, MC_ASSETS_BASE_PATH)
    return None


with open('temp/items.json', 'r') as items_file:
    itemInfo = json.load(items_file)

leather_armor_descriptions = []
model_name_mappings = {}

for item_dump in itemInfo["itemInfos"]:
    print("Dumping " + item_dump['itemName'])
    #    try:
    if "colorString" in item_dump:
        leather_armor_descriptions.append(get_leather_armor_desc(item_dump))
    else:
        json_id, mapping_name = get_item_model_mapping(item_dump)
        if json_id in model_name_mappings:
            model_name_mappings[json_id].append(mapping_name)
        else:
            model_name_mappings[json_id] = [mapping_name]
    # except FileNotFoundError as fnf:
    #     print("Failed to dump " + item_dump['itemName'] + '!')
    #     print('Cannot find file ' + fnf.filename)
    # except KeyError as k:
    #     print("Failed to dump " + item_dump['itemName'] + '!')
    #     print('Key error: ' + str(k))
    #     pass

with open('temp/ms_model_mappings.json', 'w') as mappings_out:
    json.dump(model_name_mappings, mappings_out)

with open('temp/leather_descs.json', 'w') as leather_out:
    json.dump(leather_armor_descriptions, leather_out)
