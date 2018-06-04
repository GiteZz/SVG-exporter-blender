import bpy

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



ob = bpy.context.object # active object

xmax = -float("inf")
xmin = float("inf")

ymax = -float("inf")
ymin = float("inf")
bezier_points = ob.data.splines.active.bezier_points
# iterate over points of the curve's first spline
for p in bezier_points:
    if p.handle_right[0] > xmax:
        xmax = p.co[0]
    if p.handle_right[0] < xmin:
        xmin = p.co[0]
    if p.handle_right[1] > ymax:
        ymax = p.co[1]
    if p.handle_right[1] < ymin:
        ymin = p.co[1]

    if p.handle_left[0] > xmax:
        xmax = p.co[0]
    if p.handle_left[0] < xmin:
        xmin = p.co[0]
    if p.handle_left[1] > ymax:
        ymax = p.co[1]
    if p.handle_left[1] < ymin:
        ymin = p.co[1]

print("minimum is :", xmin)
print("maximum is :", xmax)

handler = svg_handler((xmin, ymin), (xmax, ymax), 0.2, 100)

path_string = ""

#"C 0 100, 100 100, 100 0"


amount_point = len(bezier_points)

for i in range(amount_point):
    if i == 0:
        path_string += "M " + handler.get_x_str(bezier_points[0].co[0])
        path_string += " " + handler.get_y_str(bezier_points[0].co[1])

    path_string += " C "
    path_string += handler.get_x_str(bezier_points[i].handle_right[0])
    path_string += " "
    path_string += handler.get_y_str(bezier_points[i].handle_right[1])

    path_string += ", "
    path_string += handler.get_x_str(bezier_points[(i + 1) % amount_point].handle_left[0])
    path_string += " "
    path_string += handler.get_y_str(bezier_points[(i + 1) % amount_point].handle_left[1])

    path_string += ", "
    path_string += handler.get_x_str(bezier_points[(i + 1) % amount_point].co[0])
    path_string += " "
    path_string += handler.get_y_str(bezier_points[(i + 1) % amount_point].co[1])


print(path_string)