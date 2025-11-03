"""
Create solid color board binary files.
"""
from typing import List, Tuple
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.bin_maker import bin_maker, bin_maker_with_tiles


def parse_color(color_str: str) -> Tuple[int, int, int]:
    """
    Parse color string to RGB tuple.
    
    Supports formats:
    - Hex: #FF0000 or FF0000
    - RGB: 255,0,0 or (255,0,0)
    - Named colors: red, green, blue, etc.
    
    Args:
        color_str: Color string
        
    Returns:
        RGB tuple (r, g, b)
    """
    color_str = color_str.strip()
    
    # Named colors
    named_colors = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'pink': (255, 192, 203),
    }
    
    if color_str.lower() in named_colors:
        return named_colors[color_str.lower()]
    
    # Hex color
    if color_str.startswith('#'):
        color_str = color_str[1:]
    
    if len(color_str) == 6:
        try:
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)
            return (r, g, b)
        except ValueError:
            pass
    
    # RGB format
    color_str = color_str.replace('(', '').replace(')', '')
    parts = color_str.split(',')
    if len(parts) == 3:
        try:
            r, g, b = [int(p.strip()) for p in parts]
            if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                return (r, g, b)
        except ValueError:
            pass
    
    raise ValueError(f"Invalid color format: {color_str}")


def create_solid_color_board(
    color: Tuple[int, int, int],
    width: int,
    height: int,
    duration: float,
    fps: int,
    output_path: str,
    split_tiles: bool = True
):
    """
    Create a solid color board binary file.
    
    Args:
        color: RGB color tuple (r, g, b)
        width: Board width in pixels
        height: Board height in pixels
        duration: Duration in seconds
        fps: Frames per second
        output_path: Output file path (base path without extension)
        split_tiles: If True, save both full board and tiles
    """
    # Validate dimensions
    if width % 4 != 0:
        raise ValueError(f"Width {width} must be a multiple of 4")
    if height % 4 != 0:
        raise ValueError(f"Height {height} must be a multiple of 4")
    
    print(f"\n🎨 Creating solid color board...")
    print(f"   Color: RGB{color}")
    print(f"   Size: {width}x{height}")
    print(f"   Duration: {duration}s")
    print(f"   FPS: {fps}")
    
    # Create single frame
    frame = [
        [[color[0], color[1], color[2]] for _ in range(width)]
        for _ in range(height)
    ]
    
    # Repeat frame for duration
    total_frames = int(duration * fps)
    frames = [frame for _ in range(total_frames)]
    
    print(f"   Total frames: {total_frames}")
    
    # Save using appropriate bin_maker function
    if split_tiles:
        bin_maker_with_tiles(frames, output_path, fps)
    else:
        bin_maker(frames, f"{output_path}.bin", fps)


if __name__ == "__main__":
    # Test
    create_solid_color_board(
        color=(255, 0, 0),  # Red
        width=16,
        height=16,
        duration=5.0,
        fps=15,
        output_path="test_red_board",
        split_tiles=True
    )
