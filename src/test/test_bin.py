import struct
import sys
import os
import re
import glob
import argparse
from typing import Tuple, List
from PIL import Image
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def natural_sort_key(text):
    """Convert a string into a list of string and number chunks for natural sorting."""
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]


def read_bin_header(file_path: str) -> Tuple[int, int, int, int]:
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


def read_bin_trailer(file_path: str, frame_data_size: int) -> Tuple[int, int, int]:
    """
    Read the trailer from a binary file.
    
    Args:
        file_path: Path to the binary file
        frame_data_size: Size of frame data in bytes
        
    Returns:
        Tuple of (total_frames_check, save_time, end_marker)
    """
    with open(file_path, 'rb') as f:
        # Skip header (16 bytes) and frame data
        f.seek(16 + frame_data_size)
        trailer_data = f.read(16)  # 4 + 8 + 4 bytes = 16 bytes
        if len(trailer_data) != 16:
            raise ValueError("Could not read complete trailer")
        total_frames_check, save_time, end_marker = struct.unpack('<IQI', trailer_data)
        return total_frames_check, save_time, end_marker


def safe_read_frame_data(file_path: str, frame_index: int, height: int, width: int) -> List[List[List[int]]]:
    """
    Safely read a specific frame from the binary file with validation.
    
    Args:
        file_path: Path to the binary file
        frame_index: Index of the frame to read (0-based)
        height: Height of the frame
        width: Width of the frame
        
    Returns:
        RGB matrix for the frame or None if failed
    """
    frame_size = height * width * 3  # 3 bytes per pixel (RGB)
    file_size = os.path.getsize(file_path)
    
    with open(file_path, 'rb') as f:
        # Skip header (16 bytes) and previous frames
        offset = 16 + frame_index * frame_size
        
        # Check if we have enough data
        if offset + frame_size > file_size - 16:  # account for trailer
            raise ValueError(f"Frame {frame_index} would read beyond file size. Offset: {offset}, Frame size: {frame_size}, File size: {file_size}")
        
        f.seek(offset)
        frame_data = f.read(frame_size)
        
        if len(frame_data) != frame_size:
            raise ValueError(f"Could not read complete frame {frame_index}. Expected {frame_size} bytes, got {len(frame_data)} bytes")
        
        # Convert bytes to RGB matrix
        matrix = []
        byte_idx = 0
        
        for y in range(height):
            row = []
            for x in range(width):
                r = frame_data[byte_idx]
                g = frame_data[byte_idx + 1]
                b = frame_data[byte_idx + 2]
                row.append([r, g, b])
                byte_idx += 3
            matrix.append(row)
        
        return matrix


def read_frame_data(file_path: str, frame_index: int, height: int, width: int) -> List[List[List[int]]]:
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
            raise ValueError(f"Could not read complete frame {frame_index}. Expected {frame_size} bytes, got {len(frame_data)} bytes")
        
        # Convert bytes to RGB matrix
        matrix = []
        byte_idx = 0
        
        for y in range(height):
            row = []
            for x in range(width):
                r = frame_data[byte_idx]
                g = frame_data[byte_idx + 1]
                b = frame_data[byte_idx + 2]
                row.append([r, g, b])
                byte_idx += 3
            matrix.append(row)
        
        return matrix


def matrix_to_image(matrix: List[List[List[int]]]) -> Image.Image:
    """
    Convert RGB matrix to PIL Image.
    
    Args:
        matrix: RGB matrix
        
    Returns:
        PIL Image object
    """
    height = len(matrix)
    width = len(matrix[0])
    
    # Create numpy array for easier manipulation
    np_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            np_array[y, x] = matrix[y][x]
    
    return Image.fromarray(np_array, 'RGB')


def debug_bin_file(file_path: str):
    """
    Debug binary file structure to understand the actual format.
    
    Args:
        file_path: Path to the binary file to debug
    """
    print(f"Debugging binary file: {file_path}")
    print("=" * 50)
    
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size:,} bytes")
    
    with open(file_path, 'rb') as f:
        # Read first 32 bytes to see the structure
        first_bytes = f.read(32)
        print(f"\nFirst 32 bytes (hex): {' '.join(f'{b:02x}' for b in first_bytes)}")
        
        # Try different header interpretations
        f.seek(0)
        header_data = f.read(16)
        
        print(f"\nTrying different header interpretations:")
        print(f"As IIII (little-endian): {struct.unpack('<IIII', header_data)}")
        print(f"As IIII (big-endian): {struct.unpack('>IIII', header_data)}")
        
        # Check what the actual image size might be based on file size
        remaining_size = file_size - 32  # assuming 16 byte header + 16 byte trailer
        possible_frame_count = 1
        
        print(f"\nPossible image dimensions (assuming 1 frame):")
        for possible_pixels in [remaining_size // 3]:  # RGB = 3 bytes per pixel
            if possible_pixels > 0:
                # Try common aspect ratios
                import math
                sqrt_pixels = int(math.sqrt(possible_pixels))
                for width in range(max(1, sqrt_pixels - 100), sqrt_pixels + 100):
                    if possible_pixels % width == 0:
                        height = possible_pixels // width
                        print(f"  {width}x{height} pixels ({width*height*3} bytes)")
                        if width == height:  # square image
                            print(f"    ^ Square image: {width}x{width}")


def test_bin_file(file_path: str, output_dir: str = "./test_output"):
    """
    Test a binary file by reading its contents and extracting sample frames.
    
    Args:
        file_path: Path to the binary file to test
        output_dir: Directory to save extracted frames
    """
    print(f"Testing binary file: {file_path}")
    print("=" * 50)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Read header
        total_frames, height, width, fps = read_bin_header(file_path)
        print(f"Header Information:")
        print(f"  Total Frames: {total_frames}")
        print(f"  Dimensions: {width} x {height}")
        print(f"  FPS: {fps}")
        print(f"  Duration: {total_frames / fps:.1f} seconds")
        
        # Calculate file size expectations
        frame_size = height * width * 3
        expected_size = 16 + (total_frames * frame_size) + 16  # header + frames + trailer
        actual_size = os.path.getsize(file_path)
        
        print(f"\nFile Size Check:")
        print(f"  Expected: {expected_size:,} bytes")
        print(f"  Actual: {actual_size:,} bytes")
        print(f"  Match: {'✓' if expected_size == actual_size else '✗'}")
        
        # Calculate actual frames based on file size
        actual_frame_data_size = actual_size - 32  # subtract header and trailer
        actual_frames = actual_frame_data_size // (height * width * 3)
        
        print(f"\nFile Size Analysis:")
        print(f"  Header says: {total_frames} frames")
        print(f"  File size indicates: {actual_frames} frames")
        print(f"  Using: {min(total_frames, actual_frames)} frames for extraction")
        
        effective_frames = min(total_frames, actual_frames)
        
        # Read trailer
        frame_data_size = total_frames * frame_size
        total_frames_check, save_time, end_marker = read_bin_trailer(file_path, frame_data_size)
        
        print(f"\nTrailer Information:")
        print(f"  Total Frames Check: {total_frames_check}")
        print(f"  Save Time: {save_time}")
        print(f"  End Marker: 0x{end_marker:X}")
        print(f"  Header/Trailer Match: {'✓' if total_frames == total_frames_check else '✗'}")
        print(f"  End Marker Valid: {'✓' if end_marker == 0xDEADBEEF else '✗'}")
        
        # Extract sample frames
        print(f"\nExtracting Sample Frames:")
        sample_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        sample_indices = list(set(sample_indices))  # Remove duplicates
        
        for idx in sample_indices:
            if idx < effective_frames:
                try:
                    print(f"  Extracting frame {idx}...")
                    matrix = safe_read_frame_data(file_path, idx, height, width)
                    image = matrix_to_image(matrix)
                    
                    output_path = os.path.join(output_dir, f"frame_{idx:06d}.png")
                    image.save(output_path)
                    print(f"    Saved: {output_path}")
                    
                    # Check if frame is all black (delay frame)
                    is_black = all(
                        all(all(pixel == [0, 0, 0] for pixel in row) for row in matrix)
                        for row in matrix
                    )
                    if is_black:
                        print(f"    Note: Frame {idx} is a black (delay) frame")
                        
                except Exception as e:
                    print(f"    Error extracting frame {idx}: {e}")
                    # Try to extract what we can
                    try:
                        with open(file_path, 'rb') as f:
                            offset = 16 + idx * (height * width * 3)
                            f.seek(offset)
                            available_data = f.read()
                            print(f"    Available data from offset {offset}: {len(available_data)} bytes")
                    except:
                        pass
        
        print(f"\n{'✓' if expected_size == actual_size and total_frames == total_frames_check and end_marker == 0xDEADBEEF else '✗'} Binary file test completed!")
        
    except Exception as e:
        print(f"Error testing binary file: {e}")


def compare_with_original_images(bin_file: str, original_dir: str, output_dir: str = "./comparison_output"):
    """
    Compare extracted frames with original images.
    
    Args:
        bin_file: Path to the binary file
        original_dir: Directory containing original images
        output_dir: Directory to save comparison results
    """
    print(f"\nComparing with original images from: {original_dir}")
    print("=" * 50)
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Get original image files (excluding visualization files)
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(glob.glob(os.path.join(original_dir, ext)))
        
        # Filter out visualization and other non-animation files
        filtered_files = []
        for file_path in image_files:
            filename = os.path.basename(file_path).lower()
            # Exclude files with these patterns
            exclude_patterns = [
                'visualization',  # cluster visualization files
                'cluster_vis',    # alternative cluster vis naming
                'comparison',     # comparison files
                'config',         # config files
                'readme',         # readme images
                'sample',         # sample files
                'example',        # example files
            ]
            
            # Check if filename contains any exclude patterns
            should_exclude = any(pattern in filename for pattern in exclude_patterns)
            
            if not should_exclude:
                filtered_files.append(file_path)
        
        image_files = sorted(filtered_files, key=natural_sort_key)
        
        if not image_files:
            print("No original images found for comparison")
            return
        
        # Read bin file header
        total_frames, height, width, fps = read_bin_header(bin_file)
        
        # Compare first few frames with original images
        for i in range(min(len(image_files), 10)):  # Compare first 10 images
            print(f"Comparing frame {i} with {os.path.basename(image_files[i])}...")
            
            # Extract frame from bin
            matrix = safe_read_frame_data(bin_file, i, height, width)
            extracted_img = matrix_to_image(matrix)
            
            # Load original image
            original_img = Image.open(image_files[i]).convert("RGB")
            original_img = original_img.resize((width, height))  # Ensure same size
            
            # Save comparison
            comparison_path = os.path.join(output_dir, f"comparison_{i:03d}.png")
            
            # Create side-by-side comparison
            comparison_img = Image.new('RGB', (width * 2, height))
            comparison_img.paste(original_img, (0, 0))
            comparison_img.paste(extracted_img, (width, 0))
            comparison_img.save(comparison_path)
            
            print(f"  Saved comparison: {comparison_path}")
        
    except Exception as e:
        print(f"Error in comparison: {e}")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test binary file and compare with original images')
    parser.add_argument('bin_file', nargs='?', default='watermelon_sequence.bin',
                        help='Path to the binary file to test (default: watermelon_sequence.bin)')
    parser.add_argument('--original-dir', '-o', default='./data/watermelon',
                        help='Directory containing original images for comparison (default: ./data/watermelon)')
    parser.add_argument('--test-output', '-t', default='./test_output',
                        help='Directory to save extracted test frames (default: ./test_output)')
    parser.add_argument('--comparison-output', '-c', default='./comparison_output',
                        help='Directory to save comparison images (default: ./comparison_output)')
    parser.add_argument('--skip-comparison', action='store_true',
                        help='Skip comparison with original images')
    
    args = parser.parse_args()
    
    # Check if the provided path is a directory instead of a file
    if os.path.isdir(args.bin_file):
        print(f"Error: '{args.bin_file}' is a directory, not a binary file.")
        print(f"Please provide a .bin file path, for example:")
        print(f"  python {sys.argv[0]} watermelon_sequence.bin")
        print(f"  python {sys.argv[0]} output_video.bin")
        sys.exit(1)
    
    # Test the binary file
    if os.path.exists(args.bin_file):
        print(f"Testing binary file: {args.bin_file}")
        
        # First run debug to understand the structure
        debug_bin_file(args.bin_file)
        
        # Also check original image sizes
        if os.path.exists(args.original_dir):
            print(f"\nChecking original image sizes from: {args.original_dir}")
            image_files = []
            for ext in ['*.png', '*.jpg', '*.jpeg']:
                image_files.extend(glob.glob(os.path.join(args.original_dir, ext)))
            image_files = sorted(image_files, key=natural_sort_key)
            
            if image_files:
                sample_img = Image.open(image_files[0])
                print(f"Sample image size: {sample_img.size} (width x height)")
                print(f"Number of image files: {len(image_files)}")
        
        print("\n" + "="*50)
        
        test_bin_file(args.bin_file, args.test_output)
        
        # Compare with original images if not skipped and directory exists
        if not args.skip_comparison and os.path.exists(args.original_dir):
            compare_with_original_images(args.bin_file, args.original_dir, args.comparison_output)
        elif not args.skip_comparison:
            print(f"\nOriginal images directory not found: {args.original_dir}")
            print("Skipping comparison...")
    else:
        print(f"Binary file not found: {args.bin_file}")
        print(f"Available .bin files in current directory:")
        bin_files = glob.glob("*.bin")
        if bin_files:
            for bin_file in sorted(bin_files):
                print(f"  {bin_file}")
            print(f"\nExample usage:")
            print(f"  python {sys.argv[0]} {bin_files[0]}")
        else:
            print("  No .bin files found")
            print("Please run make_sequence.py first to generate a binary file.")
