import mathutils
import bpy
import math
import sys

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


def spline_in_spline(spline1, spline2):
    line_co_0 = [spline1.bezier_points[0].co[0], spline1.bezier_points[0].co[1]]
    co_list = spline_to_co_list(spline2)

    return co_in_co_list(line_co_0, co_list)


def co_in_co_list(co, co_list):
    line_co_0 = [co[0], co[1]]
    line_co_1 = [line_co_0[0] + 2 * 8, line_co_0[1] + 8]
    amount_intersection = 0
    amount_co = len(co_list)

    for co_index in range(amount_co):
        cob0 = co_list[co_index]
        cob1 = co_list[(co_index + 1) % amount_co]
        amount_intersection += intersect(line_co_0, line_co_1, cob0, cob1)
    return amount_intersection % 2 != 0


def spline_to_co_list(spline):
    co_list = []
    amount_beziers = len(spline.bezier_points)
    for curve_index in range(amount_beziers):
        co_list.append(spline.bezier_points[curve_index].co)
        detail = 4

        P0 = spline.bezier_points[curve_index].co
        P1 = spline.bezier_points[curve_index].handle_right
        P2 = spline.bezier_points[(curve_index + 1) % amount_beziers].handle_left
        P3 = spline.bezier_points[(curve_index + 1) % amount_beziers].co

        for i in range(1, detail, 1):
            co_list.append([get_point(i / detail, 0, P0, P1, P2, P3), get_point(i / detail, 1, P0, P1, P2, P3)])

    return co_list


def get_co_extremes_mul_obj(objects):
    xmax = -float("inf")

    xmin = float("inf")

    ymax = -float("inf")

    ymin = float("inf")

    for obj in objects:
        if obj.type == 'CURVE':
            xmin_n, xmax_n, ymin_n, ymax_n = get_co_extremes_obj(obj)

            if xmin_n < xmin:
                xmin = xmin_n
            if xmax_n > xmax:
                xmax = xmax_n
            if ymin_n < ymin:
                ymin = ymin_n
            if ymax_n > ymax:
                ymax = ymax_n

    return xmin, xmax, ymin, ymax


def get_in_height_order(objects):
    list_height = []
    for obj in objects:
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
    return list_height


def get_co_extremes_obj(obj):
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


def obj_to_xml(obj, svg_matrix):
    path_string = get_path_string(obj, svg_matrix)
    color_string = get_color_string(obj)
    id_string = str(obj)[1:-1:].replace('"',"")

    xml_string = '<path id="' + id_string + '" '
    xml_string += 'd="' + path_string + '" '
    xml_string += ' fill="' + color_string + '" '
    xml_string += '/>'

    return xml_string


def get_color_string(obj):
    try:
        color = obj.data.materials[0].diffuse_color
    except:
        color = (0.5, 0.5, 0.5)

    color_string = "rgb("
    color_string += str(int(255 * color[0])) + ","
    color_string += str(int(255 * color[1])) + ","
    color_string += str(int(255 * color[2]))
    color_string += ")"

    return color_string

def get_path_string(obj, svg_matrix):
    curves = obj.data.splines
    path_string = ""
    layers = {}
    layer_hier = []
    amount_curves = len(curves)
    # create list with all the relations
    # relation is if a curve is within another curve
    # when curve is outside other it will not be added
    # spline is in array from key is its inside
    for spline_index1 in range(amount_curves):
        for spline_index2 in range(spline_index1 + 1, amount_curves, 1):
            # spline_in_spline doesn't care about the rotation, position and scaling from the object
            if spline_in_spline(curves[spline_index2], curves[spline_index1]):
                if curves[spline_index1] not in layers:
                    layers[curves[spline_index1]] = [curves[spline_index2]]
                else:
                    layers[curves[spline_index1]].append(curves[spline_index2])

            if spline_in_spline(curves[spline_index1], curves[spline_index2]):
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
            path_string += curve_to_svg_path(spline.bezier_points, obj.matrix_world, svg_matrix, inverted)

    return path_string


def get_width_height_transform(co_min,co_max, margin, min_size):
    margin = margin
    min_size = min_size
    co_min = co_min
    co_max = co_max

    diff_x = co_max[0] - co_min[0]
    diff_y = co_max[1] - co_min[1]

    diff = max(diff_x, diff_y)

    target = (1 - margin) * min_size

    scale = target / diff

    # move everything so that the minimum y and x are 0
    mat_loc1 = mathutils.Matrix.Translation((-co_min[0], co_max[1], 0))
    # scale everything so that max dimension will be between the margins of min_size
    mat_scal = mathutils.Matrix.Scale(scale, 4)
    # svg's y axis is inverted
    mat_invert_y = mathutils.Matrix.Scale(-1, 4, (0, 1, 0))

    if diff_x > diff_y:
        width = min_size
        height = int(min_size * (diff_y / diff_x))
    else:
        height = min_size
        width = int(min_size * (diff_x / diff_y))
    
    # margin is total margin, so left + right
    margin_x = (margin / 2) * width
    margin_y = (margin / 2) * height

    mat_move_margin = mathutils.Matrix.Translation((margin_x, margin_y, 0))

    svg_matrix = mat_move_margin * mat_scal * mat_loc1 * mat_invert_y

    return width, height, svg_matrix


def curve_to_svg_path(curve, world_matrix, svg_matrix, clockwise=True):
    path_string = ""
    amount_point = len(curve)
    
    trans_matrix = svg_matrix * world_matrix
    
    for i in range(amount_point):
        if i == 0:
            start_co = trans_matrix * curve[0].co
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

        current_handle = trans_matrix * current_handle
        co_next = trans_matrix * co_next
        co_next_handle = trans_matrix * co_next_handle

        path_string += " C "
        path_string += co_to_string_svg(current_handle)

        path_string += ", "
        path_string += co_to_string_svg(co_next_handle)

        path_string += ", "
        path_string += co_to_string_svg(co_next)

    path_string += 'z'
    return path_string


def co_to_string_svg(co):
    return str(co[0]) + " " + str(co[1])


class xml_handler:
    def __init__(self, svg_transfrom, width, height):
        self.xml = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        self.xml += '<svg width="' + str(width) + '" '
        self.xml += 'height="' + str(height) + '" '
        self.xml += 'viewBox="0 0 ' + str(width) + ' ' + str(height) + '" '
        self.xml += 'version="1.1" '
        self.xml += 'xmlns="http://www.w3.org/2000/svg" '
        self.xml += 'xmlns:xlink="http://www.w3.org/1999/xlink" '
        self.xml += 'preserveAspectRatio="xMidYMid">'

        self.svg_transform = svg_transfrom

    def add_object(self, obj):
        self.xml += "\n"
        self.xml += obj_to_xml(obj, self.svg_transform)

    def save(self, location):
        self.xml += '\n</svg>'
        file = open(location, "w")
        file.write(self.xml)
        file.close()