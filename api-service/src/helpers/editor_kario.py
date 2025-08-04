import logging
from .data import ModelSegmentation

class EditorKario:
  def __init__(self):
    self.__data_sample = ModelSegmentation().data
    self.__obj_chrom = self.__data_sample['objects'][1].copy()
    self.contour = ""
    self.coord_sum= []

  def get_items_base(self):
    return {
      'objects': [],
      "animations": [],
      "styles": [],
      "dataSources": []
    }
  
  def get_response_first_step(self, image_base64, data, chromosomes):
    """
    This function extracts the contour 
    of segmented objects, binary image, 
    black background, white object.

    params:
      image: 
        type: binary

    return:
      dict:
        type: json
        format: hoplias editor
    """
    items = self.get_items_base()

    id=0
    for chrom in chromosomes:
      payload = self.__obj_chrom

      coords= []
      for i in range(0, len(chrom.get('contour'))):
        x = chrom['contour'][i].get('x')
        y = chrom['contour'][i].get('y')
        coords.append({"x": x, "y": y})

      payload['id'] = chrom.get('id_chromosome')
      payload['name'] = chrom.get('name') if not chrom.get('manual') else 'New polygon'
      payload['manual'] = chrom.get('manual')
      payload['points'] = coords
      payload['top'] = chrom.get('top_contour')
      payload['left'] = chrom.get('left_contour')

      items['objects'].append(payload.copy())
      id= id+1

    image = next((obj for obj in self.__data_sample['objects'] if obj["type"] == "image"), None)
    image['src'] = image_base64
    image['top'] = data.get('top')
    image['left'] = data.get('left')
    image['width'] = data.get('height')
    image['height'] = data.get('width')
    items['objects'].append(image) 
    return items
  
  def get_data_centromeres_second_step(self, chrom, image_base64_rgb=None, image_base64_gray=None):
    obj = self.__obj_chrom
    coords= []
    for i in range(0, len(chrom.get('contour'))):
      x = chrom['contour'][i].get('x')
      y = chrom['contour'][i].get('y')
      coords.append({"x": x, "y": y})
      
    obj['id'] = chrom.get('id_chromosome')
    obj['name'] = chrom.get('name') if not chrom.get('manual') else 'New polygon'
    obj['points'] = coords
    obj['top'] = chrom.get('top_contour')
    obj['left'] = chrom.get('left_contour')
    obj['dimension'] = chrom.get('dimension')
    obj['empty'] = chrom.get('empty')
    obj['chromosomes_class'] = chrom.get('chromosomes_class')
    obj['checked'] = chrom.get('checked')
    obj['size_chromosome'] = chrom.get('size_chrom')
    obj['centromere'] = chrom.get('centromere_coord')
    obj['centromere_chromosome'] = chrom.get('centromere_start')
    obj['upper_chromatide'] = chrom.get('upper_chromatide_size')
    obj['lower_chromatide'] = chrom.get('lower_chromatide_size')
    obj['base64_rgb'] = image_base64_rgb
    obj['base64_gray'] = image_base64_gray
    obj['manual'] = chrom.get('manual')
    obj['angle'] = chrom.get('rotation').get('angle') if chrom.get('rotation') else 0
    obj['rotation'] = chrom.get('rotation')
    return obj

  def get_data_image_second_step(self, image_base64, data):
    image = next((obj for obj in self.__data_sample['objects'] if obj["type"] == "image"), None)
    image['src'] = image_base64
    image['top'] = data.get('top')
    image['left'] = data.get('left')
    image['width'] = data.get('width')
    image['height'] = data.get('height')
    return image

  def load_contour(self, data):
    def format_object(item):
      return [item['x'], item['y']]

    def format_new_object(item):
      return [item['x'] + self.coord_sum[0], item['y'] + self.coord_sum[1]]

    def format_list(item):
      if item.get('type') == "polygon":
        if len(item.get('points')) > 0:
          if item.get('name') == "New polygon":
            return list(map(format_new_object, item.get('points')))
          else:
            return list(map(format_object, item.get('points')))

    def format_coord(item):
      left=0
      top=0
      if item.get('type') == "image":
        left= item.get('left')
        if left < 0:
          left= left * -1
        top= item.get('top')
        if top < 0:
          top= top * -1
      return [left, top]

    coord= list(map(format_coord, data)) #objects
    self.coord_sum= coord[0]
    
    contours = list(map(format_list, data)) #objects
    self.contour = contours
