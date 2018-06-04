import bpy
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

margin = 0.2
scalefactor = 1

x_raw_width = (xmax - xmin)
x_svg_width_no_margin = x_raw_width * scalefactor
x_margin_width = x_svg_width_no_margin * (margin/2)
x_svg_width = x_svg_width_no_margin + 2 * x_margin_width

y_raw_width = (ymax - ymin)
y_svg_width_no_margin = y_raw_width * scalefactor
y_margin_width = y_svg_width_no_margin * (margin/2)
y_svg_width = y_svg_width_no_margin + 2 * y_margin_width

path_string = ""

#"C 0 100, 100 100, 100 0"


amount_point = len(bezier_points)

for i in range(amount_point):
    if i == 0:
        path_string += "M " + str((bezier_points[0].co[0]-xmin)*scalefactor + x_margin_width)
        path_string += " " + str((bezier_points[0].co[1]-ymin)*scalefactor + y_margin_width)

    path_string += " C "
    path_string += str((bezier_points[i].handle_right[0] - xmin) * scalefactor + x_margin_width)
    path_string += " "
    path_string += str((bezier_points[i].handle_right[1] - ymin) * scalefactor + y_margin_width)

    path_string += ", "
    path_string += str((bezier_points[(i + 1) % amount_point].handle_left[0] - xmin) * scalefactor + x_margin_width)
    path_string += " "
    path_string += str((bezier_points[(i + 1) % amount_point].handle_left[1] - ymin) * scalefactor + y_margin_width)

    path_string += ", "
    path_string += str((bezier_points[(i + 1) % amount_point].co[0] - xmin) * scalefactor + x_margin_width)
    path_string += " "
    path_string += str((bezier_points[(i + 1) % amount_point].co[1] - ymin) * scalefactor + y_margin_width)


print(path_string)