# SVG exporter for Blender

This script takes the 2D bezier curves from blender and creates a svg file from them.
The exporter currently supports multiple object but they all have to be of the 'CURVE' type,
support for mesh object will probably come in the future.

The script at the moment is not configured as an addon so it just works by running it in the text editor,
currently programming the program to show up in the exporter list.

There are some options when exporting:
* desired width: this set the size of the svg to be exported, maximum x/y difference changes the size so max width or max height
* margin: this adds a border to the sides, doesn't affect the size

Currently the color comes from the viewport color defined in the material