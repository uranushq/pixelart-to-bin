#!/usr/bin/env python3
"""
Main script for pixelart-to-bin conversion.

Usage:
    python ./src/main.py <directory>
    
Example:
    python ./src/main.py ./data/watermelon

This script will:
1. Generate a binary sequence file from images and config.json
2. Create a cluster visualization image
Both files will be saved in the input directory with directory name as prefix.
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.generate.make_sequence import create_sequence_from_config
from src.cluster.cluster_expression import create_cluster_visualization_from_directory
from src.utils.color_board import create_solid_color_board, parse_color
from src.utils.psyche_effect import create_full_on_then_psyche
from src.utils.bin_maker import bin_maker_with_tiles


def validate_directory(directory: str) -> str:
    """
    Validate that the directory exists and contains required files.
    
    Args:
        directory: Path to the directory to validate
        
    Returns:
        Absolute path to the validated directory
        
    Raises:
        FileNotFoundError: If directory or required files don't exist
        ValueError: If directory structure is invalid
    """
    abs_dir = os.path.abspath(directory)
    
    if not os.path.exists(abs_dir):
        raise FileNotFoundError(f"Directory not found: {abs_dir}")
    
    if not os.path.isdir(abs_dir):
        raise ValueError(f"Path is not a directory: {abs_dir}")
    
    # Check for config.json
    config_path = os.path.join(abs_dir, 'config.json')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.json not found in {abs_dir}")
    
    # Check for image files
    import glob
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']:
        image_files.extend(glob.glob(os.path.join(abs_dir, ext)))
    
    if not image_files:
        raise FileNotFoundError(f"No image files found in {abs_dir}")
    
    print(f"✓ Directory validated: {abs_dir}")
    print(f"✓ Found config.json")
    print(f"✓ Found {len(image_files)} image file(s)")
    
    return abs_dir


def generate_output_paths(directory: str) -> tuple[str, str]:
    """
    Generate output file paths based on directory name.
    
    Args:
        directory: Input directory path
        
    Returns:
        Tuple of (bin_base_path, visualization_file_path)
    """
    dir_name = os.path.basename(os.path.normpath(directory))
    
    # Return base path without extension for bin files (tiles will be added automatically)
    bin_base = os.path.join(directory, f"{dir_name}_sequence")
    viz_file = os.path.join(directory, f"{dir_name}_cluster_visualization.png")
    
    return bin_base, viz_file


def create_binary_sequence(directory: str, output_base_path: str, scattering: bool = False, duration: float = 5.0, transition: float = 0.5, fps: int = 15):
    """
    Create binary sequence files from directory.
    Creates full board and individual 4x4 tiles.
    
    Args:
        directory: Input directory containing images and config.json
        output_base_path: Base path for output files (without extension)
        scattering: Enable scattering animation mode
        duration: Duration to hold image in scattering mode (seconds)
        transition: Duration of appear/disappear transitions (seconds)
        fps: Frames per second for scattering mode
    """
    print(f"\n🔄 Creating binary sequence...")
    print(f"   Input: {directory}")
    print(f"   Output base: {output_base_path}")
    
    try:
        create_sequence_from_config(
            directory, 
            output_base_path, 
            split_tiles=True,
            scattering_mode=scattering,
            scattering_duration=duration,
            scattering_transition=transition,
            scattering_fps=fps
        )
        print(f"✓ Binary sequences created successfully")
    except Exception as e:
        print(f"✗ Error creating binary sequence: {e}")
        raise


def create_visualization(directory: str, output_path: str):
    """
    Create cluster visualization image from directory.
    
    Args:
        directory: Input directory containing images and config.json
        output_path: Expected output path for the visualization file
    """
    print(f"\n🔄 Creating cluster visualization...")
    print(f"   Input: {directory}")
    print(f"   Output: {output_path}")
    
    try:
        # Create visualization in the target directory
        output_dir = os.path.dirname(output_path)
        created_file = create_cluster_visualization_from_directory(
            directory, 
            scale_factor=50, 
            output_dir=output_dir
        )
        
        print(f"✓ Cluster visualization created successfully")
        return created_file
    except Exception as e:
        print(f"✗ Error creating cluster visualization: {e}")
        raise


def main():
    """
    Main function to process pixelart directory and generate outputs.
    """
    parser = argparse.ArgumentParser(
        description="Convert pixelart directory to binary sequence and visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process directory with images
    python ./src/main.py ./data/watermelon
    
    # Scattering animation mode
    python ./src/main.py ./data/watermelon --scattering
    
    # Create solid color board
    python ./src/main.py --color-board --color red --width 16 --height 16 --duration 10 --fps 30 --output ./output/red_board
    
    # Create psyche effect
    python ./src/main.py --psyche --color blue --width 16 --height 16 --full-on-duration 2 --duration 10 --psyche-speed 1.5 --fps 30 --output ./output/blue_psyche

The script will generate:
    - {directory_name}_sequence.bin
    - {directory_name}_cluster_visualization.png

Both files will be saved in the input directory.
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        help='Path to directory containing images and config.json (not needed for --color-board or --psyche mode)'
    )
    
    parser.add_argument(
        '--scattering',
        action='store_true',
        help='Enable scattering animation mode (uses _1.png file only)'
    )
    
    parser.add_argument(
        '--color-board',
        action='store_true',
        help='Create a solid color board (no directory needed)'
    )
    
    parser.add_argument(
        '--psyche',
        action='store_true',
        help='Create a psyche effect (random tile blinking, no directory needed)'
    )
    
    parser.add_argument(
        '--color',
        type=str,
        default='red',
        help='Color for color board/psyche mode (hex #FF0000, rgb 255,0,0, or name like red, default: red)'
    )
    
    parser.add_argument(
        '--psyche-speed',
        type=float,
        default=1.0,
        help='Psyche effect speed multiplier (higher = faster blinking, default: 1.0)'
    )
    
    parser.add_argument(
        '--psyche-density',
        type=float,
        default=0.5,
        help='Psyche effect density (0.0-1.0, percentage of tiles ON at any time, default: 0.5)'
    )
    
    parser.add_argument(
        '--full-on-duration',
        type=float,
        default=2.0,
        help='Duration for full-on display before psyche effect in seconds (default: 2.0)'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        default=16,
        help='Width of color board in pixels (must be multiple of 4, default: 16)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=16,
        help='Height of color board in pixels (must be multiple of 4, default: 16)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output path for color board mode (without extension)'
    )
    
    parser.add_argument(
        '--duration',
        type=float,
        default=5.0,
        help='Duration in seconds (default: 5.0 for scattering, 10.0 for color board)'
    )
    
    parser.add_argument(
        '--transition',
        type=float,
        default=0.5,
        help='Duration of appear/disappear transitions in seconds (default: 0.5)'
    )
    
    parser.add_argument(
        '--fps',
        type=int,
        default=15,
        help='Frames per second for scattering animation (default: 15)'
    )
    
    parser.add_argument(
        '--scale',
        type=int,
        default=50,
        help='Scale factor for visualization (default: 50)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    print("🚀 Pixelart to Binary Converter")
    print("=" * 50)
    
    try:
        # Psyche effect mode
        if args.psyche:
            if not args.output:
                print("❌ Error: --output is required for psyche mode")
                sys.exit(1)
            
            # Parse color
            try:
                color_rgb = parse_color(args.color)
            except ValueError as e:
                print(f"❌ Error: {e}")
                sys.exit(1)
            
            # Set default duration for psyche if not specified
            psyche_duration = args.duration if args.duration != 5.0 else 10.0
            
            print(f"\n🌀 Creating psyche effect...")
            print(f"   Color: RGB{color_rgb}")
            print(f"   Size: {args.width}x{args.height}")
            print(f"   Psyche duration: {psyche_duration}s")
            print(f"   Speed: {args.psyche_speed}x")
            print(f"   Density: {args.psyche_density:.1%}")
            print(f"   FPS: {args.fps}")
            
            # Create psyche effect (full_on_duration is ignored but kept for API compatibility)
            frames = create_full_on_then_psyche(
                color=color_rgb,
                width=args.width,
                height=args.height,
                full_on_duration=args.full_on_duration,  # ignored
                psyche_duration=psyche_duration,
                fps=args.fps,
                speed=args.psyche_speed,
                density=args.psyche_density
            )
            
            print(f"   Total frames: {len(frames)}")
            print(f"   Total duration: {len(frames) / args.fps:.1f}s")
            
            # Save
            bin_maker_with_tiles(frames, args.output, args.fps)
            
            print(f"\n🎉 Psyche effect created successfully!")
            print(f"📁 Output files at: {args.output}")
            
            # List generated files
            import glob
            bin_files = glob.glob(f"{args.output}*.bin")
            for bin_file in sorted(bin_files):
                bin_size = os.path.getsize(bin_file)
                print(f"   ✓ {os.path.basename(bin_file)} ({bin_size:,} bytes)")
            
            sys.exit(0)
        
        # Color board mode
        if args.color_board:
            if not args.output:
                print("❌ Error: --output is required for color board mode")
                sys.exit(1)
            
            # Parse color
            try:
                color_rgb = parse_color(args.color)
            except ValueError as e:
                print(f"❌ Error: {e}")
                sys.exit(1)
            
            # Set default duration for color board if not specified
            duration = args.duration if args.duration != 5.0 else 10.0
            
            # Create color board
            create_solid_color_board(
                color=color_rgb,
                width=args.width,
                height=args.height,
                duration=duration,
                fps=args.fps,
                output_path=args.output,
                split_tiles=True
            )
            
            print(f"\n🎉 Color board created successfully!")
            print(f"📁 Output files at: {args.output}")
            
            # List generated files
            import glob
            bin_files = glob.glob(f"{args.output}*.bin")
            for bin_file in sorted(bin_files):
                bin_size = os.path.getsize(bin_file)
                print(f"   ✓ {os.path.basename(bin_file)} ({bin_size:,} bytes)")
            
            sys.exit(0)
        
        # Directory mode (existing functionality)
        if not args.directory:
            print("❌ Error: directory argument is required (or use --color-board mode)")
            parser.print_help()
            sys.exit(1)
        
        # Validate input directory
        validated_dir = validate_directory(args.directory)
        
        # Generate output paths
        bin_output, viz_output = generate_output_paths(validated_dir)
        
        print(f"\n📁 Processing directory: {os.path.basename(validated_dir)}")
        
        if args.scattering:
            print("🎆 Scattering animation mode")
            print(f"📄 Will create:")
            print(f"   • {os.path.basename(bin_output)}_full.bin (scattering animation)")
            print(f"   • {os.path.basename(bin_output)}_tile_XX.bin (4x4 tiles)")
        else:
            print(f"📄 Will create:")
            print(f"   • {os.path.basename(bin_output)}_full.bin (full board)")
            print(f"   • {os.path.basename(bin_output)}_tile_XX.bin (4x4 tiles)")
            print(f"   • {os.path.basename(viz_output)}")
        
        # Create binary sequence
        create_binary_sequence(
            validated_dir, 
            bin_output,
            scattering=args.scattering,
            duration=args.duration,
            transition=args.transition,
            fps=args.fps
        )
        
        # Create cluster visualization (skip in scattering mode)
        if not args.scattering:
            create_visualization(validated_dir, viz_output)
        
        # Final summary
        print(f"\n🎉 Processing completed successfully!")
        print(f"📁 Output files in: {validated_dir}")
        
        # List all generated bin files
        import glob
        bin_files = glob.glob(os.path.join(validated_dir, f"{os.path.basename(validated_dir)}_sequence*.bin"))
        for bin_file in sorted(bin_files):
            bin_size = os.path.getsize(bin_file)
            print(f"   ✓ {os.path.basename(bin_file)} ({bin_size:,} bytes)")
        
        # Visualization file
        if not args.scattering:
            print(f"   ✓ {os.path.basename(viz_output)}")
            if os.path.exists(viz_output):
                viz_size = os.path.getsize(viz_output)
                print(f"   🖼️  Visualization size: {viz_size:,} bytes")
            
    except KeyboardInterrupt:
        print(f"\n❌ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
