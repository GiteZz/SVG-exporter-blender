# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <gilles.ballegeer@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return Gilles Ballegeer
# ----------------------------------------------------------------------------

import bpy
import math
import mathutils
import svg_utils
import os
import importlib
importlib.reload(svg_utils)

from svg_utils import *

from bpy.props import (
        StringProperty,
        BoolProperty,
        CollectionProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper_factory,
        axis_conversion,
        )
from bpy.types import (
        Operator,
        OperatorFileListElement,
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

    size = IntProperty(name="Size",
                       default=500,
                       min=1,
                       max=10000)

    def execute(self, context):
        keywords = self.as_keywords()
        print(keywords)

        objects = context.selected_objects  # active object
        xmin, xmax, ymin, ymax = get_co_extremes_mul_obj(objects)
        list_height = get_in_height_order(objects)
        handler = svg_handler((xmin, ymin), (xmax, ymax), self.margin, self.size)
        index = 0
        for obj in list_height:
            print("working with object: ", obj)
            path_string = get_path_string(obj, handler)

            color = obj.data.materials[0].diffuse_color
            color_string = "rgb(" + str(int(255 * color[0])) + "," + str(int(255 * color[1])) + "," + str(
                int(255 * color[2])) + ")"

            handler.add_path(path_string, index, color=color_string)
            index += 1

        handler.terminate_svg()

        file = open(keywords['filepath'], "w")
        file.write(handler.get_xml())
        file.close()

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



