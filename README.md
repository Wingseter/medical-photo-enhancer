# Node-Based Image Processor

A visual node-based image processing application built with Python and PySide6. Create image processing workflows by connecting nodes, save them for reuse, and batch process multiple images.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-red.svg)

## Features

### Node Editor
- **Visual Programming**: Create image processing pipelines by connecting nodes
- **Real-time Preview**: See results instantly in the Output node
- **Drag & Drop**: Intuitive node placement and connection
- **Resizable Nodes**: Adjust node size by dragging edges
- **Embedded Parameters**: Edit node settings directly within the node

### Workflow System
- **Save Workflows**: Save your node graphs as reusable JSON workflows
- **Thumbnail Preview**: Workflows include a preview thumbnail
- **Workflow Library**: Browse and manage saved workflows

### Batch Processing
- **Multiple Images**: Process entire folders of images with one workflow
- **Progress Tracking**: Real-time progress bar with percentage
- **Result Gallery**: Preview all processed images in a grid

### Image Compare
- **Side-by-Side Comparison**: Compare two images simultaneously
- **Synchronized Zoom**: Both views zoom and pan together
- **Minimap Navigation**: Click on minimap to navigate large images
- **Difference Detection**: Find and highlight pixel differences between images

### Detachable Tabs
- **Multi-Tab Interface**: Switch between Runner, Editor, and Compare tabs
- **Detach Tabs**: Drag tabs out to create separate windows
- **Merge Back**: Close detached windows to return tabs

## Available Nodes

### Basic I/O
| Node | Description |
|------|-------------|
| Input | Load an image from file |
| Output | Display final result with save option |

### Color
| Node | Description |
|------|-------------|
| Grayscale | Convert to grayscale |
| Color Convert | RGB ↔ HSV/LAB/YCrCb/BGR |
| Hue/Saturation | Adjust hue and saturation |
| Brightness/Contrast | Adjust brightness and contrast |
| Invert | Invert image colors |

### Enhance
| Node | Description |
|------|-------------|
| CLAHE | Adaptive histogram equalization |
| Equalize Hist | Histogram equalization |
| Sharpen | Sharpen image details |

### Blur & Denoise
| Node | Description |
|------|-------------|
| Gaussian Blur | Apply Gaussian blur |
| Median Blur | Noise reduction with median filter |
| Bilateral Filter | Edge-preserving smoothing |

### Edge & Contour
| Node | Description |
|------|-------------|
| Canny Edge | Canny edge detection |
| Threshold | Binary thresholding |
| Morphology | Erode/Dilate/Open/Close operations |

### Transform
| Node | Description |
|------|-------------|
| Resize | Resize to specified dimensions |
| Mix (Blend) | Blend two images together |

### AI / Machine Learning
| Node | Description |
|------|-------------|
| Super Resolution | Upscale using custom model (.safetensors) |
| SD x4 Upscaler | 4x upscale using Stable Diffusion |

## Installation

### Requirements
- Python 3.10 or higher
- CUDA-compatible GPU (recommended for AI nodes)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/node-image-processor.git
cd node-image-processor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```
PySide6
numpy
opencv-python
safetensors
torch
diffusers
transformers
accelerate
realesrgan
```

## Usage

### Start the Application

```bash
python main.py
```

### Quick Start

1. **Create a Workflow**
   - Go to the "Node Editor" tab
   - Add an Input node and select an image
   - Add processing nodes (e.g., CLAHE, Sharpen)
   - Connect nodes by dragging from output port to input port
   - Add an Output node to see the result
   - Click "Save Workflow" to save

2. **Run a Workflow**
   - Go to the "Workflow Runner" tab
   - Select a workflow from the left panel
   - Add images using "Add Files" or "Add Folder"
   - Choose an output directory
   - Click "Run Workflow"

3. **Compare Images**
   - Go to the "Image Compare" tab
   - Load two images
   - Use the minimap to navigate
   - Click "Find Differences" to highlight changes

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+1` | Switch to Workflow Runner |
| `Ctrl+2` | Switch to Node Editor |
| `Ctrl+3` | Switch to Image Compare |
| `Ctrl+N` | New Workflow |
| `Ctrl+Q` | Quit Application |
| `Delete` | Delete selected nodes/connections |

## Project Structure

```
node-image-processor/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md
└── node_editor/
    ├── core/
    │   ├── node_graph.py       # Graph execution engine
    │   └── workflow_manager.py # Workflow save/load
    ├── main_app/
    │   ├── main_window.py      # Main window with tabs
    │   ├── editor_page.py      # Node editor page
    │   ├── runner_page.py      # Workflow runner page
    │   ├── compare_page.py     # Image compare page
    │   ├── tab_container.py    # Detachable tabs
    │   ├── batch_worker.py     # Batch processing thread
    │   ├── worker.py           # Single image worker
    │   └── stylesheet.py       # Application styles
    ├── nodes/
    │   ├── __init__.py         # Auto node registration
    │   ├── base_nodes.py       # Input/Output nodes
    │   ├── opencv_nodes.py     # OpenCV-based nodes
    │   ├── deep_learning_nodes.py
    │   └── huggingface_nodes.py
    ├── widgets/
    │   ├── node_items.py       # Node UI components
    │   ├── node_editor_scene.py
    │   ├── node_editor_view.py
    │   ├── node_palette.py     # Node selection panel
    │   ├── workflow_card.py    # Workflow thumbnail card
    │   ├── image_selector.py   # Batch image selector
    │   └── preview_gallery.py  # Result preview grid
    ├── icons/                  # SVG icons
    ├── fonts/                  # Inter font
    └── workflows/              # Saved workflows
```

## Adding Custom Nodes

Create a new Python file in `node_editor/nodes/` with your node class:

```python
from node_editor.core.node_graph import Node

class MyCustomNode(Node):
    category = "My Category"  # Category in the palette

    def __init__(self):
        super().__init__("My Node Name", params={
            'param1': {'type': 'int', 'value': 10, 'range': (0, 100)},
            'param2': {'type': 'float', 'value': 0.5, 'range': (0.0, 1.0)}
        })

    def process(self, input_data):
        img = input_data[0]
        param1 = self.get_parameter('param1')
        param2 = self.get_parameter('param2')

        # Your image processing logic here
        result = img  # Process the image

        return result
```

The node will be automatically registered on application startup.

### Parameter Types

| Type | Description | Example |
|------|-------------|---------|
| `int` | Integer slider | `{'type': 'int', 'value': 5, 'range': (0, 10)}` |
| `float` | Float slider | `{'type': 'float', 'value': 0.5, 'range': (0.0, 1.0)}` |
| `filepath` | File picker | `{'type': 'filepath', 'value': ''}` |

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
