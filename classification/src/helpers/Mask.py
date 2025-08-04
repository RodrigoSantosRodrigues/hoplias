"""
	Segmentation of fish chromosomes in images in a metaphase state - morphological operations.
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com


	REFERENCES:
	-----------
			
"""
import numpy as np
from skimage import morphology
import scipy.ndimage as ndimage  
#import matplotlib.pyplot 	as plt 
from skimage.draw import line_aa
import random
import math

class Mask:
  def __init__(self, image):
    self.image = image

  def build_mask(self, contour):
    """
    This function builds a binary mask from the outline points.

    params:
      image:
        type: rgb2gray

    return:
      image:
        type: binary
    """
    # Create an empty image to store the masked array
    r_mask = np.zeros_like(self.image, dtype=float)
    first_coord= True
    if contour:
      for point in contour:
        #r_mask[np.round(point[1]).astype('int'), np.round(point[0]).astype('int')] = 1
        if not first_coord:
          rr, cc, val = line_aa(math.floor(point[1]), math.floor(point[0]), math.floor(previous_coordinate[1]), math.floor(previous_coordinate[0]))
          r_mask[rr, cc] = 1
        if first_coord:
          first= point
        previous_coordinate= point
        first_coord= False

      rr, cc, val = line_aa(math.floor(previous_coordinate[1]), math.floor(previous_coordinate[0]), math.floor(first[1]), math.floor(first[0]))
      r_mask[rr, cc] = 1
      first_coord= True

    r_mask_= ndimage.binary_closing(r_mask,morphology.disk(2), iterations=4, output=None, origin=0)
    r_mask_ = ndimage.binary_fill_holes(r_mask_)
 
    #plt.imsave('src/tmp/mask.png', r_mask_)
    return r_mask_
