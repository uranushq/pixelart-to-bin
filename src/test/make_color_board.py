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
    parser.add_argument("--gradient", action="store_true", help="Create gradient from black to target RGB")
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
        frame_count = int(round(args.time * fps))
    elif args.length is not None:
        frame_count = args.length
    else:
        frame_count = 50

    # Gradient 모드: 5초 주기의 디졸브 애니메이션 (점등 2초, 하이라이트 1초, 소등 2초)
    if args.gradient:
        frames = []
        fps = args.fps
        
        # 한 주기(5초)에 필요한 프레임 수 계산
        frames_per_cycle = 5 * fps  # 5초 * fps
        frames_fade_in = 2 * fps    # 점등 2초
        frames_highlight = 1 * fps   # 하이라이트 1초
        frames_fade_out = 2 * fps   # 소등 2초
        
        # 전체 재생시간에 맞춰 반복 횟수 계산
        total_cycles = max(1, frame_count // frames_per_cycle)
        
        # 각 주기마다 프레임 생성
        for _ in range(total_cycles):
            # 1. 점등 (2초): 검은색 → 목표색상
            for i in range(frames_fade_in):
                ratio = i / (frames_fade_in - 1) if frames_fade_in > 1 else 1
                rr = int(round(r * ratio))
                gg = int(round(g * ratio))
                bb = int(round(b * ratio))
                frames.append(create_solid_color_frames(rr, gg, bb, width, height, 1)[0])
            
            # 2. 하이라이트 (1초): 목표색상 유지
            frame = create_solid_color_frames(r, g, b, width, height, 1)[0]
            for _ in range(frames_highlight):
                frames.append(frame)
            
            # 3. 소등 (2초): 목표색상 → 검은색
            for i in range(frames_fade_out):
                ratio = 1 - (i / (frames_fade_out - 1) if frames_fade_out > 1 else 1)
                rr = int(round(r * ratio))
                gg = int(round(g * ratio))
                bb = int(round(b * ratio))
                frames.append(create_solid_color_frames(rr, gg, bb, width, height, 1)[0])
        
        # 남은 프레임은 검은색으로 채우기
        while len(frames) < frame_count:
            frames.append(create_solid_color_frames(0, 0, 0, width, height, 1)[0])
            
        output_path = f"test_color_board_dissolve_R{r}_G{g}_B{b}.bin"
        print(f"   Animation info: {total_cycles} cycles of 5-second dissolve (2s fade-in, 1s highlight, 2s fade-out)")
    else:
        # 단색 보드
        frames = create_solid_color_frames(r, g, b, width, height, frame_count)
        output_path = f"test_color_board_R{r}_G{g}_B{b}.bin"

    # Save using bin_maker (includes add_metadata with header)
    bin_maker(frames, output_path, fps)

    print(f"✅ Test color board saved to: {output_path}")
    if args.gradient:
        print(f"   Gradient from (0,0,0) to ({r}, {g}, {b})")
    else:
        print(f"   RGB: ({r}, {g}, {b})")
    print(f"   Size: {width}x{height}")
    print(f"   Frames: {len(frames)}")
    print(f"   FPS: {fps}")
    print(f"   Duration: {len(frames)/fps} seconds")