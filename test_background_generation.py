#!/usr/bin/env python3
"""
Test background generation to debug yellow/orange color issues
"""

import sys
import os
from PIL import Image

sys.path.append(os.path.dirname(__file__))

from src.utils.image2matrix import image_to_matrix
from src.utils.fire_effect import (
    create_background_scattering_from_bottom,
    create_fire_flickering,
    create_fire_rise_from_bottom,
    add_solid_background,
    overlay_image_on_fire
)

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
print(f"\n=== Test 1: Yellow background rising ===")

yellow_bg_color = (180, 180, 0)
yellow_frames = create_background_scattering_from_bottom(width, height, yellow_bg_color, twelve_matrix, 0.5, 15)

print(f"Generated {len(yellow_frames)} frames")

# Analyze first, middle, and last frames
for frame_idx in [0, len(yellow_frames)//2, -1]:
    frame = yellow_frames[frame_idx]
    yellow_pixel_count = 0
    black_pixel_count = 0
    text_pixel_count = 0
    
    for row in frame:
        for pixel in row:
            if pixel == [0, 0, 0]:
                black_pixel_count += 1
            elif pixel[0] > 100 and pixel[1] > 100:  # Yellow-ish
                yellow_pixel_count += 1
            else:
                text_pixel_count += 1
    
    print(f"\nFrame {frame_idx}:")
    print(f"  Yellow pixels: {yellow_pixel_count}")
    print(f"  Black pixels: {black_pixel_count}")
    print(f"  Text pixels: {text_pixel_count}")

print(f"\n=== Test 2: Fire flickering ===")

flicker_zone = max(2, height // 4)
print(f"Flicker zone height: {flicker_zone}")

fire_frames = create_fire_flickering(width, height, 1.0, 15, flicker_zone_height=flicker_zone)

print(f"Generated {len(fire_frames)} frames")

for frame_idx in [0, len(fire_frames)//2, -1]:
    frame = fire_frames[frame_idx]
    fire_pixel_count = 0
    black_pixel_count = 0
    
    for row in frame:
        for pixel in row:
            if pixel == [0, 0, 0]:
                black_pixel_count += 1
            else:
                fire_pixel_count += 1
    
    print(f"\nFrame {frame_idx}:")
    print(f"  Fire pixels: {fire_pixel_count}")
    print(f"  Black pixels: {black_pixel_count}")

print(f"\n=== Test 3: Fire rising from bottom ===")

fire_rise = create_fire_rise_from_bottom(width, height, 1.0, 15, flicker_zone_height=flicker_zone)

print(f"Generated {len(fire_rise)} frames")

for frame_idx in [0, len(fire_rise)//2, -1]:
    frame = fire_rise[frame_idx]
    fire_pixel_count = 0
    black_pixel_count = 0
    
    for row in frame:
        for pixel in row:
            if pixel == [0, 0, 0]:
                black_pixel_count += 1
            else:
                fire_pixel_count += 1
    
    print(f"\nFrame {frame_idx}:")
    print(f"  Fire pixels: {fire_pixel_count}")
    print(f"  Black pixels: {black_pixel_count}")
