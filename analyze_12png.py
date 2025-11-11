#!/usr/bin/env python3
"""
Analyze 12.png content - check which pixels are text vs background
"""
from PIL import Image

img = Image.open("./data/s+m+t+m+12/12.png").convert("RGB")
width, height = img.size

print(f"Image size: {width}x{height}")
print(f"\nAnalyzing pixel content:")

# Count by column
for x in range(width):
    text_count = 0
    black_count = 0
    for y in range(height):
        r, g, b = img.getpixel((x, y))
        if r > 200 and g > 200 and b > 200:  # White text
            text_count += 1
        elif r < 50 and g < 50 and b < 50:  # Black background
            black_count += 1
    
    status = "TEXT" if text_count > 0 else "BG"
    print(f"  Col {x:2d}: {text_count} text, {black_count} black - {status}")

# Visualize
print(f"\nVisualization (top view):")
print("  ", end="")
for x in range(width):
    has_text = False
    for y in range(height):
        r, g, b = img.getpixel((x, y))
        if r > 200 and g > 200 and b > 200:
            has_text = True
            break
    if has_text:
        print("█", end="")
    else:
        print("·", end="")
print()

# Count total
total_text = 0
total_black = 0
for y in range(height):
    for x in range(width):
        r, g, b = img.getpixel((x, y))
        if r > 200 and g > 200 and b > 200:
            total_text += 1
        elif r < 50 and g < 50 and b < 50:
            total_black += 1

print(f"\nTotal: {total_text} text pixels, {total_black} black pixels")
print(f"Background pixels available: {total_black} (where yellow/fire can appear)")
