#!/usr/bin/env python3
"""
Simple test: Generate only yellow background frames and check
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from PIL import Image
from src.utils.image2matrix import image_to_matrix
from src.utils.fire_effect import create_background_scattering_from_bottom, add_solid_background
from src.utils.bin_maker import bin_maker

# Load 12.png
twelve_path = "./data/s+m+t+m+12/12.png"
twelve_img = Image.open(twelve_path).convert("RGB")
twelve_matrix = image_to_matrix(twelve_img)

height = len(twelve_matrix)
width = len(twelve_matrix[0])

print(f"Image size: {width}x{height}")

# DEBUG: Check twelve_matrix
print(f"\nDEBUG: twelve_matrix sample pixels:")
for y in range(min(3, height)):
    for x in range(min(5, width)):
        pixel = twelve_matrix[y][x]
        print(f"  ({x},{y}): RGB{tuple(pixel)}")

# Generate yellow background frames
yellow_bg_color = (180, 180, 0)
print(f"\nDEBUG: yellow_bg_color = {yellow_bg_color}")
fps = 15

all_frames = []

# 1. Black frame
black_frame = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
for _ in range(fps):
    all_frames.append(black_frame)

# 2. Text only
for _ in range(fps):
    all_frames.append(twelve_matrix)

# 3. Yellow rising
yellow_bg_fill = create_background_scattering_from_bottom(width, height, yellow_bg_color, twelve_matrix, 0.5, fps)
all_frames.extend(yellow_bg_fill)
print(f"Yellow rising frames: {len(yellow_bg_fill)}")

# 4. Yellow hold
twelve_yellow_bg = add_solid_background(twelve_matrix, yellow_bg_color)

# DEBUG: Check yellow background immediately after creation
print(f"\nDEBUG: twelve_yellow_bg sample pixels (after add_solid_background):")
for y in range(min(3, height)):
    for x in range(min(5, width)):
        pixel = twelve_yellow_bg[y][x]
        print(f"  ({x},{y}): RGB{tuple(pixel)}")

for _ in range(fps * 2):  # 2 seconds
    all_frames.append(twelve_yellow_bg)

# 5. Black ending
for _ in range(fps):
    all_frames.append(black_frame)

print(f"Total frames: {len(all_frames)}")

# Check frame 40 (should be yellow)
print(f"\nFrame 40 sample pixels:")
for y in range(min(3, height)):
    for x in range(min(5, width)):
        pixel = all_frames[40][y][x]
        print(f"  ({x},{y}): RGB{tuple(pixel)}")

# Save
bin_maker(all_frames, "./output/test_yellow_only.bin", fps)
print("\n✅ Saved to ./output/test_yellow_only.bin")
