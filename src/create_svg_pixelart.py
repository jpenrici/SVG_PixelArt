# -*- Mode: Python3; coding: utf-8; indent-tabs-mpythoode: nil; tab-width: 4 -*-
'''
    Objective:
        Create pixelart image in SVG.
'''

import os
import sys
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


def create(image_path):
    # Load image
    try:
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

    # Create pixels
    rectangles = ""
    for x in range(0, width):
        for y in range(0, height):
            # Color Models
            if channels == 4:
                r, g, b, a = nparray[y, x]
                if a != 255:
                    continue
            if channels == 3:
                r, g, b = nparray[y, x]
            # Hexadecimal color
            fill = "#" + dec2hex(r) + dec2hex(g) + dec2hex(b)
            # SVG
            s = base
            s = s.replace("#CF#", fill)
            s = s.replace("#ID#", TARGETS["#ID#"] + str(y * width + x))
            s = s.replace("#X0#", str(x * TARGETS["#PX#"] * PX))
            s = s.replace("#Y0#", str(y * TARGETS["#PX#"] * PX))
            rectangles += s

    # Save
    svg = svg.replace(MARKCODE, rectangles)
    save(SVG_PATH + filename + ".svg", svg)


def main(args):

    print("Check ...", args)
    if len(args) != 2:
        print("Use: python3 create_svg_pixelart.py <image-filename>")
    

if __name__ == '__main__':

    # Test
    # create("../images/image_test_1.png")
    # create("../images/image_test_2.jpg")
    create("../images/bonsai.png")    

    # Run 
    # main(sys.argv)
