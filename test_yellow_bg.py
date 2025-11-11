#!/usr/bin/env python3
"""
Test script to verify yellow background filling works correctly
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.utils.fire_effect import create_background_scattering_from_bottom
from PIL import Image

# Create a simple test image (36x8 with white text in center)
width = 36
height = 8

# Create black background with white text in center
test_image = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]

# Add white text in middle rows (rows 2-5)
for y in range(2, 6):
    for x in range(10, 26):  # Center area
        test_image[y][x] = [255, 255, 255]

# Generate yellow background filling from bottom
print("Generating yellow background (0.5s at 15fps)...")
yellow_frames = create_background_scattering_from_bottom(
    width, height, (180, 180, 0), test_image, duration=0.5, fps=15
)

print(f"Total frames generated: {len(yellow_frames)}")
print()

# Analyze each frame
for frame_idx, frame in enumerate(yellow_frames):
    yellow_count = 0
    text_count = 0
    black_count = 0
    
    for y in range(height):
        for x in range(width):
            pixel = frame[y][x]
            if pixel[0] > 100 and pixel[1] > 100 and pixel[2] == 0:  # Yellow
                yellow_count += 1
            elif pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200:  # White
                text_count += 1
            else:  # Black
                black_count += 1
    
    print(f"Frame {frame_idx}: Yellow={yellow_count}, Text={text_count}, Black={black_count}")
    
    # Print visual representation
    print("  ", end="")
    for y in range(height):
        for x in range(width):
            pixel = frame[y][x]
            if pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200:  # White
                print("█", end="")
            elif pixel[0] > 100 and pixel[1] > 100 and pixel[2] == 0:  # Yellow
                print("▓", end="")
            else:  # Black
                print("·", end="")
        print()

print("\n✅ Test complete!")
print("Expected: Yellow fills from bottom to top progressively")
print("█ = Text (white)")
print("▓ = Background (yellow)")
print("· = Empty (black)")
