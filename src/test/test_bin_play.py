import struct
import sys
import os
import time
import argparse
from typing import List
import cv2
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def read_bin_header(file_path: str):
    """
    Read the header from a binary file.
    
    Args:
        file_path: Path to the binary file
        
    Returns:
        Tuple of (total_frames, height, width, fps)
    """
    with open(file_path, 'rb') as f:
        header_data = f.read(16)  # 4 * 4 bytes = 16 bytes
        if len(header_data) != 16:
            raise ValueError("Could not read complete header")
        total_frames, height, width, fps = struct.unpack('<IIII', header_data)
        return total_frames, height, width, fps


def read_frame_data(file_path: str, frame_index: int, height: int, width: int):
    """
    Read a specific frame from the binary file.
    
    Args:
        file_path: Path to the binary file
        frame_index: Index of the frame to read (0-based)
        height: Height of the frame
        width: Width of the frame
        
    Returns:
        RGB matrix for the frame
    """
    frame_size = height * width * 3  # 3 bytes per pixel (RGB)
    
    with open(file_path, 'rb') as f:
        # Skip header (16 bytes) and previous frames
        offset = 16 + frame_index * frame_size
        f.seek(offset)
        frame_data = f.read(frame_size)
        
        if len(frame_data) != frame_size:
            # Check if we've reached the end of available data
            file_size = os.path.getsize(file_path)
            available_frames = (file_size - 32) // frame_size  # subtract header + trailer
            if frame_index >= available_frames:
                return None  # No more frames available
            raise ValueError(f"Could not read complete frame {frame_index}")
        
        # Convert bytes to numpy array (RGB)
        frame_array = np.frombuffer(frame_data, dtype=np.uint8)
        frame_array = frame_array.reshape((height, width, 3))
        
        # Convert RGB to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
        
        return frame_bgr


def play_bin_file(file_path: str, scale_factor: int = 20, loop: bool = True):
    """
    Play a binary file as video with OpenCV.
    
    Args:
        file_path: Path to the binary file
        scale_factor: Factor to scale up the image (default: 20x)
        loop: Whether to loop the video
    """
    print(f"Playing binary file: {file_path}")
    print(f"Scale factor: {scale_factor}x")
    print("Press 'q' to quit, 'space' to pause/resume")
    
    try:
        # Read header
        total_frames, height, width, fps = read_bin_header(file_path)
        print(f"Video info: {total_frames} frames, {width}x{height} pixels, {fps} FPS")
        
        # Calculate actual frames based on file size
        file_size = os.path.getsize(file_path)
        actual_frame_data_size = file_size - 32  # subtract header and trailer
        actual_frames = actual_frame_data_size // (height * width * 3)
        effective_frames = min(total_frames, actual_frames)
        
        if effective_frames != total_frames:
            print(f"Warning: Header says {total_frames} frames, but file only contains {effective_frames} frames")
        
        # Calculate frame delay for target FPS
        frame_delay = 0.2
        
        # Create window
        cv2.namedWindow('Bin File Player', cv2.WINDOW_NORMAL)
        
        frame_index = 0
        paused = False
        last_frame_time = time.time()
        
        while True:
            current_time = time.time()
            
            # Only advance frame if not paused and enough time has passed
            if not paused and (current_time - last_frame_time) >= frame_delay:
                # Read current frame
                frame = read_frame_data(file_path, frame_index, height, width)
                
                if frame is None:
                    if loop:
                        frame_index = 0  # Loop back to start
                        continue
                    else:
                        break  # End of video
                
                # Scale up the frame
                if scale_factor > 1:
                    scaled_frame = cv2.resize(frame, 
                                            (width * scale_factor, height * scale_factor), 
                                            interpolation=cv2.INTER_NEAREST)
                else:
                    scaled_frame = frame
                
                # Display frame
                cv2.imshow('Bin File Player', scaled_frame)
                
                # Move to next frame
                frame_index = (frame_index + 1) % effective_frames
                last_frame_time = current_time
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # 'q' or ESC to quit
                break
            elif key == ord(' '):  # Space to pause/resume
                paused = not paused
                if paused:
                    print("Paused - Press space to resume")
                else:
                    print("Resumed")
                    last_frame_time = time.time()  # Reset timing when resuming
            elif key == ord('r'):  # 'r' to restart
                frame_index = 0
                print("Restarted")
            elif key == ord('s'):  # 's' to step frame by frame (when paused)
                if paused:
                    frame_index = (frame_index + 1) % effective_frames
                    frame = read_frame_data(file_path, frame_index, height, width)
                    if frame is not None:
                        if scale_factor > 1:
                            scaled_frame = cv2.resize(frame, 
                                                    (width * scale_factor, height * scale_factor), 
                                                    interpolation=cv2.INTER_NEAREST)
                        else:
                            scaled_frame = frame
                        cv2.imshow('Bin File Player', scaled_frame)
                        print(f"Frame: {frame_index}/{effective_frames}")
        
        cv2.destroyAllWindows()
        print("Playback finished")
        
    except Exception as e:
        print(f"Error playing binary file: {e}")
        cv2.destroyAllWindows()


def get_video_info(file_path: str):
    """
    Get video information from binary file.
    
    Args:
        file_path: Path to the binary file
    """
    try:
        total_frames, height, width, fps = read_bin_header(file_path)
        file_size = os.path.getsize(file_path)
        
        # Calculate actual frames
        actual_frame_data_size = file_size - 32
        actual_frames = actual_frame_data_size // (height * width * 3)
        effective_frames = min(total_frames, actual_frames)
        
        duration = effective_frames / fps if fps > 0 else 0
        
        print(f"File: {os.path.basename(file_path)}")
        print(f"Resolution: {width} x {height}")
        print(f"Frames: {effective_frames} (header says {total_frames})")
        print(f"FPS: {fps}")
        print(f"Duration: {duration:.1f} seconds")
        print(f"File size: {file_size:,} bytes")
        
    except Exception as e:
        print(f"Error reading file info: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play binary video files')
    parser.add_argument('bin_file', nargs='?', default='watermelon_sequence.bin',
                        help='Path to the binary file to play (default: watermelon_sequence.bin)')
    parser.add_argument('--scale', '-s', type=int, default=20,
                        help='Scale factor for display (default: 20)')
    parser.add_argument('--no-loop', action='store_true',
                        help='Do not loop the video')
    parser.add_argument('--info', '-i', action='store_true',
                        help='Show video information only (do not play)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.bin_file):
        print(f"Binary file not found: {args.bin_file}")
        
        # List available bin files
        import glob
        bin_files = glob.glob("*.bin")
        if bin_files:
            print(f"\nAvailable .bin files:")
            for bin_file in sorted(bin_files):
                print(f"  {bin_file}")
        else:
            print("No .bin files found in current directory")
        sys.exit(1)
    
    if args.info:
        get_video_info(args.bin_file)
    else:
        try:
            play_bin_file(args.bin_file, args.scale, not args.no_loop)
        except KeyboardInterrupt:
            print("\nPlayback interrupted by user")
            cv2.destroyAllWindows()
