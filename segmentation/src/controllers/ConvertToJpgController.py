from matplotlib import pyplot as plt
import numpy as np
import json
import base64
from io import BytesIO
from imageio import imread

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
    # Decode image using imageio
    image = imread(BytesIO(binary))
    # imageio returns RGB, but we need BGR for compatibility (or keep RGB if other parts handle it)
    # For now, keep RGB as skimage uses RGB
    self.image = image

  def convert_to_jpg(self):
    converting = ConvertToJpg()
    converted = converting.convert_to_jpg_base64(self.image_base64)
    return {
      'src': converted
    }
