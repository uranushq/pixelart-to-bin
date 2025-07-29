import struct
import sys
import os
from typing import Tuple, List
from PIL import Image
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


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
        total_frames_check, save_time, end_marker = struct.unpack('<IQI', trailer_data)
        return total_frames_check, save_time, end_marker


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
        f.seek(16 + frame_index * frame_size)
        frame_data = f.read(frame_size)
        
        if len(frame_data) != frame_size:
            raise ValueError(f"Could not read complete frame {frame_index}")
        
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
        sample_indices = [0, min(10, total_frames-1), min(100, total_frames-1), total_frames-1]
        sample_indices = list(set(sample_indices))  # Remove duplicates
        
        for idx in sample_indices:
            if idx < total_frames:
                try:
                    print(f"  Extracting frame {idx}...")
                    matrix = read_frame_data(file_path, idx, height, width)
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
        # Get original image files
        import glob
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(glob.glob(os.path.join(original_dir, ext)))
        image_files = sorted(image_files)
        
        if not image_files:
            print("No original images found for comparison")
            return
        
        # Read bin file header
        total_frames, height, width, fps = read_bin_header(bin_file)
        
        # Compare first few frames with original images
        for i in range(min(len(image_files), 10)):  # Compare first 10 images
            print(f"Comparing frame {i} with {os.path.basename(image_files[i])}...")
            
            # Extract frame from bin
            matrix = read_frame_data(bin_file, i, height, width)
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
    # Test the generated binary file
    bin_file_path = "watermelon_sequence.bin"
    
    if os.path.exists(bin_file_path):
        test_bin_file(bin_file_path)
        
        # Also compare with original images if available
        original_images_dir = "./data/watermelon"
        if os.path.exists(original_images_dir):
            compare_with_original_images(bin_file_path, original_images_dir)
    else:
        print(f"Binary file not found: {bin_file_path}")
        print("Please run make_sequence.py first to generate the binary file.")
