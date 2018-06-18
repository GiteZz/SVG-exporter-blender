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


def intersect(A,B,C,D):
    """Returns if the line from A to B collides with the line from C to D"""
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


def get_point(value, index, P0, P1, P2, P3):
    """This is the definition of a bezier curve with parameters P0 -> P3.

    The index decides if the function returns x or y (0 for x, 1 for y).
    The value is the t in the formula of a bezier curve, goes from 0 to 1
    """
    return math.pow((1-value),3) * P0[index] + \
        3 * value * math.pow((1-value), 2) * P1[index] + \
        3 * math.pow(value,2) * (1 - value) * P2[index] + \
        math.pow(value,3) * P3[index]


def spline_in_spline(spline1, spline2):
    line_co_0 = [spline1.bezier_points[0].co[0], spline1.bezier_points[0].co[1]]
    co_list = spline_to_co_list(spline2)

    return co_in_co_list(line_co_0, co_list)


def co_in_co_list(co, co_list):
    """Determines is a coordinate is included in the polygon created by the co_list.

    Creates a line from the co to a location far away from the coordinates in the co_list,
    the function loops trough the edges in de co_list (co_list[i] and co_list[i + 1] form an edge).
    If there's a collision it will be counted, uneven amount means the co is in the polygon.
    """
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
    """Takes a blender curve and approximates it with discrete points."""
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
    """Get the maximum in the x and y direction from multiple objects"""
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
    """Sorts objects by their z coordinate"""
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
    """Get the maximum x and y coordinate from a mesh"""
    xmax = -float("inf")
    xmin = float("inf")
    ymax = -float("inf")
    ymin = float("inf")

    for vert in obj.data.vertices:
        vert_trans = obj.matrix_world * vert.co
        if vert_trans[0] > xmax:
            xmax = vert_trans[0]
        if vert_trans[0] < xmin:
            xmin = vert_trans[0]

        if vert_trans[1] > ymax:
            ymax = vert_trans[1]
        if vert_trans[1] < ymin:
            ymin = vert_trans[1]

    return xmin, xmax, ymin, ymax


def get_co_extremes_curve(obj):
    """Get the maximum x and y coordinate from a curve, takes the handles into account."""
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
    """Create a svg path based on a blender object."""
    color_string = get_color_string(obj)
    if obj.type == 'CURVE' and obj.data.dimensions == '3D' or \
        obj.type == 'MESH' and len(obj.data.polygons) == 0:
        print("empty mesh")
        path_string = get_path_string_empty(obj, svg_matrix)
        fill_string = ' fill="none" stroke="' + color_string + '"'
    else:
        print("full mesh")
        path_string = get_path_string_full(obj, svg_matrix)
        fill_string = ' fill="' + color_string + '" '

    id_string = str(obj)[1:-1:].replace('"',"")

    xml_string = '<path id="' + id_string + '" '
    xml_string += 'd="' + path_string + '" '
    xml_string += fill_string
    xml_string += '/>'

    return xml_string

def get_path_string_empty(obj, svg_matrix):
    path_string = ""
    if obj.type == 'CURVE':
        for spline in obj.data.splines:
            path_string += curve_to_svg_path(spline.bezier_points, obj.matrix_world, svg_matrix)
    else:
        verts = obj.data.vertices
        for edge in obj.data.edge_keys:
            print(edge)
            path_string += edge_svg_path([verts[edge[0]].co, verts[edge[1]].co], obj.matrix_world, svg_matrix)
    return path_string


def edge_svg_path(edge, world_matrix, svg_matrix):
    print(world_matrix)
    print(svg_matrix)
    trans_matrix = svg_matrix * world_matrix
    co_n1 = trans_matrix * edge[0]
    co_n2 = trans_matrix * edge[1]
    print("from: ", edge, " to ", co_n1, " , " , co_n2)
    path = " M "
    path += co_to_string_svg(trans_matrix * edge[0])
    path += " L "
    path += co_to_string_svg(trans_matrix * edge[1])
    path += " z"
    return path


def get_color_string(obj):
    """Tries to get the viewport color of the blender object

    Takes the material from the viewport, if the material is not defined then it will choose a grey color.
    """
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
    """Gives a layer hierarchy based on the co_list

    This function first creates a dict with all the relations. A relation is if a loop is in another.
    So if loop a is in loop b, b will be added as key with a as value (in an array). When the dict is
    constructed all the redundant relations will be removed. If A is in B and B in C the relation from
    C with A will be removed. After that the outer most layers will be searched. From the top layers
    down, a hierarchy will be created.
    """
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
    """Normalizes the vector so that the length will be 1."""
    # print(vector)
    length = math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))
    # print("length: %d" % length)
    return [vector[0]/length, vector[1]/length]


def get_direction(co1, co2, normalize=False):
    """Get the directon of the edge thate co1 and co2 create"""
    dx = co1[0] - co2[0]
    dy = co1[1] - co2[1]
    if not normalize:
        return [dx,dy]
    else:
        return normalize_vector([dx,dy])


def get_shared_vertex(edge1, edge2):
    """Gives the shared vertex from two edges.

    Doesn't give an error when there is no shared edge.
    """
    if edge1[0] == edge2[0]:
        return edge1[0]
    if edge1[0] == edge2[1]:
        return edge1[0]
    return edge1[1]


def mesh_to_co_list(obj):
    """Gives a list with loops in the mesh

    This function will return all the edges that are on the outside of the mesh,
    with all the same loop direction.
    """

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
    """Takes loop(co_list) and converts it into a svg path"""
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


def get_path_string_full(obj, svg_matrix):
    """Converts the object to an svg path"""
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


def get_width_height_transform(co_min, co_max, margin, des_size):
    """Calculates the width and height based on the min_size and the coordinates of the objects.

    Based on the difference between the min coordinates and the max it will decide which
    direction will be the desired and which one will be smaller. The margin is the total margin,
    a margin of .5 will have a whitespace of 0.25 left and right. This function also return
    the svg_matrix this is the transformation matrix in order to set the coordinates
    in order to fit in the svg viewport
    """
    margin = margin
    des_size = des_size
    co_min = co_min
    co_max = co_max

    diff_x = co_max[0] - co_min[0]
    diff_y = co_max[1] - co_min[1]

    diff = max(diff_x, diff_y)

    print("max diff is: ", diff)
    print("co_min is: ", co_min)
    print("co_max is: ", co_max)

    target = (1 - margin) * des_size

    scale = target / diff

    print("scale is: ", scale)

    # move everything so that the minimum y and x are 0
    mat_loc1 = mathutils.Matrix.Translation((-co_min[0], co_max[1], 0))
    # scale everything so that max dimension will be between the margins of min_size
    mat_scal = mathutils.Matrix.Scale(scale, 4)
    # svg's y axis is inverted
    mat_invert_y = mathutils.Matrix.Scale(-1, 4, (0, 1, 0))

    if diff_x > diff_y:
        width = des_size
        height = int(des_size * (diff_y / diff_x))
    else:
        height = des_size
        width = int(des_size * (diff_x / diff_y))
    
    # margin is total margin, so left + right
    margin_x = (margin / 2) * width
    margin_y = (margin / 2) * height

    mat_move_margin = mathutils.Matrix.Translation((margin_x, margin_y, 0))

    svg_matrix = mat_move_margin * mat_scal * mat_loc1 * mat_invert_y

    return width, height, svg_matrix


def curve_to_svg_path(curve, world_matrix, svg_matrix, clockwise=True):
    """Takes a curve and convert it into a svg path"""
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
    """Make a coordinate string for svg from a coordinate"""
    return str(co[0]) + " " + str(co[1])


class xml_handler:
    """This class helps with building the xml code"""
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