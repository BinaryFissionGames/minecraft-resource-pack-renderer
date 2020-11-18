import json
import math
import os
from typing import List

from PIL import Image

SCALE_ROTATION_22_5 = 1 / math.cos(math.pi / 8)
SCALE_ROTATION_GENERAL = 1 / math.cos(math.pi / 4)


class Vertex:
    def __init__(self, x, y, z, u, v, tex, tinted):
        self.x = x
        self.y = y
        self.z = z

        self.u = u
        self.v = 16 - v
        self.texture = tex
        self.tinted = tinted

    def rotate(self, origin, axis, angle, rescale):
        (self.x, self.y, self.z) = self._rotate_single(self.x, self.y, self.z, origin, axis, angle)

        if rescale:
            scale = SCALE_ROTATION_22_5 if math.fabs(math.fabs(angle) - 22.5) < 0.01 else SCALE_ROTATION_GENERAL
            if axis == "x":
                self.y = ((self.y - origin[1]) * scale) + origin[1]
                self.z = ((self.z - origin[2]) * scale) + origin[2]
            elif axis == "y":
                self.x = ((self.x - origin[0]) * scale) + origin[0]
                self.z = ((self.z - origin[2]) * scale) + origin[2]
            else:
                self.x = ((self.x - origin[0]) * scale) + origin[0]
                self.y = ((self.y - origin[1]) * scale) + origin[1]

        return self

    def _rotate_single(self, x, y, z, origin, axis, angle):
        cos = math.cos(math.radians(angle))
        sin = math.sin(math.radians(angle))

        if axis == "x":
            y_shifted = y - origin[1]
            z_shifted = z - origin[2]
            y = (y_shifted * cos) + (z_shifted * -sin) + origin[1]
            z = (y_shifted * sin) + (z_shifted * cos) + origin[2]
        elif axis == "y":
            x_shifted = x - origin[0]
            z_shifted = z - origin[2]
            x = (x_shifted * cos) + (z_shifted * sin) + origin[0]
            z = (x_shifted * -sin) + (z_shifted * cos) + origin[2]
        else:
            x_shifted = x - origin[0]
            y_shifted = y - origin[1]
            x = (x_shifted * cos) + (y_shifted * -sin) + origin[0]
            y = (x_shifted * sin) + (y_shifted * cos) + origin[1]

        return x, y, z

    # In MC's json files, UV coords are between 0 and 16, here we scale them so they are between 0 and 1
    def normalizeUV(self):
        self.u /= 16
        self.v /= 16

    def normalizePos(self):
        self.x -= 8
        self.y -= 8
        self.z -= 8


class MinecraftModel:
    def __init__(self):
        self.vertices: List[Vertex] = []
        self.textures = {}  # Map of name to tuple [file, tinted]


class ModelJSONAnimationFrame:
    def __init__(self, v_offset=0):
        self.v_offset = v_offset


class ModelJSONTexture:
    def __init__(self, name, texture_ref, tinted=False, animation_frames=None, frame_time=1):
        if animation_frames is None:
            animation_frames = [ModelJSONAnimationFrame()]
        self.name: str = name
        self.texture_ref: str = texture_ref
        self.tinted: bool = tinted
        self.frametime: int = (1000 // 20) * frame_time
        self.v_scale: float = 1  # v coord = anim_frame.v_offset + (orig_v_coord * v_scale)
        self.animation_frames: List[ModelJSONAnimationFrame] = animation_frames

    def get_transformed_v_coord(self, orig_v_coord: float, frame: int):
        return self.animation_frames[frame].v_offset + orig_v_coord * self.v_scale

    def get_num_frames(self):
        return len(self.animation_frames)

    def set_frame_time(self, num_frames):
        self.frametime = (1000 // 20) * num_frames


class Predicate:
    def __init__(self, damage, model):
        self.damage = damage
        self.model = model

    def matches(self, damage, max_damage):
        if max_damage == 0:
            return False

        # TODO FIGURE OUT WHY THIS IS A THING
        if max_damage == 1561:
            max_damage += 1

        return math.fabs((damage / (max_damage)) - self.damage) < 0.0001


class ModelJSONPosition:
    def __init__(self):
        self.rotation = [0, 0, 0]
        self.translation = [0, 0, 0]
        self.scale = [1, 1, 1]
        pass


class ModelJSONElement:
    def __init__(self):
        self.voxel_from = []
        self.voxel_to = []
        self.rotation = ModelJSONElementRotation()
        self.shade = True
        self.faces = {}


class ModelJSONElementRotation:
    def __init__(self):
        self.origin = [0, 0, 0]
        self.axis = 'x'
        self.angle = 0
        self.rescale = False


class ModelJSONElementFace:
    def __init__(self):
        self.name = ''
        self.uvs = None
        self.texture = ''
        self.cullface = ''
        self.rotation = 0
        self.tint_index = None


class ModelJSON:
    def __init__(self):
        self.full_id_path = []
        self.gui_light = 'side'
        self.ambientocclusion = True
        self.display = {}
        self.textures: List[ModelJSONTexture] = []
        self.elements: List[ModelJSONElement] = []
        self.predicates: List[Predicate] = []

    def get_texture_by_name(self, name):
        for tex in self.textures:
            if tex.name == name:
                return tex

        raise Exception('No texture named ' + name)

    def has_texture(self, name):
        for tex in self.textures:
            if tex.name == name:
                return True
        return False


def get_model_id_from_file_path(json_file_path, rsp_base_path, extra_rsp_paths):
    rel_path = os.path.relpath(os.path.abspath(json_file_path), os.path.abspath(rsp_base_path))
    parts = rel_path.split(os.path.sep)

    builtin_file_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'extra'))

    if os.path.abspath(json_file_path).startswith(builtin_file_path):
        # built-in things are not relative to the RSP, but to the extra folder
        rel_path = os.path.relpath(os.path.abspath(json_file_path), builtin_file_path)
        parts = rel_path.split(os.path.sep)
        return f"builtin/{os.path.splitext('/'.join(parts))[0]}"

    if parts[0] != 'assets':
        return get_model_id_from_file_path(json_file_path, extra_rsp_paths[0], extra_rsp_paths[1:])
    assert parts[2] == 'models'

    namespace = parts[1]
    rest_of_path = '/'.join(parts[3:])

    if namespace != 'minecraft':
        return f'{namespace}:{os.path.splitext(rest_of_path)[0]}'
    return os.path.splitext(rest_of_path)[0]


# Prepends "minecraft:" if the ID has no namespace.
def get_namespaced_json_id(json_id):
    if len(json_id.split(':')) <= 1:
        return 'minecraft:' + json_id
    return json_id


def get_path_from_model_id(path_id: str, rsp_base_path, mc_rsp_base_path, ext, type='models'):
    if len(path_id.split('/')) >= 2 and path_id.split('/')[0] == 'builtin':
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', 'extra',
            os.path.sep.join(path_id.split('/')[1:])) + ext

    namespace = 'minecraft'
    path = path_id
    if ':' in path_id:
        namespace = path_id.split(':')[0]
        path = path_id.split(':')[1]

    rsp_path = os.path.join(rsp_base_path, 'assets', namespace, type, path) + ext
    mc_rsp_path = os.path.join(mc_rsp_base_path, 'assets', namespace, type, path) + ext

    if os.path.exists(rsp_path):
        return rsp_path

    return mc_rsp_path


def generate_uvs(element: ModelJSONElement, element_face: ModelJSONElementFace, face: str):
    if face == 'north':
        element_face.uvs = [element.voxel_from[0], element.voxel_from[1], element.voxel_to[0], element.voxel_to[1]]
    elif face == 'east':
        element_face.uvs = [element.voxel_from[1], element.voxel_from[2], element.voxel_to[1], element.voxel_to[2]]
    elif face == 'south':
        element_face.uvs = [element.voxel_from[0], element.voxel_from[1], element.voxel_to[0], element.voxel_to[1]]
    elif face == 'west':
        element_face.uvs = [element.voxel_from[1], element.voxel_from[2], element.voxel_to[1], element.voxel_to[2]]
    elif face == 'up':
        element_face.uvs = [element.voxel_from[0], element.voxel_from[2], element.voxel_to[0], element.voxel_to[2]]
    elif face == 'down':
        element_face.uvs = [element.voxel_from[0], element.voxel_from[2], element.voxel_to[0], element.voxel_to[2]]


ENTITY_MAPPINGS = {
    'minecraft:item/template_shulker_box': 'builtin/entity/shulker_box',
    'item/template_shulker_box': 'builtin/entity/shulker_box',
    'minecraft:item/template_skull': 'builtin/entity/player_head',
    'item/template_skull': 'builtin/entity/player_head',
    'minecraft:item/chest': 'builtin/entity/chest',
    'item/chest': 'builtin/entity/chest'
}


def load_model_json(json_id, rsp_base_path, mc_rsp_base_path, json_ids=None) -> ModelJSON:
    if json_ids is None:
        json_ids = []

    file_path = get_path_from_model_id(json_id, rsp_base_path, mc_rsp_base_path, '.json')
    with open(file_path, "r") as model_file:
        model = json.load(model_file)

    if json_id == 'builtin/entity':
        for id in ENTITY_MAPPINGS.keys():
            if id in json_ids:
                return load_model_json(ENTITY_MAPPINGS[id], rsp_base_path, mc_rsp_base_path, json_ids)

    model_structure = ModelJSON()
    if 'parent' in model:
        json_ids.append(json_id)
        model_structure = load_model_json(model['parent'], rsp_base_path, mc_rsp_base_path, json_ids)

    if '_shulker_box' in json_id:
        model_structure.textures.append(
            ModelJSONTexture('generated', 'entity/shulker/shulker_' + json_id.split('/')[-1].split('_')[0]))
    elif 'shulker_box' in json_id:
        model_structure.textures.append(ModelJSONTexture('generated', 'entity/shulker/shulker'))

    model_structure.full_id_path.append(json_id)

    if 'ambientocclusion' in model:
        model_structure.ambientocclusion = model['ambientocclusion']

    if 'display' in model:
        for position in model['display'].keys():
            json_position = ModelJSONPosition()
            if 'rotation' in model['display'][position]:
                json_position.rotation = model['display'][position]['rotation']
            if 'translation' in model['display'][position]:
                json_position.translation = model['display'][position]['translation']
            if 'scale' in model['display'][position]:
                json_position.scale = model['display'][position]['scale']
            model_structure.display[position] = json_position

    if 'textures' in model:
        for key, val in model['textures'].items():
            tex = ModelJSONTexture(key, val)
            model_structure.textures.append(tex)

    if 'elements' in model:
        model_structure.elements = []
        for json_elem in model['elements']:
            element = ModelJSONElement()

            element.voxel_from = json_elem['from']
            element.voxel_to = json_elem['to']

            element.rotation = ModelJSONElementRotation()
            if 'rotation' in json_elem:
                element.rotation.origin = json_elem['rotation']['origin']
                element.rotation.axis = json_elem['rotation']['axis']
                element.rotation.angle = json_elem['rotation']['angle']
                if 'rescale' in json_elem['rotation']:
                    element.rotation.rescale = json_elem['rotation']['rescale']

            if 'shade' in json_elem:
                element.shade = json_elem['shade']

            if 'faces' in json_elem:
                for face in json_elem['faces'].keys():
                    element.faces[face] = ModelJSONElementFace()

                    if 'uv' in json_elem['faces'][face]:
                        element.faces[face].uvs = json_elem['faces'][face]['uv']
                    else:
                        generate_uvs(element, element.faces[face], face)

                    element.faces[face].texture = json_elem['faces'][face]['texture']

                    if 'cullface' in json_elem['faces'][face]:
                        element.faces[face].cullface = json_elem['faces'][face]['cullface']
                    else:
                        element.faces[face].cullface = face

                    if 'rotation' in json_elem['faces'][face]:
                        element.faces[face].rotation = json_elem['faces'][face]['rotation']

                    if 'tintindex' in json_elem['faces'][face]:
                        element.faces[face].tint_index = json_elem['faces'][face]['tintindex']

            model_structure.elements.append(element)

    if 'gui_light' in model:
        model_structure.gui_light = model['gui_light']

    if 'overrides' in model:
        model_structure.predicates = []
        # TODO: support other predicates?
        for override in model['overrides']:
            if 'damage' in override['predicate']:
                predicate = Predicate(override['predicate']['damage'], override['model'])
                model_structure.predicates.append(predicate)

    if json_id == 'item/zombie_head' or json_id == 'minecraft:item/zombie_head':
        model_structure.textures.append(ModelJSONTexture('head', 'entity/zombie/zombie'))

    return model_structure


def normalize_textures(mc_model: ModelJSON):
    '''
    This function "normalizes" the texture map of the model. Essentially, the textures may refer to another
    texture. This function replaces those references to other textures w/ the actual texture.
    :param mc_model: MCModel instance to normalize
    :return: void; mc_model is mutated
    '''
    for texture in mc_model.textures:
        visited = []
        texture_ref = texture.texture_ref
        while texture.texture_ref.startswith('#'):
            if texture_ref in visited:
                break
            visited.append(texture_ref)
            if mc_model.has_texture(texture_ref[1:]):
                texture.texture_ref = mc_model.get_texture_by_name(texture_ref[1:]).texture_ref
            else:
                break


def fill_frame_data(mc_model: ModelJSON, rsp_base_path, mc_base_path):
    '''
    fills frame data for textures in given model
    :param mc_model:
    '''

    normalize_textures(mc_model)

    for tex in mc_model.textures:
        animation_desc_path = get_path_from_model_id(tex.texture_ref, rsp_base_path, mc_base_path, '.png.mcmeta',
                                                     type='textures')
        if os.path.exists(animation_desc_path):
            texture_path = get_path_from_model_id(tex.texture_ref, rsp_base_path, mc_base_path, '.png',
                                                  type='textures')
            with Image.open(texture_path) as png:
                tex_width = png.width
                tex_height = png.height

            with open(animation_desc_path, 'r') as animation_file_desc_file:
                animation_desc = json.load(animation_file_desc_file)

            if 'animation' in animation_desc.keys():
                animation = animation_desc['animation']
                frame_time = 1
                frames = list(range(0, tex_height // tex_width))

                if 'frametime' in animation:
                    frame_time = animation['frametime']

                if 'frames' in animation:
                    frames = animation['frames']

                tex.set_frame_time(frame_time)
                tex.v_scale = png.width / png.height
                tex.animation_frames = [ModelJSONAnimationFrame(v_offset=(x * tex.v_scale)) for x in frames]
