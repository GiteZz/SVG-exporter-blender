# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <gilles.ballegeer@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return Gilles Ballegeer
# ----------------------------------------------------------------------------

import bpy
import math
import mathutils

class svg_handler:
    def __init__(self, co_min, co_max, margin, min_size):
        self.margin = margin
        self.min_size = min_size
        self.co_min = co_min
        self.co_max = co_max

        self.x_raw_width = (co_max[0] - co_min[0])
        self.y_raw_width = (co_max[1] - co_min[1])

        diff_x = co_max[0] - co_min[0]
        diff_y = co_max[1] - co_min[1]

        diff = max(diff_x, diff_y)

        target = (1-margin) * min_size

        scale = target/diff

        mat_loc1 = mathutils.Matrix.Translation((-self.co_min[0], self.co_max[1], 0))
        print(mat_loc1)
        mat_scal = mathutils.Matrix.Scale(scale, 4)
        mat_invert_y = mathutils.Matrix.Scale(-1, 4, (0, 1, 0))

        self.scalefactor = max(self.min_size / self.x_raw_width, self.min_size / self.y_raw_width)

        if diff_x > diff_y:
            self.width = min_size
            self.height = int(min_size * (diff_y / diff_x))
        else:
            self.height = min_size
            self.width = int(min_size * (diff_x / diff_y))

        self.margin_x = (margin / 2) * self.width
        self.margin_y = (margin / 2) * self.height

        mat_move_margin = mathutils.Matrix.Translation((self.margin_x, self.margin_y, 0))

        self.mat = mat_move_margin * mat_scal * mat_loc1 * mat_invert_y
    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

    def curve_to_xml(self, curve, world_matrix, clockwise=True):
        path_string = ""
        amount_point = len(curve)

        for i in range(amount_point):
            if i == 0:
                start_co = self.mat * world_matrix * curve[0].co
                path_string += " M " + str(start_co[0])
                path_string += " " + str(start_co[1])

            if clockwise:
                current_handle = curve[i].handle_right
                co_next = curve[(i + 1) % amount_point].co
                co_next_handle = curve[(i + 1) % amount_point].handle_left
            else:
                current_handle = curve[-i].handle_left
                co_next = curve[-1*(i + 1) % amount_point].co
                co_next_handle = curve[-1*(i + 1) % amount_point].handle_right

            current_handle = self.mat * world_matrix * current_handle
            co_next = self.mat * world_matrix * co_next
            co_next_handle = self.mat * world_matrix * co_next_handle

            path_string += " C "
            path_string += str(current_handle[0])
            path_string += " "
            path_string += str(current_handle[1])

            path_string += ", "
            path_string += str(co_next_handle[0])
            path_string += " "
            path_string += str(co_next_handle[1])

            path_string += ", "
            path_string += str(co_next[0])
            path_string += " "
            path_string += str(co_next[1])

        path_string += 'z'
        return path_string


def in_other_key(search_dict, search_value):
    for key in search_dict:
        if search_value in search_dict[key]:
            return key
    return None


def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])


# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


def get_point(value, index, P0, P1, P2, P3):
    return math.pow((1-value),3) * P0[index] + \
        3 * value * math.pow((1-value), 2) * P1[index] + \
        3 * math.pow(value,2) * (1 - value) * P2[index] + \
        math.pow(value,3) * P3[index]


def spline_in_spline(spline2, spline1):
    line_co_0 = [spline1.bezier_points[0].co[0], spline1.bezier_points[0].co[1]]
    line_co_1 = [line_co_0[0] + 2*xmax, line_co_0[1] + ymax]

    amount_intersection = 0
    amount_beziers = len(spline2.bezier_points)

    for curve_index in range(amount_beziers):
        P0 = spline2.bezier_points[curve_index].co
        P1 = spline2.bezier_points[curve_index].handle_right
        P2 = spline2.bezier_points[(curve_index + 1) % amount_beziers].handle_left
        P3 = spline2.bezier_points[(curve_index + 1) % amount_beziers].co

        for i in range(10):
            cob0 = (get_point(i / 10, 0, P0, P1, P2, P3), get_point(i / 10, 1, P0, P1, P2, P3))
            cob1 = (get_point((i + 1) / 10, 0, P0, P1, P2, P3), get_point((i + 1) / 10, 1, P0, P1, P2, P3))
            amount_intersection += intersect(line_co_0, line_co_1, cob0, cob1)
    return amount_intersection % 2 != 0


def get_co_extremes(obj):
    curves = obj.data.splines
    xmax = -float("inf")

    xmin = float("inf")

    ymax = -float("inf")

    ymin = float("inf")

    # iterate over points of the curve's first spline
    for spline in curves:
        for p in spline.bezier_points:
            co = obj.matrix_world * p.co
            co_handle_left = obj.matrix_world * p.handle_left
            co_handle_right = obj.matrix_world * p.handle_right

            if co[0] > xmax:
                xmax = co[0]
            if co[0] < xmin:
                xmin = co[0]
            if co[1] > ymax:
                ymax = co[1]
            if co[1] < ymin:
                ymin = co[1]

            if co_handle_right[0] > xmax:
                xmax = co_handle_right[0]
            if co_handle_right[0] < xmin:
                xmin = co_handle_right[0]
            if co_handle_right[1] > ymax:
                ymax = co_handle_right[1]
            if co_handle_right[1] < ymin:
                ymin = co_handle_right[1]

            if co_handle_left[0] > xmax:
                xmax = co_handle_left[0]
            if co_handle_left[0] < xmin:
                xmin = co_handle_left[0]
            if co_handle_left[1] > ymax:
                ymax = co_handle_left[1]
            if co_handle_left[1] < ymin:
                ymin = co_handle_left[1]

    return xmin, xmax, ymin, ymax


def get_path_string(obj, handler):
    curves = obj.data.splines
    path_string = ""
    layers = {}
    layer_hier = []
    amount_curves = len(curves)
    # create list with all the relations
    # relation is if a curve is within another curve
    # when curve is outside other it will not be added
    for spline_index1 in range(amount_curves):
        for spline_index2 in range(spline_index1 + 1, amount_curves, 1):
            # spline_in_spline doesn't care about the rotation, position and scaling from the object
            if spline_in_spline(curves[spline_index1], curves[spline_index2]):
                if curves[spline_index1] not in layers:
                    layers[curves[spline_index1]] = [curves[spline_index2]]
                else:
                    layers[curves[spline_index1]].append(curves[spline_index2])

            if spline_in_spline(curves[spline_index2], curves[spline_index1]):
                if curves[spline_index2] not in layers:
                    layers[curves[spline_index2]] = [curves[spline_index1]]
                else:
                    layers[curves[spline_index2]].append(curves[spline_index1])

    # when a is in b and b in c, then a will also be in relation with c, remove that relation
    keys = list(layers.keys())
    for key in keys:
        for spline in layers[key]:
            if spline in keys:
                for rem_spline in layers[spline]:
                    layers[key].remove(rem_spline)

    # find top layers
    not_visited_keys = list(curves)
    top_list = []
    while len(not_visited_keys) != 0:
        top_key = not_visited_keys[0]
        at_top = False

        while not at_top:
            new_key = in_other_key(layers, top_key)
            if new_key is not None:
                top_key = new_key
            else:
                at_top = True
                top_list.append(top_key)
                # descend and remove every key in relation with top
                remove_list = [top_key]
                prev_length = 0
                start_index = 0
                while len(remove_list) != prev_length:
                    prev_length = len(remove_list)
                    for i in range(start_index, len(remove_list), 1):
                        if remove_list[i] in layers:
                            remove_list.extend(layers[remove_list[i]])
                        start_index = prev_length
                for key in remove_list:
                    not_visited_keys.remove(key)

    layer_hier.append(top_list)
    layer_index = 0
    while (len(layer_hier[layer_index]) != 0):
        layer_hier.append([])
        for key in layer_hier[layer_index]:
            if key in layers:
                layer_hier[layer_index + 1].extend(layers[key])
        layer_index += 1

    inverted = True
    for layer in layer_hier:
        inverted = not inverted
        for spline in layer:
            path_string += handler.curve_to_xml(spline.bezier_points, obj.matrix_world, inverted)

    return path_string

print("============================================")
print("============= Start of program =============")
print("============================================")

objects = bpy.context.selected_objects# active object

xmax = -float("inf")

xmin = float("inf")

ymax = -float("inf")

ymin = float("inf")

list_height = []

for obj in objects:
    if obj.type == 'CURVE':
        xmin_n, xmax_n, ymin_n, ymax_n = get_co_extremes(obj)

        if xmin_n < xmin:
            xmin = xmin_n
        if xmax_n > xmax:
            xmax = xmax_n
        if ymin_n < ymin:
            ymin = ymin_n
        if ymax_n > ymax:
            ymax = ymax_n

        height = obj.location[2]

        if len(list_height) == 0:
            list_height.append(obj)
        else:
            inserted = False
            for i in range(len(list_height)):
                if list_height[i].location[2] > height:
                    list_height.insert(i, obj)
                    break
            if not inserted:
                list_height.append(obj)

print(xmin,xmax,ymin,ymax)

print(list_height)

handler = svg_handler((xmin, ymin), (xmax, ymax), 0, 500)

width = handler.get_width()
height = handler.get_height()

svg_string = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
svg_string += '<svg width="' + str(width) + '" height="' + str(height) + '" viewBox="0 0 ' + str(width) + ' ' + str(height) + '" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="xMidYMid">\n'


path_set = {}
index = 0
for obj in list_height:
    print("working with object: ", obj)
    path_string = get_path_string(obj, handler)

    color = obj.data.materials[0].diffuse_color
    color_string = "rgb(" + str(int(255 * color[0])) + "," + str(int(255 * color[1])) + "," + str(int(255 * color[2])) + ")"

    svg_string += '<path id="line' + str(index) + '" d="' + path_string + '" fill="' + color_string + '" />\n'
    index += 1


svg_string += '</svg>'

file = open("D:/gilles.svg","w")
file.write(svg_string)
file.close()