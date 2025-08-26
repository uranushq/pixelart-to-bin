from typing import List, Tuple

def create_color_frame(r: int, g: int, b: int, width: int = 12, height: int = 12) -> List[List[List[int]]]:
    """
    Create a single color frame of given size.
    
    Args:
        r, g, b: RGB color values (0-255)
        width: width of the frame (default: 12)
        height: height of the frame (default: 12)
        
    Returns:
        3D list representing the RGB matrix [height][width][3]
    """
    return [[[r, g, b] for _ in range(width)] for _ in range(height)]

def create_blinking_color_frames(
    colors: List[Tuple[int, int, int]], 
    width: int = 12, 
    height: int = 12,
    frames_per_color: int = 5,
    repeat: int = 100
) -> List[List[List[List[int]]]]:
    """
    Create a sequence of blinking color frames.
    
    Args:
        colors: List of RGB tuples [(r,g,b), ...]
        width: Board width (default: 12)
        height: Board height (default: 12)
        frames_per_color: How many frames each color stays (default: 5)
        repeat: How many times to repeat the sequence (default: 1)
        
    Returns:
        List of frames for blinking animation
    """
    frames = []
    for _ in range(repeat):
        for color in colors:
            r, g, b = color
            frame = create_color_frame(r, g, b, width, height)
            for _ in range(frames_per_color):
                frames.append(frame)
    return frames

def create_solid_color_frames(
    r: int, g: int, b: int,
    width: int = 12,
    height: int = 12,
    frame_count: int = 50
) -> List[List[List[List[int]]]]:
    """
    Create frames of a single solid color.
    
    Args:
        r, g, b: RGB color values (0-255)
        width: Board width (default: 12)
        height: Board height (default: 12)
        frame_count: Number of frames to create (default: 50)
        
    Returns:
        List of frames with the same color
    """
    frames = []
    frame = create_color_frame(r, g, b, width, height)
    for _ in range(frame_count):
        frames.append(frame)
    return frames

def validate_rgb(r: int, g: int, b: int) -> bool:
    """
    Validate RGB values are in valid range (0-255).
    
    Args:
        r, g, b: RGB values to validate
        
    Returns:
        True if valid, False otherwise
    """
    return 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255
