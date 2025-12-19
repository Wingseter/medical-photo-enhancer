import cv2
import numpy as np
from .base_processor import ImageProcessor

class UnsharpMasking(ImageProcessor):
    """
    Implements the Unsharp Masking algorithm using OpenCV.
    """
    @property
    def name(self):
        return "Unsharp Masking"

    def get_parameters(self):
        return {
            "amount": {"type": "float", "default": 1.0, "range": (0.0, 2.0)},
            "kernel_size": {"type": "int", "default": 3, "range": (1, 15)}
        }

    def process(self, image, params):
        amount = params["amount"]
        kernel_size = int(params["kernel_size"])
        if kernel_size % 2 == 0:
            kernel_size += 1

        blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        sharpened = cv2.addWeighted(image, 1.0 + amount, blurred, -amount, 0)
        return sharpened
