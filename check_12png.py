#!/usr/bin/env python3
"""
Check what's in 12.png file
"""
from PIL import Image

twelve_path = "./data/s+m+t+m+12/12.png"
img = Image.open(twelve_path)

print(f"Image mode: {img.mode}")
print(f"Image size: {img.size}")
print(f"Image format: {img.format}")

# Get some sample pixels
print(f"\nSample pixels (x, y): RGB")
for y in range(min(5, img.height)):
    for x in range(min(5, img.width)):
        pixel = img.getpixel((x, y))
        print(f"  ({x},{y}): {pixel}")

# Check unique colors
colors = set()
for y in range(img.height):
    for x in range(img.width):
        colors.add(img.getpixel((x, y))[:3])

print(f"\nUnique colors in image: {len(colors)}")
for color in sorted(colors):
    count = sum(1 for y in range(img.height) for x in range(img.width) if img.getpixel((x, y))[:3] == color)
    print(f"  RGB{color}: {count} pixels")
