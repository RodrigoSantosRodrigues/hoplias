# -*- coding: utf-8 -*-
"""
	Segmentation of fish chromosomes in images in a metaphase.
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com

	References:
            Jean-Patrick Pommier --> http://www.dip4fish.blogspot.com
            http://en.wikipedia.org/wiki/Polygon#Area_and_centroid

"""
from __future__ import division
import numpy as np
from scipy import ndimage as nd
import matplotlib.pyplot as plt
from skimage import color, img_as_int,  morphology
from skimage.draw import line_aa
import cv2
import mahotas
import mahotas.polygon
from PIL import Image

from .RotationAngle import RotationAngle


def PeakByModalValue(array):
    '''look for the modal value of a 2D array'''
    x=array[0,:]
    y=array[1,:]
    '''
    print ("y.shape", y.shape[0]) 
    print ("y[0]",y[0])
    print ("y[y.shape[0]-1]",y[y.shape[0]-1])
    print ("Searching modal value")
    '''
    xmin=x.min()#image min graylevel
    #xmax=x.max()#image max gray level
    mode=xmin
    countmax=0#occurence of a given grayscale
    #print "mig=",xmin,"  mag=",xmax
    for i in range(0,y.shape[0]-1):
        test=y[i]>countmax
        #print "test:",test,"histo(",i,")=", y[i],"max",countmax
        if  test:
            countmax=y[i]
            mode=x[i]
            #print "mode",mode
    return mode
      
class particle(object):
    rotatedIm=np.array([[0,0],[0,0]])
    rotatedFlag=False
    #ratio of particle area by convexhull area
    #close to 1 for a convex particle
    #lower for other as touching chromosomes
    CvxhParticleArea_ratio=1
    
    def __init__(self,arrayIm):
        '''
        Initially the rotated image is empty and the flag
        indicates that no rotation is performed
        '''
        self.particuleImage=arrayIm
        self.rotatedIm=np.array([[0,0],[0,0]])
        self.compassTable=np.array([[0,0],[0,0]])
        self.compassTablePeaks=np.array([[0,0],[0,0]])
    
    def cvxhull_area(self):
        '''
        Calculate the convexhull area such that:
        A=0.5*Sumfrom 0 to N-1 of {xn+1*yn-xn*yn+1}
        Pn(xn,yn) and PN=P0
        see http://en.wikipedia.org/wiki/Polygon#Area_and_centroid
        '''
        #print "cvxhull called"        
        binIm=self.particuleImage>0
        area=np.sum(binIm[:,:]==True)
        #print binIm.dtype
        contour=mahotas.bwperim(binIm)
        pointlist=mahotas.polygon.convexhull(contour)
        N=len(pointlist)
        fP=pointlist[0]
        #duplicate the first point P0
        #at the end such that PointN=Point0
        np.append(pointlist, fP)
        #pointlist.append(fP)
        s=0
        #compute the sum from 0 to N-1
        for i in range(0,N-1):
            cx=pointlist[i][0]#x of the current point
            cy=pointlist[i][1]#y of the current point
            #print "Point",i," x=",cx," y=",cy
            nx=pointlist[i+1][0]#x of the next point
            ny=pointlist[i+1][1]#y of the next point
            #print "Point suiv",i+1," x=",nx," y=",ny
            det=nx*cy-cx*ny
            s=s+det
            #print "det:",det," S=",s
        CvxhParticleArea_ratio=area/(0.5*abs(s))
        return 0.5*abs(s),CvxhParticleArea_ratio
        
    def getVerticalImage(self):
            return self.rotatedIm
    def getcompassTableDerivative(self):
            return self.compassTablePeaks    
    def orientationByErosion(self, step):
        ''' Performs successive rotations of a binary particle from 0 to 180 by "step" '''
        def rotate_image_without_cuts(image, angle):
            rotated = nd.rotate(image, angle, reshape=True)

            new_height, new_width = rotated.shape[:2]
            original_height, original_width = image.shape[:2]

            max_height = max(original_height, new_height)
            max_width = max(original_width, new_width)
            
            result = np.zeros((max_height, max_width), dtype=image.dtype)
            
            start_x = (max_width - new_width) // 2
            start_y = (max_height - new_height) // 2
            
            result[start_y:start_y+new_height, start_x:start_x+new_width] = rotated
            
            return result
        
        def erodeVParticle(im):
            '''Counts the number of vertical erosion necessary to destroy a particle'''
            vline = np.array([[0,1,0], [0,1,0], [0,1,0]])
            binaryIm = (im > 0)
            pixcount = np.sum(binaryIm)
            nb_erosion = 1
            while pixcount > 0:
                erodedIm = nd.binary_erosion(binaryIm, structure=vline, iterations=nb_erosion)
                nb_erosion += 1
                pixcount = np.sum(erodedIm)
            return nb_erosion

        maxRotationNubr = 180 // step
        compassTable = np.zeros((2, int(maxRotationNubr)+1), dtype=np.uint8)

        i = 0
        angle = i * step
        rotatedIm = self.particuleImage

        while i <= maxRotationNubr:
            maxErosion = erodeVParticle(rotatedIm)
            compassTable[0, i] = angle
            compassTable[1, i] = maxErosion

            # Use the rotate_image_without_cuts function
            rotatedIm = rotate_image_without_cuts(self.particuleImage, angle)
            i += 1
            angle = i * step

        majorAngle = PeakByModalValue(compassTable)
        self.rotatedIm = rotate_image_without_cuts(self.particuleImage, majorAngle)
        self.rotatedFlag = True
        return majorAngle, compassTable, self.rotatedIm

def morphological_horizontal_direction (im):
    im = color.rgb2gray(im)
    im= img_as_int(im)
    binary = (im>0).astype('int')
    return binary

def rotate_image_with_orientation(im, theta):
    image_center = (im.shape[1] // 2, im.shape[0] // 2)
    rotation_matrix = cv2.getRotationMatrix2D(image_center, theta, 1.0)
    cos_theta = np.abs(rotation_matrix[0, 0])
    sin_theta = np.abs(rotation_matrix[0, 1])
    
    new_width = int(im.shape[0] * sin_theta + im.shape[1] * cos_theta)
    new_height = int(im.shape[1] * sin_theta + im.shape[0] * cos_theta)

    rotation_matrix[0, 2] += (new_width - im.shape[1]) / 2
    rotation_matrix[1, 2] += (new_height - im.shape[0]) / 2

    im = np.asarray(im, dtype=np.uint8)

    rotated_image = cv2.warpAffine(
        im, rotation_matrix, (new_width, new_height),
        flags=cv2.INTER_NEAREST if len(im.shape) == 2 else cv2.INTER_LINEAR
    )

    return rotated_image.astype(np.uint8)

class Rotation:
    def __init__(self, image, binary, logger):
        self.image = image
        self.binary = binary
        self.angle = 0
        self.__logger = logger

    def rotation_particle(self):
        image = self.image[:, :, 0].copy()
       
        p1 = particle(image)
        theta, rosedesvents, vert_image = p1.orientationByErosion(8)
        self.angle = theta
        #self.__logger.info(f"theta1, rosedesvents: {theta1} {rosedesvents}")
   
        rotated_image = rotate_image_with_orientation(self.image, theta)
        rotated_binary = rotate_image_with_orientation(self.binary, theta)

        return rotated_image, rotated_binary

    def rotation_particle_gray(self):
        image_gray = self.image[:, :, 0].copy()
       
        p1 = particle(image_gray)
        theta, rosedesvents, vert_image = p1.orientationByErosion(8)
        self.angle = theta
        #self.__logger.info(f"theta1, rosedesvents: {theta1} {rosedesvents}")

        rotated_image = rotate_image_with_orientation(image_gray, theta)
        rotated_binary = rotate_image_with_orientation(self.binary, theta)

        return rotated_image, rotated_binary
