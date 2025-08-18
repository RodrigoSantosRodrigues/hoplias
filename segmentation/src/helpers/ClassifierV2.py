# -*- coding: utf-8 -*-
'''
	sorting images in background and object with svm.

	author: Rodrigo Junior santos
	Email:  rodrjuniorsantos@gmail.com

	REFERENCES:
	-----------
'''
import numpy as np
import cv2
from skimage.measure import label, regionprops
from skimage import color
import scipy.ndimage as nd
import joblib
from sklearn.ensemble import IsolationForest
from skimage import img_as_float
from ultralytics import YOLO
import cloudpickle

class ClassifierV2:
	def __init__(self, imageGray, imageTrash, logger):
		self.image = imageGray
		self.binary = imageTrash
		self.Ftest = np.array([])
		self.objects = np.array([])
		self.model_path = 'src//helpers//svm_model//HOPLIAS_TOOLKIT_GEN_SEG_CROM_V1.0.0_ALPHA.pkl'
		self.model_path_deep = 'src//helpers//svm_model//HOPLIAS_TOOLKIT_YOLOV8_BEST_CPU_SEG_CROM_V1.0.0_ALPHA-1.pt'
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

	def classifier_model_deep(self):
		'''
		Sorting images in background and object with yolov8-seg model.
		return:
				mask: numpy array [H, W] com todos os objetos segmentados
		'''
		model = YOLO(self.model_path_deep)

		image = self.image
		if len(image.shape) == 4 and image.shape[0] == 1 and image.shape[1] == 3:
			image = image.squeeze(0).transpose(1, 2, 0)

		if image.dtype != np.uint8:
			image = image.astype(np.uint8)

		image_bgr = image
		if len(image.shape) == 2:
			image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
		elif image.shape[2] == 4:
			image_bgr = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
		elif image.shape[2] == 3:
			if np.allclose(image[...,0], image[...,1]) and np.allclose(image[...,0], image[...,2]):
				image_bgr = cv2.cvtColor(image[...,0], cv2.COLOR_GRAY2BGR)
			else:
				image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
		else:
			raise ValueError(f"Format not suported: {image.shape}")

		results = model.predict(image_bgr)

		height, width = image.shape[:2]
		combined_mask = np.zeros((height, width), dtype=np.uint8)

		for result in results:
			if result.masks is None:
				continue

			masks = result.masks.data.cpu().numpy()
			boxes = result.boxes.xyxy.cpu().numpy().astype(int)

			for seg_mask, box in zip(masks, boxes):
				seg_mask_resized = cv2.resize(seg_mask, (width, height))
				seg_mask_bin = (seg_mask_resized > 0.5).astype(np.uint8)

				x1, y1, x2, y2 = box
				x1, y1 = max(x1,0), max(y1,0)
				x2, y2 = min(x2,width), min(y2,height)

				masked_img = cv2.bitwise_and(image_bgr, image_bgr, mask=seg_mask_bin)
				gray_roi = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)
				# crop bbox
				gray_crop = gray_roi[y1:y2, x1:x2]
				refined_crop = seg_mask_bin[y1:y2, x1:x2]

				kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
				refined_crop = cv2.morphologyEx(gray_crop, cv2.MORPH_ERODE, kernel)
				refined_mask = np.zeros_like(seg_mask_bin, dtype=np.uint8)
				refined_mask[y1:y2, x1:x2] = refined_crop
				combined_mask = np.logical_or(combined_mask, refined_mask).astype(np.uint8)

		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
		combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)

		return combined_mask, combined_mask
