#!/usr/bin/env python3
"""
Fix 12.png - replace dark red background with pure black
"""
from PIL import Image

# Load the broken 12.png
img_path = "./data/s+m+t+m+12/12.png"
img = Image.open(img_path).convert("RGBA")

print(f"Original image size: {img.size}")
print(f"Original colors:")

# Count original colors
colors = {}
for y in range(img.height):
    for x in range(img.width):
        rgb = img.getpixel((x, y))[:3]
        colors[rgb] = colors.get(rgb, 0) + 1

for color, count in sorted(colors.items()):
    print(f"  RGB{color}: {count} pixels")

# Create new image with black background
new_img = Image.new("RGB", img.size, (0, 0, 0))

# Copy only white pixels (text)
for y in range(img.height):
    for x in range(img.width):
        r, g, b, a = img.getpixel((x, y))
        # If pixel is bright (white text), copy it
        if r > 200 and g > 200 and b > 200:
            new_img.putpixel((x, y), (255, 255, 255))
        # Otherwise, leave as black (0, 0, 0)

# Save
new_img.save(img_path)
print(f"\n✅ Fixed and saved to {img_path}")

# Verify
new_colors = {}
for y in range(new_img.height):
    for x in range(new_img.width):
        rgb = new_img.getpixel((x, y))
        new_colors[rgb] = new_colors.get(rgb, 0) + 1

print(f"\nNew colors:")
for color, count in sorted(new_colors.items()):
    print(f"  RGB{color}: {count} pixels")
