"""
Directional scattering animations for special effects.
"""
import random
from typing import List, Tuple


def create_left_to_right_wipe(
    start_image: List[List[List[int]]],
    end_image: List[List[List[int]]],
    duration: float,
    fps: int
) -> List[List[List[List[int]]]]:
    """
    Create a left-to-right scattering wipe transition.
    The start image disappears and end image appears as the wipe moves from left to right.
    
    Args:
        start_image: Starting RGB matrix
        end_image: Ending RGB matrix
        duration: Duration of transition in seconds
        fps: Frames per second
        
    Returns:
        List of transition frames
    """
    height = len(start_image)
    width = len(start_image[0]) if start_image else 0
    
    total_frames = int(duration * fps)
    frames = []
    
    for frame_idx in range(total_frames):
        frame = []
        progress = frame_idx / max(1, total_frames - 1)  # 0.0 to 1.0
        
        for y in range(height):
            row = []
            for x in range(width):
                # Calculate position progress (0.0 to 1.0)
                x_progress = x / max(1, width - 1)
                
                # Add randomness to the wipe edge
                random_offset = random.uniform(-0.1, 0.1)
                threshold = progress + random_offset
                
                if x_progress < threshold:
                    # Show end image with scattering effect
                    intensity = min(1.0, (threshold - x_progress) / 0.2 + random.uniform(0, 0.3))
                    pixel = [
                        int(end_image[y][x][0] * intensity),
                        int(end_image[y][x][1] * intensity),
                        int(end_image[y][x][2] * intensity)
                    ]
                else:
                    # Show start image with scattering fade
                    intensity = max(0.0, (x_progress - threshold) / 0.2 + random.uniform(0, 0.3))
                    intensity = min(1.0, intensity)
                    pixel = [
                        int(start_image[y][x][0] * intensity),
                        int(start_image[y][x][1] * intensity),
                        int(start_image[y][x][2] * intensity)
                    ]
                
                row.append(pixel)
            frame.append(row)
        frames.append(frame)
    
    return frames


def create_bottom_to_top_scattering(
    target_image: List[List[List[int]]],
    duration: float,
    fps: int,
    appear: bool = True
) -> List[List[List[List[int]]]]:
    """
    Create a bottom-to-top scattering effect.
    
    Args:
        target_image: Target RGB matrix
        duration: Duration of transition in seconds
        fps: Frames per second
        appear: If True, appear from bottom. If False, disappear to top.
        
    Returns:
        List of transition frames
    """
    height = len(target_image)
    width = len(target_image[0]) if target_image else 0
    
    total_frames = int(duration * fps)
    frames = []
    
    intensity_levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    
    for frame_idx in range(total_frames):
        frame = []
        progress = frame_idx / max(1, total_frames - 1)  # 0.0 to 1.0
        
        for y in range(height):
            row = []
            for x in range(width):
                # Calculate vertical position (bottom = 0, top = 1)
                y_progress = (height - 1 - y) / max(1, height - 1)
                
                # Add randomness
                random_offset = random.uniform(-0.15, 0.15)
                threshold = progress + random_offset
                
                if appear:
                    # Appearing from bottom to top
                    if y_progress < threshold:
                        # Choose random intensity level with bias toward higher values
                        level_progress = min(1.0, (threshold - y_progress) / 0.3)
                        level_idx = int(level_progress * (len(intensity_levels) - 1))
                        level_idx = min(level_idx, len(intensity_levels) - 1)
                        
                        # Add flicker
                        if random.random() < 0.3:
                            level_idx = max(0, level_idx - random.randint(1, 2))
                        
                        intensity = intensity_levels[level_idx]
                    else:
                        intensity = 0.0
                else:
                    # Disappearing from bottom to top
                    if y_progress < threshold:
                        intensity = 0.0
                    else:
                        level_progress = min(1.0, (y_progress - threshold) / 0.3)
                        level_idx = int(level_progress * (len(intensity_levels) - 1))
                        level_idx = min(level_idx, len(intensity_levels) - 1)
                        intensity = intensity_levels[len(intensity_levels) - 1 - level_idx]
                
                pixel = [
                    int(target_image[y][x][0] * intensity),
                    int(target_image[y][x][1] * intensity),
                    int(target_image[y][x][2] * intensity)
                ]
                row.append(pixel)
            frame.append(row)
        frames.append(frame)
    
    return frames


def create_center_expand_scattering(
    target_image: List[List[List[int]]],
    duration: float,
    fps: int
) -> List[List[List[List[int]]]]:
    """
    Create a center-expanding scattering effect (like zooming from center).
    
    Args:
        target_image: Target RGB matrix
        duration: Duration of transition in seconds
        fps: Frames per second
        
    Returns:
        List of transition frames
    """
    height = len(target_image)
    width = len(target_image[0]) if target_image else 0
    
    total_frames = int(duration * fps)
    frames = []
    
    center_y = height / 2
    center_x = width / 2
    max_distance = ((height / 2) ** 2 + (width / 2) ** 2) ** 0.5
    
    intensity_levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    
    for frame_idx in range(total_frames):
        frame = []
        progress = frame_idx / max(1, total_frames - 1)  # 0.0 to 1.0
        
        for y in range(height):
            row = []
            for x in range(width):
                # Calculate distance from center (normalized)
                dy = y - center_y
                dx = x - center_x
                distance = (dy ** 2 + dx ** 2) ** 0.5
                normalized_distance = distance / max_distance
                
                # Add randomness
                random_offset = random.uniform(-0.1, 0.1)
                threshold = progress + random_offset
                
                # Pixels closer to center appear first
                if normalized_distance < threshold:
                    # Choose random intensity level
                    level_progress = min(1.0, (threshold - normalized_distance) / 0.2)
                    level_idx = int(level_progress * (len(intensity_levels) - 1))
                    level_idx = min(level_idx, len(intensity_levels) - 1)
                    
                    # Add flicker
                    if random.random() < 0.3:
                        level_idx = max(0, level_idx - random.randint(1, 2))
                    
                    intensity = intensity_levels[level_idx]
                else:
                    intensity = 0.0
                
                pixel = [
                    int(target_image[y][x][0] * intensity),
                    int(target_image[y][x][1] * intensity),
                    int(target_image[y][x][2] * intensity)
                ]
                row.append(pixel)
            frame.append(row)
        frames.append(frame)
    
    return frames


if __name__ == "__main__":
    # Test
    print("Testing directional scattering animations...")
    
    # Create test images
    test_image = [
        [[255, 0, 0] for _ in range(8)]
        for _ in range(8)
    ]
    
    black_image = [
        [[0, 0, 0] for _ in range(8)]
        for _ in range(8)
    ]
    
    # Test bottom-to-top
    frames = create_bottom_to_top_scattering(test_image, 0.5, 10, appear=True)
    print(f"Bottom-to-top: {len(frames)} frames")
    
    # Test center expand
    frames = create_center_expand_scattering(test_image, 0.5, 10)
    print(f"Center expand: {len(frames)} frames")
    
    # Test left-to-right wipe
    frames = create_left_to_right_wipe(test_image, black_image, 0.5, 10)
    print(f"Left-to-right wipe: {len(frames)} frames")
