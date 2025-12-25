from node_editor.core.node_graph import Node
import numpy as np

class StableDiffusionx4UpscalerNode(Node):
    category = "AI / Machine Learning"

    def __init__(self):
        super().__init__(name="SD x4 Upscaler", params={})
        self.pipeline = None

    def process(self, input_data):
        if not input_data:
            return None
            
        image = input_data[0]
        if image is None:
            return None

        if self.pipeline is None:
            from diffusers import StableDiffusionUpscalePipeline
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
            torch_dtype = torch.float16 if device != "cpu" else torch.float32

            self.pipeline = StableDiffusionUpscalePipeline.from_pretrained(
                "stabilityai/stable-diffusion-x4-upscaler",
                torch_dtype=torch_dtype
            )
            self.pipeline = self.pipeline.to(device)

        # The upscaler pipeline expects a PIL image
        from PIL import Image
        pil_image = Image.fromarray(image)
        
        upscaled_image = self.pipeline(prompt="", image=pil_image).images[0]
        
        return np.array(upscaled_image)