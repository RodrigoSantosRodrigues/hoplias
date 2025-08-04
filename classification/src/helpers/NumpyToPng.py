# -*- coding: utf-8 -*-
"""
	Segmentation of fish chromosomes in images.
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com
        
"""
from scipy.ndimage import median_filter
from scipy import ndimage as nd
from scipy.ndimage import gaussian_filter
from skimage.filters import median, gaussian, sobel
import numpy   as np 
from skimage.morphology import binary_dilation, disk
import base64
import cv2
import io
from PIL import Image
import matplotlib.pyplot 	as plt 

class NumpyToPng:
    def __init__(self, image, logger):
        self.image = image
        self.__logger = logger

    def generate_binary_mask_not_morph(self, image_rgb):
        gray_image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    
        _, binary_image = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY)
 
        kernel = np.ones((1, 1), np.uint8)
        binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)
     
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   
        mask = np.zeros_like(gray_image, dtype=np.uint8)
     
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 30:
                epsilon = 0.001 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
              
                cv2.drawContours(mask, [approx], -1, color=255, thickness=cv2.FILLED)
  
        if np.count_nonzero(mask) == 0:
            mask = (gray_image > 0).astype(np.uint8) * 255

        binary_mask = (mask > 0).astype(np.uint8)
        kernel = np.ones((3, 3), np.uint8)
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel)
        return binary_mask

    def generate_exact_binary_mask(self, image_rgb, erosion_iterations=2):
        gray_image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    
        _, binary_image = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY)
     
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        mask = np.zeros_like(gray_image, dtype=np.uint8)
     
        cv2.drawContours(mask, contours, -1, color=255, thickness=cv2.FILLED)
     
        mask_morph = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((1, 1), np.uint8))
        mask_morph = cv2.morphologyEx(mask_morph, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
   
        mask_erosion = cv2.erode(mask_morph, np.ones((3, 3), np.uint8), iterations=erosion_iterations)
     
        if not np.any(mask_erosion > 0):
            return mask_morph
        
        return mask_erosion

    def smooth_alpha_edges(self, image, median_size=3, gaussian_sigma=0.5):
        alpha = image[:, :, 3]
        alpha_edges = sobel(alpha) > 0.02
        alpha_edges_dilated = binary_dilation(alpha_edges, selem=disk(1))
     
        smoothed_alpha = alpha.copy()
        smoothed_alpha[alpha_edges_dilated] = median(
            alpha, selem=np.ones((median_size, median_size)), mode='nearest'
        )[alpha_edges_dilated]
  
        smoothed_alpha[alpha_edges_dilated] = gaussian(
            smoothed_alpha, sigma=gaussian_sigma
        )[alpha_edges_dilated]
    
        smoothed_image = image.copy()
        smoothed_image[:, :, 3] = smoothed_alpha
      
        smoothed_image = gaussian_filter(smoothed_image, sigma=0.2)
        return smoothed_image
    
    def convert_gray_image(self, rotated_image_rgb, rgba_mode=False):
        image = self.image
        if not rgba_mode:
            mask_gray = self.generate_exact_binary_mask(rotated_image_rgb)

            mask_gray = np.clip(mask_gray, 0, 255).astype(np.uint8)
            mask_gray = cv2.resize(mask_gray.astype(np.uint8), (image.shape[1], image.shape[0]))
    
            img_gray_rgba = np.stack((image,) * 4, axis=-1)
            img_gray_rgba[:, :, -1] = 255 
    
            img_rgba_mask = np.stack((mask_gray,) * 4, axis=-1) 
            img_rgba_mask[:, :, -1] = 255
            
            background_mask = (img_rgba_mask[:, :, 0:3] == [0, 0, 0]).all(2)
            img_gray_rgba[background_mask] = (0, 0, 0, 0)

            img_gray_rgba[mask_gray == 0, :] = (0, 0, 0, 0)

            non_transparent_mask = img_gray_rgba[:, :, 3] > 0
        
            img_filtered = median_filter(img_gray_rgba, size=3, mode='nearest')
            img_filtered[~non_transparent_mask] = (0, 0, 0, 0)

            img_filtered = gaussian_filter(img_filtered, sigma=0.2)
            image = img_filtered

        else:
            if image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)
           
            black_mask = (image[:, :, 0:3] == [0, 0, 0]).all(2)
            image[black_mask] = [0, 0, 0, 0]
            image = self.smooth_alpha_edges(image, median_size=2, gaussian_sigma=0.2)

        buffer = io.BytesIO()
        Image.fromarray(image, mode='RGBA').save(buffer, format='PNG')
        encoded_image = buffer.getvalue()

        img_base64 = base64.b64encode(encoded_image).decode('utf-8')

        return f"data:image/png;base64,{img_base64}"

    def convert(self, rgba_mode=False):
        image = self.image
        if not rgba_mode:
            mask_gray = self.generate_exact_binary_mask(image)

            mask_gray = np.clip(mask_gray, 0, 255).astype(np.uint8)
    
            img_rgba = np.stack((image,) * 4, axis=-1)
            img_rgba[:, :, -1] = 255 
    
            img_rgba_mask = np.stack((mask_gray,) * 4, axis=-1) 
            img_rgba_mask[:, :, -1] = 255
        
            img_rgba = cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)
        
            background_mask = (img_rgba_mask[:, :, 0:3] == [0, 0, 0]).all(2)
            img_rgba[background_mask] = (0, 0, 0, 0)

            img_rgba[mask_gray == 0, :] = (0, 0, 0, 0)

            img_rgba = median_filter(img_rgba, size=3, mode='nearest')
            img_rgba = gaussian_filter(img_rgba, sigma=0.2)
            image = img_rgba

        else:
            if image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)
        
            black_mask = (image[:, :, 0:3] == [0, 0, 0]).all(2)
            image[black_mask] = [0, 0, 0, 0]
            image = self.smooth_alpha_edges(image, median_size=2, gaussian_sigma=0.2)
   
        buffer = io.BytesIO()
        Image.fromarray(image, mode='RGBA').save(buffer, format='PNG')
        encoded_image = buffer.getvalue()

        img_base64 = base64.b64encode(encoded_image).decode('utf-8')

        return f"data:image/png;base64,{img_base64}"
