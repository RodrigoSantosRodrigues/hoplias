# -*- coding: utf-8 -*-
'''
	Segmentation of fish chromosomes in images in a metaphase state - morphological operations.
	author: Rodrigo Junior santos

	REFERENCES:
	-----------
'''
import logging
import base64
import io
from PIL import Image

from .Data import ModelSegmentation


def compress_base64_image(base64_str, max_size_bytes=3_000_000, min_quality=10, step=5):
  """
  Comprime uma imagem em base64 até que seu tamanho seja menor que `max_size_bytes`.
  
  Parâmetros:
      base64_str (str): Imagem codificada em base64.
      max_size_bytes (int): Tamanho máximo em bytes.
      min_quality (int): Qualidade mínima permitida (1 a 100).
      step (int): Passo de redução da qualidade por iteração.

  Retorna:
      str: Imagem comprimida em base64.
  """
  if "," in base64_str:
      base64_str = base64_str.split(",")[1]

  image_data = base64.b64decode(base64_str)
  image = Image.open(io.BytesIO(image_data)).convert("RGB")

  quality = 95
  while quality >= min_quality:
      buffer = io.BytesIO()
      image.save(buffer, format="JPEG", quality=quality)
      compressed_data = buffer.getvalue()
      if len(compressed_data) <= max_size_bytes:
        return compressed_data
      quality -= step
  
  return compressed_data
