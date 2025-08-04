# -*- coding: utf-8 -*-
'''
	Segmentation of chromosomes in images in a metaphase state.
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com


	REFERENCES:
	-----------
			
'''
from scipy.ndimage import filters
from skimage import color
import numpy as np

class Filter:
  def __init__(self, image):
    self.image = image

  def morphological_filtration(self) -> np.ndarray:
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
    im= np.uint8(self.image)
    im = color.rgb2gray(im)
    image = filters.median_filter(im,size=3, mode='nearest')
    return image
