# GEMINI.md

## Project Overview

This project aims to create a modular and extensible image enhancement application using Python and the PySide6 GUI framework. The application will allow users to load images, apply various enhancement algorithms (from classical techniques to deep learning models), and view the results in a user-friendly interface.

The core of the application is a custom image viewer built with `QGraphicsView` that supports panning and zooming. The image processing algorithms are designed using the Strategy Pattern, allowing for easy addition and removal of new algorithms. The UI for algorithm parameters is generated dynamically based on the selected algorithm's requirements.

The project will also include a deep learning integration example, demonstrating how to load and use `.safetensors` models for image enhancement tasks. This will be handled in a separate thread to avoid blocking the GUI.

## Key Technologies

*   **GUI:** PySide6
*   **Image Processing:** OpenCV, PyTorch (or ONNX)
*   **Core Libraries:** NumPy

## Building and Running

### Prerequisites

*   Python 3.8+
*   PySide6
*   OpenCV-Python
*   NumPy
*   PyTorch (or onnxruntime)

### Installation

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

### Running the Application

To run the application, execute the following command in your terminal:

```bash
python -m enhancer.main
```

## Project Structure

```
.
├── enhancer
│   ├── __init__.py
│   ├── main.py               # Main application window
│   ├── image_viewer.py       # Custom QGraphicsView for image display
│   └── processors
│       ├── __init__.py
│       ├── base_processor.py   # Abstract base class for image processors
│       ├── unsharp_masking.py  # Unsharp Masking algorithm
│       └── deep_learning.py    # Dummy deep learning enhancer
└── requirements.txt
```

## Development Conventions

*   **Code Style:** The project will follow the PEP 8 style guide for Python code.
*   **Modularity:** The application is designed to be modular, with clear separation of concerns between the GUI, image processing logic, and data models.
*   **Testing:** Unit tests will be added to ensure the correctness of the image processing algorithms and other critical components.
*   **Contributions:** Contributions are welcome. Please follow the existing coding style and submit a pull request with your changes.
