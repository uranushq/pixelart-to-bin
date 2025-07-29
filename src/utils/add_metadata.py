import struct
import time
from typing import List

def flatten_rgb_matrix(matrix: List[List[List[int]]]) -> List[int]:
    return [value for row in matrix for pixel in row for value in pixel]


def add_header(total_frames: int, height: int, width: int, fps: int) -> bytes:
    return struct.pack('<IIII', total_frames, height, width, fps)


def add_trailer(total_frames: int, end_marker: int = 0xDEADBEEF) -> bytes:
    save_time = int(time.time())
    return struct.pack('<IQI', total_frames, save_time, end_marker)


def add_metadata(rgb_matrices: List[List[List[List[int]]]], fps: int = 1) -> bytes:
    if not rgb_matrices:
        raise ValueError("No frame data provided.")

    total_frames = len(rgb_matrices)
    height = len(rgb_matrices[0])
    width = len(rgb_matrices[0][0])

    header = add_header(total_frames, height, width, fps)
    frames = b''.join(
        bytes(flatten_rgb_matrix(frame)) for frame in rgb_matrices
    )
    trailer = add_trailer(total_frames)

    return header + frames + trailer