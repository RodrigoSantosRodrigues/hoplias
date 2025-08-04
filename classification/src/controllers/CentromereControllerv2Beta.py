import numpy as np
import json
import cv2
import base64
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

from ..helpers.Filter import Filter
from ..helpers.Mask import Mask
from ..helpers.Extract import Extract
from ..helpers.Resize import Resize
from ..helpers.Rotation import Rotation
from ..helpers.NumpyToPng import NumpyToPng
from ..helpers.ZhangSue import ZhangSue



class NumpyEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return json.JSONEncoder.default(self, obj)

class CentromereControllerv2Beta:
  def __init__(self, logger, data):
    self.logger = logger
    self.image_base64 = ""
    self.data = data
    self.image = None
    self.contour = ""
    self.contour_formated = ""
    self.coord_sum= []
    self.load_image(data)
    self.load_contour(data)
    self.load_contour_formated(data)
    self.__max_workers = 10

  def load_image(self, data):
    images = [obj for obj in data['objects'] if obj.get('type') == 'image']
    self.image_base64 = images[0].get('src')
    image_b64 = self.image_base64.split(",")[1]
    binary = base64.b64decode(image_b64)
    image = np.asarray(bytearray(binary), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    self.image = image

  def load_contour(self, data):
    def format_object(item):
      return [item['x'], item['y']]

    def format_list(item):
      if item.get('type') == "polygon":
        if len(item.get('points')) > 0:
          return list(map(format_object, item.get('points')))

    contours = list(map(format_list, data['objects']))
    self.contour = contours

  def load_contour_formated(self, data):
    def format_object(item):
      return [item['x'], item['y']]

    def format_new_object(item):
      self.logger.info(f"item: {item['x']}, {item['y']}")
      x_in_image = item['x'] - self.coord_sum[0]
      y_in_image = item['y'] - self.coord_sum[1]
      return [x_in_image, y_in_image]

    def format_list(item):
      if item.get('type') == "polygon":
        if len(item.get('points')) > 0:
          if item.get('name') == "New polygon" or item.get('manual') == True:
            return list(map(format_new_object, item.get('points')))
          else:
            return list(map(format_object, item.get('points')))

    def format_coord(item):
      if item.get('type') == "image":
        left = item.get('left', 0)
        # if left < 0:
        #   left = -left
        top = item.get('top', 0)
        # if top < 0:
        #   top = -top

        width = item.get('width', 0)
        self.height = item.get('height', 0)
        return [left, top, width, self.height]
      return None

    self.coord_sum = None
    self.image_size = None

    coord = list(filter(None, map(format_coord, data['objects'])))
    if coord:
        self.coord_sum = coord[0][:2]
        self.image_size = coord[0][2:]
    else:
        self.coord_sum = None
        self.image_size = None

    contours = list(map(format_list, data['objects']))
    self.contour_formated = contours

  def convert_to_serializable(self, obj):
    if isinstance(obj, bytes):
        return obj.decode('utf-8')
    elif isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return str(obj)

  def proccess_contour(self, args):
    image, contour, filtered_image = args
    masking = Mask(filtered_image)
    image_mask = masking.build_mask(contour)
    extracting = Extract(image, image_mask, filtered_image)
    singles, masks = extracting.extract_rgb()
    return singles, masks

  def proccess_chromosome(self, args):
    chroms_stack_rgb, binary, contour, index, logger = args
    rotating_rgb = Rotation(chroms_stack_rgb, binary, logger)
    rotated_image_rgb, rotated_image_rgb_binary = rotating_rgb.rotation_particle()

    rotating_gray = Rotation(chroms_stack_rgb, binary, logger)
    rotated_image_gray, rotated_image_gray_binary = rotating_gray.rotation_particle_gray()

    zhang_sue = ZhangSue(rotated_image_rgb, rotated_image_rgb_binary.copy(), index)
    points = zhang_sue.skel_chromosome()

    converting_rgb = NumpyToPng(rotated_image_rgb, logger)
    image_base64_rgb = converting_rgb.convert()

    converting_gray = NumpyToPng(rotated_image_gray, logger)
    image_base64_gray = converting_gray.convert_gray_image(rotated_image_rgb)

    return {
      'id': index,
      'dimension': {
        'x': rotated_image_rgb.shape[1],
        'y': rotated_image_rgb.shape[0]
      },
      'centromere': {
        'x': int(points[1]),
        'y': int(points[0])
      },
      'contour': contour,
      'base64_rgb': image_base64_rgb,
      'base64_gray': image_base64_gray
    }

  def centromere(self):
    filtering = Filter(self.image)

    filtered_image = filtering.morphological_filtration()
    args_list = [(self.image, contour, filtered_image) for contour in self.contour_formated]

    extracted_images_rgb = []
    extracted_images_binary = []

    with ProcessPoolExecutor(max_workers=self.__max_workers) as executor:
      results = executor.map(self.proccess_contour, args_list)
      for singles, masks in results:
        extracted_images_rgb.extend(singles)
        extracted_images_binary.extend(masks)

    resizing = Resize()
    objects_rgb = resizing.Resize_images(extracted_images_rgb)
    objects_binaries = resizing.Resize_images(extracted_images_binary)
    chromosomes = []
    contour = self.contour

    args_list = [
      (rgb, binary, contour, idx, self.logger)
      for idx, (rgb, binary) in enumerate(zip(objects_rgb, objects_binaries), start=1)
    ]

    with ProcessPoolExecutor(max_workers=self.__max_workers) as executor:
      results = executor.map(self.proccess_chromosome, args_list)
      chromosomes.extend(results)

    return { 
      'image': self.image_base64,
      'objects': chromosomes
    }
