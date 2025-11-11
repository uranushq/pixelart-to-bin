#!/usr/bin/env python3
"""
Test fire effect with 40x8 image
"""
import sys
sys.path.append('.')

from PIL import Image
from src.utils.image2matrix import image_to_matrix
from src.utils.fire_effect import create_fire_rise_from_bottom, add_solid_background

# Load 12.png
img = Image.open("./data/s+m+t+m+12/12.png").convert("RGB")
matrix = image_to_matrix(img)

height = len(matrix)
width = len(matrix[0])

print(f"Image: {width}x{height}")

# Test 1: Solid yellow background
yellow_color = (180, 180, 0)

# DEBUG: Check matrix content
print("\nDEBUG: Sample pixels from matrix:")
for y in range(3):
    for x in range(5):
        pixel = matrix[y][x]
        is_black = (pixel == [0, 0, 0])
        is_black2 = (pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0)
        print(f"  ({x},{y}): {pixel} == [0,0,0]? {is_black}, alt check: {is_black2}")

yellow_bg = add_solid_background(matrix, yellow_color)

# Count yellow pixels
yellow_count = 0
for y in range(height):
    for x in range(width):
        pixel = yellow_bg[y][x]
        if pixel[0] == 180 and pixel[1] == 180 and pixel[2] == 0:
            yellow_count += 1

print(f"\nTest 1 - Solid yellow background:")
print(f"  Yellow pixels: {yellow_count}")
print(f"  Expected: ~252 (all background pixels)")

# Test 2: Fire effect
flicker_zone = max(2, height // 4)
print(f"\nTest 2 - Fire effect:")
print(f"  flicker_zone_height: {flicker_zone}")

fire_frames = create_fire_rise_from_bottom(width, height, 0.5, 15, flicker_zone_height=flicker_zone)
print(f"  Generated {len(fire_frames)} frames")

# Check last frame (should have most fire)
last_frame = fire_frames[-1]
fire_count = 0
for y in range(height):
    for x in range(width):
        pixel = last_frame[y][x]
        # Fire pixels (orange/red)
        if pixel[0] > 50 or pixel[1] > 20 or pixel[2] > 0:
            fire_count += 1

print(f"  Fire pixels in last frame: {fire_count}")
print(f"  Expected: >50 pixels (spread across bottom half)")

# Visualize last frame
print(f"\n  Last frame visualization:")
for y in range(height):
    print(f"    Row {y}: ", end="")
    for x in range(width):
        pixel = last_frame[y][x]
        if pixel[0] > 50 or pixel[1] > 20:
            print("🔥", end="")
        else:
            print("··", end="")
    print()
