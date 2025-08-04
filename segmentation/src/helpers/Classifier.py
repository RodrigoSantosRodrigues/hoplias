# -*- coding: utf-8 -*-
'''
	sorting images in background and object with svm.
	
	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com

	REFERENCES:
	-----------
'''
import numpy as np
from skimage.measure import regionprops, label
from sklearn import svm
from sklearn import preprocessing

class Classifier:
	def __init__(self, imageGray, imageTrash):
		self.image = imageGray
		self.binary = imageTrash
		self.Ftest = np.array([])
		self.path_matrix = 'src//helpers//features'
		self.objects = np.array([])

	def extract(self):
		"""
		This function builds a matrix of chromosome 
		characteristics using skimage measure regionprops.

		params:
			image:
				type: rgb2gray
			image: 
				type: binary

		return:
			array:
				type: numpy
		"""
		image_label = label(self.binary)
		image = regionprops(image_label, self.image)
		mes =[]

		# extracting features
		for i, prop in enumerate(image):
			mes.append((prop.area, prop.solidity, prop.mean_intensity, prop.eccentricity, prop.equivalent_diameter, prop.label, 0, 2))
		self.Ftest = np.array(mes)

	def classifier(self):
		'''
			sorting images in background and object with svm.

			params:
				Ftest: 
					type: numpy

			return:
				objects:
					type: numpy

			references:
				http://scikit-learn.org/stable/modules/preprocessing.html
				4.3.1.1. Scaling features to a range
		'''
		#Opening training files
		Ftrain= np.genfromtxt(self.path_matrix +'//F_train.csv',delimiter=',')
		Ttrain= np.genfromtxt(self.path_matrix +'/r_train.csv',delimiter=',')

		scaler = preprocessing.StandardScaler().fit(Ftrain[:, 0:4])

		F_train = scaler.transform(Ftrain[:, 0:4])
		r_train= Ttrain.astype(int)

		F_test = scaler.transform(self.Ftest[:, 0:4])

		# all columns
		F_test_= self.Ftest[:, :]
		# classification SVM.
		clf = svm.SVC()
		# training SVM.
		clf.fit(F_train, r_train)
		# predict SVM.
		clf = clf.predict(F_test)

		aux=[]
		for i in range(0, len(clf)):
			if clf[i] == 2:
				if F_test_[i, 7:] == 2:
					aux.append((F_test_[i, 5:6], F_test_[i, 6:7], 2))
				
		self.objects = np.array(aux, dtype=object).astype(int)
