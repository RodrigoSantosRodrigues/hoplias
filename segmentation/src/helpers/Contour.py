# -*- coding: utf-8 -*-
'''
	Segmentation of fish chromosomes in images in a metaphase state - morphological operations.
	author: Rodrigo Junior santos

	REFERENCES:
	-----------
'''
import logging
from skimage.measure import find_contours
import numpy as np
import json
import base64
import io
from PIL import Image

from .Data import ModelSegmentation

class Contour:
  def __init__(self, image_base64, binary, binary_cleaned, data):
    self.data = data
    self.image_base64 = image_base64
    self.binary = binary
    self.binary_cleaned = binary_cleaned
    self.data_sample = ModelSegmentation()

  def filter_object_by_area(self, points, min_area=3):
    # Function to calculate the area of a polygon with up to 6 points using the polygon area formula
    def calculate_area(points):
        n = len(points)
        area = 0.0
        for i in range(n):
            x1, y1 = points[i]['x'], points[i]['y']
            x2, y2 = points[(i + 1) % n]['x'], points[(i + 1) % n]['y']
            area += x1 * y2 - y1 * x2
        return abs(area) / 2.0

    # Filter objects that have between 3 and 6 points to form a polygon
    if 3 <= len(points):
      if len(points) <= 20:
        area = calculate_area(points)
        if area >= min_area:
          return True
        return False
      return True
    return False

  def extract_contours(self):
    """
    This function extracts the contour of segmented objects from both:
    - self.binary_cleaned (objects will be green)
    - self.binary difference with cleaned (objects will be orange)
    
    return:
      dict: json in hoplias editor format with colored objects
    """
    items = {
        'objects': [],
        "animations": [],
        "styles": [],
        "dataSources": []
    }

    id = 0
    for contour in find_contours(self.binary_cleaned, 0.5):
        payload = self.data_sample.data['objects'][1].copy()
        Xmin = np.min(contour[:,0])
        Ymin = np.min(contour[:,1])
        top = Xmin - 75
        left = Ymin
        coords = [{"x": p[1], "y": p[0]} for p in contour]
        
        if self.filter_object_by_area(coords):
            id += 1
            payload.update({
              'points': coords,
              'top': top,
              'left': left,
              'id': f"Chromosome {id}",
              'name': str(id),
              'stroke': "rgba(0,255,0,1)",  # Green stroke
            })
            items['objects'].append(payload)

    # Add base image
    image = next((obj for obj in self.data_sample.data['objects'] 
                if obj["type"] == "image"), None)
    if image:
        image.update({
            'src': self.image_base64,
            'workareaWidth': self.data.get('width'),
            'workareaHeight': self.data.get('height')
        })
        items['objects'].append(image)
    
    return items
