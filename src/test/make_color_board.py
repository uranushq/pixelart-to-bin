import sys
import os
import random
from typing import List, Tuple
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.bin_maker import bin_maker
from src.utils.color_board_utils import create_solid_color_frames, validate_rgb, create_rainbow_frames, create_sequential_pixel_frames, apply_luminance, create_sequential_fill_frames


import argparse

def create_psyche_frames(r: int, g: int, b: int, width: int, height: int, 
                        total_duration: float, fps: int,
                        min_interval: float = 1.0, 
                        max_interval: float = 3.0,
                        fade_duration: float = 0.3) -> List[List[List[List[int]]]]:
    """
    사이키 조명처럼 랜덤한 간격으로 깜빡이는 프레임 생성
    
    Args:
        r, g, b: 목표 RGB 값
        width, height: 보드 크기
        total_duration: 총 재생 시간 (초)
        fps: 초당 프레임 수
        min_interval: 최소 깜빡임 간격 (초)
        max_interval: 최대 깜빡임 간격 (초)
        fade_duration: 페이드 인/아웃 시간 (초)
    """
    frames = []
    current_time = 0.0
    fade_frames = int(fade_duration * fps)
    
    while current_time < total_duration:
        # 랜덤 간격 선택 (1~3초)
        interval = random.uniform(min_interval, max_interval)
        interval_frames = int(interval * fps)
        
        # 1. 페이드 아웃 (켜진 상태 → 꺼짐)
        for i in range(fade_frames):
            ratio = 1 - (i / (fade_frames - 1) if fade_frames > 1 else 1)
            rr = int(round(r * ratio))
            gg = int(round(g * ratio))
            bb = int(round(b * ratio))
            frames.append(create_solid_color_frames(rr, gg, bb, width, height, 1)[0])
        
        # 2. 잠시 꺼진 상태 유지
        off_frames = max(1, interval_frames - 2 * fade_frames)
        frames.extend([create_solid_color_frames(0, 0, 0, width, height, 1)[0]] * off_frames)
        
        # 3. 페이드 인 (꺼짐 → 켜진 상태)
        for i in range(fade_frames):
            ratio = i / (fade_frames - 1) if fade_frames > 1 else 1
            rr = int(round(r * ratio))
            gg = int(round(g * ratio))
            bb = int(round(b * ratio))
            frames.append(create_solid_color_frames(rr, gg, bb, width, height, 1)[0])
        
        # 4. 잠시 켜진 상태 유지
        on_frames = max(1, interval_frames - 2 * fade_frames)
        frames.extend([create_solid_color_frames(r, g, b, width, height, 1)[0]] * on_frames)
        
        current_time += interval * 2  # 한 주기 완료
    
    return frames[:int(total_duration * fps)]  # 정확한 길이로 잘라내기

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a solid color board bin file.")
    parser.add_argument("--rainbow", action="store_true", help="Create beautiful rainbow color animation")
    parser.add_argument("--sequential", action="store_true", help="Create sequential pixel lighting with rainbow colors")
    parser.add_argument("--sequential-fill", action="store_true", help="Create sequential scan + fill + off pattern with rainbow colors")
    parser.add_argument("--off-seconds", type=float, default=1.0, help="Duration of off state between colors for rainbow mode (seconds)")
    parser.add_argument("--luminance", type=float, default=1.0, help="Luminance ratio for brightness control (0.0-1.0, default: 1.0)")
    parser.add_argument("--frames-per-pixel", type=int, default=3, help="Number of frames each pixel stays on in sequential mode (default: 3)")
    parser.add_argument("--cycles", type=int, default=10, help="Number of cycles to repeat in sequential mode (default: 10)")
    parser.add_argument("--fill-seconds", type=float, default=2.0, help="Duration to keep board filled in sequential-fill mode (default: 2.0)")
    parser.add_argument("--off-seconds-fill", type=float, default=2.0, help="Duration to keep board off in sequential-fill mode (default: 2.0)")
    parser.add_argument("r", type=int, nargs='?', default=255, help="Red value (0-255), ignored in rainbow mode")
    parser.add_argument("g", type=int, nargs='?', default=0, help="Green value (0-255), ignored in rainbow mode")
    parser.add_argument("b", type=int, nargs='?', default=0, help="Blue value (0-255), ignored in rainbow mode")
    parser.add_argument("-l", "--length", type=int, default=None, help="Frame length (number of frames)")
    parser.add_argument("-t", "--time", type=float, default=None, help="Duration in seconds (overrides length if set)")
    parser.add_argument("--fps", type=int, default=5, help="Frames per second (default: 5)")
    parser.add_argument("--width", type=int, default=12, help="Board width (default: 12)")
    parser.add_argument("--height", type=int, default=12, help="Board height (default: 12)")
    parser.add_argument("--gradient", action="store_true", help="Create gradient from black to target RGB")
    parser.add_argument("--psyche", action="store_true", help="Create psychedelic light effect with random intervals")
    parser.add_argument("--min-interval", type=float, default=1.0, help="Minimum interval for psyche effect (seconds)")
    parser.add_argument("--max-interval", type=float, default=3.0, help="Maximum interval for psyche effect (seconds)")
    parser.add_argument("--fade", type=float, default=0.3, help="Fade duration for psyche effect (seconds)")
    parser.add_argument("--rainbow-steps", type=int, default=60, help="Number of rainbow color steps (more = smoother transition)")
    args = parser.parse_args()

    # Validate luminance
    if not (0.0 <= args.luminance <= 1.0):
        print("Error: Luminance must be between 0.0 and 1.0")
        sys.exit(1)

    # Sequential-fill mode handling
    if args.sequential_fill:
        fps = args.fps
        width = args.width
        height = args.height
        
        frames = create_sequential_fill_frames(
            width=width,
            height=height,
            frames_per_pixel=args.frames_per_pixel,
            luminance=args.luminance,
            cycles=args.cycles,
            fill_seconds=args.fill_seconds,
            off_seconds=args.off_seconds_fill,
            fps=fps
        )
        
        output_path = f"test_color_board_sequential_fill_{width}x{height}_luminance{args.luminance}_fill{args.fill_seconds}s_off{args.off_seconds_fill}s_cycles{args.cycles}.bin"
        
        # Save using bin_maker (includes add_metadata with header)
        bin_maker(frames, output_path, fps)
        
        scan_duration = (width * height * args.frames_per_pixel) / fps
        cycle_duration = scan_duration + args.fill_seconds + args.off_seconds_fill
        
        print(f"✅ Sequential-fill color board saved to: {output_path}")
        print(f"   Animation: Sequential scan → Fill → Off pattern")
        print(f"   Pattern per cycle:")
        print(f"     1. Scan pixels sequentially ({scan_duration:.1f}s)")
        print(f"     2. Fill entire board with color ({args.fill_seconds}s)")
        print(f"     3. Turn off entire board ({args.off_seconds_fill}s)")
        print(f"   Rainbow colors: 7 fixed colors cycling")
        print(f"   Frames per pixel: {args.frames_per_pixel}")
        print(f"   Cycles: {args.cycles} (each cycle = {cycle_duration:.1f}s)")
        print(f"   Luminance: {args.luminance} ({int(args.luminance*100)}% brightness)")
        print(f"   Size: {width}x{height}")
        print(f"   Total frames: {len(frames)}")
        print(f"   FPS: {fps}")
        print(f"   Duration: {len(frames)/fps:.1f} seconds")
        exit(0)

    # Sequential pixel mode handling
    if args.sequential:
        fps = args.fps
        width = args.width
        height = args.height
        
        frames = create_sequential_pixel_frames(
            width=width,
            height=height,
            frames_per_pixel=args.frames_per_pixel,
            luminance=args.luminance,
            steps=args.rainbow_steps,
            cycles=args.cycles
        )
        
        output_path = f"test_color_board_sequential_{width}x{height}_luminance{args.luminance}_fperpx{args.frames_per_pixel}_cycles{args.cycles}.bin"
        
        # Save using bin_maker (includes add_metadata with header)
        bin_maker(frames, output_path, fps)
        
        print(f"✅ Sequential pixel color board saved to: {output_path}")
        print(f"   Animation: Sequential pixel lighting with rainbow colors")
        print(f"   Pixel order: (0,0) → (0,1) → (0,2) → ... → ({height-1},{width-1})")
        print(f"   Behavior: Only ONE pixel lit at a time")
        print(f"   Color cycling: Same color per cycle, changes between cycles") 
        print(f"   Rainbow colors: 7 fixed colors (Red→Orange→Yellow→Green→Blue→Indigo→Violet)")
        print(f"   Color repetition: Cycles {args.cycles} uses colors in order: {[f'Color {(i%7)+1}' for i in range(min(args.cycles, 7))]}")
        print(f"   Frames per pixel: {args.frames_per_pixel}")
        print(f"   Cycles: {args.cycles} (each cycle = {width*height} pixels)")
        print(f"   Luminance: {args.luminance} ({int(args.luminance*100)}% brightness)")
        print(f"   Size: {width}x{height}")
        print(f"   Total frames: {len(frames)}")
        print(f"   FPS: {fps}")
        print(f"   Duration: {len(frames)/fps:.1f} seconds")
        exit(0)

    # Rainbow mode handling
    if args.rainbow:
        # Set default values if not specified
        if args.time is None and args.length is None:
            print("Warning: No duration specified for rainbow mode. Using default 30 seconds.")
            args.time = 30.0
        
        fps = args.fps
        width = args.width
        height = args.height
        
        # Determine frame_count for rainbow
        if args.time is not None:
            frame_count = int(round(args.time * fps))
        elif args.length is not None:
            frame_count = args.length
        else:
            frame_count = 30 * fps  # default 30 seconds
        
        frames = create_rainbow_frames(
            width=width,
            height=height,
            total_duration=frame_count/fps,
            fps=fps,
            off_seconds=args.off_seconds,
            steps=args.rainbow_steps
        )
        
        # Apply luminance to all frames if not 1.0
        if args.luminance != 1.0:
            for frame_idx in range(len(frames)):
                for row in range(height):
                    for col in range(width):
                        r, g, b = frames[frame_idx][row][col]
                        frames[frame_idx][row][col] = list(apply_luminance(r, g, b, args.luminance))
        
        output_path = f"test_color_board_rainbow_off{args.off_seconds}s_luminance{args.luminance}.bin"
        
        # Save using bin_maker (includes add_metadata with header)
        bin_maker(frames, output_path, fps)
        
        print(f"✅ Rainbow color board saved to: {output_path}")
        print(f"   Animation: Beautiful rainbow from red to violet")
        print(f"   Rainbow steps: {args.rainbow_steps} (smoother with more steps)")
        print(f"   Off duration: {args.off_seconds} seconds between color cycles")
        print(f"   Luminance: {args.luminance} ({int(args.luminance*100)}% brightness)")
        print(f"   Size: {width}x{height}")
        print(f"   Frames: {len(frames)}")
        print(f"   FPS: {fps}")
        print(f"   Duration: {len(frames)/fps:.1f} seconds")
        exit(0)

    r = args.r
    g = args.g
    b = args.b

    # Validate RGB values
    if not validate_rgb(r, g, b):
        print("Error: RGB values must be between 0 and 255")
        sys.exit(1)
    
    # Apply luminance to RGB values
    r, g, b = apply_luminance(r, g, b, args.luminance)

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

    # 애니메이션 모드 선택
    if args.psyche:
        # 사이키 조명 모드
        if args.time is None and args.length is None:
            print("Warning: No duration specified. Using default 60 seconds.")
            args.time = 60.0
            frame_count = int(round(args.time * fps))
        
        frames = create_psyche_frames(
            r, g, b, width, height,
            total_duration=frame_count/fps,
            fps=fps,
            min_interval=args.min_interval,
            max_interval=args.max_interval,
            fade_duration=args.fade
        )
        
        output_path = f"test_color_board_psyche_R{r}_G{g}_B{b}_luminance{args.luminance}.bin"
        print(f"   Animation info: Psychedelic effect with {args.min_interval}-{args.max_interval}s intervals")
        print(f"   Fade duration: {args.fade}s")
        
    elif args.gradient:
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
            
        output_path = f"test_color_board_dissolve_R{r}_G{g}_B{b}_luminance{args.luminance}.bin"
        print(f"   Animation info: {total_cycles} cycles of 5-second dissolve (2s fade-in, 1s highlight, 2s fade-out)")
    else:
        # 단색 보드
        frames = create_solid_color_frames(r, g, b, width, height, frame_count)
        output_path = f"test_color_board_R{r}_G{g}_B{b}_luminance{args.luminance}.bin"

    # Save using bin_maker (includes add_metadata with header)
    bin_maker(frames, output_path, fps)

    print(f"✅ Test color board saved to: {output_path}")
    if args.gradient:
        print(f"   Gradient from (0,0,0) to ({r}, {g}, {b})")
    else:
        print(f"   RGB: ({r}, {g}, {b})")
    print(f"   Luminance: {args.luminance} ({int(args.luminance*100)}% brightness)")
    print(f"   Size: {width}x{height}")
    print(f"   Frames: {len(frames)}")
    print(f"   FPS: {fps}")
    print(f"   Duration: {len(frames)/fps} seconds")