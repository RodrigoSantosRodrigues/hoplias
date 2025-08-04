# -*- coding: utf-8 -*-
"""
	Segmentation of fish chromosomes in images in a metaphase.
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com

"""
import cv2
import numpy as np
from scipy import ndimage as nd
from skimage import color
from PIL import Image
from skimage import img_as_ubyte
from skimage.util import img_as_float
from math import ceil, cos, sin, radians


class RotationAngle:
    def __init__(self, image, angle, logger):
        self.image = image
        self.angle = angle
        self.logger = logger

    def rotate_image(self):
        if self.image.dtype != np.uint8:
            self.image = img_as_ubyte(self.image)

        img = self.image
        angle = -self.angle
        rads = radians(angle)

        rowsi, colsi = img.shape[:2]
        has_channels = len(img.shape) == 3
        channels = img.shape[2] if has_channels else 1

        background = img[0, 0] if not has_channels else img[0, 0, :]

        rowsf = ceil(rowsi * abs(cos(rads)) + colsi * abs(sin(rads)))
        colsf = ceil(rowsi * abs(sin(rads)) + colsi * abs(cos(rads)))

        if has_channels:
            C = np.ones((rowsf, colsf, channels), dtype=np.uint8) * background
        else:
            C = np.ones((rowsf, colsf), dtype=np.uint8) * background

        xo, yo = ceil(rowsi / 2), ceil(colsi / 2)
        midx, midy = ceil(rowsf / 2), ceil(colsf / 2)

        for i in range(rowsf):
            for j in range(colsf):
                x =  (i - midx) * cos(rads) + (j - midy) * sin(rads)
                y = -(i - midx) * sin(rads) + (j - midy) * cos(rads)

                x = round(x) + xo
                y = round(y) + yo

                if 0 <= x < rowsi and 0 <= y < colsi:
                    if has_channels:
                        C[i, j, :] = img[x, y, :]
                    else:
                        C[i, j] = img[x, y]

        half_h, half_w = rowsi // 2, colsi // 2
        start_y = midx - half_h
        end_y = start_y + rowsi
        start_x = midy - half_w
        end_x = start_x + colsi

        cropped = C[start_y:end_y, start_x:end_x]
        return cropped.astype(np.uint8)
   