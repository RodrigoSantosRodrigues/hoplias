# -*- coding: utf-8 -*-
'''
	sorting images in background and object with svm.

	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com

	REFERENCES:
	-----------
'''
import numpy as np
from skimage.measure import label, regionprops
from skimage import color
import scipy.ndimage as nd
import joblib
from sklearn.ensemble import IsolationForest
from skimage import img_as_float
import cloudpickle

class ClassifierV2:
	def __init__(self, imageGray, imageTrash, logger):
		self.image = imageGray
		self.binary = imageTrash
		self.Ftest = np.array([])
		self.path_matrix = 'src//helpers//features//v2'
		self.objects = np.array([])
		self.model_path = 'src//helpers//svm_model//image-best-seg-model-animals-pipeline_V2_balanced.pkl'
		self.scaler_path = 'src//helpers/svm_model//best-seg-scaler-animals-f023-py-11.1.pkl'
		self.logger = logger

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
		im = self.image
		if self.image.shape[-1] == 4:
			im = self.image[:, :, :3]

		binary = self.binary
		im = color.rgb2gray(im)
		
		#binary, num = nd.label(binary)
		image_label = label(binary)
		image = regionprops(image_label, im)
		mes = []

		for i, prop in enumerate(image):
			area_safe = max(prop.area, 1e-6)
			intensity_normalized = (prop.mean_intensity - prop.min_intensity) / (prop.max_intensity - prop.min_intensity + 1e-6)

			mes.append((
				prop.solidity,
				prop.eccentricity,
				intensity_normalized,
				np.log1p(prop.area),
				np.log1p(prop.equivalent_diameter),
				np.std(np.extract(image_label, im)),
				prop.perimeter**2 / (4 * np.pi * area_safe),
				intensity_normalized * prop.solidity, # combined feature - intensity_shape_score
				np.log1p(prop.area) / intensity_normalized, # combined feature - area_intensity_ratio
				prop.label,
				0,
				2
			))
		self.Ftest = np.array(mes)

	def classifier(self):
		'''
		Sorting images in background and object with SVM.

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
		model = joblib.load(self.model_path)
		F_test = self.Ftest[:, [0, 2, 3]]
		self.logger.info(f"F_test: {F_test}")
		probabilities = model.predict_proba(F_test)
		#self.logger.info(f"Probabilitie: {probabilities}")
		model_predictions = (probabilities[:, 1] >= 0.96).astype(int) + 1
		#self.logger.info(f"Classes 2: {[i for i in range(len(model_predictions)) if model_predictions[i] == 2]}")

		aux = []
		for i in range(0, len(model_predictions)):
			if model_predictions[i] == 2:
				aux.append((self.Ftest[i, [9]], self.Ftest[i, [10]], 2))

		self.objects = np.array(aux, dtype=object).astype(int)

	def classifier_model(self, block_value, hard_process):
		'''
		Sorting images in background and object with image-best-seg-model.
		return:
			objects:
				type: numpy []
		'''
		with open(self.model_path, "rb") as f:
			model = cloudpickle.load(f)
			
		if not hasattr(model, 'predict_image') or not callable(model.predict_image):
			error_message = "Loaded model doesn't have required predict_image method"
			self.logger.error(error_message)
			raise ValueError(error_message)

		predictions_img = model.predict_image(self.image, block_value, hard_process)

		predicted_cleaned = model.refine_predictions_outliers(model.props, predictions_img)

		prediction_mask_clean = np.zeros_like(model.im_binary_label)
		for prop, pred in zip(model.props, predicted_cleaned):
			if pred == 2:
				prediction_mask_clean[model.im_binary_label == prop.label] = 1
	
		return model.prediction_mask, prediction_mask_clean
		
