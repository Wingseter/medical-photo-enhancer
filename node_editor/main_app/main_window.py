import cv2
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QListWidget, QListWidgetItem, 
    QDockWidget, QLabel, QFormLayout, QDoubleSpinBox, QSpinBox, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QImage, QIcon

from node_editor.core.node_graph import NodeGraph
from node_editor.nodes import NODE_TYPES
from node_editor.widgets.node_items import NodeWidget
from node_editor.widgets.node_editor_scene import NodeEditorScene
from node_editor.widgets.node_editor_view import NodeEditorView
from node_editor.main_app.worker import GraphExecutionWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Node-Based Image Processor"); self.setGeometry(100, 100, 1600, 900)
        
        self.graph = NodeGraph()
        self.scene = NodeEditorScene(self)
        self.view = NodeEditorView(self.scene)
        self.setCentralWidget(self.view)
        
        self.current_selected_node_id = None
        self.worker = None
        
        self.create_docks()
        
    def create_docks(self):
        node_list_dock = QDockWidget("Nodes", self)
        self.node_list_widget = QListWidget()
        
        self.node_icon_map = {
            "Input": "node_editor/icons/image.svg",
            "Output": "node_editor/icons/eye.svg",
        }

        for node_name in sorted(NODE_TYPES.keys()):
            item = QListWidgetItem(node_name)
            if node_name in self.node_icon_map:
                item.setIcon(QIcon(self.node_icon_map[node_name]))
            self.node_list_widget.addItem(item)
            
        self.node_list_widget.itemDoubleClicked.connect(self.add_node_from_list)
        node_list_dock.setWidget(self.node_list_widget); self.addDockWidget(Qt.LeftDockWidgetArea, node_list_dock)

        properties_dock = QDockWidget("Properties", self)
        properties_dock.setFixedWidth(300) # Set a fixed width for the properties dock
        properties_container_widget = QWidget()
        properties_container_layout = QVBoxLayout(properties_container_widget)
        
        self.properties_widget = QWidget()
        self.properties_layout = QFormLayout(self.properties_widget)
        self.properties_layout.setContentsMargins(5, 5, 5, 5)
        self.properties_layout.setVerticalSpacing(10)
        
        properties_container_layout.addWidget(self.properties_widget)
        properties_container_layout.addStretch(1)
        
        properties_dock.setWidget(properties_container_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, properties_dock)

        
        viewer_dock = QDockWidget("Viewer", self)
        self.viewer_label = QLabel("Select a node and press 'Run / Update'"); self.viewer_label.setAlignment(Qt.AlignCenter)
        viewer_dock.setWidget(self.viewer_label); self.addDockWidget(Qt.RightDockWidgetArea, viewer_dock)

        control_dock = QDockWidget("Controls", self)
        control_widget = QWidget(); control_layout = QVBoxLayout(control_widget)
        self.run_button = QPushButton("Run / Update"); self.run_button.clicked.connect(self.execute_graph_threaded)
        self.run_button.setIcon(QIcon("node_editor/icons/play.svg"))
        control_layout.addWidget(self.run_button); control_dock.setWidget(control_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, control_dock)

    @Slot(QListWidgetItem)
    def add_node_from_list(self, item):
        node_name = item.text()
        node_class = NODE_TYPES[node_name]
        node = self.graph.add_node(node_class)
        widget = NodeWidget(node.id, node_name)
        widget.setPos(self.view.mapToScene(self.view.viewport().rect().center()))
        widget.node_selected.connect(self.on_node_selected)
        self.scene.addItem(widget)

    @Slot(str)
    def on_node_selected(self, node_id):
        if self.current_selected_node_id != node_id:
            self.current_selected_node_id = node_id
            self.update_properties_panel()

    def update_properties_panel(self):
        # Clear existing widgets
        while self.properties_layout.count():
            item = self.properties_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        node = self.graph.get_node(self.current_selected_node_id)
        if not node: return

        # Add parameter controls
        for name, props in node.parameters.items():
            if props['type'] == 'filepath':
                button = QPushButton(str(props['value']) or "Select File...")
                button.clicked.connect(lambda _, n=node, p=name: self.select_file(n, p))
                self.properties_layout.addRow(name, button)
            elif props['type'] == 'int':
                widget = QSpinBox()
                if 'range' in props: widget.setRange(*props['range'])
                if 'step' in props: widget.setSingleStep(props['step'])
                widget.setValue(props['value'])
                widget.valueChanged.connect(lambda v, n=node, p=name: n.set_parameter(p, v))
                self.properties_layout.addRow(name, widget)
            elif props['type'] == 'float':
                widget = QDoubleSpinBox()
                if 'range' in props: widget.setRange(*props['range'])
                widget.setValue(props['value'])
                widget.valueChanged.connect(lambda v, n=node, p=name: n.set_parameter(p, v))
                self.properties_layout.addRow(name, widget)

        # Add Save Image button
        self.properties_layout.addRow(QWidget()) # Spacer
        save_button = QPushButton("Save Image")
        save_button.setIcon(QIcon("node_editor/icons/save.svg"))
        save_button.clicked.connect(self.save_node_output)
        is_cached = node.cached_data is not None
        save_button.setEnabled(is_cached)
        if not is_cached:
            save_button.setToolTip("Run the node first to enable saving.")
        self.properties_layout.addRow(save_button)


    def select_file(self, node, param_name):
        current_val = node.get_parameter(param_name)
        filepath, _ = QFileDialog.getOpenFileName(self, "Select File", str(current_val), "Files (*.png *.jpg *.bmp *.safetensors)")
        if filepath: 
            node.set_parameter(param_name, filepath)
            self.update_properties_panel()

    def save_node_output(self):
        node = self.graph.get_node(self.current_selected_node_id)
        if node and node.cached_data is not None:
            filepath, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Image (*.png);;JPG Image (*.jpg)")
            if filepath:
                image = node.cached_data
                # Convert RGB (internal) to BGR (for OpenCV) before saving
                if len(image.shape) == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(filepath, image)
                print(f"Saved output of node {node.name} to {filepath}")

    def execute_graph_threaded(self):
        if not self.current_selected_node_id:
            QMessageBox.warning(self, "Warning", "No node selected to execute.")
            return

        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        self.run_button.setText("Processing...")
        self.run_button.setEnabled(False)
        
        self.worker = GraphExecutionWorker(self.graph, self.current_selected_node_id)
        self.worker.result_ready.connect(self.on_execution_finished)
        self.worker.error_occurred.connect(self.on_execution_error)
        self.worker.start()

    def on_execution_finished(self, result_image):
        self.run_button.setText("Run / Update")
        self.run_button.setEnabled(True)
        self.display_image(result_image)
        # Refresh properties to enable the save button
        self.update_properties_panel()

    def on_execution_error(self, error_msg):
        self.run_button.setText("Run / Update")
        self.run_button.setEnabled(True)
        QMessageBox.critical(self, "Execution Error", error_msg)
        self.display_image(None)

    def display_image(self, np_image):
        if np_image is None: 
            self.viewer_label.setText("Processing failed or no output.")
            return
        
        h, w = np_image.shape[:2]
        # Handle grayscale vs color images
        bytes_per_line = w * (1 if len(np_image.shape) == 2 else 3)
        fmt = QImage.Format_Grayscale8 if len(np_image.shape) == 2 else QImage.Format_RGB888
        
        q_image = QImage(np_image.data, w, h, bytes_per_line, fmt)
        self.viewer_label.setPixmap(QPixmap.fromImage(q_image).scaled(self.viewer_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def closeEvent(self, event):
        # Ensure worker thread is cleaned up when closing the app
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()