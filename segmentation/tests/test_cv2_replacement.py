# -*- coding: utf-8 -*-
"""
Testes unitários simples para validar substituições de cv2 por skimage/numpy/scipy.
"""
import numpy as np
import pytest
from skimage import color, transform, morphology
from scipy import ndimage
from io import BytesIO
from imageio import imread
import base64


class TestColorConversions:
    """Testes para conversões de cores."""
    
    def test_gray_to_bgr(self):
        """Testa conversão de GRAY para BGR."""
        gray = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        # Convert GRAY to RGB then to BGR
        rgb = color.gray2rgb(gray)
        bgr = rgb[..., ::-1]
        
        assert bgr.shape == (100, 100, 3)
        assert bgr.dtype == rgb.dtype
        # Check that all channels are equal in RGB (since it's grayscale)
        assert np.allclose(rgb[:, :, 0], rgb[:, :, 1])
        assert np.allclose(rgb[:, :, 0], rgb[:, :, 2])
    
    def test_rgba_to_bgr(self):
        """Testa conversão de RGBA para BGR."""
        rgba = np.random.randint(0, 255, (100, 100, 4), dtype=np.uint8)
        # Convert RGBA to RGB then to BGR
        rgb = color.rgba2rgb(rgba)
        bgr = rgb[..., ::-1]
        
        assert bgr.shape == (100, 100, 3)
        assert bgr.dtype == rgb.dtype
    
    def test_rgb_to_bgr(self):
        """Testa inversão de canais RGB para BGR."""
        rgb = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        bgr = rgb[..., ::-1]
        
        assert bgr.shape == rgb.shape
        assert np.array_equal(bgr[:, :, 0], rgb[:, :, 2])  # B = R
        assert np.array_equal(bgr[:, :, 1], rgb[:, :, 1])  # G = G
        assert np.array_equal(bgr[:, :, 2], rgb[:, :, 0])  # R = B
    
    def test_bgr_to_gray(self):
        """Testa conversão de BGR para GRAY."""
        bgr = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        # Convert BGR to RGB first, then to gray
        rgb = bgr[..., ::-1]
        gray = color.rgb2gray(rgb)
        
        assert gray.shape == (100, 100)
        assert gray.dtype == np.float64 or gray.dtype == np.float32


class TestResize:
    """Testes para operações de resize."""
    
    def test_resize_dimensions(self):
        """Testa que resize produz dimensões corretas."""
        img = np.random.rand(50, 50)
        target_height, target_width = 100, 150
        
        resized = transform.resize(img, (target_height, target_width), 
                                   anti_aliasing=False, preserve_range=True)
        
        assert resized.shape == (target_height, target_width)
    
    def test_resize_preserve_range(self):
        """Testa que preserve_range mantém valores originais."""
        img = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
        
        resized = transform.resize(img, (100, 100), 
                                   anti_aliasing=False, preserve_range=True)
        
        assert resized.min() >= 0
        assert resized.max() <= 255


class TestMorphologicalOperations:
    """Testes para operações morfológicas."""
    
    def test_binary_erosion(self):
        """Testa erosão binária."""
        binary = np.array([[0, 0, 0, 0, 0],
                           [0, 1, 1, 1, 0],
                           [0, 1, 1, 1, 0],
                           [0, 1, 1, 1, 0],
                           [0, 0, 0, 0, 0]], dtype=np.uint8)
        kernel = morphology.disk(1)
        
        eroded = ndimage.binary_erosion(binary, kernel).astype(binary.dtype)
        
        assert eroded.shape == binary.shape
        assert eroded.dtype == binary.dtype
        # Erosion should shrink the object
        assert eroded.sum() <= binary.sum()
    
    def test_binary_opening(self):
        """Testa abertura binária."""
        binary = np.array([[0, 0, 0, 0, 0],
                           [0, 1, 1, 1, 0],
                           [0, 1, 1, 1, 0],
                           [0, 1, 1, 1, 0],
                           [0, 0, 0, 0, 0]], dtype=np.uint8)
        kernel = morphology.disk(1)
        
        opened = ndimage.binary_opening(binary, kernel).astype(binary.dtype)
        
        assert opened.shape == binary.shape
        assert opened.dtype == binary.dtype
    
    def test_cross_kernel(self):
        """Testa criação de kernel cross manual."""
        kernel = np.zeros((3, 3), dtype=np.uint8)
        kernel[1, :] = 1  # horizontal line
        kernel[:, 1] = 1  # vertical line
        
        assert kernel.shape == (3, 3)
        assert kernel.sum() == 5  # 3 horizontal + 3 vertical - 1 center (overlap)
        assert kernel[1, 1] == 1  # center should be 1


class TestImageDecode:
    """Testes para decodificação de imagens."""
    
    def test_imread_from_bytes(self):
        """Testa que imageio pode ler de BytesIO."""
        # Create a simple test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Save to bytes using PIL (simulating base64 decode scenario)
        from PIL import Image
        img = Image.fromarray(test_image)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Read back using imageio
        decoded = imread(buffer)
        
        assert decoded.shape[0] == test_image.shape[0]
        assert decoded.shape[1] == test_image.shape[1]
        assert len(decoded.shape) >= 2


class TestNumpyOperations:
    """Testes para operações numpy que substituem cv2."""
    
    def test_subtract_with_dtype(self):
        """Testa np.subtract com dtype específico."""
        a = np.array([100, 200, 300], dtype=np.uint8)
        b = np.array([50, 100, 150], dtype=np.uint8)
        
        result = np.subtract(a, b, dtype=np.int16)
        
        assert result.dtype == np.int16
        assert np.array_equal(result, [50, 100, 150])
    
    def test_inrange_equivalent(self):
        """Testa equivalente de cv2.inRange."""
        img = np.array([10, 50, 100, 150, 200, 250], dtype=np.uint8)
        low, high = 50, 150
        
        mask = np.logical_and(img >= low, img <= high).astype(np.uint8) * 255
        
        assert mask.dtype == np.uint8
        assert mask[0] == 0  # 10 < 50
        assert mask[1] == 255  # 50 <= 50 <= 150
        assert mask[2] == 255  # 100 <= 100 <= 150
        assert mask[3] == 255  # 150 <= 150 <= 150
        assert mask[4] == 0  # 200 > 150
        assert mask[5] == 0  # 250 > 150
    
    def test_bitwise_and_with_mask(self):
        """Testa equivalente de cv2.bitwise_and com mask."""
        img = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
        mask = np.zeros((10, 10), dtype=np.uint8)
        mask[3:7, 3:7] = 1
        
        result = np.where(mask[..., None] > 0, img, 0)
        
        assert result.shape == img.shape
        assert np.all(result[0:3, :, :] == 0)  # Outside mask should be 0
        assert np.all(result[7:, :, :] == 0)  # Outside mask should be 0
        assert not np.all(result[3:7, 3:7, :] == 0)  # Inside mask should have values


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

