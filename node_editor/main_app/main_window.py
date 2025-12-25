import cv2
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QDockWidget, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QImage, QIcon, QAction

from node_editor.core.node_graph import NodeGraph
from node_editor.nodes import NODE_TYPES, NODE_CATEGORIES
from node_editor.widgets.node_items import NodeWidget
from node_editor.widgets.node_editor_scene import NodeEditorScene
from node_editor.widgets.node_editor_view import NodeEditorView
from node_editor.widgets.node_palette import NodePalette
from node_editor.widgets.loading_overlay import LoadingOverlay
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
        self.create_menus()

        # Loading overlay (must be created after central widget is set)
        self.loading_overlay = LoadingOverlay(self.view)
        self.loading_overlay.setGeometry(self.view.rect())
        
    def create_docks(self):
        # Node palette with categories and search
        self.node_list_dock = QDockWidget("Nodes", self)
        self.node_palette = NodePalette(NODE_CATEGORIES)
        self.node_palette.node_double_clicked.connect(self.add_node_by_name)
        self.node_list_dock.setWidget(self.node_palette)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.node_list_dock)

        # Controls dock
        self.control_dock = QDockWidget("Controls", self)
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        self.run_button = QPushButton("Run / Update")
        self.run_button.clicked.connect(self.execute_graph_threaded)
        self.run_button.setIcon(QIcon("node_editor/icons/play.svg"))
        control_layout.addWidget(self.run_button)
        self.control_dock.setWidget(control_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.control_dock)

    def create_menus(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction(self.node_list_dock.toggleViewAction())
        view_menu.addAction(self.control_dock.toggleViewAction())

    @Slot(str)
    def add_node_by_name(self, node_name):
        """Add a node to the graph by its name."""
        node_class = NODE_TYPES[node_name]
        node = self.graph.add_node(node_class)
        category = getattr(node_class, 'category', 'Uncategorized')
        is_output = (node_name == "Output")
        widget = NodeWidget(node.id, node_name, category, parameters=node.parameters, is_output_node=is_output)
        widget.setPos(self.view.mapToScene(self.view.viewport().rect().center()))
        widget.node_selected.connect(self.on_node_selected)
        widget.parameter_changed.connect(self.on_parameter_changed)
        widget.file_select_requested.connect(self.on_file_select_requested)
        if is_output:
            widget.save_requested.connect(self.save_node_output)
        self.scene.addItem(widget)

    @Slot(str, str, object)
    def on_parameter_changed(self, node_id, param_name, value):
        """Handle parameter changes from embedded widgets."""
        node = self.graph.get_node(node_id)
        if node:
            node.set_parameter(param_name, value)

    @Slot(str, str)
    def on_file_select_requested(self, node_id, param_name):
        """Handle file selection requests from embedded widgets."""
        node = self.graph.get_node(node_id)
        if node:
            current_val = node.get_parameter(param_name) or ""
            filepath, _ = QFileDialog.getOpenFileName(
                self, "Select File", str(current_val),
                "Image Files (*.png *.jpg *.bmp);;All Files (*.*)"
            )
            if filepath:
                node.set_parameter(param_name, filepath)
                # Update the widget's display
                for item in self.scene.items():
                    if isinstance(item, NodeWidget) and item.node_id == node_id:
                        item.update_filepath_display(param_name, filepath)
                        break

    @Slot(str)
    def on_node_selected(self, node_id):
        self.current_selected_node_id = node_id

    @Slot(str)
    def save_node_output(self, node_id):
        """Save the output of a node to a file."""
        node = self.graph.get_node(node_id)
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

        # Show loading overlay
        self.loading_overlay.show_loading("Preparing execution...", "Analyzing node graph")
        self.run_button.setEnabled(False)

        self.worker = GraphExecutionWorker(self.graph, self.current_selected_node_id)
        self.worker.result_ready.connect(self.on_execution_finished)
        self.worker.error_occurred.connect(self.on_execution_error)
        self.worker.progress_update.connect(self._on_progress_update)
        self.worker.start()

    @Slot(str, str, int)
    def _on_progress_update(self, message, detail, percent):
        self.loading_overlay.set_message(message)
        self.loading_overlay.set_detail(detail)
        self.loading_overlay.set_progress(percent)

    def on_execution_finished(self, result_image):
        self.loading_overlay.hide_loading()
        self.run_button.setEnabled(True)
        # Update the Output node's preview
        self._update_output_node_preview(result_image)

    def on_execution_error(self, error_msg):
        self.loading_overlay.hide_loading()
        self.run_button.setEnabled(True)
        QMessageBox.critical(self, "Execution Error", error_msg)

    def _update_output_node_preview(self, np_image):
        """Update the preview image in the executed Output node."""
        if np_image is None:
            return
        # Find the Output node widget that was executed
        for item in self.scene.items():
            if isinstance(item, NodeWidget) and item.node_id == self.current_selected_node_id:
                item.set_preview_image(np_image)
                break

    def resizeEvent(self, event):
        """Ensure overlay covers the entire view."""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.view.rect())

    def closeEvent(self, event):
        # Ensure worker thread is cleaned up when closing the app
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()