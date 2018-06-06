import bpy
import math

class svg_handler:
    def __init__(self, co_min, co_max, margin, min_size):
        self.margin = margin
        self.min_size = min_size
        self.co_min = co_min
        self.co_max = co_max

        self.x_raw_width = (co_max[0] - co_min[0])
        self.y_raw_width = (co_max[1] - co_min[1])

        self.scalefactor = max(self.min_size / self.x_raw_width, self.min_size / self.y_raw_width)

        self.x_svg_width_no_margin = self.x_raw_width * self.scalefactor
        self.x_margin_width = self.x_svg_width_no_margin * (self.margin / 2)
        self.x_svg_width = self.x_svg_width_no_margin + 2 * self.x_margin_width

        self.y_svg_width_no_margin = self.y_raw_width * self.scalefactor
        self.y_margin_width = self.y_svg_width_no_margin * (self.margin / 2)
        self.y_svg_width = self.y_svg_width_no_margin + 2 * self.y_margin_width

    def get_x(self, x_co):
        return (x_co - self.co_min[0]) * self.scalefactor + self.x_margin_width

    def get_y(self, y_co):
        y_loc = (y_co - self.co_min[1]) * self.scalefactor
        return self.y_svg_width - y_loc + self.y_margin_width

    def get_x_str(self, x_co):
        return str(self.get_x(x_co))

    def get_y_str(self, y_co):
        return str(self.get_y(y_co))

    def curve_to_xml(self, curve, clockwise=True):
        path_string = ""
        amount_point = len(curve)

        for i in range(amount_point):
            if i == 0:
                path_string += " M " + self.get_x_str(curve[0].co[0])
                path_string += " " + self.get_y_str(curve[0].co[1])

            if clockwise:
                path_string += " C "
                path_string += self.get_x_str(curve[i].handle_right[0])
                path_string += " "
                path_string += self.get_y_str(curve[i].handle_right[1])

                path_string += ", "
                path_string += self.get_x_str(curve[(i + 1) % amount_point].handle_left[0])
                path_string += " "
                path_string += self.get_y_str(curve[(i + 1) % amount_point].handle_left[1])

                path_string += ", "
                path_string += self.get_x_str(curve[(i + 1) % amount_point].co[0])
                path_string += " "
                path_string += self.get_y_str(curve[(i + 1) % amount_point].co[1])
            else:
                path_string += " C "
                path_string += self.get_x_str(curve[-i].handle_left[0])
                path_string += " "
                path_string += self.get_y_str(curve[-i].handle_left[1])

                path_string += ", "
                path_string += self.get_x_str(curve[-1*(i + 1) % amount_point].handle_right[0])
                path_string += " "
                path_string += self.get_y_str(curve[-1*(i + 1) % amount_point].handle_right[1])

                path_string += ", "
                path_string += self.get_x_str(curve[-1*(i + 1) % amount_point].co[0])
                path_string += " "
                path_string += self.get_y_str(curve[-1*(i + 1) % amount_point].co[1])
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
    print(line_co_0)
    print(line_co_1)
    for curve_index in range(amount_beziers):
        P0 = spline2.bezier_points[curve_index].co
        P1 = spline2.bezier_points[curve_index].handle_right
        P2 = spline2.bezier_points[(curve_index + 1) % amount_beziers].handle_left
        P3 = spline2.bezier_points[(curve_index + 1) % amount_beziers].co

        for i in range(10):
            cob0 = (get_point(i / 10, 0, P0, P1, P2, P3), get_point(i / 10, 1, P0, P1, P2, P3))
            cob1 = (get_point((i + 1) / 10, 0, P0, P1, P2, P3), get_point((i + 1) / 10, 1, P0, P1, P2, P3))
            amount_intersection += intersect(line_co_0, line_co_1, cob0, cob1)
    print(amount_intersection)
    return amount_intersection % 2 != 0

ob = bpy.context.object # active object
curves = ob.data.splines

xmax = -float("inf")
x_max_spline = curves[0]

xmin = float("inf")
x_min_spline = curves[0]

ymax = -float("inf")
ymax_spline = curves[0]

ymin = float("inf")
ymin_spline = curves[0]

# iterate over points of the curve's first spline
for spline in curves:
    for p in spline.bezier_points:
        if p.co[0] > xmax:
            xmax = p.co[0]
            x_max_spline = spline
        if p.co[0] < xmin:
            xmin = p.co[0]

        if p.handle_right[0] > xmax:
            xmax = p.handle_right[0]
            x_max_spline = spline
        if p.handle_right[0] < xmin:
            xmin = p.handle_right[0]
        if p.handle_right[1] > ymax:
            ymax = p.handle_right[1]
        if p.handle_right[1] < ymin:
            ymin = p.handle_right[1]

        if p.handle_left[0] > xmax:
            xmax = p.handle_left[0]
            x_max_spline = spline
        if p.handle_left[0] < xmin:
            xmin = p.handle_left[0]
        if p.handle_left[1] > ymax:
            ymax = p.handle_left[1]
        if p.handle_left[1] < ymin:
            ymin = p.handle_left[1]

svg_string = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
svg_string += '<svg width="120px" height="120px" viewBox="0 0 256 315" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" preserveAspectRatio="xMidYMid">\n'


print("minimum is :", xmin)
print("maximum is :", xmax)

handler = svg_handler((xmin, ymin), (xmax, ymax), 0.2, 100)

path_string = ""
layers = {}
layer_hier = []
amount_curves = len(curves)

# create list with all the relations
# relation is if a curve is within another curve
# when curve is outside other it will not be added
for spline_index1 in range(amount_curves):
    for spline_index2 in range(spline_index1 + 1,amount_curves,1):
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

# find top layer
top_key = keys[0]
at_top = False
while not at_top:
    new_key = in_other_key(layers, top_key)
    if new_key is not None:
        top_key = new_key
    else:
        at_top = True

for key in layers:
    print(key.bezier_points[0].co)
    for s in layers[key]:
        print('/t', s.bezier_points[0].co)

print('top key: ')
print(top_key.bezier_points[0].co)

layer_hier.append([top_key])
layer_index = 0
while(len(layer_hier[layer_index]) != 0):
    layer_hier.append([])
    for key in layer_hier[layer_index]:
        if key in layers:
            layer_hier[layer_index + 1].extend(layers[key])
    print(layer_hier[layer_index])
    layer_index += 1



print(layers)

print(path_string)
svg_string += '<path id="lineAB" d="' + path_string + '" fill="red" />\n'
svg_string += '</svg>'

file = open("D:/gilles.svg","w")
file.write(svg_string)
file.close()