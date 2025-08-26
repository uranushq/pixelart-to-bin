import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.bin_maker import bin_maker
from src.utils.color_board_utils import create_solid_color_frames, validate_rgb

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python make_color_board.py <R> <G> <B>")
        print("Example: python make_color_board.py 255 0 0  # for red")
        sys.exit(1)
    
    try:
        r = int(sys.argv[1])
        g = int(sys.argv[2])
        b = int(sys.argv[3])
        
        # Validate RGB values
        if not validate_rgb(r, g, b):
            print("Error: RGB values must be between 0 and 255")
            sys.exit(1)
            
    except ValueError:
        print("Error: RGB values must be integers")
        sys.exit(1)
    
    # Create filename with RGB values
    output_path = f"test_color_board_R{r}_G{g}_B{b}.bin"
    
    # Test parameters
    width = 12
    height = 12
    frame_count = 50
    fps = 5
    
    # Generate frames using utils
    frames = create_solid_color_frames(r, g, b, width, height, frame_count)
    
    # Save using bin_maker (includes add_metadata with header)
    bin_maker(frames, output_path, fps)
    
    print(f"✅ Test color board saved to: {output_path}")
    print(f"   RGB: ({r}, {g}, {b})")
    print(f"   Size: {width}x{height}")
    print(f"   Frames: {frame_count}")
    print(f"   FPS: {fps}")
    print(f"   Duration: {frame_count/fps} seconds")