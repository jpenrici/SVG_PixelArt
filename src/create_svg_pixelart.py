# -*- coding: utf-8 -*-
'''
    Objective:
        Create pixelart image in SVG.
'''

import os
import sys
import time
import numpy as np
from PIL import Image
from collections import deque


# Constants
PX = 25.4 / 96
DIST_X = 5   # horizontal distance between rectangles
DIST_Y = 5   # vertical distance between rectangles
LIMIT = 500  # recursive method

TARGETS = {
    "#ID#": "p_",
    "#PX#": 64,
    "#CF#": "#FFFFFF",
    "#CS#": "#000000"
}

MARKCODE = "<!-- ##PIXELART## -->"
RECTANGLE = """    <rect
       style="fill:#CF#;fill-opacity:1;stroke:#CS#;stroke-width:0.1;stroke-opacity:1"
       id="#ID#"
       width="#PX#"
       height="#PX#"
       x="#X0#"
       y="#Y0#" />
"""
GROUP="""   <g id="g_#ID#" >
#SHAPE#   </g>
"""

# Default path
PATH, _ = os.path.split(os.path.realpath(__file__))
TEMPLATE = os.path.join(PATH, "template.txt")
SVG_PATH = os.path.join("..", "output")


def load_file(path: str) -> list[str]:
    print(f"Load: {path}")
    try:
        with open(path, "r") as f:
            return f.readlines()
    except Exception as e:
        print(f"Error opening file.\n{e}")
        return []


def save_file(path: str, content: str) -> None:
    try:
        with open(path, "w") as f:
            f.write(content)
        print(f"Output: {path}")
    except Exception as e:
        print(f"Error saving file.\n{e}")
        sys.exit(1)


def rgba(x: int, y: int, array: np.ndarray) -> dict[str, int]:
    r, g, b = array[y, x][:3]
    a = array[y, x][3] if array.shape[2] == 4 else 255
    return {'R': r, 'G': g, 'B': b, 'A': a}


def rgb2hex(rgb: dict[str, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(rgb['R'], rgb['G'], rgb['B'])


def flood_fill(x0: int, y0: int, color_hex: str, array: np.ndarray, visited: np.ndarray) -> list[dict[str, int]]:
    height, width = visited.shape
    region = []
    queue = deque()
    queue.append((x0, y0))

    while queue and len(region) < LIMIT:
        x, y = queue.popleft()
        if x < 0 or x >= width or y < 0 or y >= height:
            continue
        if visited[y, x]:
            continue

        pixel = rgba(x, y, array)
        if pixel['A'] != 255 or rgb2hex(pixel) != color_hex:
            continue

        visited[y, x] = True
        region.append({'x': x, 'y': y, 'fill': color_hex[1:]})

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    queue.append((x + dx, y + dy))

    return region


def process_image(image_path: str) -> None:
    try:
        filename = os.path.basename(image_path)
        img = Image.open(image_path).convert("RGBA")
        array = np.array(img)
        height, width = array.shape[:2]
        print(f"Image: {filename} ({width}x{height})")
    except Exception as e:
        print(f"Error opening image.\n{e}")
        sys.exit(1)

    if not os.path.exists(SVG_PATH):
        os.makedirs(SVG_PATH)

    template_content = load_file(TEMPLATE)  # List
    svg = "".join(template_content)  # Joins the list items into a string.

    px_size = (TARGETS["#PX#"] + DIST_X) * PX
    svg = svg.replace("#VBX#", str(width * px_size))
    svg = svg.replace("#VBY#", str(height * px_size))

    base = RECTANGLE.replace("#PX#", str(TARGETS["#PX#"] * PX)).replace("#CS#", TARGETS["#CS#"])

    visited = np.zeros((height, width), dtype=bool)
    shapes = ""
    counter = 0

    print("Processing ...")

    for y in range(height):
        for x in range(width):
            if visited[y, x]:
                continue

            pixel = rgba(x, y, array)
            if pixel['A'] != 255:
                continue

            color_hex = rgb2hex(pixel)
            region = flood_fill(x, y, color_hex, array, visited)
            if not region:
                continue

            temp = ""
            for p in region:
                r = base.replace("#CF#", f"#{p['fill']}")
                r = r.replace("#ID#", f"{TARGETS['#ID#']}x{p['x']}y{p['y']}")
                r = r.replace("#X0#", str(p['x'] * px_size))
                r = r.replace("#Y0#", str(p['y'] * px_size))
                temp += r

            if len(region) > 1:
                temp = GROUP.replace("#ID#", str(counter)).replace("#SHAPE#", temp)
                counter += 1

            shapes += temp

    svg = svg.replace(MARKCODE, shapes)
    filename = os.path.splitext(os.path.basename(image_path))[0] + ".svg"
    save_file(os.path.join(SVG_PATH, filename), svg)
    print("Image processing completed.")


def main(args: list[str]) -> None:
    # print("Input:", args)
    if len(args) != 2:
        print("Use: python3 create_svg_pixelart.py <image_path>")
        sys.exit(1)

    image_path = args[1]
    if not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        print("Unsupported image format.")
        sys.exit(1)

    start = time.time()
    process_image(image_path)
    end = time.time()
    print(f"Processing time: {end - start:.2f} seconds.")


def test() -> None:
    main(["example 1", "../images/image_test_1.png"])
    main(["example 2", "../images/image_test_2.jpg"])
    main(["example 3", "../images/image_test_3.png"])
    main(["example 4", "../images/bonsai.png"])


if __name__ == '__main__':
    # Example
    # test()

    # Run 
    main(sys.argv)
