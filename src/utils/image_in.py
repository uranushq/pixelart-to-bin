from PIL import Image

def image_read(path) -> Image.Image:
    img = Image.open(path)
    return img

if __name__ == "__main__":
    img = image_read(r"C:\Users\URANUS\Desktop\baejeongwon\pixeltobin\pixelart-to-bin\data\watermelon\수박_15.png")
    img.show()