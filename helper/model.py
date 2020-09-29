import json
import math
import os

SCALE_ROTATION_22_5 = 1 / math.cos(math.pi / 8)
SCALE_ROTATION_GENERAL = 1 / math.cos(math.pi / 4)


class MinecraftModel:
    def __init__(self):
        self.vertices = []
        self.textures = {}  # Map of name to tuple [file, tinted]


class Vertex:
    def __init__(self, x, y, z, u, v, tex, tinted):
        self.x = x
        self.y = y
        self.z = z

        self.u = u
        self.v = 16 - v

        if tex == '#up' or tex == '#down' or tex == '#north' or tex == '#east' or tex == '#west' or tex == '#south':
            self.texture = '#all'
        else:
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


class ModelJSON:
    def __init__(self):
        self.full_id_path = []
        self.gui_light = 'side'
        self.ambientocclusion = True
        self.display = {}
        self.textures = {}
        self.elements = []
        pass


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


def load_model_json(json_id, rsp_base_path, mc_rsp_base_path) -> ModelJSON:
    file_path = get_path_from_model_id(json_id, rsp_base_path, mc_rsp_base_path, '.json')
    with open(file_path, "r") as model_file:
        model = json.load(model_file)

    model_structure = ModelJSON()
    if 'parent' in model:
        model_structure = load_model_json(model['parent'], rsp_base_path, mc_rsp_base_path)

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
        model_structure.textures.update(model['textures'])

    if 'elements' in model:
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

                    element.faces[face].texture = json_elem['faces'][face]['texture']

                    if 'cullface' in json_elem['faces'][face]:
                        element.faces[face].cullface = json_elem['faces'][face]['cullface']
                    else:
                        element.faces[face].cullface = face

                    if 'rotation' in json_elem['faces'][face]:
                        element.faces[face].rotation = json_elem['faces'][face]['rotation']

                    if 'tintindex' in json_elem['faces'][face]:
                        element.faces[face].tintindex = json_elem['faces'][face]['rotation']['tintindex']

            model_structure.elements.append(element)

    if 'gui_light' in model:
        model_structure.gui_light = model['gui_light']

    return model_structure
