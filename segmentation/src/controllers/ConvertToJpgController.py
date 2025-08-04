from matplotlib import pyplot as plt
import numpy as np
import json
import cv2
import base64

from ..helpers.ConvertToJpg import ConvertToJpg

class ConvertToJpgController:
  def __init__(self):
    self.image = np.ndarray([])
    self.image_base64 = ""

  def load_image(self, data):
    json_load = json.loads(data)
    image = np.asarray(json_load["image"])
    self.image = image

  def load_image_hoplias(self, data):
    self.image_base64 = data.get('src')
    image_b64 = self.image_base64.split(",")[1]
    binary = base64.b64decode(image_b64)
    image = np.asarray(bytearray(binary), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    self.image = image

  def convert_to_jpg(self):
    converting = ConvertToJpg()
    converted = converting.convert_to_jpg_base64(self.image_base64)
    return {
      'src': converted
    }
