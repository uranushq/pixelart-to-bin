import sys
import os
import random
from typing import List, Tuple
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.bin_maker import bin_maker
from src.utils.color_board_utils import create_solid_color_frames, validate_rgb


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
    parser.add_argument("r", type=int, help="Red value (0-255)")
    parser.add_argument("g", type=int, help="Green value (0-255)")
    parser.add_argument("b", type=int, help="Blue value (0-255)")
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
        
        output_path = f"test_color_board_psyche_R{r}_G{g}_B{b}.bin"
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