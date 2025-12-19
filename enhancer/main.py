import sys
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QComboBox, QFormLayout, QDoubleSpinBox,
    QSpinBox, QCheckBox, QLabel, QSplitter
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QThread, Signal

from .image_viewer import ImageViewer
from .processors import UnsharpMasking, DeepLearningEnhancer

class Worker(QThread):
    """
    Worker thread for running image processing tasks.
    """
    result_ready = Signal(np.ndarray)

    def __init__(self, processor, image, params):
        super().__init__()
        self.processor = processor
        self.image = image
        self.params = params

    def run(self):
        result = self.processor.process(self.image, self.params)
        self.result_ready.emit(result)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Photo Enhancer")
        self.setGeometry(100, 100, 1200, 600)

        self.original_image = None
        self.processed_image = None

        self.processors = {
            "Unsharp Masking": UnsharpMasking(),
            "Deep Learning Super Resolution (Dummy)": DeepLearningEnhancer()
        }

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # Image viewers
        self.original_viewer = ImageViewer()
        self.processed_viewer = ImageViewer()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.original_viewer)
        splitter.addWidget(self.processed_viewer)
        main_layout.addWidget(splitter, 4)

        # Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        main_layout.addWidget(controls_widget, 1)

        # File operations
        self.load_button = QPushButton("Load Image")
        self.load_button.clicked.connect(self.load_image)
        controls_layout.addWidget(self.load_button)

        self.save_button = QPushButton("Save Image")
        self.save_button.clicked.connect(self.save_image)
        controls_layout.addWidget(self.save_button)

        # Algorithm selection
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(self.processors.keys())
        self.algorithm_combo.currentTextChanged.connect(self.update_parameters_ui)
        controls_layout.addWidget(QLabel("Algorithm:"))
        controls_layout.addWidget(self.algorithm_combo)

        # Dynamic parameters UI
        self.parameters_widget = QWidget()
        self.parameters_layout = QFormLayout(self.parameters_widget)
        controls_layout.addWidget(self.parameters_widget)

        self.update_parameters_ui(self.algorithm_combo.currentText())

        # Process button
        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.process_image)
        controls_layout.addWidget(self.process_button)

        controls_layout.addStretch()

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_path:
            self.original_image = cv2.imread(file_path)
            self.display_image(self.original_image, self.original_viewer)

    def save_image(self):
        if self.processed_image is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Image (*.png)")
            if file_path:
                cv2.imwrite(file_path, self.processed_image)

    def display_image(self, image, viewer):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_image)
        viewer.set_image(pixmap)

    def update_parameters_ui(self, algorithm_name):
        # Clear old widgets
        for i in reversed(range(self.parameters_layout.count())):
            self.parameters_layout.itemAt(i).widget().setParent(None)

        processor = self.processors[algorithm_name]
        parameters = processor.get_parameters()
        self.parameter_widgets = {}

        for name, props in parameters.items():
            if props["type"] == "float":
                widget = QDoubleSpinBox()
                widget.setRange(props["range"][0], props["range"][1])
                widget.setValue(props["default"])
                widget.setSingleStep(0.1)
            elif props["type"] == "int":
                widget = QSpinBox()
                widget.setRange(props["range"][0], props["range"][1])
                widget.setValue(props["default"])
            elif props["type"] == "bool":
                widget = QCheckBox()
                widget.setChecked(props["default"])
            else: # string
                widget = QLabel(props["default"])

            self.parameters_layout.addRow(name, widget)
            self.parameter_widgets[name] = widget

    def process_image(self):
        if self.original_image is None:
            return

        algorithm_name = self.algorithm_combo.currentText()
        processor = self.processors[algorithm_name]
        params = {}
        for name, widget in self.parameter_widgets.items():
            if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                params[name] = widget.value()
            elif isinstance(widget, QCheckBox):
                params[name] = widget.isChecked()
            else:
                params[name] = widget.text()

        self.worker = Worker(processor, self.original_image, params)
        self.worker.result_ready.connect(self.on_processing_finished)
        self.worker.start()
        self.process_button.setText("Processing...")
        self.process_button.setEnabled(False)

    def on_processing_finished(self, result):
        self.processed_image = result
        self.display_image(self.processed_image, self.processed_viewer)
        self.process_button.setText("Process")
        self.process_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
