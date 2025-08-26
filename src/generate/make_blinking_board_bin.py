import sys
import os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.bin_maker import bin_maker
from src.utils.color_board_utils import create_blinking_color_frames, validate_rgb

def main():
    """
    Generate a blinking color board bin file with command line flags.
    """
    parser = argparse.ArgumentParser(description='Generate blinking color board bin file')
    
    # RGB color arguments (required)
    parser.add_argument('r', type=int, help='Red value (0-255)')
    parser.add_argument('g', type=int, help='Green value (0-255)')
    parser.add_argument('b', type=int, help='Blue value (0-255)')
    
    # Optional flags
    parser.add_argument('-w', '--width', type=int, default=12, help='Board width (default: 12)')
    parser.add_argument('--height', type=int, default=12, help='Board height (default: 12)')
    parser.add_argument('-r', '--repeat', type=int, default=5, help='Number of blink cycles (default: 5)')
    parser.add_argument('-f', '--frames-per-color', type=int, default=10, help='Frames per color (default: 10)')
    parser.add_argument('--fps', type=int, default=5, help='Frames per second (default: 5)')
    parser.add_argument('-o', '--output', type=str, help='Output filename (auto-generated if not specified)')
    
    args = parser.parse_args()
    
    # Validate RGB values
    if not validate_rgb(args.r, args.g, args.b):
        print("Error: RGB values must be between 0 and 255")
        sys.exit(1)
    
    # Validate other parameters
    if args.width <= 0 or args.height <= 0 or args.repeat <= 0 or args.frames_per_color <= 0 or args.fps <= 0:
        print("Error: width, height, repeat, frames-per-color, and fps must be positive integers")
        sys.exit(1)
    
    # RGB mode: use single color and black for blinking
    colors = [(args.r, args.g, args.b), (0, 0, 0)]  # Color and black
    
    # Create output directory path (parent/data)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    data_dir = os.path.join(parent_dir, 'data')
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate filename
    if args.output:
        output_filename = args.output
        if not output_filename.endswith('.bin'):
            output_filename += '.bin'
    else:
        output_filename = f"blinking_R{args.r}_G{args.g}_B{args.b}_{args.width}x{args.height}_repeat{args.repeat}.bin"
    
    output_path = os.path.join(data_dir, output_filename)
    
    print(f"RGB Mode: Blinking between ({args.r},{args.g},{args.b}) and black")
    print(f"Parameters: repeat={args.repeat}, size={args.width}x{args.height}, frames_per_color={args.frames_per_color}, fps={args.fps}")
    print(f"Output directory: {data_dir}")
    
    # Generate blinking frames
    frames = create_blinking_color_frames(colors, args.width, args.height, args.frames_per_color, args.repeat)
    
    # Save using bin_maker
    bin_maker(frames, output_path, args.fps)
    
    total_frames = len(frames)
    duration = total_frames / args.fps
    
    print(f"✅ Blinking color board saved to: {output_path}")
    print(f"   Size: {args.width}x{args.height}")
    print(f"   Colors: {len(colors)} colors")
    print(f"   Frames per color: {args.frames_per_color}")
    print(f"   Repeat: {args.repeat} times")
    print(f"   Total frames: {total_frames}")
    print(f"   FPS: {args.fps}")
    print(f"   Duration: {duration:.1f} seconds")

if __name__ == "__main__":
    main()
