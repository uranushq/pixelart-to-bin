"""
Utility for splitting RGB matrices into 4x4 tiles.
"""
from typing import List, Tuple


def validate_dimensions(matrix: List[List[List[int]]]) -> Tuple[int, int]:
    """
    Validate that matrix dimensions are multiples of 4.
    
    Args:
        matrix: RGB matrix to validate (height x width x 3)
        
    Returns:
        Tuple of (height, width)
        
    Raises:
        ValueError: If dimensions are not multiples of 4
    """
    if not matrix:
        raise ValueError("Matrix is empty")
    
    height = len(matrix)
    width = len(matrix[0]) if matrix else 0
    
    if height % 4 != 0:
        raise ValueError(f"Height {height} is not a multiple of 4")
    
    if width % 4 != 0:
        raise ValueError(f"Width {width} is not a multiple of 4")
    
    return height, width


def split_into_4x4_tiles(matrix: List[List[List[int]]]) -> List[List[List[List[int]]]]:
    """
    Split an RGB matrix into 4x4 tiles.
    Tiles are numbered 0-15 from top to bottom, left to right:
    
    0  1  2  3
    4  5  6  7
    8  9  10 11
    12 13 14 15
    
    Args:
        matrix: RGB matrix (height x width x 3)
        
    Returns:
        List of 4x4 tiles, each tile is a 4x4 RGB matrix
        
    Raises:
        ValueError: If dimensions are not multiples of 4
    """
    height, width = validate_dimensions(matrix)
    
    tiles = []
    tile_height = 4
    tile_width = 4
    
    # Calculate number of tiles
    num_tiles_vertical = height // tile_height
    num_tiles_horizontal = width // tile_width
    
    # Extract tiles in order: top to bottom, left to right
    for tile_row in range(num_tiles_vertical):
        for tile_col in range(num_tiles_horizontal):
            # Extract 4x4 tile
            tile = []
            start_y = tile_row * tile_height
            start_x = tile_col * tile_width
            
            for y in range(start_y, start_y + tile_height):
                row = []
                for x in range(start_x, start_x + tile_width):
                    row.append(matrix[y][x])
                tile.append(row)
            
            tiles.append(tile)
    
    return tiles


def get_tile_layout(matrix: List[List[List[int]]]) -> Tuple[int, int, int]:
    """
    Get the layout information for tiles.
    
    Args:
        matrix: RGB matrix
        
    Returns:
        Tuple of (num_tiles_horizontal, num_tiles_vertical, total_tiles)
    """
    height, width = validate_dimensions(matrix)
    
    num_tiles_horizontal = width // 4
    num_tiles_vertical = height // 4
    total_tiles = num_tiles_horizontal * num_tiles_vertical
    
    return num_tiles_horizontal, num_tiles_vertical, total_tiles


if __name__ == "__main__":
    # Test with a 16x16 matrix
    test_matrix = [
        [
            [i*16 + j, 0, 0]  # Red channel shows position
            for j in range(16)
        ]
        for i in range(16)
    ]
    
    try:
        tiles = split_into_4x4_tiles(test_matrix)
        print(f"Split 16x16 matrix into {len(tiles)} tiles")
        
        # Print first tile (top-left corner)
        print("\nTile 0 (top-left):")
        for row in tiles[0]:
            print([pixel[0] for pixel in row])
        
        # Print tile 5 (second row, second column)
        print("\nTile 5:")
        for row in tiles[5]:
            print([pixel[0] for pixel in row])
            
    except ValueError as e:
        print(f"Error: {e}")
    
    # Test with invalid dimensions
    print("\nTesting with 15x16 matrix (should fail):")
    invalid_matrix = [
        [
            [0, 0, 0]
            for j in range(16)
        ]
        for i in range(15)
    ]
    
    try:
        tiles = split_into_4x4_tiles(invalid_matrix)
    except ValueError as e:
        print(f"Expected error: {e}")
