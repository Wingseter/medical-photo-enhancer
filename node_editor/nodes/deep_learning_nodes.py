import cv2
import numpy as np
import torch
from safetensors.torch import load_file
from node_editor.core.node_graph import Node

class SuperResolutionNode(Node):
    """
    A node for performing super-resolution using a PyTorch model
    loaded from a .safetensors file.
    """
    def __init__(self):
        super().__init__("Super Resolution", params={
            'model_path': {'type': 'filepath', 'value': ''}
        })
        self.model = None

    def load_model(self, model_path):
        """
_        Loads the model from the .safetensors file.
        This is a placeholder for a real model definition.
        """
        try:
            # In a real application, you would define your PyTorch model class here.
            # For example: class MySRModel(torch.nn.Module): ...
            # self.model = MySRModel()
            
            # For this example, we assume the safetensor file contains state for a simple
            # torch.nn.Conv2d layer as a placeholder.
            self.model = torch.nn.Conv2d(3, 3, 3, padding=1)
            
            state_dict = load_file(model_path)
            self.model.load_state_dict(state_dict)
            self.model.eval() # Set the model to evaluation mode
            print(f"Successfully loaded model from {model_path}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
            return False

    def process(self, input_data):
        img = input_data[0]
        model_path = self.get_parameter('model_path')

        if not model_path or self.model is None:
            # Attempt to load the model if the path is set but model isn't loaded
            if model_path and (self.model is None):
                if not self.load_model(model_path):
                    print("Model could not be loaded. Returning original image.")
                    return img
            else:
                print("Model path not set. Returning original image.")
                return img

        # 1. Preprocess: Convert NumPy array (H, W, C) to PyTorch tensor (B, C, H, W)
        img_tensor = torch.from_numpy(img).float().permute(2, 0, 1).unsqueeze(0) / 255.0

        # 2. Inference: Run the model
        with torch.no_grad():
            # The dummy model just applies a convolution. A real SR model would upscale.
            # We'll simulate upscaling with interpolate and then apply the conv.
            upscaled_tensor = torch.nn.functional.interpolate(img_tensor, scale_factor=2, mode='bicubic')
            output_tensor = self.model(upscaled_tensor)

        # 3. Postprocess: Convert back to NumPy array
        output_image = output_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
        output_image = np.clip(output_image * 255.0, 0, 255).astype(np.uint8)

        return output_image