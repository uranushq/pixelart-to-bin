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
    Create a psyche effect where each pixel randomly blinks independently.
    Each pixel has its own random blinking pattern.
    
    Args:
        color: RGB color tuple for the pixels
        width: Board width in pixels
        height: Board height in pixels
        duration: Total duration in seconds
        fps: Frames per second
        speed: Blink speed multiplier (higher = faster blinking, default: 1.0)
        density: Percentage of pixels that are ON at any given time (0.0-1.0, default: 0.5)
        
    Returns:
        List of frames with psyche effect
    """
    total_frames = int(duration * fps)
    frames = []
    
    # Create pixel state array (each pixel has independent blinking pattern)
    pixel_patterns = []
    for y in range(height):
        row_patterns = []
        for x in range(width):
            # Random blink frequency (frames between state changes)
            base_frequency = random.randint(3, 10)
            frequency = max(1, int(base_frequency / speed))
            
            # Random phase offset
            phase_offset = random.randint(0, frequency - 1)
            
            row_patterns.append({
                'frequency': frequency,
                'phase': phase_offset,
                'on_probability': density
            })
        pixel_patterns.append(row_patterns)
    
    # Generate frames
    for frame_idx in range(total_frames):
        frame = []
        for y in range(height):
            row = []
            for x in range(width):
                pattern = pixel_patterns[y][x]
                
                # Calculate if this pixel should be on or off this frame
                cycle_position = (frame_idx + pattern['phase']) % pattern['frequency']
                
                # Pixel is on if within the "on" portion of its cycle
                is_on = cycle_position < pattern['frequency'] * pattern['on_probability']
                
                if is_on:
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
    Create animation: psyche effect loop (no black frames)
    Each pixel blinks independently for full psyche effect.
    
    Args:
        color: RGB color tuple
        width: Board width in pixels
        height: Board height in pixels
        full_on_duration: IGNORED - kept for API compatibility
        psyche_duration: Duration of psyche effect in seconds
        fps: Frames per second
        speed: Psyche blink speed multiplier
        density: Percentage of pixels ON at any time (0.0-1.0)
        
    Returns:
        List of all frames
    """
    # Only psyche effect, no black frames
    psyche_frames = create_psyche_effect(color, width, height, psyche_duration, fps, speed, density)
    
    return psyche_frames


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
