# -*- coding: utf-8 -*-
"""
	Segmentation of fish chromosomes in images in a metaphase.
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com

	REFERENCES:
	-----------
    Jean-Patrick Pommier --> http://www.dip4fish.blogspot.com
"""
import logging
import numpy   as np 
from scipy import ndimage as nd
from skimage.measure import label


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Extract:
  def __init__(self, image, binary, image_gray):
    self.image = image
    self.binary = binary
    self.image_gray = image_gray

  @staticmethod
  def extract_particles(image, LabelImg):
    locations = nd.find_objects(LabelImg)
    extracted_images = []
    extracted_binaries = []

    for i, loc in enumerate(locations, 1):
      lab_image = np.copy(LabelImg[loc])
      im = np.copy(image[loc])

      if len(im.shape) == 3 and im.shape[2] == 3:
        mask = (lab_image == i)

        extracted_particle = np.zeros_like(im)

        for c in range(3):
          extracted_particle[:, :, c] = im[:, :, c] * mask

        extracted_images.append(extracted_particle)
        extracted_binaries.append(mask)

      elif len(im.shape) == 2:
        mask = (lab_image == i)

        extracted_particle = np.zeros_like(im)
        extracted_particle[mask] = im[mask]

        extracted_images.append(extracted_particle)
        extracted_binaries.append(mask)

    return extracted_images, extracted_binaries

  def extract_rgb(self):
    labelled = label(self.binary)
    singles, masks= Extract.extract_particles(self.image, labelled)
    return singles, masks
