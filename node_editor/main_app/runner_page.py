"""
Workflow Runner Page - Main page for running saved workflows on image batches.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QLineEdit, QScrollArea,
    QFileDialog, QMessageBox, QProgressBar, QFrame
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon

from node_editor.widgets.workflow_card import WorkflowCard
from node_editor.widgets.image_selector import ImageSelector
from node_editor.widgets.preview_gallery import PreviewGallery
from node_editor.core.workflow_manager import WorkflowManager
from node_editor.main_app.batch_worker import BatchProcessingWorker


class WorkflowRunnerPage(QWidget):
    """Main page for running saved workflows on image batches."""

    edit_workflow_requested = Signal(str)  # workflow filepath
    new_workflow_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.workflow_manager = WorkflowManager()
        self.selected_workflow = None
        self.batch_worker = None
        self.workflow_cards = []

        self._setup_ui()
        self._load_workflows()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Left panel: Workflow list
        left_panel = self._create_workflow_panel()
        splitter.addWidget(left_panel)

        # Right panel: Execution area
        right_panel = self._create_execution_panel()
        splitter.addWidget(right_panel)

        # Set splitter sizes (1:3 ratio)
        splitter.setSizes([280, 900])

    def _create_workflow_panel(self):
        """Create the workflow list panel."""
        panel = QFrame()
        panel.setStyleSheet("QFrame { background: #2D3142; }")
        panel.setMinimumWidth(250)
        panel.setMaximumWidth(350)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header
        header = QLabel("Workflows")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(header)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search workflows...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                background: #353849;
                border: 1px solid #4A4F6A;
                border-radius: 6px;
                padding: 10px;
                color: #E8EAF0;
            }
            QLineEdit:focus {
                border-color: #7986CB;
            }
        """)
        self.search_box.textChanged.connect(self._filter_workflows)
        layout.addWidget(self.search_box)

        # Workflow cards scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        self.workflow_container = QWidget()
        self.workflow_container.setStyleSheet("background: transparent;")
        self.workflow_layout = QVBoxLayout(self.workflow_container)
        self.workflow_layout.setAlignment(Qt.AlignTop)
        self.workflow_layout.setSpacing(8)
        scroll.setWidget(self.workflow_container)
        layout.addWidget(scroll, 1)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.new_btn = QPushButton("+ New Workflow")
        self.new_btn.setStyleSheet("""
            QPushButton {
                background: #2D7D46;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background: #3D8D56; }
        """)
        self.new_btn.clicked.connect(self._create_new_workflow)
        btn_layout.addWidget(self.new_btn)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._load_workflows)
        btn_layout.addWidget(self.refresh_btn)

        layout.addLayout(btn_layout)

        return panel

    def _create_execution_panel(self):
        """Create the execution/preview panel."""
        panel = QFrame()
        panel.setStyleSheet("QFrame { background: #252836; }")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Workflow info header
        self.workflow_title = QLabel("Select a workflow to begin")
        self.workflow_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(self.workflow_title)

        self.workflow_desc = QLabel("")
        self.workflow_desc.setWordWrap(True)
        self.workflow_desc.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(self.workflow_desc)

        # Input images section
        input_section = QLabel("Input Images")
        input_section.setStyleSheet("font-size: 16px; font-weight: bold; color: #E0E0E0; margin-top: 12px;")
        layout.addWidget(input_section)

        self.image_selector = ImageSelector()
        layout.addWidget(self.image_selector)

        # Output folder section
        output_section = QLabel("Output Folder")
        output_section.setStyleSheet("font-size: 16px; font-weight: bold; color: #E0E0E0; margin-top: 12px;")
        layout.addWidget(output_section)

        output_layout = QHBoxLayout()
        output_layout.setSpacing(8)

        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output folder...")
        self.output_path.setStyleSheet("""
            QLineEdit {
                background: #353849;
                border: 1px solid #4A4F6A;
                border-radius: 6px;
                padding: 10px;
                color: #E8EAF0;
            }
        """)
        output_layout.addWidget(self.output_path)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_output_folder)
        output_layout.addWidget(browse_btn)
        layout.addLayout(output_layout)

        # Progress section
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(4)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: #353849;
                border: none;
                border-radius: 4px;
                height: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5C6BC0, stop:1 #7986CB);
                border-radius: 4px;
            }
        """)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #888; font-size: 11px;")
        self.progress_label.setVisible(False)
        progress_layout.addWidget(self.progress_label)

        layout.addWidget(progress_container)

        # Preview gallery
        preview_section = QLabel("Results Preview")
        preview_section.setStyleSheet("font-size: 16px; font-weight: bold; color: #E0E0E0; margin-top: 12px;")
        layout.addWidget(preview_section)

        self.preview_gallery = PreviewGallery()
        layout.addWidget(self.preview_gallery, 1)

        # Run/Stop buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.run_btn = QPushButton("Run Workflow")
        self.run_btn.setIcon(QIcon("node_editor/icons/play.svg"))
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self._run_workflow)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background: #2D7D46;
                font-size: 16px;
                font-weight: bold;
                padding: 16px 40px;
            }
            QPushButton:hover { background: #3D8D56; }
            QPushButton:disabled { background: #555; color: #888; }
        """)
        btn_layout.addWidget(self.run_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_workflow)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #C62828;
                font-size: 16px;
                padding: 16px 28px;
            }
            QPushButton:hover { background: #E53935; }
            QPushButton:disabled { background: #555; color: #888; }
        """)
        btn_layout.addWidget(self.stop_btn)

        btn_layout.addStretch()

        # Open output folder button
        self.open_folder_btn = QPushButton("Open Output Folder")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self._open_output_folder)
        btn_layout.addWidget(self.open_folder_btn)

        layout.addLayout(btn_layout)

        return panel

    def _load_workflows(self):
        """Load all saved workflows."""
        workflows = self.workflow_manager.list_workflows()

        # Clear existing cards
        for card in self.workflow_cards:
            card.deleteLater()
        self.workflow_cards.clear()

        # Create workflow cards
        for workflow in workflows:
            card = WorkflowCard(workflow)
            card.clicked.connect(self._select_workflow)
            self.workflow_layout.addWidget(card)
            self.workflow_cards.append(card)

        if not workflows:
            empty_label = QLabel("No workflows yet.\nCreate one in the Editor tab.")
            empty_label.setStyleSheet("color: #666; font-size: 12px;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.workflow_layout.addWidget(empty_label)

    def _filter_workflows(self, text):
        """Filter workflow cards by search text."""
        search_text = text.lower()
        for card in self.workflow_cards:
            name = card.workflow_data.get('metadata', {}).get('name', '').lower()
            desc = card.workflow_data.get('metadata', {}).get('description', '').lower()
            visible = search_text in name or search_text in desc
            card.setVisible(visible)

    @Slot(object)
    def _select_workflow(self, workflow_data):
        """Handle workflow selection."""
        self.selected_workflow = workflow_data

        # Update selection visuals
        for card in self.workflow_cards:
            card.set_selected(card.workflow_data == workflow_data)

        # Update info display
        self.workflow_title.setText(workflow_data.get('metadata', {}).get('name', 'Untitled'))
        desc = workflow_data.get('metadata', {}).get('description', '')
        self.workflow_desc.setText(desc if desc else "No description")

        self.run_btn.setEnabled(True)

    def _create_new_workflow(self):
        """Request to create a new workflow (switch to editor)."""
        self.new_workflow_requested.emit()

    def _browse_output_folder(self):
        """Browse for output folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path.setText(folder)
            self.open_folder_btn.setEnabled(True)

    def _open_output_folder(self):
        """Open the output folder in file explorer."""
        import subprocess
        import sys
        folder = self.output_path.text()
        if folder:
            if sys.platform == 'darwin':
                subprocess.run(['open', folder])
            elif sys.platform == 'win32':
                subprocess.run(['explorer', folder])
            else:
                subprocess.run(['xdg-open', folder])

    @Slot()
    def _run_workflow(self):
        """Start batch processing."""
        if not self.selected_workflow:
            return

        images = self.image_selector.get_selected_images()
        output_folder = self.output_path.text()

        if not images:
            QMessageBox.warning(self, "Warning", "Please select input images.")
            return

        if not output_folder:
            QMessageBox.warning(self, "Warning", "Please select an output folder.")
            return

        # Clear previous results
        self.preview_gallery.clear()

        # Start batch worker
        self.batch_worker = BatchProcessingWorker(
            self.selected_workflow,
            images,
            output_folder
        )
        self.batch_worker.progress.connect(self._on_batch_progress)
        self.batch_worker.image_completed.connect(self._on_image_completed)
        self.batch_worker.finished.connect(self._on_batch_finished)
        self.batch_worker.error.connect(self._on_batch_error)

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("Starting...")
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.open_folder_btn.setEnabled(True)

        self.batch_worker.start()

    @Slot()
    def _stop_workflow(self):
        """Stop batch processing."""
        if self.batch_worker and self.batch_worker.isRunning():
            self.batch_worker.stop()
            self.progress_label.setText("Stopping...")

    @Slot(int, int, str)
    def _on_batch_progress(self, current, total, filename):
        """Update progress display."""
        percent = int((current / total) * 100)
        self.progress_bar.setValue(percent)
        self.progress_label.setText(f"Processing {current}/{total}: {filename}")

    @Slot(str, object)
    def _on_image_completed(self, filepath, result_image):
        """Add completed image to preview gallery."""
        self.preview_gallery.add_image(filepath, result_image)

    @Slot()
    def _on_batch_finished(self):
        """Handle batch completion."""
        self.progress_bar.setValue(100)
        self.progress_label.setText("Complete!")
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        count = len(self.preview_gallery.images)
        QMessageBox.information(
            self, "Complete",
            f"Batch processing complete!\n{count} images processed."
        )

    @Slot(str)
    def _on_batch_error(self, error_msg):
        """Handle batch error."""
        self.progress_label.setText("Error occurred")
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        QMessageBox.critical(self, "Error", error_msg)

    def refresh_workflows(self):
        """Refresh the workflow list (called when editor saves a workflow)."""
        self._load_workflows()

    def cleanup(self):
        """Cleanup resources."""
        if self.batch_worker and self.batch_worker.isRunning():
            self.batch_worker.stop()
            self.batch_worker.wait()
