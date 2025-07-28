### convert pil image to matrix

from typing import List, Dict, Union, Literal, Any
from PIL import Image

def image_to_matrix(image: Image.Image) -> List[List[List[int]]]:

    """
    Convert a PIL Image to a matrix representation.
    Args:
        image (Image.Image): The input image to convert.
    Returns:
        List[List[List[int]]]: A matrix where each element is a list of RGB values.
    """

    width, height = image.size
    matrix: List[List[List[int]]] = []
    for y in range(height):
        row: List[List[int]] = []
        for x in range(width):
            r, g, b = image.getpixel((x, y))[:3]  # Get RGB values
            row.append([r, g, b])  # Append RGB values as a list
        matrix.append(row)  # Append the row to the matrix
    
    return matrix

if __name__ == "__main__":
    img_path = r"C:\Users\URANUS\Desktop\baejeongwon\pixeltobin\pixelart-to-bin\data\watermelon\수박_1.png"
    img = Image.open(img_path)
    matrix = image_to_matrix(img)
    print(matrix)  # Print the matrix representation of the image
    ## flatten 1 dimension
    matrix = [pixel for row in matrix for pixel in row]  # Flatten the matrix to 1D
    print(len(matrix))  # Print the length of the flattened matrix, Total pixels