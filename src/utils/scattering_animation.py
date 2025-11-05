"""
Scattering animation generator for pixel transitions.
Creates random flickering effect with gradual intensity levels (20%, 40%, 60%, 80%, 100%)
"""
import random
from typing import List, Tuple


def create_scattering_transition(
    target_image: List[List[List[int]]],
    transition_duration: float,
    fps: int,
    appear: bool = True
) -> List[List[List[List[int]]]]:
    """
    Create scattering transition frames for an image.
    
    The scattering effect shows pixels randomly flickering at different intensity levels
    (20%, 40%, 60%, 80%, 100%) before reaching the final state.
    
    Args:
        target_image: Target RGB matrix (height x width x 3)
        transition_duration: Duration of transition in seconds
        fps: Frames per second
        appear: If True, transition from black to target. If False, from target to black.
        
    Returns:
        List of frames showing the scattering transition
    """
    height = len(target_image)
    width = len(target_image[0]) if target_image else 0
    
    total_frames = int(transition_duration * fps)
    frames = []
    
    # Intensity levels for scattering effect
    intensity_levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    
    # Create a random scattering sequence for each pixel
    pixel_sequences = []
    for y in range(height):
        row_sequences = []
        for x in range(width):
            # Generate random scattering sequence for this pixel
            sequence = generate_pixel_scattering_sequence(total_frames, intensity_levels)
            row_sequences.append(sequence)
        pixel_sequences.append(row_sequences)
    
    # Generate frames
    for frame_idx in range(total_frames):
        frame = []
        for y in range(height):
            row = []
            for x in range(width):
                target_pixel = target_image[y][x]
                intensity = pixel_sequences[y][x][frame_idx]
                
                # If disappearing, invert the intensity
                if not appear:
                    intensity = 1.0 - intensity
                
                # Apply intensity to target pixel
                pixel = [
                    int(target_pixel[0] * intensity),
                    int(target_pixel[1] * intensity),
                    int(target_pixel[2] * intensity)
                ]
                row.append(pixel)
            frame.append(row)
        frames.append(frame)
    
    return frames


def generate_pixel_scattering_sequence(total_frames: int, intensity_levels: List[float]) -> List[float]:
    """
    Generate a random scattering sequence for a single pixel.
    
    The sequence randomly picks intensity levels with random intervals,
    gradually progressing from 0% to 100%.
    
    Args:
        total_frames: Total number of frames in the sequence
        intensity_levels: List of intensity levels (e.g., [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        
    Returns:
        List of intensity values for each frame
    """
    sequence = [0.0] * total_frames
    
    if total_frames == 0:
        return sequence
    
    # Divide transition into random intervals
    current_frame = 0
    current_level_idx = 0  # Start at 0%
    
    while current_frame < total_frames and current_level_idx < len(intensity_levels):
        # Randomly choose next intensity level (can go up or flicker back)
        if random.random() < 0.7:  # 70% chance to progress
            next_level_idx = min(current_level_idx + 1, len(intensity_levels) - 1)
        else:  # 30% chance to flicker (stay or go back)
            next_level_idx = random.randint(0, current_level_idx) if current_level_idx > 0 else 0
        
        intensity = intensity_levels[next_level_idx]
        
        # Random duration for this intensity (1-5 frames typically)
        if next_level_idx == len(intensity_levels) - 1:
            # Last level (100%) - hold until end
            duration = total_frames - current_frame
        else:
            max_duration = max(1, (total_frames - current_frame) // (len(intensity_levels) - next_level_idx))
            duration = random.randint(1, min(5, max_duration))
        
        # Fill frames with this intensity
        for i in range(duration):
            if current_frame + i < total_frames:
                sequence[current_frame + i] = intensity
        
        current_frame += duration
        
        # Progress to next level
        if next_level_idx > current_level_idx:
            current_level_idx = next_level_idx
    
    # Ensure the last part reaches 100%
    if current_frame < total_frames:
        for i in range(current_frame, total_frames):
            sequence[i] = intensity_levels[-1]
    
    return sequence


def create_scattering_animation(
    target_image: List[List[List[int]]],
    appear_duration: float,
    hold_duration: float,
    disappear_duration: float,
    fps: int
) -> List[List[List[List[int]]]]:
    """
    Create a complete scattering animation: black -> appear -> hold -> disappear -> black.
    
    Args:
        target_image: Target RGB matrix
        appear_duration: Duration of appearing transition in seconds
        hold_duration: Duration to hold the image in seconds
        disappear_duration: Duration of disappearing transition in seconds
        fps: Frames per second
        
    Returns:
        List of all frames in the animation
    """
    frames = []
    height = len(target_image)
    width = len(target_image[0]) if target_image else 0
    
    # Create black frame
    black_frame = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
    
    # Black frame at start (0.3 seconds instead of 1 second)
    black_frame_count = int(fps * 0.3)  # 0.3 seconds
    for _ in range(black_frame_count):
        frames.append(black_frame)
    
    # Appearing transition
    if appear_duration > 0:
        appear_frames = create_scattering_transition(target_image, appear_duration, fps, appear=True)
        frames.extend(appear_frames)
    
    # Hold the image
    if hold_duration > 0:
        hold_frame_count = int(hold_duration * fps)
        for _ in range(hold_frame_count):
            frames.append(target_image)
    
    # Disappearing transition
    if disappear_duration > 0:
        disappear_frames = create_scattering_transition(target_image, disappear_duration, fps, appear=False)
        frames.extend(disappear_frames)
    
    # Black frame at end (1 second)
    for _ in range(black_frame_count):
        frames.append(black_frame)
    
    return frames


if __name__ == "__main__":
    # Test with a simple 4x4 red square
    test_image = [
        [[255, 0, 0] for _ in range(4)]
        for _ in range(4)
    ]
    
    print("Testing scattering animation generator...")
    frames = create_scattering_animation(
        target_image=test_image,
        appear_duration=0.5,
        hold_duration=1.0,
        disappear_duration=0.5,
        fps=10
    )
    
    print(f"Generated {len(frames)} frames")
    print(f"  Black start: 10 frames (1.0s @ 10fps)")
    print(f"  Appear: ~5 frames (0.5s @ 10fps)")
    print(f"  Hold: 10 frames (1.0s @ 10fps)")
    print(f"  Disappear: ~5 frames (0.5s @ 10fps)")
    print(f"  Black end: 10 frames (1.0s @ 10fps)")
    
    # Show first few frames
    print("\nFirst 3 frames (should be black):")
    for i in range(min(3, len(frames))):
        pixel_00 = frames[i][0][0]
        print(f"  Frame {i}: pixel[0][0] = {pixel_00}")
