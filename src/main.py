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
        Tuple of (bin_file_path, visualization_file_path)
    """
    dir_name = os.path.basename(os.path.normpath(directory))
    
    bin_file = os.path.join(directory, f"{dir_name}_sequence.bin")
    viz_file = os.path.join(directory, f"{dir_name}_cluster_visualization.png")
    
    return bin_file, viz_file


def create_binary_sequence(directory: str, output_path: str):
    """
    Create binary sequence file from directory.
    
    Args:
        directory: Input directory containing images and config.json
        output_path: Output path for the binary file
    """
    print(f"\n🔄 Creating binary sequence...")
    print(f"   Input: {directory}")
    print(f"   Output: {output_path}")
    
    try:
        create_sequence_from_config(directory, output_path)
        print(f"✓ Binary sequence created successfully")
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
    python ./src/main.py ./data/watermelon
    python ./src/main.py ./data/another_dataset

The script will generate:
    - {directory_name}_sequence.bin
    - {directory_name}_cluster_visualization.png

Both files will be saved in the input directory.
        """
    )
    
    parser.add_argument(
        'directory',
        help='Path to directory containing images and config.json'
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
        # Validate input directory
        validated_dir = validate_directory(args.directory)
        
        # Generate output paths
        bin_output, viz_output = generate_output_paths(validated_dir)
        
        print(f"\n📁 Processing directory: {os.path.basename(validated_dir)}")
        print(f"📄 Will create:")
        print(f"   • {os.path.basename(bin_output)}")
        print(f"   • {os.path.basename(viz_output)}")
        
        # Create binary sequence
        create_binary_sequence(validated_dir, bin_output)
        
        # Create cluster visualization  
        create_visualization(validated_dir, viz_output)
        
        # Final summary
        print(f"\n🎉 Processing completed successfully!")
        print(f"📁 Output files in: {validated_dir}")
        print(f"   ✓ {os.path.basename(bin_output)}")
        print(f"   ✓ {os.path.basename(viz_output)}")
        
        # File size information
        if os.path.exists(bin_output):
            bin_size = os.path.getsize(bin_output)
            print(f"   📊 Binary file size: {bin_size:,} bytes")
        
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
