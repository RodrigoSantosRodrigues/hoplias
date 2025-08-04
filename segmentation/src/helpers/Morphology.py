# -*- coding: utf-8 -*-
'''
	Segmentation of chromosomes in images in a metaphase state - morphological operations.
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com

	REFERENCES:
	-----------
			
'''
import numpy as np
from skimage import morphology
from skimage.filters import threshold_local
from skimage.measure import label
from skimage.segmentation import clear_border
from scipy import ndimage as nd
from matplotlib import pyplot as plt

class Morphology:
	def __init__(self, image, block_value):
		self.image = image
		self.__block_value = block_value

	def get_block_value(self):
		return self.__block_value

	def morphological_operations(self):
		"""
			Morphological segmentation operation using local 
				block threshold.

			params:
			image : 
				type: rgb2gray

			return:
			image:
				type: binary
		"""
		if self.__block_value % 2 == 0:
			self.__block_value += 1
		adaptive_thresh = threshold_local(self.image, self.__block_value, offset=0.02)
		binary_adaptive = self.image < adaptive_thresh

		#Holes to fill holes
		image_fill = nd.binary_fill_holes(binary_adaptive)

		im_fill_label, n= label(image_fill, return_num=True)
		if n < 1:
			image_fill = binary_adaptive
				
		ee_ = morphology.disk(2)

		#Opening morphological operation
		image_opening= nd.binary_opening(image_fill, ee_, iterations=2, output=None, origin=0).astype(np.int)
		image_opening= nd.binary_erosion(image_fill, ee_, iterations=1, output=None, origin=0).astype(np.int) 

		#Labeling for remove objects
		label_image_opening, nun = label(image_opening, return_num=True)
		if nun < 3:
			img= image_fill
		else:    
			#Remove small object
			remove_img = morphology.remove_small_objects(label_image_opening, 5)
			#Removes edge-connected artifacts 
			img = clear_border(remove_img).astype(np.int)
			
		return img
