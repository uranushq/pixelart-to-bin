"""
Test script for tile splitting functionality
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from PIL import Image
from src.utils.image2matrix import image_to_matrix
from src.utils.tile_splitter import split_into_4x4_tiles, validate_dimensions, get_tile_layout

# Test with watermelon image
test_image_path = "./data/watermelon/수박_1.png"

if os.path.exists(test_image_path):
    img = Image.open(test_image_path).convert("RGB")
    print(f"Image size: {img.size} (width x height)")
    
    matrix = image_to_matrix(img)
    height = len(matrix)
    width = len(matrix[0]) if matrix else 0
    print(f"Matrix dimensions: {height}x{width}")
    
    # Check if dimensions are multiples of 4
    if height % 4 == 0 and width % 4 == 0:
        print(f"✓ Dimensions are valid for 4x4 splitting")
        
        # Get tile layout
        num_h, num_v, total = get_tile_layout(matrix)
        print(f"Tile layout: {num_h}x{num_v} = {total} tiles")
        
        # Split into tiles
        tiles = split_into_4x4_tiles(matrix)
        print(f"\n✓ Successfully split into {len(tiles)} tiles")
        
        # Show tile numbering
        print(f"\nTile numbering (top to bottom, left to right):")
        for row in range(num_v):
            tile_nums = []
            for col in range(num_h):
                tile_num = row * num_h + col
                tile_nums.append(f"{tile_num:2d}")
            print("  " + "  ".join(tile_nums))
            
    else:
        print(f"✗ Invalid dimensions for 4x4 splitting:")
        if height % 4 != 0:
            print(f"  Height {height} is not a multiple of 4")
        if width % 4 != 0:
            print(f"  Width {width} is not a multiple of 4")
else:
    print(f"Test image not found: {test_image_path}")
