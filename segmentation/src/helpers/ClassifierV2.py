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
from skimage import color, transform, morphology
from scipy import ndimage
import joblib
#from sklearn.ensemble import IsolationForest
from skimage import img_as_float
#from ultralytics import YOLO
import cloudpickle
import os

class ClassifierV2:
	def __init__(self, imageGray, imageTrash, logger):
		self.image = imageGray
		self.binary = imageTrash
		self.Ftest = np.array([])
		self.objects = np.array([])
		
		# Construir caminho absoluto do modelo baseado no diretório de trabalho do Docker (/app)
		# ou no diretório do script se executado localmente
		base_dir = os.getenv('APP_DIR', '/app')
		if not os.path.exists(base_dir):
			# Fallback: usar diretório do script
			base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
		
		model_dir = os.path.join(base_dir, 'src', 'helpers', 'svm_model')
		self.model_path = os.path.join(model_dir, 'HOPLIAS_TOOLKIT_GEN_SEG_CROM_V1.0.0_ALPHA.pkl')
		self.model_path_deep = os.path.join(model_dir, 'HOPLIAS_TOOLKIT_YOLOV8_BEST_CPU_SEG_CROM_V1.0.0_ALPHA-1.pt')
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
		# Verificar se o arquivo existe antes de tentar abrir
		if not os.path.exists(self.model_path):
			error_message = f"Arquivo de modelo não encontrado: {self.model_path}"
			self.logger.error(error_message)
			self.logger.error(f"Diretório atual: {os.getcwd()}")
			self.logger.error(f"Diretório do script: {os.path.dirname(os.path.abspath(__file__))}")
			raise FileNotFoundError(error_message)
		
		# Verificar permissões de leitura
		if not os.access(self.model_path, os.R_OK):
			error_message = f"Sem permissão de leitura no arquivo: {self.model_path}"
			self.logger.error(error_message)
			raise PermissionError(error_message)
		
		try:
			with open(self.model_path, "rb") as f:
				model = cloudpickle.load(f)
		except FileNotFoundError as e:
			error_message = f"Arquivo de modelo não encontrado: {self.model_path}"
			self.logger.error(error_message)
			self.logger.error(f"Erro original: {e}")
			raise FileNotFoundError(error_message) from e
		except PermissionError as e:
			error_message = f"Sem permissão para ler o arquivo: {self.model_path}"
			self.logger.error(error_message)
			self.logger.error(f"Erro original: {e}")
			raise PermissionError(error_message) from e
		except ImportError as e:
			if 'libGL' in str(e) or 'cv2' in str(e):
				self.logger.error(f"OpenGL/OpenCV import error: {e}")
				self.logger.error("Verifique se as dependências OpenGL estão instaladas no container")
				raise ImportError(
					f"Erro ao carregar modelo: dependência OpenGL não encontrada. "
					f"Erro original: {e}"
				) from e
			raise
		except Exception as e:
			error_message = f"Erro ao carregar modelo pickle: {e}"
			self.logger.error(error_message)
			self.logger.error(f"Tipo de erro: {type(e).__name__}")
			self.logger.error(f"Caminho do arquivo: {self.model_path}")
			raise
			
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

"""
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
			# Convert GRAY to BGR: gray -> RGB -> BGR
			image_rgb = color.gray2rgb(image)
			image_bgr = image_rgb[..., ::-1]  # RGB to BGR
		elif image.shape[2] == 4:
			# Convert RGBA to BGR: RGBA -> RGB -> BGR
			image_rgb = color.rgba2rgb(image)
			image_bgr = image_rgb[..., ::-1]  # RGB to BGR
		elif image.shape[2] == 3:
			if np.allclose(image[...,0], image[...,1]) and np.allclose(image[...,0], image[...,2]):
				# Convert GRAY to BGR: gray -> RGB -> BGR
				image_rgb = color.gray2rgb(image[...,0])
				image_bgr = image_rgb[..., ::-1]  # RGB to BGR
			else:
				# Convert RGB to BGR: just invert channels
				image_bgr = image[..., ::-1]  # RGB to BGR
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
				seg_mask_resized = transform.resize(seg_mask, (height, width), anti_aliasing=False, preserve_range=True)
				seg_mask_bin = (seg_mask_resized > 0.5).astype(np.uint8)

				x1, y1, x2, y2 = box
				x1, y1 = max(x1,0), max(y1,0)
				x2, y2 = min(x2,width), min(y2,height)

				# Apply mask: bitwise_and equivalent
				masked_img = np.where(seg_mask_bin[..., None] > 0, image_bgr, 0)
				# Convert BGR to GRAY: BGR -> RGB -> GRAY
				masked_img_rgb = masked_img[..., ::-1]  # BGR to RGB
				gray_roi = color.rgb2gray(masked_img_rgb)
				# crop bbox
				gray_crop = gray_roi[y1:y2, x1:x2]
				refined_crop = seg_mask_bin[y1:y2, x1:x2]

				# Create 3x3 cross kernel manually
				kernel = np.zeros((3, 3), dtype=np.uint8)
				kernel[1, :] = 1  # horizontal line
				kernel[:, 1] = 1  # vertical line
				# Apply erosion (gray erosion for grayscale image, not binary)
				refined_crop = ndimage.grey_erosion(gray_crop, footprint=kernel).astype(gray_crop.dtype)
				refined_mask = np.zeros_like(seg_mask_bin, dtype=np.uint8)
				refined_mask[y1:y2, x1:x2] = refined_crop
				combined_mask = np.logical_or(combined_mask, refined_mask).astype(np.uint8)

		kernel = morphology.disk(1)  # 3x3 ellipse equivalent
		combined_mask = ndimage.binary_opening(combined_mask, kernel).astype(combined_mask.dtype)

		return combined_mask, combined_mask
"""