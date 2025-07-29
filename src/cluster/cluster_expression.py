from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
import sys
import os
import json
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to the config.json file
        
    Returns:
        Dictionary containing configuration data
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_set_coordinates(set_index: int, image_width: int, image_height: int, grid_size: int = 4) -> Tuple[int, int, int, int]:
    """
    Calculate the pixel coordinates for a given set index.
    
    Args:
        set_index: Index of the set (0-based)
        image_width: Width of the image
        image_height: Height of the image
        grid_size: Size of each grid cell (4x4 pixels)
        
    Returns:
        Tuple of (x1, y1, x2, y2) coordinates
    """
    sets_per_row = image_width // grid_size
    sets_per_col = image_height // grid_size
    
    row = set_index // sets_per_row
    col = set_index % sets_per_row
    
    x1 = col * grid_size
    y1 = row * grid_size
    x2 = x1 + grid_size
    y2 = y1 + grid_size
    
    return x1, y1, x2, y2


def get_cluster_bounding_box(cluster_sets: List[int], image_width: int, image_height: int, grid_size: int = 4) -> Tuple[int, int, int, int]:
    """
    Calculate the bounding box that encompasses all sets in a cluster.
    
    Args:
        cluster_sets: List of set indices in the cluster
        image_width: Width of the image
        image_height: Height of the image
        grid_size: Size of each grid cell
        
    Returns:
        Tuple of (x1, y1, x2, y2) coordinates for the bounding box
    """
    if not cluster_sets:
        return 0, 0, 0, 0
    
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = -1, -1
    
    for set_idx in cluster_sets:
        x1, y1, x2, y2 = calculate_set_coordinates(set_idx, image_width, image_height, grid_size)
        min_x = min(min_x, x1)
        min_y = min(min_y, y1)
        max_x = max(max_x, x2)
        max_y = max(max_y, y2)
    
    return int(min_x), int(min_y), int(max_x), int(max_y)


def create_cluster_visualization(image_path: str, config_path: str, output_path: str, scale_factor: int = 50):
    """
    Create a visualization of clusters on the representative image.
    
    Args:
        image_path: Path to the representative image (e.g., XXX_1.png)
        config_path: Path to the config.json file
        output_path: Path to save the visualization
        scale_factor: Factor to scale up the image for better visibility
    """
    # Load configuration
    config = load_config(config_path)
    cluster_config = config['cluster']
    
    # Load and scale up the image
    original_img = Image.open(image_path).convert("RGB")
    width, height = original_img.size
    
    # Scale up for better visibility
    scaled_img = original_img.resize((width * scale_factor, height * scale_factor), Image.NEAREST)
    scaled_width, scaled_height = scaled_img.size
    
    # Create drawing context
    draw = ImageDraw.Draw(scaled_img)
    
    # Define colors for each cluster
    cluster_colors = [
        '#FF0000',  # Red
        '#00FF00',  # Green
        '#0000FF',  # Blue
        '#FFFF00',  # Yellow
        '#FF00FF',  # Magenta
        '#00FFFF',  # Cyan
        '#FFA500',  # Orange
        '#800080',  # Purple
        '#FFC0CB',  # Pink
        '#A52A2A',  # Brown
    ]
    
    # Grid size (scaled)
    grid_size = 4 * scale_factor
    
    print(f"Image size: {width}x{height} pixels")
    print(f"Scaled size: {scaled_width}x{scaled_height} pixels")
    print(f"Grid size: {grid_size} pixels")
    
    # Draw grid lines for reference
    for x in range(0, scaled_width + 1, grid_size):
        draw.line([(x, 0), (x, scaled_height)], fill='black', width=1)
    for y in range(0, scaled_height + 1, grid_size):
        draw.line([(0, y), (scaled_width, y)], fill='black', width=1)
    
    # Draw cluster bounding boxes and labels
    for cluster_id in sorted(cluster_config.keys()):
        if cluster_id in ['loop', 'loopDelay']:
            continue
        
        cluster_sets = cluster_config[cluster_id]
        color_idx = int(cluster_id) % len(cluster_colors)
        color = cluster_colors[color_idx]
        
        print(f"Cluster {cluster_id}: sets {cluster_sets}, color: {color}")
        
        # Get bounding box for this cluster (scaled)
        x1, y1, x2, y2 = get_cluster_bounding_box(cluster_sets, width, height, 4)
        x1_scaled = x1 * scale_factor
        y1_scaled = y1 * scale_factor
        x2_scaled = x2 * scale_factor
        y2_scaled = y2 * scale_factor
        
        # Draw bounding rectangle
        draw.rectangle([x1_scaled, y1_scaled, x2_scaled, y2_scaled], 
                      outline=color, width=3)
        
        # Draw cluster label
        label_x = x1_scaled + 5
        label_y = y1_scaled + 5
        
        try:
            # Try to use a font (might not be available on all systems)
            font = ImageFont.truetype("arial.ttf", size=max(12, grid_size // 4))
        except:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Draw label background
        label_text = f"C{cluster_id}"
        bbox = draw.textbbox((label_x, label_y), label_text, font=font)
        draw.rectangle(bbox, fill='white', outline='black')
        draw.text((label_x, label_y), label_text, fill='black', font=font)
        
        # Draw set indices within each cluster
        for set_idx in cluster_sets:
            set_x1, set_y1, set_x2, set_y2 = calculate_set_coordinates(set_idx, width, height, 4)
            set_x1_scaled = set_x1 * scale_factor
            set_y1_scaled = set_y1 * scale_factor
            set_x2_scaled = set_x2 * scale_factor
            set_y2_scaled = set_y2 * scale_factor
            
            # Draw set border
            draw.rectangle([set_x1_scaled, set_y1_scaled, set_x2_scaled, set_y2_scaled], 
                          outline=color, width=2)
            
            # Draw set index
            center_x = (set_x1_scaled + set_x2_scaled) // 2
            center_y = (set_y1_scaled + set_y2_scaled) // 2
            
            set_text = str(set_idx)
            text_bbox = draw.textbbox((center_x, center_y), set_text, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            
            # Center the text
            text_x = center_x - text_w // 2
            text_y = center_y - text_h // 2
            
            # Draw text background
            draw.rectangle([text_x - 2, text_y - 2, text_x + text_w + 2, text_y + text_h + 2], 
                          fill='white', outline='black')
            draw.text((text_x, text_y), set_text, fill='red', font=font)
    
    # Save the visualization
    scaled_img.save(output_path)
    print(f"Cluster visualization saved to: {output_path}")


def create_cluster_visualization_from_directory(directory: str, scale_factor: int = 50, output_dir: str = None):
    """
    Create a visualization of clusters from a directory containing images and config.json.
    
    Args:
        directory: Directory containing images and config.json
        scale_factor: Factor to scale up the image for better visibility
        output_dir: Directory to save the output file (default: same as input directory)
        
    Returns:
        Path to the generated visualization file
    """
    # Find representative image (first image in sorted order or specifically named)
    import glob
    
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
    image_files = sorted(image_files)
    
    if not image_files:
        raise FileNotFoundError(f"No image files found in {directory}")
    
    # Look for specifically named file (ending with _1) or use first image
    representative_image = None
    for img_file in image_files:
        filename = os.path.basename(img_file)
        if '_1.' in filename:
            representative_image = img_file
            break
    
    if not representative_image:
        representative_image = image_files[0]
    
    config_file = os.path.join(directory, "config.json")
    
    # Generate output filename based on directory name
    dir_name = os.path.basename(os.path.normpath(directory))
    output_filename = f"{dir_name}_cluster_visualization.png"
    
    # Use specified output directory or input directory
    if output_dir is None:
        output_dir = directory
    
    output_file = os.path.join(output_dir, output_filename)
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"config.json not found in {directory}")
    
    create_cluster_visualization(representative_image, config_file, output_file, scale_factor)
    return output_file
    """
    Create a visualization of clusters on the representative image.
    
    Args:
        image_path: Path to the representative image (e.g., XXX_1.png)
        config_path: Path to the config.json file
        output_path: Path to save the visualization
        scale_factor: Factor to scale up the image for better visibility
    """
    # Load configuration
    config = load_config(config_path)
    cluster_config = config['cluster']
    
    # Load and scale up the image
    original_img = Image.open(image_path).convert("RGB")
    width, height = original_img.size
    
    # Scale up for better visibility
    scaled_img = original_img.resize((width * scale_factor, height * scale_factor), Image.NEAREST)
    scaled_width, scaled_height = scaled_img.size
    
    # Create drawing context
    draw = ImageDraw.Draw(scaled_img)
    
    # Define colors for each cluster
    cluster_colors = [
        '#FF0000',  # Red
        '#00FF00',  # Green
        '#0000FF',  # Blue
        '#FFFF00',  # Yellow
        '#FF00FF',  # Magenta
        '#00FFFF',  # Cyan
        '#FFA500',  # Orange
        '#800080',  # Purple
        '#FFC0CB',  # Pink
        '#A52A2A',  # Brown
    ]
    
    # Grid size (scaled)
    grid_size = 4 * scale_factor
    
    print(f"Image size: {width}x{height} pixels")
    print(f"Scaled size: {scaled_width}x{scaled_height} pixels")
    print(f"Grid size: {grid_size} pixels")
    
    # Draw grid lines for reference
    for x in range(0, scaled_width + 1, grid_size):
        draw.line([(x, 0), (x, scaled_height)], fill='black', width=1)
    for y in range(0, scaled_height + 1, grid_size):
        draw.line([(0, y), (scaled_width, y)], fill='black', width=1)
    
    # Draw cluster bounding boxes and labels
    for cluster_id in sorted(cluster_config.keys()):
        if cluster_id in ['loop', 'loopDelay']:
            continue
        
        cluster_sets = cluster_config[cluster_id]
        color_idx = int(cluster_id) % len(cluster_colors)
        color = cluster_colors[color_idx]
        
        print(f"Cluster {cluster_id}: sets {cluster_sets}, color: {color}")
        
        # Get bounding box for this cluster (scaled)
        x1, y1, x2, y2 = get_cluster_bounding_box(cluster_sets, width, height, 4)
        x1_scaled = x1 * scale_factor
        y1_scaled = y1 * scale_factor
        x2_scaled = x2 * scale_factor
        y2_scaled = y2 * scale_factor
        
        # Draw bounding rectangle
        draw.rectangle([x1_scaled, y1_scaled, x2_scaled, y2_scaled], 
                      outline=color, width=3)
        
        # Draw cluster label
        label_x = x1_scaled + 5
        label_y = y1_scaled + 5
        
        try:
            # Try to use a font (might not be available on all systems)
            font = ImageFont.truetype("arial.ttf", size=max(12, grid_size // 4))
        except:
            # Fall back to default font
            font = ImageFont.load_default()
        
        # Draw label background
        label_text = f"C{cluster_id}"
        bbox = draw.textbbox((label_x, label_y), label_text, font=font)
        draw.rectangle(bbox, fill='white', outline='black')
        draw.text((label_x, label_y), label_text, fill='black', font=font)
        
        # Draw set indices within each cluster
        for set_idx in cluster_sets:
            set_x1, set_y1, set_x2, set_y2 = calculate_set_coordinates(set_idx, width, height, 4)
            set_x1_scaled = set_x1 * scale_factor
            set_y1_scaled = set_y1 * scale_factor
            set_x2_scaled = set_x2 * scale_factor
            set_y2_scaled = set_y2 * scale_factor
            
            # Draw set border
            draw.rectangle([set_x1_scaled, set_y1_scaled, set_x2_scaled, set_y2_scaled], 
                          outline=color, width=2)
            
            # Draw set index
            center_x = (set_x1_scaled + set_x2_scaled) // 2
            center_y = (set_y1_scaled + set_y2_scaled) // 2
            
            set_text = str(set_idx)
            text_bbox = draw.textbbox((center_x, center_y), set_text, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            
            # Center the text
            text_x = center_x - text_w // 2
            text_y = center_y - text_h // 2
            
            # Draw text background
            draw.rectangle([text_x - 2, text_y - 2, text_x + text_w + 2, text_y + text_h + 2], 
                          fill='white', outline='black')
            draw.text((text_x, text_y), set_text, fill='red', font=font)
    
    # Save the visualization
    scaled_img.save(output_path)
    print(f"Cluster visualization saved to: {output_path}")


def analyze_image_grid(image_path: str, grid_size: int = 4):
    """
    Analyze the image grid structure and print information.
    
    Args:
        image_path: Path to the image
        grid_size: Size of each grid cell
    """
    img = Image.open(image_path)
    width, height = img.size
    
    sets_per_row = width // grid_size
    sets_per_col = height // grid_size
    total_sets = sets_per_row * sets_per_col
    
    print(f"Image Analysis:")
    print(f"  Image size: {width}x{height} pixels")
    print(f"  Grid size: {grid_size}x{grid_size} pixels per set")
    print(f"  Sets per row: {sets_per_row}")
    print(f"  Sets per column: {sets_per_col}")
    print(f"  Total sets: {total_sets}")
    print(f"  Set indices: 0 to {total_sets - 1}")
    print()
    
    # Show set layout
    print("Set layout (reading order):")
    for row in range(sets_per_col):
        row_indices = []
        for col in range(sets_per_row):
            set_index = row * sets_per_row + col
            row_indices.append(f"{set_index:2d}")
        print(f"  Row {row}: {' '.join(row_indices)}")
    print()


if __name__ == "__main__":
    # Configuration
    watermelon_dir = r"./data/watermelon"
    representative_image = os.path.join(watermelon_dir, "수박_1.png")
    config_file = os.path.join(watermelon_dir, "config.json")
    
    # Use directory name for output file
    dir_name = os.path.basename(os.path.normpath(watermelon_dir))
    output_file = f"{dir_name}_cluster_visualization.png"
    
    if not os.path.exists(representative_image):
        print(f"Representative image not found: {representative_image}")
        exit(1)
    
    if not os.path.exists(config_file):
        print(f"Config file not found: {config_file}")
        exit(1)
    
    # Analyze the image grid
    analyze_image_grid(representative_image)
    
    # Create cluster visualization using the new function
    output_file = create_cluster_visualization_from_directory(watermelon_dir, scale_factor=50)
    
    print(f"Visualization complete! Check {output_file}")
