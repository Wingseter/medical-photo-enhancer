"""
Image Selector Widget - For selecting single or multiple images.
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from pathlib import Path


class ImageSelector(QWidget):
    """Widget for selecting single or multiple images."""

    selection_changed = Signal(list)  # list of file paths

    SUPPORTED_FORMATS = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff", "*.tif"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_paths = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Buttons row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.add_files_btn = QPushButton("Add Files")
        self.add_files_btn.clicked.connect(self._add_files)
        self.add_files_btn.setStyleSheet("""
            QPushButton { padding: 10px 20px; font-size: 12px; }
        """)
        btn_layout.addWidget(self.add_files_btn)

        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.clicked.connect(self._add_folder)
        self.add_folder_btn.setStyleSheet("""
            QPushButton { padding: 10px 20px; font-size: 12px; }
        """)
        btn_layout.addWidget(self.add_folder_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear)
        self.clear_btn.setStyleSheet("""
            QPushButton { padding: 10px 20px; font-size: 12px; }
        """)
        btn_layout.addWidget(self.clear_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # File list
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(140)
        self.file_list.setStyleSheet("""
            QListWidget {
                background: #2D3142;
                border: 1px solid #3D4259;
                border-radius: 6px;
                color: #E8EAF0;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 6px 10px;
            }
            QListWidget::item:selected {
                background: #5C6BC0;
            }
        """)
        layout.addWidget(self.file_list)

        # Summary label
        self.summary_label = QLabel("No images selected")
        self.summary_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.summary_label)

    def _add_files(self):
        """Open file dialog to add images."""
        filter_str = "Images (" + " ".join(self.SUPPORTED_FORMATS) + ")"
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", filter_str
        )

        for f in files:
            if f not in self.image_paths:
                self.image_paths.append(f)
                self.file_list.addItem(Path(f).name)

        self._update_summary()
        self.selection_changed.emit(self.image_paths)

    def _add_folder(self):
        """Add all images from a folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        if folder:
            folder_path = Path(folder)
            for pattern in self.SUPPORTED_FORMATS:
                for f in folder_path.glob(pattern):
                    if str(f) not in self.image_paths:
                        self.image_paths.append(str(f))
                        self.file_list.addItem(f.name)
                # Also check case-insensitive
                for f in folder_path.glob(pattern.upper()):
                    if str(f) not in self.image_paths:
                        self.image_paths.append(str(f))
                        self.file_list.addItem(f.name)

        self._update_summary()
        self.selection_changed.emit(self.image_paths)

    def _clear(self):
        """Clear all selected images."""
        self.image_paths.clear()
        self.file_list.clear()
        self._update_summary()
        self.selection_changed.emit(self.image_paths)

    def _update_summary(self):
        """Update the summary label."""
        count = len(self.image_paths)
        if count == 0:
            self.summary_label.setText("No images selected")
        elif count == 1:
            self.summary_label.setText("1 image selected")
        else:
            self.summary_label.setText(f"{count} images selected")

    def get_selected_images(self):
        """Return list of selected image paths."""
        return self.image_paths.copy()

    def set_images(self, image_paths):
        """Set the list of images programmatically."""
        self._clear()
        for path in image_paths:
            if path not in self.image_paths:
                self.image_paths.append(path)
                self.file_list.addItem(Path(path).name)
        self._update_summary()
