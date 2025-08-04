# -*- coding: utf-8 -*-
'''
	Segmentation of fish chromosomes in images in a metaphase - morphological operations.
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com

	REFERENCES:
	-----------
			References:
				Jean-Patrick Pommier --> http://www.dip4fish.blogspot.com
'''
import cv2
import numpy as np
from skimage.filters import threshold_otsu, threshold_local, threshold_niblack, threshold_sauvola
from skimage import img_as_ubyte
import mahotas
from skimage import morphology, exposure
from skimage.measure import label
from skimage.segmentation import clear_border, watershed
from scipy import ndimage as nd
from scipy.stats import mode as mode_stat
from matplotlib import pyplot as plt

class MorphologyV2:
	def __init__(self, image, block_value, hard_process, logger):
		self.image = image
		self.__block_value = block_value
		self.__hard_process = hard_process
		self.__specie = 'animals'
		self.logger = logger

	def get_block_value(self):
		return self.__block_value
	
	def get_hard_process(self):
		return self.__hard_process
	
	def get_specie(self):
		return self.__specie
	
	def find_optimal_threshold(self, gray_image, method='auto', block_size=35, k=0.2, r=128):
		"""
		Finds the optimal adaptive threshold for grayscale images using scikit-image.
		
		Parameters:
		- gray_image: Input image (2D numpy array) in grayscale
		- method: 'auto' (tests all), 'otsu', 'local', 'niblack' or 'sauvola'
		- block_size: Neighborhood size for adaptive methods (odd recommended)
		- k: Parameter for Niblack/Sauvola (typically between -0.2 and 0.2)
		- r: Parameter for Sauvola (typically between 32 and 128)
		
		Returns:
		- binary_mask: Thresholded binary image
		- threshold_value: Calculated threshold value
		- method_used: Name of the selected method
		"""
		
		# Convert to 8-bit (0-255) if needed
		image = img_as_ubyte(gray_image)
		
		if method == 'auto':
			# Test all methods and select the one with maximum inter-class variance
			results = {}
			
			# 1. Otsu (global)
			try:
				otsu_thresh = threshold_otsu(image)
				otsu_binary = image > otsu_thresh
				results['otsu'] = {
					'threshold': otsu_thresh,
					'binary': otsu_binary,
					'score': np.abs(np.mean(image[otsu_binary]) - np.mean(image[~otsu_binary]))
				}
			except:
				pass
			
			# 2. Local adaptive (gaussian-weighted mean)
			local_thresh = threshold_local(image, block_size=block_size, method='gaussian')
			local_binary = image > local_thresh
			results['local'] = {
				'threshold': np.mean(local_thresh),
				'binary': local_binary,
				'score': np.abs(np.mean(image[local_binary]) - np.mean(image[~local_binary]))
			}
			
			# 3. Niblack (for uneven illumination)
			try:
				niblack_thresh = threshold_niblack(image, window_size=block_size, k=k)
				niblack_binary = image > niblack_thresh
				results['niblack'] = {
					'threshold': np.mean(niblack_thresh),
					'binary': niblack_binary,
					'score': np.abs(np.mean(image[niblack_binary]) - np.mean(image[~niblack_binary]))
				}
			except:
				pass
			
			# 4. Sauvola (for document/text images)
			try:
				sauvola_thresh = threshold_sauvola(image, window_size=block_size, k=k, r=r)
				sauvola_binary = image > sauvola_thresh
				results['sauvola'] = {
					'threshold': np.mean(sauvola_thresh),
					'binary': sauvola_binary,
					'score': np.abs(np.mean(image[sauvola_binary]) - np.mean(image[~sauvola_binary]))
				}
			except:
				pass
			
			# Select method with maximum class separation
			best_method = max(results.items(), key=lambda x: x[1]['score'])
			return 255 - best_method[1]['binary']

	def modal_value(self, image):
		'''
		Look for the modal value of an image considering both dark and light backgrounds.

		Parâmetros:
			image: numpy.ndarray
				Imagem de entrada (em escala de cinza).

		Retorna:
			mode: int
				Valor modal da imagem.
		'''

		histo = mahotas.fullhistogram(image)
		countmax = histo.max()
	
		mig = image.min()
		mag = image.max()
		mode = 0
		countmax = 0
		tolerance = countmax * 0.05
	
		for i in range(mig, mag - 1):
			if histo[i] > countmax:
				countmax = histo[i]
				mode = i
			elif histo[i] > (countmax - tolerance):
				mode = i

		return mode
	
	def segment_hard_metaphase(self, no_background):
		blur_low_res = nd.gaussian_filter(no_background,35)
		blur_hi_res = nd.gaussian_filter(no_background,1)
		mid_pass = cv2.subtract(blur_hi_res,0.70*blur_low_res,dtype=16)
		bin = ( mid_pass>1.5*mid_pass.mean())
		bin_low_res = nd.binary_opening(bin,morphology.disk(4))
		bin_lr = clear_border(bin_low_res)
		blur = nd.gaussian_filter(no_background,5)
		hi_pass = cv2.subtract(no_background,1.0*blur,dtype=16)
		grad_low_res = nd.morphological_gradient(no_background, (3, 3))

		b_seeds1 = (hi_pass>hi_pass.mean())
		b_seeds2 = np.logical_and(b_seeds1,bin_lr)

		b_seeds4 = nd.binary_opening(b_seeds2,iterations=4)

		markers, nr_obj = nd.label(b_seeds4)
		labeled = mahotas.cwatershed(grad_low_res, markers, Bc=None, return_lines=False)
		labeled[labeled.copy() == -1] = 0
		labeled = label(labeled)
		
		return labeled
	
	def morphological_operations(self):
		image = self.image.copy()
		gray = self.image.copy()
		dark_image = False
		if len(image.shape) == 3:
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		else:
			gray = image.copy()

		if gray.dtype == np.uint16:
			gray_8bit = (gray / 256).astype(np.uint8)
		else:
			gray_8bit = gray.copy()

		median_value = np.median(gray_8bit)

		if median_value < 50:
			dark_image = True
		elif median_value > 200:
			dark_image = False
		else:
			dark_image = False

		image_corrected = image
		if not dark_image and self.__hard_process:
			blurred = cv2.GaussianBlur(gray, (1, 1), 0)
		
			mode_val =  mode_stat(blurred.ravel(), keepdims=True)[0][0]
			mode_val = int(mode_val)
			mask_background = cv2.inRange(blurred, mode_val - 1, mode_val + 1)
			grad_mask = cv2.GaussianBlur(mask_background.astype(np.float32), (1, 1), 0)
			grad_mask = grad_mask / grad_mask.max()
			grad_mask = (grad_mask * 255).astype(np.uint8)
		
			image_corrected = gray.copy()
			image_corrected[grad_mask > 0.3] = 255
			image_corrected = image_corrected.astype(np.uint8)
			
			if self.__block_value % 2 == 0:
				self.__block_value += 1
			block_size = self.__block_value
			adaptive_thresh = threshold_local(image_corrected, block_size, offset=10)
			image_corrected = (image_corrected < adaptive_thresh).astype(np.uint8) * 255

			image_corrected= nd.binary_opening(image_corrected, morphology.disk(3), iterations=2, output=None, origin=0)
			image_corrected= nd.binary_erosion(image_corrected, morphology.disk(1), iterations=2, output=None, origin=0)
			image_corrected= nd.binary_closing(image_corrected,morphology.disk(1), iterations=3, output=None, origin=0)
			image_corrected = nd.binary_fill_holes(image_corrected)
			image_corrected = morphology.remove_small_objects(image_corrected, 15)
			image_corrected, nun = label(image_corrected, return_num=True)
			image_corrected = image_corrected.astype(np.uint8)

		if not dark_image and not self.__hard_process:
			if self.__block_value % 2 == 0:
				self.__block_value += 1
			block_size = self.__block_value
			adaptive_thresh = threshold_local(image_corrected, block_size, offset=10)
			image_corrected = (image_corrected < adaptive_thresh).astype(np.uint8) * 255

			image_corrected= nd.binary_opening(image_corrected, morphology.disk(3), iterations=2, output=None, origin=0)
			image_corrected= nd.binary_erosion(image_corrected, morphology.disk(1), iterations=2, output=None, origin=0)
			image_corrected= nd.binary_closing(image_corrected,morphology.disk(1), iterations=3, output=None, origin=0)
			image_corrected = nd.binary_fill_holes(image_corrected)
			image_corrected = morphology.remove_small_objects(image_corrected, 15)
			image_corrected, nun = label(image_corrected, return_num=True)
			image_corrected = image_corrected.astype(np.uint8)

		mode = self.modal_value(image_corrected)
		back = np.zeros(image_corrected.shape, image_corrected.dtype)
		back.fill(mode)
		im = cv2.subtract(image_corrected, back)

		if dark_image:
			im = self.segment_hard_metaphase(im)

		return im
