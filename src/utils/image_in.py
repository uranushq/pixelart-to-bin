from PIL import Image

def image_read(path) -> Image.Image:
    img = Image.open(path)
    return img

if __name__ == "__main__":
    img = image_read(r"data/watermelon/수박_15.png")
    img.show()