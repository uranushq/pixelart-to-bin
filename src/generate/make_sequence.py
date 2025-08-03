from typing import List, Dict, Any
from PIL import Image
import sys
import os
import json
import glob

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.image2matrix import image_to_matrix
from src.utils.bin_maker import bin_maker


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to the config.json file
        
    Returns:
        Dictionary containing configuration data
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_image_files_in_directory(directory: str) -> List[str]:
    """
    Get all image files in a directory sorted by filename (natural sort for numbers).
    Excludes visualization and config files.
    
    Args:
        directory: Directory path containing images
        
    Returns:
        Sorted list of image file paths (excluding visualization files)
    """
    import re
    
    def natural_sort_key(text):
        """Convert a string into a list of string and number chunks for natural sorting."""
        return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]
    
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
    
    # Filter out visualization and other non-animation files
    filtered_files = []
    for file_path in image_files:
        filename = os.path.basename(file_path).lower()
        # Exclude files with these patterns
        exclude_patterns = [
            'visualization',  # cluster visualization files
            'cluster_vis',    # alternative cluster vis naming
            'comparison',     # comparison files
            'config',         # config files (shouldn't be images anyway)
            'readme',         # readme images
            'sample',         # sample files
            'example',        # example files
        ]
        
        # Check if filename contains any exclude patterns
        should_exclude = any(pattern in filename for pattern in exclude_patterns)
        
        if not should_exclude:
            filtered_files.append(file_path)
        else:
            print(f"Excluding file: {os.path.basename(file_path)}")
    
    return sorted(filtered_files, key=natural_sort_key)


def create_sequence_from_config(directory: str, output_path: str):
    """
    Create binary sequence from images using config.json settings.
    
    Args:
        directory: Directory containing images and config.json
        output_path: Output binary file path
    """
    config_path = os.path.join(directory, 'config.json')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.json not found in {directory}")
    
    # Load configuration
    config = load_config(config_path)
    loop_count = config.get('loop', -1)
    loop_delay_ms = config.get('loopDelay', 1000)
    countdown_enabled = config.get('countDown', True)
    
    # Get all image files
    image_files = get_image_files_in_directory(directory)
    print(f"Found {len(image_files)} image files:")
    for img_file in image_files:
        print(f"  {os.path.basename(img_file)}")
    
    # Create sequence from all sorted images
    frames = []
    frame_duration = 0.2  # 0.2 seconds per frame
    
    # Build image sequences from all sorted images
    image_sequences = []
    for image_file in image_files:
        img = Image.open(image_file).convert("RGB")
        matrix = image_to_matrix(img)
        image_sequences.append(matrix)
    
    if not image_sequences:
        print("No images found to process!")
        return
    
    # Get image dimensions for countdown frames
    image_height = len(image_sequences[0])
    image_width = len(image_sequences[0][0])
    
    def create_countdown_frames():
        """Create countdown frames: red, yellow, green, black (1 second each)"""
        countdown_frames = []
        fps = int(1 / frame_duration)  # 5 FPS
        frames_per_second = fps
        
        # 1 second red frame
        red_frame = [[[255, 0, 0] for _ in range(image_width)] for _ in range(image_height)]
        for _ in range(frames_per_second):
            countdown_frames.append(red_frame)
        
        # 1 second yellow frame  
        yellow_frame = [[[255, 255, 0] for _ in range(image_width)] for _ in range(image_height)]
        for _ in range(frames_per_second):
            countdown_frames.append(yellow_frame)
        
        # 1 second green frame
        green_frame = [[[0, 255, 0] for _ in range(image_width)] for _ in range(image_height)]
        for _ in range(frames_per_second):
            countdown_frames.append(green_frame)
        
        # 1 second black frame
        black_frame = [[[0, 0, 0] for _ in range(image_width)] for _ in range(image_height)]
        for _ in range(frames_per_second):
            countdown_frames.append(black_frame)
        
        return countdown_frames
    
    # Handle loop settings
    if loop_count == -1:
        # Infinite loop for 1 hour (3600 seconds)
        total_duration = 3600  # 1 hour in seconds
        
        # Calculate delay frames per loop
        delay_frames_per_loop = 0
        if loop_delay_ms > 0:
            delay_frames_per_loop = int((loop_delay_ms / 1000) / frame_duration)
        
        # Calculate countdown frames per loop (4 seconds = red + yellow + green + black)
        countdown_frames_per_loop = 0
        if countdown_enabled:
            fps = int(1 / frame_duration)  # 5 FPS
            countdown_frames_per_loop = 4 * fps  # 4 seconds * 5 FPS = 20 frames
        
        # Calculate total frames per loop (countdown + image frames + delay frames)
        frames_per_loop = countdown_frames_per_loop + len(image_sequences) + delay_frames_per_loop
        sequence_duration_per_loop = frames_per_loop * frame_duration
        
        # Calculate how many loops we need for exactly 1 hour
        loops_needed = int(total_duration / sequence_duration_per_loop)
        
        print(f"Creating 1-hour sequence with {loops_needed} loops")
        print(f"Frames per loop: {frames_per_loop} (countdown: {countdown_frames_per_loop}, images: {len(image_sequences)}, delay: {delay_frames_per_loop})")
        if countdown_enabled:
            print("Countdown frames enabled: 4 seconds per loop (red, yellow, green, black)")
        
        for loop_idx in range(loops_needed):
            # Add countdown frames at the beginning of each loop
            if countdown_enabled:
                countdown_frames = create_countdown_frames()
                frames.extend(countdown_frames)
            
            # Add the actual image sequence
            frames.extend(image_sequences)
            
            # Add delay frames (black frames for loopDelay) - except for the last loop
            if loop_delay_ms > 0 and delay_frames_per_loop > 0 and image_sequences and loop_idx < loops_needed - 1:
                # Create black frame with same dimensions
                black_frame = [[[0, 0, 0] for _ in range(image_width)] for _ in range(image_height)]
                
                for _ in range(delay_frames_per_loop):
                    frames.append(black_frame)
        
        # Fill remaining time to exactly 1 hour if needed
        current_duration = len(frames) * frame_duration
        remaining_time = total_duration - current_duration
        if remaining_time > 0:
            remaining_frames = int(remaining_time / frame_duration)
            print(f"Adding {remaining_frames} frames to reach exactly 1 hour")
            
            # Add frames from the beginning of sequence to fill remaining time
            frame_idx = 0
            for _ in range(remaining_frames):
                if frame_idx < len(image_sequences):
                    frames.append(image_sequences[frame_idx])
                    frame_idx += 1
                else:
                    frame_idx = 0
                    frames.append(image_sequences[frame_idx])
                    frame_idx += 1
    else:
        # Finite loop
        print(f"Creating sequence with {loop_count} loops")
        if countdown_enabled:
            print("Countdown frames enabled: 4 seconds per loop (red, yellow, green, black)")
        
        for loop_idx in range(loop_count):
            # Add countdown frames at the beginning of each loop
            if countdown_enabled:
                countdown_frames = create_countdown_frames()
                frames.extend(countdown_frames)
            
            # Add the actual image sequence
            frames.extend(image_sequences)
            
            # Add delay frames (black frames for loopDelay)
            if loop_delay_ms > 0:
                delay_frames = int((loop_delay_ms / 1000) / frame_duration)
                if delay_frames > 0 and image_sequences:
                    # Create black frame with same dimensions
                    black_frame = [[[0, 0, 0] for _ in range(image_width)] for _ in range(image_height)]
                    
                    for _ in range(delay_frames):
                        frames.append(black_frame)
    
    # Calculate FPS (frames per second)
    fps = int(1 / frame_duration)  # 5 FPS for 0.2 seconds per frame
    
    # Save using bin_maker
    bin_maker(frames, output_path, fps)
    
    total_duration = len(frames) * frame_duration
    print(f"Total sequence duration: {total_duration:.1f} seconds ({len(frames)} frames)")


def save_bin_from_images(image_paths: List[str], output_path: str, fps: int = 1):
    """
    Convert image files to binary format.
    
    Args:
        image_paths: List of image file paths
        output_path: Path to save the output binary file
        fps: Frames per second
    """
    frames = []
    for path in image_paths:
        img = Image.open(path).convert("RGB")
        matrix = image_to_matrix(img)
        frames.append(matrix)

    # Use bin_maker to save the frames
    bin_maker(frames, output_path, fps)


if __name__ == "__main__":
    # Example 1: Using config.json from watermelon directory
    watermelon_dir = r"./data/watermelon"
    output_file = "watermelon_sequence.bin"
    create_sequence_from_config(watermelon_dir, output_file)
    
    # Example 2: Using individual images (legacy method)
    # image_paths = [r"./data/watermelon/수박_1.png"]
    # output_file = "output_video.bin"
    # save_bin_from_images(image_paths, output_file, fps=1)
