import base64
from io import BytesIO
from PIL import Image

class ConvertToJpg:
  def __init__(self):
    pass

  @staticmethod
  def convert_to_jpg_base64(base64_img):
    if base64_img.startswith("data:image"):
      base64_img = base64_img.split(",")[1]

      image_data = base64.b64decode(base64_img)

      with BytesIO(image_data) as img_io:
        with Image.open(img_io) as img:
          with BytesIO() as jpg_io:
            img.convert("RGB").save(jpg_io, format="JPEG")
            jpg_base64 = base64.b64encode(jpg_io.getvalue()).decode('utf-8')

    return f"data:image/jpg;base64,{jpg_base64}"
