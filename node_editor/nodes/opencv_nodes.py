import cv2
import numpy as np
from node_editor.core.node_graph import Node

class GaussianBlurNode(Node):
    def __init__(self):
        super().__init__("GaussianBlur", params={'kernel_size': {'type': 'int', 'value': 5, 'range': (1, 31), 'step': 2}})
    def process(self, input_data):
        img = input_data[0]
        ksize = self.get_parameter('kernel_size')
        return cv2.GaussianBlur(img, (ksize, ksize), 0)

class SharpenNode(Node):
    def __init__(self):
        super().__init__("Sharpen", params={'strength': {'type': 'float', 'value': 1.0, 'range': (0.1, 5.0)}})
    def process(self, input_data):
        img, strength = input_data[0], self.get_parameter('strength')
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(img, -1, kernel)
        return cv2.addWeighted(img, 1 - strength, sharpened, strength, 0)

class GrayscaleNode(Node):
    def __init__(self): super().__init__("Grayscale")
    def process(self, input_data):
        img = input_data[0]
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if len(img.shape) == 3 else img

class BrightnessContrastNode(Node):
    def __init__(self): super().__init__("Brightness/Contrast", params={'brightness': {'type': 'int', 'value': 0, 'range': (-100, 100)}, 'contrast': {'type': 'float', 'value': 1.0, 'range': (0.1, 3.0)}})
    def process(self, input_data):
        img = input_data[0].astype(np.float32)
        brightness, contrast = self.get_parameter('brightness'), self.get_parameter('contrast')
        return np.clip(img * contrast + brightness, 0, 255).astype(np.uint8)

class CannyEdgeNode(Node):
    def __init__(self): super().__init__("CannyEdge", params={'threshold1': {'type': 'int', 'value': 100, 'range': (0, 500)}, 'threshold2': {'type': 'int', 'value': 200, 'range': (0, 500)}})
    def process(self, input_data):
        img = input_data[0]
        if len(img.shape) > 2: img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        return cv2.Canny(img, self.get_parameter('threshold1'), self.get_parameter('threshold2'))

class ThresholdNode(Node):
    def __init__(self): super().__init__("Threshold", params={'threshold': {'type': 'int', 'value': 127, 'range': (0, 255)}, 'max_value': {'type': 'int', 'value': 255, 'range': (0, 255)}})
    def process(self, input_data):
        img = input_data[0]
        if len(img.shape) > 2: img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, result = cv2.threshold(img, self.get_parameter('threshold'), self.get_parameter('max_value'), cv2.THRESH_BINARY)
        return result

class HueSaturationNode(Node):
    def __init__(self): super().__init__("Hue/Saturation", params={'hue': {'type': 'int', 'value': 0, 'range': (-90, 90)}, 'saturation': {'type': 'float', 'value': 1.0, 'range': (0.0, 2.0)}})
    def process(self, input_data):
        hsv = cv2.cvtColor(input_data[0], cv2.COLOR_RGB2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        h = (h + self.get_parameter('hue')) % 180
        s = np.clip(s * self.get_parameter('saturation'), 0, 255)
        final_hsv = cv2.merge([h, s, v])
        return cv2.cvtColor(final_hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

class ResizeNode(Node):
    def __init__(self): super().__init__("Resize", params={'width': {'type': 'int', 'value': 512, 'range': (1, 4096)}, 'height': {'type': 'int', 'value': 512, 'range': (1, 4096)}})
    def process(self, input_data):
        return cv2.resize(input_data[0], (self.get_parameter('width'), self.get_parameter('height')), interpolation=cv2.INTER_AREA)

class InvertNode(Node):
    def __init__(self): super().__init__("Invert")
    def process(self, input_data): return cv2.bitwise_not(input_data[0])

class MixNode(Node):
    def __init__(self):
        super().__init__("Mix (Overlay)", params={'factor': {'type': 'float', 'value': 0.5, 'range': (0.0, 1.0)}})
        self.max_inputs = 2
    def process(self, input_data):
        if len(input_data) < 2: return input_data[0] if input_data else None
        img1, img2 = input_data[0], input_data[1]
        h, w, _ = img1.shape
        img2_resized = cv2.resize(img2, (w, h))
        return cv2.addWeighted(img1, 1.0 - self.get_parameter('factor'), img2_resized, self.get_parameter('factor'), 0)
