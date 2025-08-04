from matplotlib import pyplot as plt
import numpy as np
import json
import cv2
import base64

from ..helpers.FilterV2 import FilterV2
from ..helpers.MorphologyV2 import MorphologyV2
from ..helpers.ClassifierV2 import ClassifierV2
from ..helpers.Rebuild import Rebuild
from ..helpers.Contour import Contour

class SegmentationController:
  def __init__(self, logger):
    self.image = np.ndarray([])
    self.image_base64 = ""
    self.block_value = 45
    self.hard_process = False
    self.data = None
    self.logger = logger

  def load_image_hoplias(self, data):
    self.data = data
    self.image_base64 = data.get('src')
    image_b64 = self.image_base64.split(",")[1]
    self.logger.info(f"Loading image from base64: {image_b64}")
    binary = base64.b64decode(image_b64)
    image = np.asarray(bytearray(binary), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    self.image = image

  def load_block_value(self, data):
    self.block_value = int(data.get('block_value', 45))

  def load_hard_process(self, data):
    self.hard_process = int(data.get('hard_process', False))

  def segmentation_hoplias(self):
    classifying = ClassifierV2(self.image, None, self.logger)
    predictions_img, predicted_cleaned = classifying.classifier_model(self.block_value, self.hard_process)
    contouring = Contour(self.image_base64, predictions_img, predicted_cleaned, self.data)
    data = contouring.extract_contours()
    data['block_value'] = self.block_value
    return data
