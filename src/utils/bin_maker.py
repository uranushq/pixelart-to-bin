from typing import List
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.add_metadata import add_metadata

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