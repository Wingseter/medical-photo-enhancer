"""
Node Editor Page - The graph canvas for creating and editing workflows.
"""
import cv2
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QMessageBox, QSplitter, QInputDialog, QFrame
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QIcon

from node_editor.core.node_graph import NodeGraph
from node_editor.core.workflow_manager import WorkflowManager
from node_editor.nodes import NODE_TYPES, NODE_CATEGORIES
from node_editor.widgets.node_items import NodeWidget, EdgeWidget
from node_editor.widgets.node_editor_scene import NodeEditorScene
from node_editor.widgets.node_editor_view import NodeEditorView
from node_editor.widgets.node_palette import NodePalette
from node_editor.widgets.loading_overlay import LoadingOverlay
from node_editor.main_app.worker import GraphExecutionWorker


class NodeEditorPage(QWidget):
    """The node editor page containing the graph canvas and controls."""

    workflow_saved = Signal()  # Emitted when a workflow is saved

    def __init__(self, parent=None):
        super().__init__(parent)

        self.graph = NodeGraph()
        self.workflow_manager = WorkflowManager()
        self.scene = NodeEditorScene(self)
        self.view = NodeEditorView(self.scene)
        self.current_selected_node_id = None
        self.worker = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create splitter for palette | canvas | controls
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel: Node palette
        left_panel = self._create_palette_panel()
        splitter.addWidget(left_panel)

        # Center: Canvas
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.addWidget(self.view)
        splitter.addWidget(canvas_container)

        # Loading overlay
        self.loading_overlay = LoadingOverlay(self.view)
        self.loading_overlay.setGeometry(self.view.rect())

        # Right panel: Controls
        right_panel = self._create_controls_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([220, 1000, 180])

    def _create_palette_panel(self):
        """Create the left-side node palette panel."""
        panel = QFrame()
        panel.setMinimumWidth(200)
        panel.setMaximumWidth(300)
        panel.setStyleSheet("QFrame { background: #2A2A2A; }")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        self.node_palette = NodePalette(NODE_CATEGORIES)
        self.node_palette.node_double_clicked.connect(self.add_node_by_name)
        layout.addWidget(self.node_palette)

        return panel

    def _create_controls_panel(self):
        """Create the right-side controls panel."""
        panel = QFrame()
        panel.setMinimumWidth(150)
        panel.setMaximumWidth(220)
        panel.setStyleSheet("QFrame { background: #2A2A2A; }")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Run section
        run_label = QLabel("Execution")
        run_label.setStyleSheet("font-weight: bold; color: #E0E0E0;")
        layout.addWidget(run_label)

        self.run_button = QPushButton("Run / Update")
        self.run_button.setIcon(QIcon("node_editor/icons/play.svg"))
        self.run_button.clicked.connect(self.execute_graph_threaded)
        self.run_button.setStyleSheet("""
            QPushButton {
                background: #2D7D46;
                padding: 10px;
                font-size: 13px;
            }
            QPushButton:hover { background: #3D8D56; }
            QPushButton:disabled { background: #555; }
        """)
        layout.addWidget(self.run_button)

        layout.addSpacing(20)

        # Workflow section
        workflow_label = QLabel("Workflow")
        workflow_label.setStyleSheet("font-weight: bold; color: #E0E0E0;")
        layout.addWidget(workflow_label)

        self.save_workflow_btn = QPushButton("Save Workflow")
        self.save_workflow_btn.clicked.connect(self._save_current_workflow)
        layout.addWidget(self.save_workflow_btn)

        self.load_workflow_btn = QPushButton("Load Workflow")
        self.load_workflow_btn.clicked.connect(self._load_workflow)
        layout.addWidget(self.load_workflow_btn)

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self._clear_graph)
        layout.addWidget(self.clear_btn)

        layout.addStretch()

        return panel

    def _get_node_widgets_map(self):
        """Get a dict mapping node_id to NodeWidget."""
        widgets = {}
        for item in self.scene.items():
            if isinstance(item, NodeWidget):
                widgets[item.node_id] = item
        return widgets

    def _save_current_workflow(self):
        """Save the current graph as a workflow."""
        if not self.graph.nodes:
            QMessageBox.warning(self, "Warning", "No nodes to save.")
            return

        name, ok = QInputDialog.getText(
            self, "Save Workflow", "Workflow name:"
        )

        if ok and name:
            description, _ = QInputDialog.getText(
                self, "Save Workflow", "Description (optional):"
            )

            # Generate thumbnail from current view
            thumbnail = self.view.grab().scaled(200, 150, Qt.KeepAspectRatio)

            try:
                filepath = self.workflow_manager.save_workflow(
                    name=name,
                    graph=self.graph,
                    node_widgets=self._get_node_widgets_map(),
                    description=description,
                    thumbnail=thumbnail
                )
                QMessageBox.information(
                    self, "Success", f"Workflow saved:\n{filepath}"
                )
                self.workflow_saved.emit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save workflow:\n{e}")

    def _load_workflow(self):
        """Load a workflow from file."""
        workflows_dir = str(self.workflow_manager.workflows_dir)
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Workflow", workflows_dir,
            "Workflow Files (*.json)"
        )

        if filepath:
            self.load_workflow_from_file(filepath)

    def load_workflow_from_file(self, filepath: str):
        """Load and recreate graph from workflow file."""
        try:
            workflow_data = self.workflow_manager.load_workflow(filepath)
            self._recreate_from_workflow(workflow_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load workflow:\n{e}")

    def _recreate_from_workflow(self, workflow_data: dict):
        """Recreate the scene from workflow data."""
        # Clear current scene
        self.scene.clear()

        # Recreate graph
        id_mapping = self.graph.recreate_from_workflow(workflow_data, NODE_TYPES)

        # Recreate visual widgets
        for node_data in workflow_data.get('nodes', []):
            old_id = node_data['id']
            new_id = id_mapping.get(old_id)

            if not new_id:
                continue

            node = self.graph.get_node(new_id)
            if not node:
                continue

            node_class = NODE_TYPES.get(node.name)
            category = getattr(node_class, 'category', 'Uncategorized')
            is_output = (node.name == "Output")

            widget = NodeWidget(
                new_id, node.name, category,
                parameters=node.parameters,
                is_output_node=is_output
            )

            pos = node_data.get('position', {'x': 0, 'y': 0})
            widget.setPos(pos['x'], pos['y'])

            # Restore size if available
            size = node_data.get('size')
            if size:
                widget.set_size(size.get('width', 180), size.get('height', 100))

            widget.node_selected.connect(self.on_node_selected)
            widget.parameter_changed.connect(self.on_parameter_changed)
            widget.file_select_requested.connect(self.on_file_select_requested)

            if is_output:
                widget.save_requested.connect(self.save_node_output)

            self.scene.addItem(widget)

        # Build a map from new_id to widget for edge creation
        widget_map = self._get_node_widgets_map()

        # Recreate edges
        for conn in workflow_data.get('connections', []):
            from_old_id = conn['from_node']
            to_old_id = conn['to_node']
            from_new_id = id_mapping.get(from_old_id)
            to_new_id = id_mapping.get(to_old_id)

            if from_new_id and to_new_id:
                from_widget = widget_map.get(from_new_id)
                to_widget = widget_map.get(to_new_id)
                if from_widget and to_widget:
                    edge = EdgeWidget(from_widget.output_port, to_widget.input_port)
                    self.scene.addItem(edge)

    def _clear_graph(self):
        """Clear all nodes and connections."""
        reply = QMessageBox.question(
            self, "Clear All",
            "Are you sure you want to clear all nodes?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.scene.clear()
            self.graph.clear()
            self.current_selected_node_id = None

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
            QMessageBox.warning(self, "Warning", "No node selected to execute.\nPlease click on an Output node first.")
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

    def cleanup(self):
        """Cleanup resources when closing."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
