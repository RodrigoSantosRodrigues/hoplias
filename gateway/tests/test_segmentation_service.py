# -*- coding: utf-8 -*-
"""
Teste unitário para validar a decodificação de imagem usando imageio
"""
import numpy as np
from io import BytesIO
from imageio import imread, imwrite


def test_image_decode_png():
    """Testa a decodificação de uma imagem PNG usando imageio"""
    # Criar uma imagem de teste simples (10x10 pixels RGB)
    test_image = np.zeros((10, 10, 3), dtype=np.uint8)
    test_image[:, :, 0] = 255  # Canal vermelho
    
    # Converter para PNG em bytes usando imageio
    buffer = BytesIO()
    imwrite(buffer, test_image, format='PNG')
    image_bytes = buffer.getvalue()
    
    # Decodificar usando imageio (mesma lógica do SegmentationService)
    decoded_image = imread(BytesIO(image_bytes))
    
    # Verificar que retorna um array numpy válido
    assert isinstance(decoded_image, np.ndarray)
    assert decoded_image.shape[0] > 0
    assert decoded_image.shape[1] > 0
    assert len(decoded_image.shape) >= 2


def test_image_decode_jpeg():
    """Testa a decodificação de uma imagem JPEG usando imageio"""
    # Criar uma imagem de teste simples (10x10 pixels RGB)
    test_image = np.zeros((10, 10, 3), dtype=np.uint8)
    test_image[:, :, 1] = 255  # Canal verde
    
    # Converter para JPEG em bytes usando imageio
    buffer = BytesIO()
    imwrite(buffer, test_image, format='JPEG')
    image_bytes = buffer.getvalue()
    
    # Decodificar usando imageio
    decoded_image = imread(BytesIO(image_bytes))
    
    # Verificar que retorna um array numpy válido
    assert isinstance(decoded_image, np.ndarray)
    assert decoded_image.shape[0] > 0
    assert decoded_image.shape[1] > 0
    assert len(decoded_image.shape) >= 2

