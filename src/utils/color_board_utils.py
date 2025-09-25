from typing import List, Tuple
import colorsys

def create_color_frame(r: int, g: int, b: int, width: int = 12, height: int = 12) -> List[List[List[int]]]:
    """
    Create a single color frame of given size.
    
    Args:
        r, g, b: RGB color values (0-255)
        width: width of the frame (default: 12)
        height: height of the frame (default: 12)
        
    Returns:
        3D list representing the RGB matrix [height][width][3]
    """
    return [[[r, g, b] for _ in range(width)] for _ in range(height)]

def create_blinking_color_frames(
    colors: List[Tuple[int, int, int]], 
    width: int = 12, 
    height: int = 12,
    frames_per_color: int = 5,
    repeat: int = 100
) -> List[List[List[List[int]]]]:
    """
    Create a sequence of blinking color frames.
    
    Args:
        colors: List of RGB tuples [(r,g,b), ...]
        width: Board width (default: 12)
        height: Board height (default: 12)
        frames_per_color: How many frames each color stays (default: 5)
        repeat: How many times to repeat the sequence (default: 1)
        
    Returns:
        List of frames for blinking animation
    """
    frames = []
    for _ in range(repeat):
        for color in colors:
            r, g, b = color
            frame = create_color_frame(r, g, b, width, height)
            for _ in range(frames_per_color):
                frames.append(frame)
    return frames

def create_solid_color_frames(
    r: int, g: int, b: int,
    width: int = 12,
    height: int = 12,
    frame_count: int = 50
) -> List[List[List[List[int]]]]:
    """
    Create frames of a single solid color.
    
    Args:
        r, g, b: RGB color values (0-255)
        width: Board width (default: 12)
        height: Board height (default: 12)
        frame_count: Number of frames to create (default: 50)
        
    Returns:
        List of frames with the same color
    """
    frames = []
    frame = create_color_frame(r, g, b, width, height)
    for _ in range(frame_count):
        frames.append(frame)
    return frames

def validate_rgb(r: int, g: int, b: int) -> bool:
    """
    Validate RGB values are in valid range (0-255).
    
    Args:
        r, g, b: RGB values to validate
        
    Returns:
        True if valid, False otherwise
    """
    return 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255


def create_rainbow_colors(steps: int) -> List[Tuple[int, int, int]]:
    """
    Create a beautiful rainbow color sequence from red to violet.
    
    Args:
        steps: Number of color steps in the rainbow
        
    Returns:
        List of RGB tuples representing rainbow colors
    """
    colors = []
    for i in range(steps):
        # HSV에서 H값을 0 (빨강)부터 300 (보라)까지 변화
        # 색상환에서 빨강(0°) → 주황(30°) → 노랑(60°) → 초록(120°) → 파랑(240°) → 보라(300°)
        hue = (i / steps) * 300 / 360  # 0~300도를 0~1 범위로 변환
        saturation = 1.0  # 채도는 최대
        value = 1.0  # 명도도 최대
        
        # HSV를 RGB로 변환
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        
        # 0-1 범위를 0-255 범위로 변환
        r = int(round(rgb[0] * 255))
        g = int(round(rgb[1] * 255))
        b = int(round(rgb[2] * 255))
        
        colors.append((r, g, b))
    
    return colors


def create_rainbow_frames(
    width: int = 12,
    height: int = 12,
    total_duration: float = 10.0,
    fps: int = 5,
    off_seconds: float = 1.0,
    steps: int = 60
) -> List[List[List[List[int]]]]:
    """
    Create rainbow color animation frames with off periods.
    
    Args:
        width: Board width (default: 12)
        height: Board height (default: 12)  
        total_duration: Total animation duration in seconds
        fps: Frames per second
        off_seconds: Duration of off state between colors (seconds)
        steps: Number of rainbow color steps (more = smoother transition)
        
    Returns:
        List of frames for rainbow animation
    """
    frames = []
    rainbow_colors = create_rainbow_colors(steps)
    
    total_frames = int(total_duration * fps)
    off_frames = int(off_seconds * fps)
    
    # 무지개 색상당 할당할 프레임 수 계산
    color_cycle_frames = max(1, steps + off_frames)  # 각 색상 + 꺼짐 시간
    
    frame_index = 0
    while frame_index < total_frames:
        # 모든 무지개 색상을 순회
        for i, (r, g, b) in enumerate(rainbow_colors):
            if frame_index >= total_frames:
                break
                
            # 해당 색상 프레임 추가
            color_frame = create_color_frame(r, g, b, width, height)
            frames.append(color_frame)
            frame_index += 1
            
            # 주기적으로 꺼짐 상태 추가 (예: 매 10번째 색상마다)
            if (i + 1) % 10 == 0 and off_frames > 0:
                for _ in range(min(off_frames, total_frames - frame_index)):
                    if frame_index >= total_frames:
                        break
                    off_frame = create_color_frame(0, 0, 0, width, height)
                    frames.append(off_frame)
                    frame_index += 1
    
    return frames[:total_frames]  # 정확한 길이로 자르기


def apply_luminance(r: int, g: int, b: int, luminance: float) -> Tuple[int, int, int]:
    """
    Apply luminance ratio to RGB values.
    
    Args:
        r, g, b: RGB color values (0-255)
        luminance: Luminance ratio (0.0-1.0)
        
    Returns:
        Tuple of adjusted RGB values
    """
    luminance = max(0.0, min(1.0, luminance))  # Clamp to 0-1 range
    new_r = int(round(r * luminance))
    new_g = int(round(g * luminance))
    new_b = int(round(b * luminance))
    return (new_r, new_g, new_b)


def create_sequential_pixel_frames(
    width: int = 12,
    height: int = 12,
    frames_per_pixel: int = 3,
    luminance: float = 1.0,
    steps: int = 60,
    cycles: int = 10
) -> List[List[List[List[int]]]]:
    """
    Create frames where pixels are turned on sequentially with rainbow colors.
    Only one pixel is lit at a time. Each cycle uses the same color, 
    and color changes between cycles.
    
    Args:
        width: Board width (default: 12)
        height: Board height (default: 12)
        frames_per_pixel: Number of frames each pixel stays on (default: 3)
        luminance: Luminance ratio for brightness control (0.0-1.0, default: 1.0)
        steps: Number of rainbow color steps (ignored - always uses 7 colors)
        cycles: Number of cycles to repeat (default: 10)
        
    Returns:
        List of frames for sequential pixel animation
    """
    frames = []
    # 고정된 7가지 무지개 색상 사용
    rainbow_colors = create_rainbow_colors(7)
    
    total_pixels = width * height
    
    # 각 사이클에 대해 처리
    for cycle in range(cycles):
        # 현재 사이클의 색상 선택 (7가지 색상을 순환)
        color_index = cycle % 7
        r, g, b = rainbow_colors[color_index]
        
        # Luminance 적용
        r, g, b = apply_luminance(r, g, b, luminance)
        
        # 현재 사이클에서 모든 픽셀을 순차적으로 켜기
        for pixel_index in range(total_pixels):
            # 픽셀 좌표 계산 (행 우선 순서)
            row = pixel_index // width
            col = pixel_index % width
            
            # 각 픽셀에 대해 frames_per_pixel 만큼 프레임 생성
            for _ in range(frames_per_pixel):
                # 모든 픽셀을 꺼진 상태로 초기화
                frame = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
                
                # 현재 픽셀만 켜기
                frame[row][col] = [r, g, b]
                
                frames.append(frame)
    
    return frames


def create_sequential_fill_frames(
    width: int = 12,
    height: int = 12,
    frames_per_pixel: int = 3,
    luminance: float = 1.0,
    cycles: int = 7,
    fill_seconds: float = 2.0,
    off_seconds: float = 2.0,
    fps: int = 5
) -> List[List[List[List[int]]]]:
    """
    Create frames where pixels scan sequentially, then fill entire board for fill_seconds,
    then turn off for off_seconds. Cycles through 7 rainbow colors.
    
    Args:
        width: Board width (default: 12)
        height: Board height (default: 12)
        frames_per_pixel: Number of frames each pixel stays on during scan (default: 3)
        luminance: Luminance ratio for brightness control (0.0-1.0, default: 1.0)
        cycles: Number of cycles to repeat (default: 7)
        fill_seconds: Duration to keep entire board filled (default: 2.0)
        off_seconds: Duration to keep entire board off (default: 2.0)
        fps: Frames per second for timing calculations (default: 5)
        
    Returns:
        List of frames for sequential-fill animation
    """
    frames = []
    # 고정된 7가지 무지개 색상 사용
    rainbow_colors = create_rainbow_colors(7)
    
    total_pixels = width * height
    fill_frames = int(fill_seconds * fps)
    off_frames = int(off_seconds * fps)
    
    # 각 사이클에 대해 처리
    for cycle in range(cycles):
        # 현재 사이클의 색상 선택 (7가지 색상을 순환)
        color_index = cycle % 7
        r, g, b = rainbow_colors[color_index]
        
        # Luminance 적용
        r, g, b = apply_luminance(r, g, b, luminance)
        
        # 1. 픽셀 단위로 순차적 스캔
        for pixel_index in range(total_pixels):
            # 픽셀 좌표 계산 (행 우선 순서)
            row = pixel_index // width
            col = pixel_index % width
            
            # 각 픽셀에 대해 frames_per_pixel 만큼 프레임 생성
            for _ in range(frames_per_pixel):
                # 모든 픽셀을 꺼진 상태로 초기화
                frame = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
                
                # 현재 픽셀만 켜기
                frame[row][col] = [r, g, b]
                
                frames.append(frame)
        
        # 2. 전체 보드를 해당 색상으로 fill_seconds 동안 켜기
        fill_frame = create_color_frame(r, g, b, width, height)
        for _ in range(fill_frames):
            frames.append(fill_frame)
        
        # 3. 전체 보드를 off_seconds 동안 끄기
        off_frame = create_color_frame(0, 0, 0, width, height)
        for _ in range(off_frames):
            frames.append(off_frame)
    
    return frames
