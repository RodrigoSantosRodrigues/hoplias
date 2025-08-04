# -*- coding: utf-8 -*-
'''
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com
	Sistemas de Informação

	REFERENCES:
	-----------

'''
import numpy               as np
from skimage.measure        import label

class Rebuild:
  def __init__(self, image, objects, logger):
    self.binary_image = image
    self.objects = objects
    self.logger = logger

  def rebuild(self):
    """
    This function reconstructs a segmented and classified image.

    params:
      image:
        type: binary or labeled

      objects:
        type: tuple
        format: objects[label, image, class=2]

    return:
      image:
        type: binary
    """
    new_image = np.zeros(self.binary_image.shape, np.uint8)
    image = label(self.binary_image)

    if len(self.objects):
      class2_ids = self.objects[self.objects[:, 2] == 2, 0]
    
      for obj_id in class2_ids:
        new_image[image == obj_id] = 1

    return new_image
