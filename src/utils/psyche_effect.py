"""
Psyche effect - Random tile blinking animation.
Each 4x4 tile randomly blinks on/off creating a psychedelic effect.
"""
import random
from typing import List, Tuple


def create_psyche_effect(
    color: Tuple[int, int, int],
    width: int,
    height: int,
    duration: float,
    fps: int,
    speed: float = 1.0,
    density: float = 0.5
) -> List[List[List[List[int]]]]:
    """
    Create a psyche effect where tiles (4x4 blocks) randomly blink.
    Each tile blinks as a complete unit (all 16 pixels on/off together).
    
    Args:
        color: RGB color tuple for the tiles
        width: Board width in pixels (must be multiple of 4)
        height: Board height in pixels (must be multiple of 4)
        duration: Total duration in seconds
        fps: Frames per second
        speed: Blink speed multiplier (higher = faster blinking, default: 1.0)
        density: Percentage of tiles that are ON at any given time (0.0-1.0, default: 0.5)
        
    Returns:
        List of frames with psyche effect
    """
    if width % 4 != 0 or height % 4 != 0:
        raise ValueError("Width and height must be multiples of 4")
    
    total_frames = int(duration * fps)
    frames = []
    
    # Calculate number of tiles
    tiles_horizontal = width // 4
    tiles_vertical = height // 4
    total_tiles = tiles_horizontal * tiles_vertical
    
    # Create tile state array (each tile has independent blinking pattern)
    tile_patterns = []
    for _ in range(total_tiles):
        # Random blink frequency (frames between state changes)
        base_frequency = random.randint(3, 10)
        frequency = max(1, int(base_frequency / speed))
        
        # Random phase offset
        phase_offset = random.randint(0, frequency - 1)
        
        tile_patterns.append({
            'frequency': frequency,
            'phase': phase_offset,
            'on_probability': density  # Use density parameter
        })
    
    # Generate frames
    for frame_idx in range(total_frames):
        # Determine state of each tile for this frame
        tile_states = []
        for tile_idx in range(total_tiles):
            pattern = tile_patterns[tile_idx]
            
            # Calculate if this tile should be on or off this frame
            cycle_position = (frame_idx + pattern['phase']) % pattern['frequency']
            
            # Tile is on if within the "on" portion of its cycle
            is_on = cycle_position < pattern['frequency'] * pattern['on_probability']
            
            tile_states.append(is_on)
        
        # Build frame based on tile states
        frame = []
        for y in range(height):
            row = []
            for x in range(width):
                # Determine which tile this pixel belongs to
                tile_x = x // 4
                tile_y = y // 4
                tile_idx = tile_y * tiles_horizontal + tile_x
                
                # All pixels in the same tile have the same state
                if tile_states[tile_idx]:
                    pixel = [color[0], color[1], color[2]]
                else:
                    pixel = [0, 0, 0]
                
                row.append(pixel)
            frame.append(row)
        
        frames.append(frame)
    
    return frames


def create_full_on_then_psyche(
    color: Tuple[int, int, int],
    width: int,
    height: int,
    full_on_duration: float,
    psyche_duration: float,
    fps: int,
    speed: float = 1.0,
    density: float = 0.5
) -> List[List[List[List[int]]]]:
    """
    Create animation: black → psyche effect → black
    (No full-on phase, starts with psyche effect immediately)
    
    Args:
        color: RGB color tuple
        width: Board width in pixels (must be multiple of 4)
        height: Board height in pixels (must be multiple of 4)
        full_on_duration: IGNORED - kept for API compatibility
        psyche_duration: Duration of psyche effect in seconds
        fps: Frames per second
        speed: Psyche blink speed multiplier
        density: Percentage of tiles ON at any time (0.0-1.0)
        
    Returns:
        List of all frames
    """
    if width % 4 != 0 or height % 4 != 0:
        raise ValueError("Width and height must be multiples of 4")
    
    all_frames = []
    
    # Create black frame
    black_frame = [
        [[0, 0, 0] for _ in range(width)]
        for _ in range(height)
    ]
    
    # 1. Black frame (1 second)
    for _ in range(fps):
        all_frames.append(black_frame)
    
    # 2. Psyche effect (no full-on phase)
    psyche_frames = create_psyche_effect(color, width, height, psyche_duration, fps, speed, density)
    all_frames.extend(psyche_frames)
    
    # 3. Black frame (1 second)
    for _ in range(fps):
        all_frames.append(black_frame)
    
    return all_frames


if __name__ == "__main__":
    # Test
    print("Testing psyche effect...")
    
    frames = create_full_on_then_psyche(
        color=(255, 0, 0),
        width=16,
        height=16,
        full_on_duration=2.0,
        psyche_duration=5.0,
        fps=30,
        speed=1.5
    )
    
    print(f"Generated {len(frames)} frames")
    print(f"Duration: {len(frames) / 30:.1f}s at 30fps")
    
    # Check tile layout
    tiles_h = 16 // 4
    tiles_v = 16 // 4
    print(f"Tile layout: {tiles_h}x{tiles_v} = {tiles_h * tiles_v} tiles")
