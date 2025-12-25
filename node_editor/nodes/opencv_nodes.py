import cv2
import numpy as np
from node_editor.core.node_graph import Node


# =============================================================================
# Color Category - Color Space & Adjustments
# =============================================================================

class GrayscaleNode(Node):
    """Convert image to grayscale."""
    category = "Color"

    def __init__(self):
        super().__init__("Grayscale")

    def process(self, input_data):
        img = input_data[0]
        if len(img.shape) == 2:
            return img  # Already grayscale
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


class ColorConvertNode(Node):
    """Convert between color spaces (RGB, HSV, LAB, etc.)."""
    category = "Color"

    def __init__(self):
        super().__init__("Color Convert", params={
            'mode': {'type': 'int', 'value': 0, 'range': (0, 3)}
            # 0: RGB→HSV, 1: RGB→LAB, 2: RGB→YCrCb, 3: RGB→BGR
        })

    def process(self, input_data):
        img = input_data[0]
        mode = self.get_parameter('mode')

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        conversions = [
            (cv2.COLOR_RGB2HSV, cv2.COLOR_HSV2RGB),
            (cv2.COLOR_RGB2LAB, cv2.COLOR_LAB2RGB),
            (cv2.COLOR_RGB2YCrCb, cv2.COLOR_YCrCb2RGB),
            (cv2.COLOR_RGB2BGR, cv2.COLOR_BGR2RGB),
        ]

        if 0 <= mode < len(conversions):
            converted = cv2.cvtColor(img, conversions[mode][0])
            return converted

        return img


class HueSaturationNode(Node):
    """Adjust hue and saturation."""
    category = "Color"

    def __init__(self):
        super().__init__("Hue/Saturation", params={
            'hue': {'type': 'int', 'value': 0, 'range': (-90, 90)},
            'saturation': {'type': 'float', 'value': 1.0, 'range': (0.0, 2.0)}
        })

    def process(self, input_data):
        hsv = cv2.cvtColor(input_data[0], cv2.COLOR_RGB2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        h = (h + self.get_parameter('hue')) % 180
        s = np.clip(s * self.get_parameter('saturation'), 0, 255)
        final_hsv = cv2.merge([h, s, v])
        return cv2.cvtColor(final_hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)


class BrightnessContrastNode(Node):
    """Adjust brightness and contrast."""
    category = "Color"

    def __init__(self):
        super().__init__("Brightness/Contrast", params={
            'brightness': {'type': 'int', 'value': 0, 'range': (-100, 100)},
            'contrast': {'type': 'float', 'value': 1.0, 'range': (0.1, 3.0)}
        })

    def process(self, input_data):
        img = input_data[0].astype(np.float32)
        brightness = self.get_parameter('brightness')
        contrast = self.get_parameter('contrast')
        return np.clip(img * contrast + brightness, 0, 255).astype(np.uint8)


class InvertNode(Node):
    """Invert image colors."""
    category = "Color"

    def __init__(self):
        super().__init__("Invert")

    def process(self, input_data):
        return cv2.bitwise_not(input_data[0])


# =============================================================================
# Enhance Category - Image Quality Enhancement
# =============================================================================

class EqualizeHistNode(Node):
    """Histogram equalization for contrast enhancement."""
    category = "Enhance"

    def __init__(self):
        super().__init__("Equalize Hist")

    def process(self, input_data):
        img = input_data[0]

        if len(img.shape) == 2:
            return cv2.equalizeHist(img)
        else:
            # Convert to YCrCb and equalize Y channel
            ycrcb = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
            ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
            return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)


class CLAHENode(Node):
    """Contrast Limited Adaptive Histogram Equalization."""
    category = "Enhance"

    def __init__(self):
        super().__init__("CLAHE", params={
            'clip_limit': {'type': 'float', 'value': 2.0, 'range': (0.1, 10.0)},
            'tile_size': {'type': 'int', 'value': 8, 'range': (2, 16)}
        })

    def process(self, input_data):
        img = input_data[0]
        clip_limit = self.get_parameter('clip_limit')
        tile_size = self.get_parameter('tile_size')

        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))

        if len(img.shape) == 2:
            return clahe.apply(img)
        else:
            lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)


class SharpenNode(Node):
    """Sharpen image details."""
    category = "Enhance"

    def __init__(self):
        super().__init__("Sharpen", params={
            'strength': {'type': 'float', 'value': 1.0, 'range': (0.1, 5.0)}
        })

    def process(self, input_data):
        img = input_data[0]
        strength = self.get_parameter('strength')
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(img, -1, kernel)
        return cv2.addWeighted(img, 1 - strength, sharpened, strength, 0)


# =============================================================================
# Blur & Denoise Category - Smoothing & Noise Reduction
# =============================================================================

class GaussianBlurNode(Node):
    """Apply Gaussian blur."""
    category = "Blur & Denoise"

    def __init__(self):
        super().__init__("Gaussian Blur", params={
            'kernel_size': {'type': 'int', 'value': 5, 'range': (1, 31), 'step': 2}
        })

    def process(self, input_data):
        img = input_data[0]
        ksize = self.get_parameter('kernel_size')
        return cv2.GaussianBlur(img, (ksize, ksize), 0)


class MedianBlurNode(Node):
    """Median blur for noise reduction."""
    category = "Blur & Denoise"

    def __init__(self):
        super().__init__("Median Blur", params={
            'kernel_size': {'type': 'int', 'value': 5, 'range': (3, 31), 'step': 2}
        })

    def process(self, input_data):
        img = input_data[0]
        ksize = self.get_parameter('kernel_size')
        return cv2.medianBlur(img, ksize)


class BilateralFilterNode(Node):
    """Bilateral filter for edge-preserving smoothing."""
    category = "Blur & Denoise"

    def __init__(self):
        super().__init__("Bilateral Filter", params={
            'd': {'type': 'int', 'value': 9, 'range': (1, 15)},
            'sigma_color': {'type': 'int', 'value': 75, 'range': (10, 200)},
            'sigma_space': {'type': 'int', 'value': 75, 'range': (10, 200)}
        })

    def process(self, input_data):
        img = input_data[0]
        d = self.get_parameter('d')
        sigma_color = self.get_parameter('sigma_color')
        sigma_space = self.get_parameter('sigma_space')
        return cv2.bilateralFilter(img, d, sigma_color, sigma_space)


# =============================================================================
# Edge & Contour Category - Edge Detection & Morphology
# =============================================================================

class CannyEdgeNode(Node):
    """Canny edge detection."""
    category = "Edge & Contour"

    def __init__(self):
        super().__init__("Canny Edge", params={
            'threshold1': {'type': 'int', 'value': 100, 'range': (0, 500)},
            'threshold2': {'type': 'int', 'value': 200, 'range': (0, 500)}
        })

    def process(self, input_data):
        img = input_data[0]
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        return cv2.Canny(img, self.get_parameter('threshold1'), self.get_parameter('threshold2'))


class ThresholdNode(Node):
    """Binary thresholding."""
    category = "Edge & Contour"

    def __init__(self):
        super().__init__("Threshold", params={
            'threshold': {'type': 'int', 'value': 127, 'range': (0, 255)},
            'max_value': {'type': 'int', 'value': 255, 'range': (0, 255)}
        })

    def process(self, input_data):
        img = input_data[0]
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, result = cv2.threshold(img, self.get_parameter('threshold'), self.get_parameter('max_value'), cv2.THRESH_BINARY)
        return result


class MorphologyNode(Node):
    """Morphological operations (erode, dilate, open, close)."""
    category = "Edge & Contour"

    def __init__(self):
        super().__init__("Morphology", params={
            'operation': {'type': 'int', 'value': 0, 'range': (0, 3)},
            # 0: Erode, 1: Dilate, 2: Open, 3: Close
            'kernel_size': {'type': 'int', 'value': 3, 'range': (1, 15), 'step': 2}
        })

    def process(self, input_data):
        img = input_data[0]
        op = self.get_parameter('operation')
        ksize = self.get_parameter('kernel_size')
        kernel = np.ones((ksize, ksize), np.uint8)

        operations = [
            cv2.MORPH_ERODE,
            cv2.MORPH_DILATE,
            cv2.MORPH_OPEN,
            cv2.MORPH_CLOSE
        ]

        return cv2.morphologyEx(img, operations[op], kernel)


# =============================================================================
# Transform Category - Geometric & Blending Operations
# =============================================================================

class ResizeNode(Node):
    """Resize image to specified dimensions."""
    category = "Transform"

    def __init__(self):
        super().__init__("Resize", params={
            'width': {'type': 'int', 'value': 512, 'range': (1, 4096)},
            'height': {'type': 'int', 'value': 512, 'range': (1, 4096)}
        })

    def process(self, input_data):
        return cv2.resize(input_data[0], (self.get_parameter('width'), self.get_parameter('height')), interpolation=cv2.INTER_AREA)


class MixNode(Node):
    """Mix/blend two images together."""
    category = "Transform"

    def __init__(self):
        super().__init__("Mix (Blend)", params={
            'factor': {'type': 'float', 'value': 0.5, 'range': (0.0, 1.0)}
        })
        self.max_inputs = 2

    def process(self, input_data):
        if len(input_data) < 2:
            return input_data[0] if input_data else None
        img1, img2 = input_data[0], input_data[1]
        h, w = img1.shape[:2]
        img2_resized = cv2.resize(img2, (w, h))
        return cv2.addWeighted(img1, 1.0 - self.get_parameter('factor'), img2_resized, self.get_parameter('factor'), 0)
