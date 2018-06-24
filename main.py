# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <gilles.ballegeer@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return Gilles Ballegeer
# ----------------------------------------------------------------------------

import bpy
import svg_utils
import os
import importlib
importlib.reload(svg_utils)

from svg_utils import (
        get_co_extremes_mul_obj,
        get_width_height_transform,
        get_in_height_order,
        xml_handler,
        object_after_mod,
        get_co_extremes_emptys)

from bpy.props import (
        FloatProperty,
        IntProperty,
        BoolProperty
        )

from bpy_extras.io_utils import (
        ExportHelper
        )

from bpy.types import (
        Operator
        )


bl_info = {
    "name": "SVG format",
    "author": "Gilles Ballegeer",
    "version": (0,0,1),
    "blender": (2, 79, 0),
    "location": "File > Export > Svg",
    "warning": "",
    "wiki_url": "",
    "category": "Export"
}


class ExportSVG(Operator, ExportHelper):
    bl_idname = "export.stl"
    bl_label = "Export SVG"

    filename_ext = ".svg"

    margin = FloatProperty(
        name="Margin",
        min=0.0, max=1.0,
        default=0.2,
    )

    by_empty = BoolProperty(
        name="Define max co by empty"
    )

    size = IntProperty(name="Size",
                       default=500,
                       min=1,
                       max=10000)

    def execute(self, context):
        keywords = self.as_keywords()
        print(keywords)

        objects = context.selected_objects
        obj_list = []
        empty_list = []
        for obj in context.selected_objects:
            if len(obj.modifiers) > 0 and obj.type == 'MESH':
                obj_list.append(object_after_mod(obj, context))
            elif obj.type == 'CURVE':
                obj_list.append(obj)
            elif obj.type == 'EMPTY':
                empty_list.append(obj)

        if not self.by_empty:
            xmin, xmax, ymin, ymax = get_co_extremes_mul_obj(obj_list)
        else:
            xmin, xmax, ymin, ymax = get_co_extremes_emptys(empty_list)

        width, height, svg_matrix = get_width_height_transform((xmin, ymin), (xmax, ymax), self.margin, self.size)
        print(svg_matrix)
        list_height = get_in_height_order(obj_list)
        print(list_height)

        xml_obj = xml_handler(svg_matrix, width, height)

        for obj in list_height:
            print("working with object: ", obj)
            print(obj.matrix_world)

            xml_obj.add_object(obj)

        xml_obj.save(keywords['filepath'])

        return {'FINISHED'}


def menu_export(self, context):
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".stl"
    self.layout.operator(ExportSVG.bl_idname, text="Svg (.svg)")


def register():
    bpy.utils.register_class(ExportSVG)
    bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
    bpy.utils.register_class(ExportSVG)

    bpy.types.INFO_MT_file_export.remove(menu_export)


if __name__ == "__main__":
    register()



