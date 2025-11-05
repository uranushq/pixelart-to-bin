#!/usr/bin/env python3
"""
SMTM Temporary Generation Script
Generate special binary sequences for SMTM show with 3 different modes.

Usage:
    python smtm_temp_generation.py --mode <1|2|3> --duration <seconds> [--fps <fps>] [--output <path>]

Modes:
    1: SMTM.png display, then left-to-right wipe to 12.png
    2: SMTM12.png bottom-to-top scattering appearance
    3: S→M→T→M (each letter scattering), then 12.png from bottom
"""

import sys
import os
import argparse
from PIL import Image

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from src.utils.image2matrix import image_to_matrix
from src.utils.bin_maker import bin_maker_with_tiles
from src.utils.scattering_animation import create_scattering_transition
from src.utils.directional_scattering import (
    create_left_to_right_wipe,
    create_bottom_to_top_scattering,
    create_center_expand_scattering
)
from src.utils.fire_effect import (
    create_fire_rise_from_bottom,
    create_fire_flickering,
    overlay_image_on_fire,
    add_solid_background,
    create_background_scattering,
    create_background_scattering_from_bottom,
    overlay_fire_on_yellow_background
)


def mode1_smtm_to_12(duration: float, fps: int, output_path: str):
    """
    Mode 1: SMTM.png → (wipe transition) → 12.png with burning background effect
    
    Args:
        duration: Duration to hold SMTM.png in seconds
        fps: Frames per second
        output_path: Output file base path
    """
    print("\n🎬 Mode 1: SMTM → 12 (Left-to-Right Wipe + Fire Effect)")
    print(f"   Duration: {duration}s")
    print(f"   FPS: {fps}")
    
    # Load images
    smtm_path = "./data/smtm+12/SMTM.png"
    twelve_path = "./data/smtm+12/12.png"
    
    if not os.path.exists(smtm_path) or not os.path.exists(twelve_path):
        raise FileNotFoundError("Required images not found in ./data/smtm+12/")
    
    smtm_img = Image.open(smtm_path).convert("RGB")
    twelve_img = Image.open(twelve_path).convert("RGB")
    
    smtm_matrix = image_to_matrix(smtm_img)
    twelve_matrix = image_to_matrix(twelve_img)
    
    height = len(smtm_matrix)
    width = len(smtm_matrix[0])
    
    print(f"   Image size: {width}x{height}")
    
    all_frames = []
    
    # 1. Black frame (1 second)
    black_frame = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
    for _ in range(fps):
        all_frames.append(black_frame)
    
    # 2. SMTM.png display (duration seconds)
    hold_frames = int(duration * fps)
    for _ in range(hold_frames):
        all_frames.append(smtm_matrix)
    print(f"   SMTM display: {hold_frames} frames")
    
    # 3. SMTM scattering disappear (0.5 seconds)
    disappear_frames = create_scattering_transition(smtm_matrix, 0.5, fps, appear=False)
    all_frames.extend(disappear_frames)
    print(f"   SMTM disappear: {len(disappear_frames)} frames")
    
    # 4. Left-to-right wipe to 12.png (0.5 seconds)
    wipe_frames = create_left_to_right_wipe(black_frame, twelve_matrix, 0.5, fps)
    all_frames.extend(wipe_frames)
    print(f"   Wipe to 12: {len(wipe_frames)} frames")
    
    # 5. Fire rises from bottom to middle (1.0 second)
    fire_rise_frames = create_fire_rise_from_bottom(width, height, 1.0, fps, flicker_zone_height=8)
    # Overlay 12.png on rising fire
    twelve_with_fire_rise = overlay_image_on_fire(twelve_matrix, fire_rise_frames)
    all_frames.extend(twelve_with_fire_rise)
    print(f"   Fire rising: {len(twelve_with_fire_rise)} frames")
    
    # 6. Hold 12.png with flickering fire background (duration seconds)
    fire_flicker_frames = create_fire_flickering(width, height, duration, fps, flicker_zone_height=8)
    twelve_with_fire_flicker = overlay_image_on_fire(twelve_matrix, fire_flicker_frames)
    all_frames.extend(twelve_with_fire_flicker)
    print(f"   12 with flickering fire: {len(twelve_with_fire_flicker)} frames")
    
    # 7. Black frame (1 second)
    for _ in range(fps):
        all_frames.append(black_frame)
    
    print(f"   Total frames: {len(all_frames)} ({len(all_frames)/fps:.1f}s)")
    
    # Save
    bin_maker_with_tiles(all_frames, output_path, fps)


def mode2_smtm12_bottom_up(duration: float, fps: int, output_path: str):
    """
    Mode 2: SMTM12.png multi-stage appearance:
    1. White text appears with scattering
    2. Yellow background fills with scattering
    3. Fire rises from bottom (orange background)
    4. Flickering fire effect with dimmer pixels blinking
    
    Args:
        duration: Duration to hold SMTM12.png with fire in seconds
        fps: Frames per second
        output_path: Output file base path
    """
    print("\n🎬 Mode 2: SMTM12 (White Text → Yellow BG → Fire Effect)")
    print(f"   Duration: {duration}s")
    print(f"   FPS: {fps}")
    
    # Load image
    smtm12_path = "./data/smtm12/SMTM12.png"
    
    if not os.path.exists(smtm12_path):
        raise FileNotFoundError("Required image not found in ./data/smtm12/")
    
    smtm12_img = Image.open(smtm12_path).convert("RGB")
    smtm12_matrix = image_to_matrix(smtm12_img)
    
    height = len(smtm12_matrix)
    width = len(smtm12_matrix[0])
    
    print(f"   Image size: {width}x{height}")
    
    all_frames = []
    black_frame = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
    
    # 1. Black frame (1 second)
    for _ in range(fps):
        all_frames.append(black_frame)
    
    # 2. White text appears with scattering (0.5 seconds)
    text_appear = create_scattering_transition(smtm12_matrix, 0.5, fps, appear=True)
    all_frames.extend(text_appear)
    print(f"   White text scattering appear: {len(text_appear)} frames (0.5s)")
    
    # 3. Yellow background fills with scattering (0.5 seconds)
    yellow_bg_color = (180, 180, 0)
    yellow_bg_fill = create_background_scattering(smtm12_matrix, yellow_bg_color, 0.5, fps)
    all_frames.extend(yellow_bg_fill)
    print(f"   Yellow background scattering: {len(yellow_bg_fill)} frames (0.5s)")
    
    # 4. Hold with yellow background (0.5 seconds)
    smtm12_yellow_bg = add_solid_background(smtm12_matrix, yellow_bg_color)
    yellow_hold_frames = int(0.5 * fps)
    for _ in range(yellow_hold_frames):
        all_frames.append(smtm12_yellow_bg)
    print(f"   Yellow bg hold: {yellow_hold_frames} frames (0.5s)")
    
    # 5. Fire rises from bottom to middle on yellow background (1.0 second)
    fire_rise_frames = create_fire_rise_from_bottom(width, height, 1.0, fps, flicker_zone_height=8)
    # Overlay fire on yellow background, keeping yellow where fire is off
    smtm12_with_fire_rise = overlay_fire_on_yellow_background(smtm12_matrix, yellow_bg_color, fire_rise_frames)
    all_frames.extend(smtm12_with_fire_rise)
    print(f"   Fire rising (yellow bg): {len(smtm12_with_fire_rise)} frames (1.0s)")
    
    # 6. Hold SMTM12 with flickering fire on yellow background (duration seconds)
    fire_flicker_frames = create_fire_flickering(width, height, duration, fps, flicker_zone_height=8)
    # Fire flickers on yellow background - yellow shows where fire is off
    smtm12_with_fire_flicker = overlay_fire_on_yellow_background(smtm12_matrix, yellow_bg_color, fire_flicker_frames)
    all_frames.extend(smtm12_with_fire_flicker)
    print(f"   SMTM12 with flickering fire (yellow bg): {len(smtm12_with_fire_flicker)} frames ({duration}s)")
    
    # 7. Black frame (1 second)
    for _ in range(fps):
        all_frames.append(black_frame)
    
    print(f"   Total frames: {len(all_frames)} ({len(all_frames)/fps:.1f}s)")
    
    # Save
    bin_maker_with_tiles(all_frames, output_path, fps)


def mode3_letters_sequence(duration: float, fps: int, output_path: str):
    """
    Mode 3: S→M→T→M (scattering) → black (1s) → 12 (bottom-up)
    
    Args:
        duration: Duration for 12.png hold in seconds (letters are 0.5s each)
        fps: Frames per second
        output_path: Output file base path
    """
    print("\n🎬 Mode 3: S→M→T→M→12 (Letter Sequence)")
    print(f"   Letter duration: 0.5s each")
    print(f"   12 duration: {duration}s")
    print(f"   FPS: {fps}")
    
    # Load images
    s_path = "./data/s+m+t+m+12/S.png"
    m_path = "./data/s+m+t+m+12/M.png"
    t_path = "./data/s+m+t+m+12/T.png"
    twelve_path = "./data/s+m+t+m+12/12.png"
    
    if not all(os.path.exists(p) for p in [s_path, m_path, t_path, twelve_path]):
        raise FileNotFoundError("Required images not found in ./data/s+m+t+m+12/")
    
    s_img = Image.open(s_path).convert("RGB")
    m_img = Image.open(m_path).convert("RGB")
    t_img = Image.open(t_path).convert("RGB")
    twelve_img = Image.open(twelve_path).convert("RGB")
    
    s_matrix = image_to_matrix(s_img)
    m_matrix = image_to_matrix(m_img)
    t_matrix = image_to_matrix(t_img)
    twelve_matrix = image_to_matrix(twelve_img)
    
    height = len(s_matrix)
    width = len(s_matrix[0])
    
    print(f"   Image size: {width}x{height}")
    
    all_frames = []
    black_frame = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
    
    # 1. Black frame (1 second)
    for _ in range(fps):
        all_frames.append(black_frame)
    
    # 2. S.png - center expand scattering (0.2s appear)
    s_appear = create_center_expand_scattering(s_matrix, 0.2, fps)
    all_frames.extend(s_appear)
    print(f"   S appear (center expand): {len(s_appear)} frames")
    
    # Hold S (0.5s total - 0.2s = 0.3s)
    s_hold = int(0.3 * fps)
    for _ in range(s_hold):
        all_frames.append(s_matrix)
    
    # S disappear (0.2s)
    s_disappear = create_scattering_transition(s_matrix, 0.2, fps, appear=False)
    all_frames.extend(s_disappear)
    print(f"   S total: {len(s_appear) + s_hold + len(s_disappear)} frames (0.7s)")
    
    # 3. M.png - normal scattering (0.2s appear)
    m_appear = create_scattering_transition(m_matrix, 0.2, fps, appear=True)
    all_frames.extend(m_appear)
    print(f"   M appear: {len(m_appear)} frames")
    
    # Hold M (0.3s)
    for _ in range(s_hold):
        all_frames.append(m_matrix)
    
    # M disappear (0.2s)
    m_disappear = create_scattering_transition(m_matrix, 0.2, fps, appear=False)
    all_frames.extend(m_disappear)
    print(f"   M total: {len(m_appear) + s_hold + len(m_disappear)} frames (0.7s)")
    
    # 4. T.png - normal scattering (0.2s appear)
    t_appear = create_scattering_transition(t_matrix, 0.2, fps, appear=True)
    all_frames.extend(t_appear)
    print(f"   T appear: {len(t_appear)} frames")
    
    # Hold T (0.3s)
    for _ in range(s_hold):
        all_frames.append(t_matrix)
    
    # T disappear (0.2s)
    t_disappear = create_scattering_transition(t_matrix, 0.2, fps, appear=False)
    all_frames.extend(t_disappear)
    print(f"   T total: {len(t_appear) + s_hold + len(t_disappear)} frames (0.7s)")
    
    # 5. M.png again - normal scattering (0.2s appear)
    m2_appear = create_scattering_transition(m_matrix, 0.2, fps, appear=True)
    all_frames.extend(m2_appear)
    
    # Hold M (0.3s)
    for _ in range(s_hold):
        all_frames.append(m_matrix)
    
    # M disappear (0.2s)
    m2_disappear = create_scattering_transition(m_matrix, 0.2, fps, appear=False)
    all_frames.extend(m2_disappear)
    print(f"   M(2nd) total: {len(m2_appear) + s_hold + len(m2_disappear)} frames (0.7s)")
    
    # 6. Black frame (1 second)
    for _ in range(fps):
        all_frames.append(black_frame)
    print(f"   Black pause: {fps} frames (1.0s)")
    
    # 7. 12.png - bottom-to-top scattering with yellow background (0.5s appear)
    yellow_bg_color = (180, 180, 0)
    twelve_yellow_bg = add_solid_background(twelve_matrix, yellow_bg_color)
    
    twelve_appear = create_bottom_to_top_scattering(twelve_yellow_bg, 0.5, fps, appear=True)
    all_frames.extend(twelve_appear)
    print(f"   12 appear (bottom-up, yellow bg): {len(twelve_appear)} frames")
    
    # Hold 12 with yellow background (0.2 seconds) - quick transition
    yellow_hold_frames = int(0.2 * fps)
    for _ in range(yellow_hold_frames):
        all_frames.append(twelve_yellow_bg)
    print(f"   12 yellow bg hold: {yellow_hold_frames} frames (0.2s)")
    
    # Fire rises from bottom on yellow background (1.0 second)
    fire_rise_frames = create_fire_rise_from_bottom(width, height, 1.0, fps, flicker_zone_height=8)
    twelve_with_fire_rise = overlay_fire_on_yellow_background(twelve_matrix, yellow_bg_color, fire_rise_frames)
    all_frames.extend(twelve_with_fire_rise)
    print(f"   Fire rising (yellow bg): {len(twelve_with_fire_rise)} frames (1.0s)")
    
    # Hold 12 with flickering fire on yellow background (longer duration)
    fire_hold_duration = max(2.0, duration)  # Minimum 2 seconds, or specified duration
    fire_flicker_frames = create_fire_flickering(width, height, fire_hold_duration, fps, flicker_zone_height=8)
    twelve_with_fire_flicker = overlay_fire_on_yellow_background(twelve_matrix, yellow_bg_color, fire_flicker_frames)
    all_frames.extend(twelve_with_fire_flicker)
    print(f"   12 with flickering fire (yellow bg): {len(twelve_with_fire_flicker)} frames ({fire_hold_duration}s)")
    
    # 8. Black frame (1 second)
    for _ in range(fps):
        all_frames.append(black_frame)
    
    print(f"   Total frames: {len(all_frames)} ({len(all_frames)/fps:.1f}s)")
    
    # Save
    bin_maker_with_tiles(all_frames, output_path, fps)


def main():
    parser = argparse.ArgumentParser(
        description="SMTM Temporary Generation - Create special binary sequences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Mode 1: SMTM → 12 wipe
    python smtm_temp_generation.py --mode 1 --duration 5 --fps 30 --output ./output/smtm_mode1
    
    # Mode 2: SMTM12 bottom-up
    python smtm_temp_generation.py --mode 2 --duration 10 --fps 30 --output ./output/smtm_mode2
    
    # Mode 3: Letter sequence
    python smtm_temp_generation.py --mode 3 --duration 8 --fps 30 --output ./output/smtm_mode3

Modes:
    1: SMTM.png (hold) → scattering disappear → left-to-right wipe to 12.png
    2: SMTM12.png appears from bottom-to-top with scattering
    3: S→M→T→M (each scattering 0.5s, S expands from center) → black 1s → 12 bottom-up
        """
    )
    
    parser.add_argument(
        '--mode',
        type=int,
        required=True,
        choices=[1, 2, 3],
        help='Mode number (1, 2, or 3)'
    )
    
    parser.add_argument(
        '--duration',
        type=float,
        required=True,
        help='Duration to hold main image(s) in seconds'
    )
    
    parser.add_argument(
        '--fps',
        type=int,
        default=30,
        help='Frames per second (default: 30)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output file base path (without extension)'
    )
    
    args = parser.parse_args()
    
    print("🎥 SMTM Temporary Generation")
    print("=" * 50)
    
    try:
        if args.mode == 1:
            mode1_smtm_to_12(args.duration, args.fps, args.output)
        elif args.mode == 2:
            mode2_smtm12_bottom_up(args.duration, args.fps, args.output)
        elif args.mode == 3:
            mode3_letters_sequence(args.duration, args.fps, args.output)
        
        print(f"\n🎉 Generation completed successfully!")
        print(f"📁 Output files at: {args.output}")
        
        # List generated files
        import glob
        bin_files = glob.glob(f"{args.output}*.bin")
        for bin_file in sorted(bin_files):
            bin_size = os.path.getsize(bin_file)
            print(f"   ✓ {os.path.basename(bin_file)} ({bin_size:,} bytes)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
