import os
import base64
from PIL import Image

def encode_image(img_path):
  with open(img_path, "rb") as image_file:
    return 'data:image/jpeg;base64,'+base64.b64encode(image_file.read()).decode('utf-8')


def scale_to_width(img, width):
    height = round(img.height * width / img.width)
    return img.resize((width, height))
def scale_to_height(img, height):
    width = round(img.width * height / img.height)
    return img.resize((width, height))

def resize_suit(filename: str, size: int=400):
    img = Image.open(filename)
    if img.height > img.width:
        img = scale_to_height(img, size)
    else:
        img = scale_to_width(img, size)
    img.save(filename)

    return filename

