import sys
import json
import os

from direct.task.Task import Task
from panda3d.core import *  # Contains most of Panda's modules
from direct.showbase.ShowBase import ShowBase

from helper.filepaths import get_texture_path
from helper.model import MinecraftModel, Vertex, get_model_id_from_file_path, load_model_json, ModelJSON, \
    ModelJSONElement, \
    get_path_from_model_id, ModelJSONPosition, fill_frame_data
from helper.options import parse_args
from helper.tints import find_leaf_tint
from helper.transform import get_light_one_vec, get_light_zero_vec, get_light_zero_item_vec, get_light_one_item_vec


def load_mc_model_json(file_path):
    with open(file_path, "r") as model_file:
        model = json.load(model_file)

    return model


def convert_mc_model_to_egg(base_path, base_mc_path, model_json: ModelJSON, filename):
    model = get_minecraft_model(base_path, model_json, filename)

    egg_text = ""
    # egg_text += "<CoordinateSystem> { Y-up-right }\n"

    for texture in model.textures.keys():
        texturePath = get_path_from_model_id(model.textures[texture][0], base_path, base_mc_path, '.png',
                                             type='textures')
        egg_text += f"<Texture> {texture} {{\n"
        egg_text += f"\t{Filename.from_os_specific(texturePath)}\n"
        egg_text += "\t<Scalar> format { RGBA }\n"
        egg_text += "\t<Scalar> minfilter { NEAREST }\n"
        egg_text += "\t<Scalar> magfilter { NEAREST }\n"
        egg_text += "}\n\n"

    egg_text += "<VertexPool> model {\n"
    for vertex in model.vertices:
        egg_text += "\t<Vertex> {\n"
        egg_text += f"\t\t{vertex.x} {vertex.y} {vertex.z}\n"
        egg_text += f"\t\t<UV> {{ {vertex.u} {model_json.get_texture_by_name(vertex.texture[1:]).get_transformed_v_coord(vertex.v, 0)} }}\n"

        if vertex.tinted:
            texture_tint = model.textures[vertex.texture[1:]][1]
            egg_text += f"\t\t<RGBA> {{ {texture_tint[0] / 255} {texture_tint[1] / 255} {texture_tint[2] / 255} {1} }}\n"

        egg_text += "\t}\n"

    egg_text += "}\n\n"

    total_vertices = len(model.vertices)
    for i in range(0, (total_vertices // 4)):
        vec_3_2 = LVecBase3f(model.vertices[i * 4 + 2].x - model.vertices[i * 4 + 1].x,
                             model.vertices[i * 4 + 2].y - model.vertices[i * 4 + 1].y,
                             model.vertices[i * 4 + 2].z - model.vertices[i * 4 + 1].z)
        vec_3_1 = LVecBase3f(model.vertices[i * 4 + 2].x - model.vertices[i * 4].x,
                             model.vertices[i * 4 + 2].y - model.vertices[i * 4].y,
                             model.vertices[i * 4 + 2].z - model.vertices[i * 4].z)

        normal = vec_3_2.cross(vec_3_1).normalized()

        egg_text += f"<Polygon> tri{i * 2 + 1} {{\n"
        egg_text += f"\t<TRef> {{ {model.vertices[i * 4].texture[1:]} }}\n"
        egg_text += f"\t<Normal> {{ {normal.getX()} {normal.getY()} {normal.getZ()} }}\n"
        egg_text += f"\t<VertexRef> {{\n"
        egg_text += f"\t\t{i * 4 + 3} {i * 4 + 2} {i * 4 + 1}\n"
        egg_text += f"\t\t<Ref> {{ model }}\n"
        egg_text += f"\t}}\n"
        egg_text += f"}}\n\n"

        egg_text += f"<Polygon> tri{i * 2 + 2} {{\n"
        egg_text += f"\t<TRef> {{ {model.vertices[i * 4].texture[1:]} }}\n"
        egg_text += f"\t<Normal> {{ {normal.getX()} {normal.getY()} {normal.getZ()} }}\n"
        egg_text += f"\t<VertexRef> {{\n"
        egg_text += f"\t\t{i * 4 + 2} {i * 4 + 3} {i * 4 + 4}\n"
        egg_text += f"\t\t<Ref> {{ model }}\n"
        egg_text += f"\t}}\n"
        egg_text += f"}}\n\n"

    return egg_text


def get_minecraft_model(base_path, model_json: ModelJSON, filename):
    model = MinecraftModel()
    model.vertices.extend(get_vertices_for_model(model_json))
    model.textures = {val.name: [val.texture_ref, False] for val in model_json.textures}

    # Set tinted property if any cube has tinted set
    for vertex in model.vertices:
        if vertex.texture[1:] in model.textures and not model.textures[vertex.texture[1:]][1]:
            if vertex.tinted:
                model.textures[vertex.texture[1:]] = \
                    [model.textures[vertex.texture[1:]][0],
                     find_leaf_tint(model_json.full_id_path)]

    return model


def get_vertices_for_model(model_json: ModelJSON):
    verts = []
    for voxel in model_json.elements:
        verts += get_vertices_for_voxel(voxel)

    for vert in verts:
        vert.normalizeUV()
        vert.normalizePos()

    return verts


def get_vertices_for_voxel(voxel_json: ModelJSONElement):
    x1 = voxel_json.voxel_from[0]
    y1 = voxel_json.voxel_from[1]
    z1 = voxel_json.voxel_from[2]
    x2 = voxel_json.voxel_to[0]
    y2 = voxel_json.voxel_to[1]
    z2 = voxel_json.voxel_to[2]

    rotateOrigin = voxel_json.rotation.origin
    rotateAxis = voxel_json.rotation.axis
    rotateAngle = voxel_json.rotation.angle

    # Top
    tinted = False
    if 'up' in voxel_json.faces:
        tinted = tinted or voxel_json.faces["up"].tint_index is not None
        topVertices = [
            Vertex(x1, y2, z1, voxel_json.faces["up"].uvs[0], voxel_json.faces["up"].uvs[1],
                   voxel_json.faces["up"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                  voxel_json.rotation.rescale),
            Vertex(x2, y2, z1, voxel_json.faces["up"].uvs[2], voxel_json.faces["up"].uvs[1],
                   voxel_json.faces["up"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                  voxel_json.rotation.rescale),
            Vertex(x1, y2, z2, voxel_json.faces["up"].uvs[0], voxel_json.faces["up"].uvs[3],
                   voxel_json.faces["up"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                  voxel_json.rotation.rescale),
            Vertex(x2, y2, z2, voxel_json.faces["up"].uvs[2], voxel_json.faces["up"].uvs[3],
                   voxel_json.faces["up"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                  voxel_json.rotation.rescale)
        ]

        rotate_tex_coord(topVertices[0], topVertices[1], topVertices[2], topVertices[3],
                         voxel_json.faces["up"].rotation)
    else:
        topVertices = []

    # Bottom
    if 'down' in voxel_json.faces:
        tinted = tinted or voxel_json.faces["down"].tint_index is not None
        bottomVertices = [
            Vertex(x1, y1, z2, voxel_json.faces["down"].uvs[0], voxel_json.faces["down"].uvs[1],
                   voxel_json.faces["down"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale),
            Vertex(x2, y1, z2, voxel_json.faces["down"].uvs[2], voxel_json.faces["down"].uvs[1],
                   voxel_json.faces["down"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale),
            Vertex(x1, y1, z1, voxel_json.faces["down"].uvs[0], voxel_json.faces["down"].uvs[3],
                   voxel_json.faces["down"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale),
            Vertex(x2, y1, z1, voxel_json.faces["down"].uvs[2], voxel_json.faces["down"].uvs[3],
                   voxel_json.faces["down"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale)
        ]

        rotate_tex_coord(bottomVertices[0], bottomVertices[1], bottomVertices[2], bottomVertices[3],
                         voxel_json.faces["down"].rotation)
    else:
        bottomVertices = []

    # North
    if 'north' in voxel_json.faces:
        tinted = tinted or voxel_json.faces["north"].tint_index is not None
        northVertices = [
            Vertex(x2, y2, z1, voxel_json.faces["north"].uvs[0], voxel_json.faces["north"].uvs[1],
                   voxel_json.faces["north"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                     voxel_json.rotation.rescale),
            Vertex(x1, y2, z1, voxel_json.faces["north"].uvs[2], voxel_json.faces["north"].uvs[1],
                   voxel_json.faces["north"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                     voxel_json.rotation.rescale),
            Vertex(x2, y1, z1, voxel_json.faces["north"].uvs[0], voxel_json.faces["north"].uvs[3],
                   voxel_json.faces["north"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                     voxel_json.rotation.rescale),
            Vertex(x1, y1, z1, voxel_json.faces["north"].uvs[2], voxel_json.faces["north"].uvs[3],
                   voxel_json.faces["north"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                     voxel_json.rotation.rescale)
        ]

        rotate_tex_coord(northVertices[0], northVertices[1], northVertices[2], northVertices[3],
                         voxel_json.faces["north"].rotation)
    else:
        northVertices = []

    # East
    if 'east' in voxel_json.faces:
        tinted = tinted or voxel_json.faces["east"].tint_index is not None
        eastVertices = [
            Vertex(x2, y2, z2, voxel_json.faces["east"].uvs[0], voxel_json.faces["east"].uvs[1],
                   voxel_json.faces["east"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale),
            Vertex(x2, y2, z1, voxel_json.faces["east"].uvs[2], voxel_json.faces["east"].uvs[1],
                   voxel_json.faces["east"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale),
            Vertex(x2, y1, z2, voxel_json.faces["east"].uvs[0], voxel_json.faces["east"].uvs[3],
                   voxel_json.faces["east"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale),
            Vertex(x2, y1, z1, voxel_json.faces["east"].uvs[2], voxel_json.faces["east"].uvs[3],
                   voxel_json.faces["east"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale)
        ]

        rotate_tex_coord(eastVertices[0], eastVertices[1], eastVertices[2], eastVertices[3],
                         voxel_json.faces["east"].rotation)
    else:
        eastVertices = []

    # South
    if 'south' in voxel_json.faces:
        tinted = tinted or voxel_json.faces["south"].tint_index is not None
        southVertices = [
            Vertex(x1, y2, z2, voxel_json.faces["south"].uvs[0], voxel_json.faces["south"].uvs[1],
                   voxel_json.faces["south"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                     voxel_json.rotation.rescale),
            Vertex(x2, y2, z2, voxel_json.faces["south"].uvs[2], voxel_json.faces["south"].uvs[1],
                   voxel_json.faces["south"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                     voxel_json.rotation.rescale),
            Vertex(x1, y1, z2, voxel_json.faces["south"].uvs[0], voxel_json.faces["south"].uvs[3],
                   voxel_json.faces["south"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                     voxel_json.rotation.rescale),
            Vertex(x2, y1, z2, voxel_json.faces["south"].uvs[2], voxel_json.faces["south"].uvs[3],
                   voxel_json.faces["south"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                     voxel_json.rotation.rescale)
        ]

        rotate_tex_coord(southVertices[0], southVertices[1], southVertices[2], southVertices[3],
                         voxel_json.faces["south"].rotation)
    else:
        southVertices = []

    # West
    if 'west' in voxel_json.faces:
        tinted = tinted or voxel_json.faces["west"].tint_index is not None
        westVertices = [
            Vertex(x1, y2, z1, voxel_json.faces["west"].uvs[0], voxel_json.faces["west"].uvs[1],
                   voxel_json.faces["west"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale),
            Vertex(x1, y2, z2, voxel_json.faces["west"].uvs[2], voxel_json.faces["west"].uvs[1],
                   voxel_json.faces["west"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale),
            Vertex(x1, y1, z1, voxel_json.faces["west"].uvs[0], voxel_json.faces["west"].uvs[3],
                   voxel_json.faces["west"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale),
            Vertex(x1, y1, z2, voxel_json.faces["west"].uvs[2], voxel_json.faces["west"].uvs[3],
                   voxel_json.faces["west"].texture, tinted).rotate(rotateOrigin, rotateAxis, rotateAngle,
                                                                    voxel_json.rotation.rescale)
        ]

        rotate_tex_coord(westVertices[0], westVertices[1], westVertices[2], westVertices[3],
                         voxel_json.faces["west"].rotation)
    else:
        westVertices = []

    return topVertices + bottomVertices + northVertices + eastVertices + southVertices + westVertices


def rotate_tex_coord(vert1, vert2, vert3, vert4, rotation):
    if rotation == 90:
        u1 = vert3.u
        v1 = vert3.v

        vert3.u = vert4.u
        vert3.v = vert4.v
        vert4.u = vert2.u
        vert4.v = vert2.v
        vert2.u = vert1.u
        vert2.v = vert1.v
        vert1.u = u1
        vert1.v = v1
        pass
    elif rotation == 180:
        rotate_tex_coord(vert1, vert2, vert3, vert4, 90)
        rotate_tex_coord(vert1, vert2, vert3, vert4, 90)
        pass
    elif rotation == 270:
        rotate_tex_coord(vert1, vert2, vert3, vert4, 90)
        rotate_tex_coord(vert1, vert2, vert3, vert4, 90)
        rotate_tex_coord(vert1, vert2, vert3, vert4, 90)


def main():
    base = ShowBase(windowType='offscreen')
    options = parse_args()

    model_id = get_model_id_from_file_path(options.file_in, options.rsp_path, [options.mc_base_rsp_path])
    model = load_model_json(model_id, options.rsp_path, options.mc_base_rsp_path)
    fill_frame_data(model, options.rsp_path, options.mc_base_rsp_path)

    egg_file_text = convert_mc_model_to_egg(options.rsp_path, options.mc_base_rsp_path, model,
                                            os.path.split(options.file_in)[1])

    if not os.path.exists('./temp'):
        os.mkdir('./temp')

    with open('./temp/temp.egg', 'w') as fileout:
        fileout.write(egg_file_text)

    pandaModel = loader.loadModel('./temp/temp.egg')

    if not 'item/generated' in model.full_id_path and not 'minecraft:item/generated' in model.full_id_path:
        pandaModel.setHpr(0,
                          -90,
                          0)

    pandaModel.flattenLight()

    if options.view not in model.display:
        print('Position "' + options.view + '" not found; Using default view (no rotation, scale, or translation)')
        model.display[options.view] = ModelJSONPosition()

    pandaModel.setScale(model.display[options.view].scale[0],
                        model.display[options.view].scale[1],
                        model.display[options.view].scale[2])

    pandaModel.flattenLight()

    pandaModel.setHpr(model.display[options.view].rotation[2],
                      0,
                      0)

    pandaModel.flattenLight()

    pandaModel.setHpr(0,
                      0,
                      model.display[options.view].rotation[1])

    pandaModel.flattenLight()

    pandaModel.setHpr(0,
                      model.display[options.view].rotation[0],
                      0)

    pandaModel.flattenLight()

    pandaModel.setPos(model.display[options.view].translation[0],
                      model.display[options.view].translation[1],
                      model.display[options.view].translation[2])
    pandaModel.flattenLight()

    # pandaModel.setTwoSided(True)

    mybuffer = base.win.makeTextureBuffer("buffer", options.size, options.size, None, True)
    base.set_background_color(0, 0, 0, 0)
    mybuffer.setSort(-100)

    lens = OrthographicLens()
    if options.scale_to_fit:
        min_point, max_point = pandaModel.getTightBounds()
        film_size = max(max_point.getX() - min_point.getX(), max_point.getY() - min_point.getY())
        lens.setFilmSize(film_size, film_size)
    else:
        lens.setFilmSize(16, 16)

    lens.setCoordinateSystem(CSYupRight)
    lens.setFar(100)
    lens.setNear(0)
    mycamera = base.makeCamera(mybuffer, lens=lens)
    if options.scale_to_fit:
        min_point, max_point = pandaModel.getTightBounds()
        mycamera.setPos((max_point.getX() - min_point.getX()) / 2 + min_point.getX(),
                        (max_point.getY() - min_point.getY()) / 2 + min_point.getY(), 32)
    else:
        mycamera.setPos(0, 0, 32)

    myscene = NodePath("MyScene")
    mycamera.reparentTo(myscene)
    pandaModel.reparentTo(myscene)

    if model.gui_light == 'front':
        l0_vec = get_light_zero_item_vec().getXyz()
        l1_vec = get_light_one_item_vec().getXyz()
    else:
        l0_vec = get_light_zero_vec().getXyz()
        l1_vec = get_light_one_vec().getXyz()

    lightzero = DirectionalLight('lightone')
    lightzero.setDirection(l0_vec)
    lightzero.setColor((0.6, 0.6, 0.6, 1))

    lightone = DirectionalLight('lightone')
    lightone.setDirection(l1_vec)
    lightone.setColor((0.6, 0.6, 0.6, 1))

    alight = AmbientLight('alight')
    alight.setColor((0.5, 0.5, 0.5, 1))
    alnp = render.attachNewNode(alight)
    render.setLight(alnp)

    l0 = render.attachNewNode(lightzero)
    l1 = render.attachNewNode(lightone)

    if model.gui_light == 'front':
        l0.setHpr(0, -90, 0)
        l1.setHpr(0, -90, 0)
    else:
        l0.setHpr(90, 0, 0)
        l1.setHpr(90, 0, 0)

    pandaModel.setLight(l1)
    pandaModel.setLight(l0)

    myscene.reparentTo(render)

    frame = 0

    if os.path.exists(options.file_out):
        os.remove(options.file_out)

    def copyAndClose(task):
        nonlocal frame
        if frame >= 1:
            base.screenshot(source=mybuffer, namePrefix=options.file_out, defaultFilename=0)
            sys.exit(0)
        frame += 1
        return Task.cont

    taskMgr.add(copyAndClose, "copyAndClose")

    base.run()


main()
