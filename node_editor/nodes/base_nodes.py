import cv2
import numpy as np
from node_editor.core.node_graph import Node

class InputNode(Node):
    def __init__(self):
        super().__init__("Input", params={'filepath': {'type': 'filepath', 'value': ''}})
    def process(self, input_data):
        filepath = self.get_parameter('filepath')
        if filepath and isinstance(filepath, str):
            img = cv2.imread(filepath, cv2.IMREAD_COLOR)
            if img is None:
                print(f"Error: Could not load image from {filepath}")
                return None
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return None

class OutputNode(Node):
    def __init__(self): super().__init__("Output")
    def process(self, input_data): return input_data[0] if input_data else None
