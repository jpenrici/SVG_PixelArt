# Create SVG PixelArt (SVG_PixelArt)

This project converts raster images (PNG, JPG) into vector pixel art in SVG format, preserving color mapping and shapes.

---

## Features

- Color region detection using a flood fill algorithm.
- Automatic SVG code generation.
- Efficient processing with support for high-resolution images.
- Image conversion with transparency handling.

---

## Requirements

- Python >= 3.12
- Libraries:
  - Pillow
  - numpy

Quick installation:
```bash
pip install pillow numpy
```

---

## Usage

1. Place the desired image inside the `images/` folder (or adjust the path as needed).

2. Run:
```bash
python3 create_svg_pixelart.py <image-path>
```

The generated SVG file will be saved inside the `output/` folder.

---

## Project Structure

```
create_svg_pixelart.py   # Main code
images/                  # Suggested folder for input images
output/                  # Output folder for SVGs
template.txt             # SVG template file
```

---

## License

This project is free to use for educational and personal purposes.

---

# Display

![example](https://github.com/jpenrici/SVG_PixelArt/blob/main/display/display.png)
