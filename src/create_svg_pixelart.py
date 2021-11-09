# -*- Mode: Python3; coding: utf-8; indent-tabs-mpythoode: nil; tab-width: 4 -*-
'''
    Objective:
        Create pixelart image in SVG.
'''

import os
import sys
import time
import numpy as np
from PIL import Image


PX = 25.4 / 96
TARGETS = {
    "#ID#": "p_",
    "#PX#": 64,
    "#CF#": "#FFFFFF",
    "#CS#": "#000000"
}

PATH, _ = os.path.split(os.path.realpath(__file__))
TEMPLATE = "template.txt"
SVG_PATH = "../output/"

MARKCODE = "    <!-- ##PIXELART## -->"
RECTANGLE = """    <rect
       style="fill:#CF#;fill-opacity:1;stroke:#CS#;stroke-width:0.1;stroke-opacity:1"
       id="#ID#"
       width="#PX#"
       height="#PX#"
       x="#X0#"
       y="#Y0#" />
"""
GROUP="""   <g
     id="g_#ID#" >
#SHAPE#
   </g>
"""

LIMIT = 500      # recursion

nparray = []     # image
visited = []     # pixels
connected = []   # region


def load(path):
    lines = []
    print("Loaded: {}".format(path))
    try:
        f = open(path)
        lines = [line for line in f]
        f.close()
    except Exception:
        print("Error: couldn't open file.")
        pass
    return lines


def save(path, text):
    print("Saved: {}".format(path))
    try:
        f = open(path, "w")
        f.write(text)
        f.close()
    except Exception:
        print("Error: cannot save " + path)
        exit(0)


def text(data):
    txt = ""
    for item in data:
        txt += item 
    return txt


def dec2hex(dec):
    d = "0123456789ABCDEF"
    n = dec % 16
    r = dec // 16
    return d[r] + d[n]


def conect(x, y, fill, pixel_by_group):
    global nparray, visited, connected
    height, width, channels = nparray.shape

    if (pixel_by_group > LIMIT):
        return

    if x < 0 or x >= (width - 1) or y < 0 or y >= (height - 1):
        return

    if not visited[y, x]:
        # Color Models
        if channels == 4:
            r, g, b, a = nparray[y, x]
            if a != 255:
                visited[y, x] = True
                return
        if channels == 3:
            r, g, b = nparray[y, x]
        # Hexadecimal color
        if fill != "#" + dec2hex(r) + dec2hex(g) + dec2hex(b) :
            return
        # Store
        connected += [{'x': x, 'y': y, 'fill': fill}]
        # Update
        visited[y,x] = True
        pixel_by_group += 1

        # Recursion
        conect(x + 1, y, fill, pixel_by_group)      # right
        conect(x, y + 1, fill, pixel_by_group)      # down
        conect(x - 1, y, fill, pixel_by_group)      # left
        conect(x, y - 1, fill, pixel_by_group)      # up
        conect(x + 1, y + 1, fill, pixel_by_group)  # right, down
        conect(x - 1, y + 1, fill, pixel_by_group)  # left, down
        conect(x + 1, y - 1, fill, pixel_by_group)  # right, up
        conect(x - 1, y - 1, fill, pixel_by_group)  # left, up


def create(image_path):
    global nparray, visited, connected

    # Inform
    start = time.time()
    print("Attention: Slow algorithm for large images!")

    # Load image
    try:
        print("Loaded: {}".format(image_path))
        img = Image.open(image_path)
        nparray = np.array(img)
        height, width, channels = nparray.shape
        print("Image {0} x {1} : {2} channels".format(height, width, channels))
        if channels < 3:
            print("RGB images only!")
            exit(0)
    except Exception:
        print("Error: couldn't open file \"{0}\".".format(image_path))
        exit(0)

    # Check output directory
    if not os.path.exists(SVG_PATH):
        print("Create " + SVG_PATH)
        os.makedirs(SVG_PATH)

    # Filename
    file = os.path.basename(image_path)
    filename = os.path.splitext(file)[0]

    # SVG base
    svg = text(load(TEMPLATE))
    svg = svg.replace("#VBX#", str(width * TARGETS["#PX#"] * PX))
    svg = svg.replace("#VBY#", str(height * TARGETS["#PX#"] * PX))
         
    base = RECTANGLE
    base = base.replace("#PX#", str(TARGETS["#PX#"] * PX))
    base = base.replace("#CS#", TARGETS["#CS#"]) 

    print("Start processing ...")

    # Create pixels
    counter = 0
    rectangles = ""
    visited = np.zeros((height, width))
    for x in range(0, width):
        for y in range(0, height):
            if visited[y, x]:
                continue
            # Color Models
            if channels == 4:
                r, g, b, a = nparray[y, x]
                if a != 255:
                    visited[y, x] = True
                    continue
            if channels == 3:
                r, g, b = nparray[y, x]
            # Hexadecimal color
            fill = "#" + dec2hex(r) + dec2hex(g) + dec2hex(b)
            # SVG
            connected = []
            conect(x, y, fill, 0)
            if len(connected) == 0:
                continue
            temp = ""
            for pixel in connected:
                s = base
                s = s.replace("#CF#", pixel['fill'])
                s = s.replace("#ID#", TARGETS["#ID#"] + str(pixel['y'] * width + pixel['x']))
                s = s.replace("#X0#", str(pixel['x'] * TARGETS["#PX#"] * PX))
                s = s.replace("#Y0#", str(pixel['y'] * TARGETS["#PX#"] * PX))
                temp += s
            if len(connected) > 1:
                g = GROUP.replace("#ID#", str(counter))
                temp = g.replace("#SHAPE#", temp)
                counter += 1
            rectangles += temp

    # Time
    end = time.time()
    print("Finished! Time: {0:.2f} seconds".format(end - start))

    # Save
    svg = svg.replace(MARKCODE, rectangles)
    save(SVG_PATH + filename + ".svg", svg)


def main(args):

    print("Check ...", args)
    if len(args) != 2:
        print("Use: python3 create_svg_pixelart.py <image-filename>")
        exit(0)

    create(args[-1])
    

if __name__ == '__main__':

    # Test
    # create("../images/image_test_1.png")
    # create("../images/image_test_2.jpg")
    # create("../images/bonsai.png")

    # Run 
    main(sys.argv)
