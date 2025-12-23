# GEMINI.md

## Project Overview

This project implements a Node-Based Image Processing Application using PySide6 and OpenCV. Users can visually construct image processing pipelines by connecting nodes in a graph editor. Key features include:

*   **Smart Caching (DAG):** Optimizes computations by only re-executing nodes whose inputs or parameters have changed, leveraging a Directed Acyclic Graph (DAG) structure.
*   **Extensible Node System:** Easily add new image processing algorithms as independent nodes.
*   **Custom GUI (QGraphicsView):** An interactive node editor allowing drag-and-drop node placement, connection drawing, and dynamic parameter editing via a properties panel.
*   **Viewer:** A dedicated panel to display the output of any selected node.

## Key Technologies

*   **GUI:** PySide6
*   **Image Processing:** OpenCV, NumPy

## Building and Running

### Prerequisites

*   Python 3.8+
*   PySide6
*   OpenCV-Python
*   NumPy

### Installation

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

### Running the Application

To run the application, execute the following command in your terminal:

```bash
python main.py
```

## Project Structure

```
.
├── main.py                               # Application entry point
├── requirements.txt                      # Project dependencies
└── node_editor/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   └── node_graph.py                 # Core Node and NodeGraph logic (DAG, caching)
    ├── nodes/
    │   ├── __init__.py                   # Aggregates all node types into NODE_TYPES dictionary
    │   ├── base_nodes.py                 # InputNode, OutputNode
    │   ├── opencv_nodes.py               # GaussianBlurNode, SharpenNode, GrayscaleNode, etc.
    │   └── deep_learning_nodes.py        # Dummy DeepLearningNode
    ├── widgets/
    │   ├── __init__.py
    │   ├── node_items.py                 # QGraphicsObject for NodePort, NodeWidget, EdgeWidget
    │   ├── node_editor_view.py           # QGraphicsView with zoom/pan functionality
    │   └── node_editor_scene.py          # QGraphicsScene for managing nodes and connections
    └── main_app/
        ├── __init__.py
        └── main_window.py                # Main application window, docks, and UI connections
```

## Development Conventions

*   **Code Style:** The project will follow the PEP 8 style guide for Python code.
*   **Modularity:** The application is designed to be highly modular, with clear separation of concerns between core logic, algorithms, and GUI components.
*   **Testing:** Unit tests will be added in future iterations to ensure the correctness of the node processing logic and graph operations.
*   **Contributions:** Contributions are welcome. Please follow the existing coding style and submit a pull request with your changes.