#!/usr/bin/env python3
"""
Deep test: Check what 12.png image actually contains
"""

import sys
import os
from PIL import Image

sys.path.append(os.path.dirname(__file__))

from src.utils.image2matrix import image_to_matrix

# Load 12.png for testing
twelve_path = "./data/s+m+t+m+12/12.png"
if not os.path.exists(twelve_path):
    print(f"❌ Image not found: {twelve_path}")
    sys.exit(1)

twelve_img = Image.open(twelve_path).convert("RGB")
twelve_matrix = image_to_matrix(twelve_img)

height = len(twelve_matrix)
width = len(twelve_matrix[0])

print(f"Image size: {width}x{height}")
print(f"Total pixels: {width * height}")

# Analyze pixels
text_pixel_count = 0
black_pixel_count = 0
other_pixel_count = 0
other_colors = set()

for y in range(height):
    for x in range(width):
        pixel = twelve_matrix[y][x]
        if pixel == [0, 0, 0]:
            black_pixel_count += 1
        elif pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200:  # White-ish
            text_pixel_count += 1
        else:
            other_pixel_count += 1
            other_colors.add(tuple(pixel))

print(f"\nPixel analysis:")
print(f"  Black pixels: {black_pixel_count}")
print(f"  White text pixels: {text_pixel_count}")
print(f"  Other pixels: {other_pixel_count}")
print(f"  Unique other colors: {len(other_colors)}")

if other_colors:
    print(f"  Sample other colors: {list(other_colors)[:5]}")

# Display pixel grid for debugging
print(f"\nPixel grid (B=black, T=text, O=other):")
for y in range(height):
    row_str = ""
    for x in range(width):
        pixel = twelve_matrix[y][x]
        if pixel == [0, 0, 0]:
            row_str += "."
        elif pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200:
            row_str += "#"
        else:
            row_str += "?"
    print(f"y={y}: {row_str}")
