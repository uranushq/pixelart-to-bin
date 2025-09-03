import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.bin_maker import bin_maker
from src.utils.color_board_utils import create_solid_color_frames, validate_rgb


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a solid color board bin file.")
    parser.add_argument("r", type=int, help="Red value (0-255)")
    parser.add_argument("g", type=int, help="Green value (0-255)")
    parser.add_argument("b", type=int, help="Blue value (0-255)")
    parser.add_argument("-l", "--length", type=int, default=None, help="Frame length (number of frames)")
    parser.add_argument("-t", "--time", type=float, default=None, help="Duration in seconds (overrides length if set)")
    parser.add_argument("--fps", type=int, default=5, help="Frames per second (default: 5)")
    parser.add_argument("--width", type=int, default=12, help="Board width (default: 12)")
    parser.add_argument("--height", type=int, default=12, help="Board height (default: 12)")
    args = parser.parse_args()

    r = args.r
    g = args.g
    b = args.b

    # Validate RGB values
    if not validate_rgb(r, g, b):
        print("Error: RGB values must be between 0 and 255")
        sys.exit(1)

    fps = args.fps
    width = args.width
    height = args.height

    # Determine frame_count
    if args.time is not None:
        # -t 옵션이 있으면 초 단위로 프레임 개수 계산
        frame_count = int(round(args.time * fps))
    elif args.length is not None:
        frame_count = args.length
    else:
        frame_count = 50

    # Create filename with RGB values
    output_path = f"test_color_board_R{r}_G{g}_B{b}.bin"

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