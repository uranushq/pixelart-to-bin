from typing import List
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.add_metadata import add_metadata
from src.utils.tile_splitter import split_into_4x4_tiles, validate_dimensions, get_tile_layout

def bin_maker(frames: List[List[List[List[int]]]], output_path: str, fps: int = 1):
    """
    Create a binary file from RGB matrices.
    
    Args:
        frames: List of RGB matrices (frames)
        output_path: Path to save the output binary file
        fps: Frames per second
    """
    bin_data = add_metadata(frames, fps=fps)

    with open(output_path, 'wb') as f:
        f.write(bin_data)

    print(f"[✔] Saved {len(frames)} frame(s) to: {output_path}")


def bin_maker_with_tiles(frames: List[List[List[List[int]]]], output_base_path: str, fps: int = 1):
    """
    Create binary files from RGB matrices.
    Saves both the full board and individual 4x4 tiles.
    
    Tiles are numbered 0-15 from top to bottom, left to right:
    0  1  2  3
    4  5  6  7
    8  9  10 11
    12 13 14 15
    
    Args:
        frames: List of RGB matrices (frames)
        output_base_path: Base path for output files (without extension)
        fps: Frames per second
        
    Raises:
        ValueError: If frame dimensions are not multiples of 4
    """
    if not frames:
        raise ValueError("No frames provided")
    
    # Validate dimensions of first frame
    validate_dimensions(frames[0])
    num_h, num_v, total_tiles = get_tile_layout(frames[0])
    
    print(f"\n[INFO] Frame dimensions: {len(frames[0])}x{len(frames[0][0])}")
    print(f"[INFO] Tile layout: {num_h}x{num_v} = {total_tiles} tiles")
    
    # Save full board
    full_board_path = f"{output_base_path}_full.bin"
    bin_data = add_metadata(frames, fps=fps)
    with open(full_board_path, 'wb') as f:
        f.write(bin_data)
    print(f"[✔] Saved full board ({len(frames)} frames) to: {full_board_path}")
    
    # Split each frame into tiles and organize by tile number
    tiles_by_number = [[] for _ in range(total_tiles)]
    
    for frame_idx, frame in enumerate(frames):
        tiles = split_into_4x4_tiles(frame)
        for tile_idx, tile in enumerate(tiles):
            tiles_by_number[tile_idx].append(tile)
    
    # Save each tile sequence
    print(f"\n[INFO] Saving {total_tiles} tile files...")
    for tile_idx in range(total_tiles):
        tile_path = f"{output_base_path}_tile_{tile_idx:02d}.bin"
        tile_frames = tiles_by_number[tile_idx]
        
        bin_data = add_metadata(tile_frames, fps=fps)
        with open(tile_path, 'wb') as f:
            f.write(bin_data)
        
        print(f"[✔] Saved tile {tile_idx:02d} ({len(tile_frames)} frames) to: {tile_path}")
    
    print(f"\n[✔] Total files saved: 1 full board + {total_tiles} tiles = {total_tiles + 1} files")