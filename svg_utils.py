import mathutils
import bpy
import math

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
            xmin_n, xmax_n, ymin_n, ymax_n = get_co_extremes_curve(obj)
        else:
            xmin_n, xmax_n, ymin_n, ymax_n = get_co_extremes_mesh(obj)

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
                    inserted = True
                    break
            if not inserted:
                list_height.append(obj)
    return list_height


def get_co_extremes_mesh(obj):
    xmax = -float("inf")
    xmin = float("inf")
    ymax = -float("inf")
    ymin = float("inf")

    for verts in obj.data.vertices:
        if verts.co[0] > xmax:
            xmax = verts.co[0]
        if verts.co[0] < xmin:
            xmin = verts.co[0]

        if verts.co[1] > ymax:
            ymax = verts.co[1]
        if verts.co[1] < ymin:
            ymin = verts.co[1]

    return xmin, xmax, ymin, ymax


def get_co_extremes_curve(obj):
    xmax = -float("inf")
    xmin = float("inf")
    ymax = -float("inf")
    ymin = float("inf")

    # iterate over points of the curve's first spline
    for spline in obj.data.splines:
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

def get_layer_relation(co_list):
    layers = {}
    layer_hier = []
    amount_co = len(co_list)
    for co_list_index1 in range(amount_co):
        for co_list_index2 in range(co_list_index1 + 1, amount_co, 1):
            # 2 in 1
            if co_in_co_list(co_list[co_list_index2][0], co_list[co_list_index1]):
                if co_list_index1 not in layers:
                    layers[co_list_index1] = [co_list_index2]
                else:
                    layers[co_list_index1].append(co_list_index2)
            # 1 in 2
            if co_in_co_list(co_list[co_list_index1][0], co_list[co_list_index2]):
                if co_list_index2 not in layers:
                    layers[co_list_index2] = [co_list_index1]
                else:
                    layers[co_list_index2].append(co_list_index1)

    for key in layers:
        print(key)
        for co in layers[key]:
            print("   ", co)

    # when a is in b and b in c, then a will also be in relation with c, remove that relation
    keys = list(layers.keys())
    for key in keys:
        for spline in layers[key]:
            if spline in keys:
                for rem_spline in layers[spline]:
                    layers[key].remove(rem_spline)

    # find top layers
    not_visited_keys = list(range(len(co_list)))
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
    while len(layer_hier[layer_index]) != 0:
        layer_hier.append([])
        for key in layer_hier[layer_index]:
            if key in layers:
                layer_hier[layer_index + 1].extend(layers[key])
        layer_index += 1

    return layer_hier


def normalize_vector(vector):
    # print(vector)
    length = math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))
    # print("length: %d" % length)
    return [vector[0]/length, vector[1]/length]


def get_direction(co1, co2, normalize=False):
    dx = co1[0] - co2[0]
    dy = co1[1] - co2[1]
    if not normalize:
        return [dx,dy]
    else:
        return normalize_vector([dx,dy])


def get_shared_vertex(edge1, edge2):
    if edge1[0] == edge2[0]:
        return edge1[0]
    if edge1[0] == edge2[1]:
        return edge1[0]
    return edge1[1]


def mesh_to_co_list(obj):
    # goes trough all the face and save the connected edges, if an edge only has one face then it is an outside edge
    facedict = {}
    for f in obj.data.polygons:
        for e in f.edge_keys:
            if e in facedict:
                facedict[e] += 1
            else:
                facedict[e] = 1
    edges = []
    for e in facedict:
        if facedict[e] == 1:
            print(e)
            edges.append(e)

    # create the individual loops from all the outside edges
    start_edge = edges.pop(0)
    current_start_vert = start_edge[0]
    current_end_vert = start_edge[1]
    edge_list = [[start_edge]]
    edge_index = 0
    new_list = False
    while len(edges) != 0:
        for e in edges:
            if e[0] == current_start_vert:
                edge_list[edge_index].append(e)
                edges.remove(e)
                if e[1] == current_end_vert:
                    new_list = True
                else:
                    current_start_vert = e[1]
                break
            elif e[1] == current_start_vert:
                edge_list[edge_index].append(e)

                edges.remove(e)
                if e[0] == current_end_vert:
                    new_list = True
                else:
                    current_start_vert = e[0]
                break

            if new_list:
                if len(edges) > 0:
                    start_edge = edges.pop(0)
                    current_start_vert = start_edge[0]
                    current_end_vert = start_edge[1]
                    edge_list.append([start_edge])
                    edge_index += 1
                    new_list = False
                break

    # create the coordinate list from the edge list, goes trough the last and takes the common vertex
    co_list = [[] for i in range(len(edge_list))]
    for loop_index in range(len(edge_list)):
        for edge_index in range(-1, len(edge_list[loop_index]) - 1, 1):
            shared_v = get_shared_vertex(edge_list[loop_index][edge_index], edge_list[loop_index][edge_index + 1])
            co_list[loop_index].append(obj.data.vertices[shared_v].co)

    # set loop orientation the same for every loop
    for loop_index in range(len(co_list)):
        dir1 = get_direction(co_list[loop_index][1], co_list[loop_index][0], normalize=True)[1]
        dir2 = get_direction(co_list[loop_index][-1], co_list[loop_index][0], normalize=True)[1]

        if dir2 > dir1:
            co_list[loop_index] = co_list[loop_index][::-1]

    return co_list


def loop_to_svg_path(loop, matrix_world, svg_matrix, inverted=False):
    transform_matrix = svg_matrix * matrix_world
    path_string = ""
    for co_index in range(len(loop)):
        if co_index == 0:
            path_string += " M"
        else:
            path_string += " L"

        if inverted:
            co = loop[len(loop) - 1 - co_index]
        else:
            co = loop[co_index]

        co = transform_matrix * co
        path_string += co_to_string_svg(co)

    path_string += "Z"
    return path_string


def get_path_string(obj, svg_matrix):
    if obj.type == 'CURVE':
        co_list = [spline_to_co_list(curve) for curve in obj.data.splines]
    else:
        co_list = mesh_to_co_list(obj)

    layer_hier = get_layer_relation(co_list)
    path_string = ""

    inverted = True
    for layer in layer_hier:
        inverted = not inverted
        for loop_index in layer:
            if obj.type == 'CURVE':
                path_string += curve_to_svg_path(obj.data.splines[loop_index].bezier_points, obj.matrix_world, svg_matrix, inverted)
            else:
                path_string += loop_to_svg_path(co_list[loop_index], obj.matrix_world, svg_matrix, inverted)

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