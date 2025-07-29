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
    Get all image files in a directory sorted by filename.
    
    Args:
        directory: Directory path containing images
        
    Returns:
        Sorted list of image file paths
    """
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
    
    return sorted(image_files)


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
    cluster_config = config['cluster']
    loop_count = cluster_config.get('loop', 1)
    loop_delay_ms = cluster_config.get('loopDelay', 1000)
    
    # Get all image files
    image_files = get_image_files_in_directory(directory)
    
    # Create sequence based on clusters
    frames = []
    frame_duration = 0.2  # 0.2 seconds per frame
    
    # Build cluster sequences
    cluster_sequences = []
    for cluster_id in sorted(cluster_config.keys()):
        if cluster_id in ['loop', 'loopDelay']:
            continue
            
        indices = cluster_config[cluster_id]
        cluster_frames = []
        
        for idx in indices:
            if idx < len(image_files):
                img = Image.open(image_files[idx]).convert("RGB")
                matrix = image_to_matrix(img)
                cluster_frames.append(matrix)
        
        cluster_sequences.extend(cluster_frames)
    
    # Handle loop settings
    if loop_count == -1:
        # Infinite loop for 1 hour (3600 seconds)
        total_duration = 3600  # 1 hour in seconds
        
        # Calculate delay frames per loop
        delay_frames_per_loop = 0
        if loop_delay_ms > 0:
            delay_frames_per_loop = int((loop_delay_ms / 1000) / frame_duration)
        
        # Calculate total frames per loop (cluster frames + delay frames)
        frames_per_loop = len(cluster_sequences) + delay_frames_per_loop
        sequence_duration_per_loop = frames_per_loop * frame_duration
        
        # Calculate how many loops we need for exactly 1 hour
        loops_needed = int(total_duration / sequence_duration_per_loop)
        
        print(f"Creating 1-hour sequence with {loops_needed} loops")
        print(f"Frames per loop: {frames_per_loop} (cluster: {len(cluster_sequences)}, delay: {delay_frames_per_loop})")
        
        for loop_idx in range(loops_needed):
            frames.extend(cluster_sequences)
            
            # Add delay frames (black frames for loopDelay) - except for the last loop
            if loop_delay_ms > 0 and delay_frames_per_loop > 0 and cluster_sequences and loop_idx < loops_needed - 1:
                # Create black frame with same dimensions
                height = len(cluster_sequences[0])
                width = len(cluster_sequences[0][0])
                black_frame = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
                
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
                if frame_idx < len(cluster_sequences):
                    frames.append(cluster_sequences[frame_idx])
                    frame_idx += 1
                else:
                    frame_idx = 0
                    frames.append(cluster_sequences[frame_idx])
                    frame_idx += 1
    else:
        # Finite loop
        print(f"Creating sequence with {loop_count} loops")
        
        for _ in range(loop_count):
            frames.extend(cluster_sequences)
            
            # Add delay frames (black frames for loopDelay)
            if loop_delay_ms > 0:
                delay_frames = int((loop_delay_ms / 1000) / frame_duration)
                if delay_frames > 0 and cluster_sequences:
                    # Create black frame with same dimensions
                    height = len(cluster_sequences[0])
                    width = len(cluster_sequences[0][0])
                    black_frame = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
                    
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
