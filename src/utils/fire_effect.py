"""
Fire effect - Create realistic burning background effect with smooth flickering.
"""
import random
import math
from typing import List, Tuple


def create_fire_rise_from_bottom(
    width: int,
    height: int,
    duration: float,
    fps: int,
    fire_color: Tuple[int, int, int] = (255, 140, 0),  # Orange
    flicker_zone_height: int = 6
) -> List[List[List[List[int]]]]:
    """
    Create fire rising from bottom to middle (50%) with flickering effect.
    Fire appears at bottom (high y values) and rises upward (to middle y values).
    Uses same flickering algorithm as create_fire_flickering for smooth transition.
    
    Args:
        width: Board width in pixels
        height: Board height in pixels
        duration: Duration of fire rising in seconds
        fps: Frames per second
        fire_color: RGB color for fire (default: orange)
        flicker_zone_height: Height of the flickering transition zone
        
    Returns:
        List of frames showing fire rising from bottom to middle with flickering
    """
    total_frames = int(duration * fps)
    frames = []
    
    mid_line = height // 2  # Target middle of screen
    
    # Create wave pattern for each pixel for smooth transitions (same as flickering)
    pixel_waves = {}
    for y in range(height):
        for x in range(width):
            # Random phase and frequency for smooth wave effect
            phase = random.uniform(0, 2 * math.pi)
            frequency = random.uniform(0.05, 0.15)  # Slow wave for smooth effect
            
            pixel_waves[(x, y)] = {
                'phase': phase,
                'frequency': frequency
            }
    
    # Create random boundary offsets for each pixel to blur zone boundaries
    boundary_offsets = {}
    for y in range(height):
        for x in range(width):
            # Random offset for zone boundaries: -0.1 to +0.1 (±10%)
            boundary_offsets[(x, y)] = random.uniform(-0.1, 0.1)
    
    for frame_idx in range(total_frames):
        # Current fill line position (rises from bottom to middle)
        progress = frame_idx / max(1, total_frames - 1)
        current_fill_line = height - int(mid_line * progress)  # Starts at height, ends at mid_line
        
        frame = []
        for y in range(height):
            row = []
            for x in range(width):
                # Only show pixels if fire has reached this area
                if y < current_fill_line:
                    row.append([0, 0, 0])
                    continue
                
                # Calculate position from bottom (0 = bottom, 1 = top)
                pos_from_bottom = (height - 1 - y) / (height - 1)  # 0.0 (top) to 1.0 (bottom)
                
                # Apply random boundary offset to create fuzzy boundaries
                offset = boundary_offsets[(x, y)]
                adjusted_pos = pos_from_bottom + offset
                
                # Determine zone based on adjusted position from bottom
                if adjusted_pos <= 0.3:  # Bottom 0-30%: 100% density, red tint
                    # 100% density - always on
                    intensities = [0.9, 1.0]
                    final_intensity = random.choice(intensities)
                    
                    # More red tint: reduce green more (green -30 to -20)
                    green_adjustment = -30 + int(10 * max(0, min(1, pos_from_bottom / 0.3)))
                    
                    r = int(fire_color[0] * final_intensity)
                    g = int(max(0, min(255, fire_color[1] * final_intensity + green_adjustment)))
                    b = int(fire_color[2] * final_intensity)
                    
                    row.append([r, g, b])
                        
                elif adjusted_pos <= 0.6:  # 30-60%: Higher density, orange 60% with more variation
                    # Higher density (85-90% on probability)
                    base_prob = 0.85
                    wave = pixel_waves[(x, y)]
                    wave_value = 1.0 + 0.1 * math.sin(frame_idx * wave['frequency'] + wave['phase'])
                    final_prob = base_prob * wave_value
                    
                    if random.random() < final_prob:
                        # Orange color around 60% intensity with variation (40-80%)
                        final_intensity = random.uniform(0.4, 0.8)
                        
                        # Transition from red to orange: green -20 to 0
                        ratio = max(0, min(1, (pos_from_bottom - 0.3) / 0.3))
                        green_adjustment = -20 + int(20 * ratio)
                        
                        r = int(fire_color[0] * final_intensity)
                        g = int(max(0, min(255, fire_color[1] * final_intensity + green_adjustment)))
                        b = int(fire_color[2] * final_intensity)
                        
                        row.append([r, g, b])
                    else:
                        row.append([0, 0, 0])
                        
                else:  # Above 60%: Normal flickering
                    # Normal flickering for rest of area
                    # Distance from current fill line (positive = below fill line, negative = above)
                    dist_from_fill = y - current_fill_line
                    
                    # Base probability and color intensity based on distance from fill line
                    if dist_from_fill > flicker_zone_height:
                        # Far below fill line (solid fire area)
                        base_prob = 0.95
                        color_intensity = 1.0  # 100% color
                    elif dist_from_fill < -flicker_zone_height:
                        # Far above fill line (empty area)
                        base_prob = 0.0
                        color_intensity = 0.0
                    else:
                        # Transition zone - gradient from top to bottom
                        ratio = (dist_from_fill + flicker_zone_height) / (2 * flicker_zone_height)
                        base_prob = 0.1 + (ratio * 0.8)
                        color_intensity = 0.2 + (ratio * 0.8)  # 20% to 100%
                    
                    wave = pixel_waves[(x, y)]
                    
                    # Calculate smooth wave value (oscillates between 0.7 and 1.3)
                    wave_value = 1.0 + 0.3 * math.sin(frame_idx * wave['frequency'] + wave['phase'])
                    
                    # Final probability with wave modulation
                    final_prob = base_prob * wave_value
                    final_prob = max(0.0, min(1.0, final_prob))
                    
                    # Determine if pixel is on
                    if random.random() < final_prob:
                        # Apply color intensity (with slight random variation)
                        intensity_variation = random.uniform(0.8, 1.0)
                        final_intensity = color_intensity * intensity_variation
                        final_intensity = max(0.2, min(1.0, final_intensity))
                        
                        # Calculate vertical gradient for green (bottom: red, top: yellow)
                        # y=0 (top) -> green +20, y=height-1 (bottom) -> green -20
                        green_adjustment = 20 - int(40 * y / (height - 1))  # Range: +20 (top) to -20 (bottom)
                        
                        # Calculate final color with gradient
                        r = int(fire_color[0] * final_intensity)
                        g = int(max(0, min(255, fire_color[1] * final_intensity + green_adjustment)))
                        b = int(fire_color[2] * final_intensity)
                        
                        row.append([r, g, b])
                    else:
                        row.append([0, 0, 0])
            
            frame.append(row)
        frames.append(frame)
    
    return frames


def create_fire_flickering(
    width: int,
    height: int,
    duration: float,
    fps: int,
    fire_color: Tuple[int, int, int] = (255, 140, 0),
    flicker_zone_height: int = 6
) -> List[List[List[List[int]]]]:
    """
    Create realistic fire flickering effect.
    Bottom half is filled with fire, top half is black, with flickering boundary.
    - Bottom area (y > mid): dense fire (90% on) at 100% color intensity
    - Middle boundary: flickering with smooth waves and varying color intensity
    - Top area (y < mid): sparse fire (10% on) at 20-40% color intensity
    
    Args:
        width: Board width in pixels
        height: Board height in pixels
        duration: Duration of flickering in seconds
        fps: Frames per second
        fire_color: RGB color for fire (full intensity)
        flicker_zone_height: Height of the flickering transition zone
        
    Returns:
        List of frames with smooth fire flickering
    """
    total_frames = int(duration * fps)
    frames = []
    
    mid_line = height // 2  # Middle of screen (boundary between fire and no fire)
    
    # Create wave pattern for each pixel for smooth transitions
    pixel_waves = {}
    for y in range(height):
        for x in range(width):
            # Distance from middle line (positive = below/fire area, negative = above/black area)
            dist_from_mid = y - mid_line
            
            # Base probability and color intensity based on distance from middle
            if dist_from_mid > flicker_zone_height:
                # Far below middle (bottom area) - solid fire area
                base_prob = 0.95
                color_intensity = 1.0  # 100% color
            elif dist_from_mid < -flicker_zone_height:
                # Far above middle (top area) - mostly empty
                base_prob = 0.05
                color_intensity = 0.2  # 20% color
            else:
                # Transition zone - gradient from top to bottom
                # Top of zone (negative): 10% prob, 20% color
                # Bottom of zone (positive): 90% prob, 100% color
                ratio = (dist_from_mid + flicker_zone_height) / (2 * flicker_zone_height)
                base_prob = 0.1 + (ratio * 0.8)
                color_intensity = 0.2 + (ratio * 0.8)  # 20% to 100%
            
            # Random phase and frequency for smooth wave effect
            phase = random.uniform(0, 2 * math.pi)
            frequency = random.uniform(0.05, 0.15)  # Slow wave for smooth effect
            
            pixel_waves[(x, y)] = {
                'base_prob': base_prob,
                'phase': phase,
                'frequency': frequency,
                'color_intensity': color_intensity
            }
    
    # Create random boundary offsets for each pixel to blur zone boundaries
    boundary_offsets = {}
    for y in range(height):
        for x in range(width):
            # Random offset for zone boundaries: -0.1 to +0.1 (±10%)
            boundary_offsets[(x, y)] = random.uniform(-0.1, 0.1)
    
    # Generate frames with smooth transitions
    for frame_idx in range(total_frames):
        frame = []
        
        for y in range(height):
            row = []
            for x in range(width):
                wave = pixel_waves[(x, y)]
                
                # Calculate position from bottom (0 = bottom, 1 = top)
                pos_from_bottom = (height - 1 - y) / (height - 1)  # 0.0 (top) to 1.0 (bottom)
                
                # Apply random boundary offset to create fuzzy boundaries
                offset = boundary_offsets[(x, y)]
                adjusted_pos = pos_from_bottom + offset
                
                # Determine zone based on adjusted position from bottom
                if adjusted_pos <= 0.3:  # Bottom 0-30%: 100% density, red tint
                    # 100% density - always on
                    intensities = [0.9, 1.0]
                    final_intensity = random.choice(intensities)
                    
                    # More red tint: reduce green more (green -30 to -20)
                    green_adjustment = -30 + int(10 * max(0, min(1, pos_from_bottom / 0.3)))
                    
                    r = int(fire_color[0] * final_intensity)
                    g = int(max(0, min(255, fire_color[1] * final_intensity + green_adjustment)))
                    b = int(fire_color[2] * final_intensity)
                    
                    row.append([r, g, b])
                    
                elif adjusted_pos <= 0.6:  # 30-60%: Higher density, orange 60% with more variation
                    # Higher density (85-90% on probability)
                    base_prob = 0.85
                    wave_value = 1.0 + 0.1 * math.sin(frame_idx * wave['frequency'] + wave['phase'])
                    final_prob = base_prob * wave_value
                    
                    if random.random() < final_prob:
                        # Orange color around 60% intensity with variation (40-80%)
                        final_intensity = random.uniform(0.4, 0.8)
                        
                        # Transition from red to orange: green -20 to 0
                        ratio = max(0, min(1, (pos_from_bottom - 0.3) / 0.3))
                        green_adjustment = -20 + int(20 * ratio)
                        
                        r = int(fire_color[0] * final_intensity)
                        g = int(max(0, min(255, fire_color[1] * final_intensity + green_adjustment)))
                        b = int(fire_color[2] * final_intensity)
                        
                        row.append([r, g, b])
                    else:
                        row.append([0, 0, 0])
                        
                else:  # Above 60%: Normal flickering
                    # Calculate smooth wave value (oscillates between 0.7 and 1.3)
                    wave_value = 1.0 + 0.3 * math.sin(frame_idx * wave['frequency'] + wave['phase'])
                    
                    # Final probability with wave modulation
                    final_prob = wave['base_prob'] * wave_value
                    final_prob = max(0.0, min(1.0, final_prob))
                    
                    # Determine if pixel is on
                    if random.random() < final_prob:
                        # Apply color intensity (with slight random variation for more natural look)
                        intensity_variation = random.uniform(0.8, 1.0)
                        final_intensity = wave['color_intensity'] * intensity_variation
                        final_intensity = max(0.2, min(1.0, final_intensity))
                        
                        # Calculate vertical gradient for green (bottom: red, top: yellow)
                        # y=0 (top) -> green +20, y=height-1 (bottom) -> green -20
                        green_adjustment = 20 - int(40 * y / (height - 1))  # Range: +20 (top) to -20 (bottom)
                        
                        # Calculate final color with gradient
                        r = int(fire_color[0] * final_intensity)
                        g = int(max(0, min(255, fire_color[1] * final_intensity + green_adjustment)))
                        b = int(fire_color[2] * final_intensity)
                        
                        row.append([r, g, b])
                    else:
                        row.append([0, 0, 0])
            
            frame.append(row)
        frames.append(frame)
    
    return frames


def overlay_image_on_fire(
    image_matrix: List[List[List[int]]],
    fire_frames: List[List[List[List[int]]]]
) -> List[List[List[List[int]]]]:
    """
    Overlay an image on top of fire background frames.
    Where image has non-black pixels, use image. Otherwise use fire.
    
    Args:
        image_matrix: The image to overlay (e.g., "12")
        fire_frames: Background fire frames
        
    Returns:
        List of frames with image overlaid on fire
    """
    overlaid_frames = []
    
    height = len(image_matrix)
    width = len(image_matrix[0])
    
    for fire_frame in fire_frames:
        frame = []
        for y in range(height):
            row = []
            for x in range(width):
                image_pixel = image_matrix[y][x]
                
                # If image pixel is not black, use it; otherwise use fire background
                if image_pixel != [0, 0, 0]:
                    row.append(image_pixel)
                else:
                    row.append(fire_frame[y][x])
            frame.append(row)
        overlaid_frames.append(frame)
    
    return overlaid_frames


def overlay_fire_on_yellow_background(
    image_matrix: List[List[List[int]]],
    yellow_bg_color: Tuple[int, int, int],
    fire_frames: List[List[List[List[int]]]]
) -> List[List[List[List[int]]]]:
    """
    Overlay fire effect on yellow background, keeping yellow where fire is off.
    Where fire is black, show yellow. Where fire is orange, show fire.
    Image (white text) always stays on top.
    
    Args:
        image_matrix: The image to overlay (e.g., "12" white text)
        yellow_bg_color: RGB color for yellow background (255, 255, 0)
        fire_frames: Fire effect frames (black where no fire, orange where fire)
        
    Returns:
        List of frames with fire overlaid on yellow background and image on top
    """
    overlaid_frames = []
    
    height = len(image_matrix)
    width = len(image_matrix[0])
    
    for fire_frame in fire_frames:
        frame = []
        for y in range(height):
            row = []
            for x in range(width):
                image_pixel = image_matrix[y][x]
                fire_pixel = fire_frame[y][x]
                
                # If image pixel is not black, use it (white text on top)
                if image_pixel != [0, 0, 0]:
                    row.append(image_pixel)
                else:
                    # Background area: yellow or fire
                    # If fire is black (no fire), show yellow background
                    # If fire has color, show fire
                    if fire_pixel == [0, 0, 0]:
                        row.append([yellow_bg_color[0], yellow_bg_color[1], yellow_bg_color[2]])
                    else:
                        row.append(fire_pixel)
            frame.append(row)
        overlaid_frames.append(frame)
    
    return overlaid_frames


def create_background_scattering_from_bottom(
    width: int,
    height: int,
    bg_color: Tuple[int, int, int],
    image_matrix: List[List[List[int]]],
    duration: float,
    fps: int
) -> List[List[List[List[int]]]]:
    """
    Fill background with color from bottom to top using scattering effect.
    Image (white text) stays on top, background fills underneath.
    
    Args:
        width: Board width in pixels
        height: Board height in pixels
        bg_color: RGB color for background
        image_matrix: Image to overlay (white text)
        duration: Duration of background filling in seconds
        fps: Frames per second
        
    Returns:
        List of frames showing background filling from bottom to top
    """
    total_frames = int(duration * fps)
    frames = []
    
    # Intensity levels for scattering: 0%, 20%, 40%, 60%, 80%, 100%
    intensity_levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    
    for frame_idx in range(total_frames):
        # Determine current fill height (0 to height)
        progress = frame_idx / max(1, total_frames - 1)
        current_fill_line = int(height * (1.0 - progress))  # Starts at height, goes to 0
        
        frame = []
        for y in range(height):
            row = []
            for x in range(width):
                # Check if image has content at this position
                image_pixel = image_matrix[y][x]
                
                # If image pixel is not black, use it
                if image_pixel != [0, 0, 0]:
                    row.append(image_pixel)
                else:
                    # Fill background based on position and progress
                    if y > current_fill_line + 3:
                        # Fully filled area - solid background
                        row.append([bg_color[0], bg_color[1], bg_color[2]])
                    elif y > current_fill_line - 3:
                        # Transition zone - scattering effect
                        # Determine intensity level based on distance from fill line
                        dist_from_line = y - current_fill_line
                        if dist_from_line > 0:
                            # Below line - higher probability
                            prob = 0.5 + (dist_from_line / 6) * 0.5
                        else:
                            # Above line - lower probability
                            prob = 0.5 - (abs(dist_from_line) / 6) * 0.5
                        
                        if random.random() < prob:
                            row.append([bg_color[0], bg_color[1], bg_color[2]])
                        else:
                            row.append([0, 0, 0])
                    else:
                        # Empty area above fill line
                        row.append([0, 0, 0])
            
            frame.append(row)
        frames.append(frame)
    
    return frames


def create_background_scattering(
    image_matrix: List[List[List[int]]],
    bg_color: Tuple[int, int, int],
    duration: float,
    fps: int
) -> List[List[List[List[int]]]]:
    """
    Fill background with scattering effect while preserving foreground image.
    Background pixels (black in image) gradually fill with the specified color.
    
    Args:
        image_matrix: The foreground image (non-black pixels are preserved)
        bg_color: RGB color for background
        duration: Duration of scattering in seconds
        fps: Frames per second
        
    Returns:
        List of frames with background scattering effect
    """
    height = len(image_matrix)
    width = len(image_matrix[0])
    total_frames = int(duration * fps)
    frames = []
    
    # Intensity levels for scattering: 0%, 20%, 40%, 60%, 80%, 100%
    intensity_levels = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    
    # Create random scattering sequence for each background pixel
    pixel_sequences = {}
    for y in range(height):
        for x in range(width):
            # Only create sequence for background pixels (black in original image)
            if image_matrix[y][x] == [0, 0, 0]:
                # Generate random scattering sequence
                sequence = []
                current_level_idx = 0
                current_frame = 0
                
                while current_frame < total_frames:
                    # Progress to next level with some randomness
                    if random.random() < 0.7:
                        next_level_idx = min(current_level_idx + 1, len(intensity_levels) - 1)
                    else:
                        next_level_idx = random.randint(0, current_level_idx) if current_level_idx > 0 else 0
                    
                    intensity = intensity_levels[next_level_idx]
                    
                    # Random duration for this intensity
                    if next_level_idx == len(intensity_levels) - 1:
                        duration_frames = total_frames - current_frame
                    else:
                        max_dur = max(1, (total_frames - current_frame) // (len(intensity_levels) - next_level_idx))
                        duration_frames = random.randint(1, min(5, max_dur))
                    
                    # Fill sequence
                    for i in range(duration_frames):
                        if current_frame + i < total_frames:
                            sequence.append(intensity)
                    
                    current_frame += duration_frames
                    if next_level_idx > current_level_idx:
                        current_level_idx = next_level_idx
                
                # Ensure reaches 100%
                while len(sequence) < total_frames:
                    sequence.append(intensity_levels[-1])
                
                pixel_sequences[(x, y)] = sequence
    
    # Generate frames
    for frame_idx in range(total_frames):
        frame = []
        for y in range(height):
            row = []
            for x in range(width):
                image_pixel = image_matrix[y][x]
                
                # If foreground pixel (non-black), keep it
                if image_pixel != [0, 0, 0]:
                    row.append(image_pixel)
                else:
                    # Background pixel - apply scattering
                    if (x, y) in pixel_sequences:
                        intensity = pixel_sequences[(x, y)][frame_idx]
                        r = int(bg_color[0] * intensity)
                        g = int(bg_color[1] * intensity)
                        b = int(bg_color[2] * intensity)
                        row.append([r, g, b])
                    else:
                        row.append([0, 0, 0])
            frame.append(row)
        frames.append(frame)
    
    return frames


def add_solid_background(
    image_matrix: List[List[List[int]]],
    bg_color: Tuple[int, int, int]
) -> List[List[List[int]]]:
    """
    Add a solid color background to an image.
    Where image has black pixels, replace with background color.
    
    Args:
        image_matrix: The image (single frame)
        bg_color: RGB color for background
        
    Returns:
        Image with solid background
    """
    height = len(image_matrix)
    width = len(image_matrix[0])
    
    result = []
    for y in range(height):
        row = []
        for x in range(width):
            pixel = image_matrix[y][x]
            # If pixel is black, use background color
            if pixel == [0, 0, 0]:
                row.append([bg_color[0], bg_color[1], bg_color[2]])
            else:
                row.append(pixel)
        result.append(row)
    
    return result


if __name__ == "__main__":
    # Test
    print("Testing fire effect...")
    
    # Test fire rising
    rise_frames = create_fire_rise_from_bottom(16, 16, 1.0, 30)
    print(f"Created {len(rise_frames)} rise frames")
    
    # Test flickering fire
    flicker_frames = create_fire_flickering(16, 16, 3.0, 30, flicker_zone_height=8)
    print(f"Created {len(flicker_frames)} flickering frames")

    all_frames = rise_frames + flicker_frames

    import cv2
    import numpy as np
    
    # Visualize frames using OpenCV
    print(f"\nVisualizing {len(all_frames)} frames (press 'q' to quit)...")
    
    for i, frame in enumerate(all_frames):
        # Convert Python list to NumPy array
        frame_np = np.array(frame, dtype=np.uint8)
        
        # OpenCV uses BGR, convert from RGB to BGR
        frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        
        # Scale up for better visibility
        scaled_frame = cv2.resize(frame_bgr, 
                    (16 * 20, 16 * 20), 
                    interpolation=cv2.INTER_NEAREST)
        
        # Add frame counter
        cv2.putText(scaled_frame, f"Frame {i+1}/{len(all_frames)}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Fire Effect Test', scaled_frame)
        
        # Wait 33ms (approximately 30fps) or until 'q' is pressed
        if cv2.waitKey(33) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()
    print("Visualization complete!")