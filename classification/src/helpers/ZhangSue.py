# -*- coding: utf-8 -*-
'''
   Script para separar cromossomos sobrepostos
   Author: Rodrigo Junior Santos
   Email:  rodrjuniorsantos@gmail.com
 
'''
import os
import cv2
import numpy as np
import mahotas as mh
import matplotlib.pyplot as plt

from skimage.morphology import skeletonize, dilation, erosion, disk
from skimage import io, color, filters, morphology, util, feature
from skimage.morphology import skeletonize
from skimage.transform import rescale
import numpy as np
from scipy.ndimage import distance_transform_edt
import logging

class ZhangSue:
    def __init__(self, gray_image, image_binary, file_id):
        self.gray_image = gray_image
        self.image = image_binary
        self.file_id = file_id
        self.skel = self.pre_processing()

    def pre_processing(self):
        """
        Apply any necessary pre-processing to the image before skeletonization.

        Returns:
        -------
        pre_processed_image : np.array
            The pre-processed image ready for skeletonization.
        """
        binary_processed = None
        try:
            # selem = disk(1)
            # binary_dilated = dilation(binary_image, selem)
            # res_process = erosion(binary_dilated, selem)
            binary_processed = skeletonize(self.image.copy())
        except Exception:
            binary_processed = None
        return binary_processed
    
    def central_point_morph(im_bin, vert):
        def line_centroide(point_one, point_two):
            return [(point_one[0]+point_two[0])/2, (point_one[1]+point_two[1])/2]

        numberPixels=im_bin.shape[1]
        #print("Dimension:", im.shape[0], im.shape[1])
        #coordenadas ponto 1 e 2 da reta
        x1 = 0
        y1 = 0
        x2 = 0
        y2 = 0
        for i in range(0, im_bin.shape[0]):
            countPixels=0
            countx1 = 0
            county1 = 0
            countx2 = 0
            county2 = 0
            for j in range(0, im_bin.shape[1]):
                if im_bin[i][j] == 1:
                    if countx1 == 0:
                        countx1=i
                        county1=j
                    countx2=i
                    county2=j
                    countPixels= countPixels+1
            if countPixels !=0:
                if countPixels > 3:
                    if countPixels < numberPixels:
                        numberPixels= countPixels
                        x1 = countx1
                        y1 = county1
                        x2 = countx2
                        y2 = county2
        #print("Number  of pixels", numberPixels)

        vert = color.gray2rgb(vert)
        vert = cv2.line(vert, (y2,x1), (y1,x2), (255, 0, 0) , 1) 
        '''
        plt.figure(figsize=(200,200))
        plt.subplot(2,2,1)
        plt.imshow(vert, cmap='nipy_spectral')
        plt.title('Centromere')
        plt.show()
        '''
        pt1= [y2, x1]
        pt2= [y1, x2]
        return line_centroide(pt1, pt2)

    def skel_chromosome(self):
        """
        Apply skeletonization to the image and find intersection points using hit-or-miss.
        If no intersection points are found, use the central point of the skeleton line.

        Returns:
        -------
        centromere_point : tuple
            Coordinates of the intersection point in the skeleton, or the central point if no intersection is found.

        Formula:
        -------
        Given the skeletonized image `skel`, the intersection points are detected using various hit-or-miss templates.
        If no intersection points are found, the central point of the skeleton line is returned as the centromere point.
       
        """
        def branchedPoints(skel):
            branch1 = np.array([[0, 1, 0], [1, 1, 1], [0, 0, 0]])
            branch2 = np.array([[1, 0, 1], [0, 1, 0], [1, 0, 1]])
            branch3 = np.array([[1, 0, 1], [0, 1, 0], [1, 0, 0]])
            branch4 = np.array([[0, 1, 0], [1, 1, 0], [0, 1, 0]])
            branch5 = np.array([[1, 0, 0], [0, 1, 0], [1, 0, 1]])
            branch6 = np.array([[0, 0, 0], [1, 1, 1], [0, 1, 0]])
            branch7 = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 1]])
            branch8 = np.array([[0, 1, 0], [0, 1, 1], [0, 1, 0]])
            branch9 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
            br1 = mh.morph.hitmiss(skel, branch1)
            br2 = mh.morph.hitmiss(skel, branch2)
            br3 = mh.morph.hitmiss(skel, branch3)
            br4 = mh.morph.hitmiss(skel, branch4)
            br5 = mh.morph.hitmiss(skel, branch5)
            br6 = mh.morph.hitmiss(skel, branch6)
            br7 = mh.morph.hitmiss(skel, branch7)
            br8 = mh.morph.hitmiss(skel, branch8)
            br9 = mh.morph.hitmiss(skel, branch9)
            return br1 + br2 + br3 + br4 + br5 + br6 + br7 + br8 + br9

        skel = self.skel
        pts = branchedPoints(skel)
        centromere_point = None
        intersection_points = np.argwhere(pts > 0)
        if intersection_points.shape[0] > 0:
            centromere_point = tuple(intersection_points[0])
        else:
            # Find the central point of the skeleton line
            skel_points = np.argwhere(skel > 0)
            if skel_points.shape[0] > 0:
                mid_index = skel_points.shape[0] // 2
                centromere_point = tuple(skel_points[mid_index])
            else:
                # binary_points = np.argwhere(self.image > 0)
                # min_x, min_y = np.min(binary_points, axis=0)
                # max_x, max_y = np.max(binary_points, axis=0)
         
                # center_x = (min_x + max_x) // 2
                # center_y = (min_y + max_y) // 2
                # centromere_point = (center_x, center_y)

                centromere_point = self.central_point_morph(self.image, self.gray_image)

        return centromere_point
    