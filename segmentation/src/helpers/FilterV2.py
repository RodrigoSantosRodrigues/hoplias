# -*- coding: utf-8 -*-
'''
	Segmentation of fish chromosomes in images in a metaphase state - morphological operations.
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com

	REFERENCES:
	-----------
			
'''
from skimage import color
from skimage import  img_as_uint
import numpy as np

class FilterV2:
  def __init__(self, image):
    self.image = image

  def morphological_filtration(self):
    """
    This function performs a morphological
    filtering, using a medium low pass filter 
    with a 3x3  mask using the scipy ndimage library and skimage.

    params:
      image : 
        type: RBG

    return:
      image:
        type: rgb2gray
    """
    im = self.image
    if self.image.shape[-1] == 4:
      im = self.image[:, :, :3]

    im = color.rgb2gray(im)
    im = img_as_uint(im, force_copy=False)
    return im
