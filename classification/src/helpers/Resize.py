# -*- coding: utf-8 -*-
"""
	Segmentation of fish chromosomes in images in a metaphase.
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com

	REFERENCES:
	-----------

"""
import numpy as np
from concurrent.futures import ProcessPoolExecutor

class Resize:
    __max_workers = 10

    @staticmethod
    def _resize_single_image(args):
        """
        Internal helper function to pad a single image to the target width and height.
        """
        img, max_height, max_width, is_rgb, components, imtype = args
        height, width = img.shape[:2]
        diffw = max_width - width
        diffh = max_height - height

        startw = diffw // 2
        starth = diffh // 2

        if is_rgb:
            newIm = np.zeros((max_height, max_width, components), dtype=imtype)
            newIm[starth:starth + height, startw:startw + width, :] = img
        else:
            newIm = np.zeros((max_height, max_width), dtype=imtype)
            newIm[starth:starth + height, startw:startw + width] = img

        return newIm

    @staticmethod
    def Resize_images(image_list):
        """
        Resize a list of images by padding them to match the maximum width and height 
        found in the list. The padding is centered for each image.

        Parameters:
        -----------
        image_list : list of np.ndarray
            List of input images (either grayscale or RGB) to be resized.

        Returns:
        --------
        list of np.ndarray
            List of resized images, all having the same dimensions (max width and height).
            The content of each image is centered with zero-padding.
        """
        if not image_list:
            return []

        imtype = image_list[0].dtype
        is_rgb = len(image_list[0].shape) == 3
        components = image_list[0].shape[2] if is_rgb else 1

        # Determine max width and height
        max_width = max(img.shape[1] for img in image_list)
        max_height = max(img.shape[0] for img in image_list)

        # Prepare arguments for multiprocessing
        args_list = [
            (img, max_height, max_width, is_rgb, components, imtype)
            for img in image_list
        ]

        with ProcessPoolExecutor(max_workers=Resize.__max_workers) as executor:
            resized_images = list(executor.map(Resize._resize_single_image, args_list))

        return resized_images
