"""
Check image dimensions for smile dataset
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from PIL import Image

test_image_path = "./data/smile/스마일_1.png"

if os.path.exists(test_image_path):
    img = Image.open(test_image_path).convert("RGB")
    print(f"Smile image size: {img.size} (width x height)")
    
    width, height = img.size
    if width % 4 == 0 and height % 4 == 0:
        print(f"✓ Valid for 4x4 splitting")
        num_tiles_h = width // 4
        num_tiles_v = height // 4
        total_tiles = num_tiles_h * num_tiles_v
        print(f"  Tiles: {num_tiles_h}x{num_tiles_v} = {total_tiles}")
    else:
        print(f"✗ Invalid for 4x4 splitting")
else:
    print(f"Test image not found: {test_image_path}")
