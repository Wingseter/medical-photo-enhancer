"""
Preview Gallery Widget - A scrollable gallery of processed image previews.
"""
from PySide6.QtWidgets import (
    QWidget, QScrollArea, QGridLayout, QLabel, QVBoxLayout, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
import numpy as np
from pathlib import Path


class ImageThumbnail(QFrame):
    """A single image thumbnail with filename."""

    clicked = Signal(str)  # filepath

    THUMBNAIL_SIZE = 140

    def __init__(self, filepath, pixmap, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self._setup_ui(pixmap)
        self.setCursor(Qt.PointingHandCursor)

    def _setup_ui(self, pixmap):
        self.setStyleSheet("""
            ImageThumbnail {
                background: #2A2A2A;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
            }
            ImageThumbnail:hover {
                border-color: #007ACC;
            }
        """)
        self.setFixedSize(self.THUMBNAIL_SIZE + 8, self.THUMBNAIL_SIZE + 30)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Image
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setPixmap(pixmap.scaled(
            self.THUMBNAIL_SIZE, self.THUMBNAIL_SIZE,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        layout.addWidget(img_label)

        # Filename
        filename = Path(self.filepath).name
        name_label = QLabel(filename)
        name_label.setStyleSheet("color: #AAA; font-size: 9px;")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setMaximumHeight(20)
        layout.addWidget(name_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.filepath)
        super().mousePressEvent(event)


class PreviewGallery(QScrollArea):
    """A scrollable gallery of processed image previews."""

    image_clicked = Signal(str)  # filepath

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("""
            QScrollArea {
                background: #252525;
                border: 1px solid #444;
                border-radius: 6px;
            }
        """)

        # Container widget
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(8)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setWidget(self.container)

        self.images = []
        self._columns = 4

    def add_image(self, filepath: str, np_image: np.ndarray):
        """Add a processed image to the gallery."""
        # Convert numpy to QPixmap
        h, w = np_image.shape[:2]

        if len(np_image.shape) == 2:
            # Grayscale
            bytes_per_line = w
            fmt = QImage.Format_Grayscale8
        else:
            # RGB
            bytes_per_line = w * 3
            fmt = QImage.Format_RGB888

        # Make a copy to ensure data persists
        img_copy = np_image.copy()
        q_image = QImage(img_copy.data, w, h, bytes_per_line, fmt)
        pixmap = QPixmap.fromImage(q_image.copy())

        # Create thumbnail widget
        thumb = ImageThumbnail(filepath, pixmap)
        thumb.clicked.connect(self.image_clicked.emit)

        # Add to grid
        idx = len(self.images)
        row = idx // self._columns
        col = idx % self._columns
        self.grid_layout.addWidget(thumb, row, col)

        self.images.append((filepath, pixmap))

    def add_image_from_file(self, filepath: str):
        """Add an image to the gallery from file path."""
        pixmap = QPixmap(filepath)
        if pixmap.isNull():
            return

        thumb = ImageThumbnail(filepath, pixmap)
        thumb.clicked.connect(self.image_clicked.emit)

        idx = len(self.images)
        row = idx // self._columns
        col = idx % self._columns
        self.grid_layout.addWidget(thumb, row, col)

        self.images.append((filepath, pixmap))

    def clear(self):
        """Clear all images from the gallery."""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.images.clear()

    def set_columns(self, columns):
        """Set the number of columns for the grid."""
        self._columns = max(1, columns)
        # Rebuild grid layout if needed
        if self.images:
            # Store images
            stored = self.images.copy()
            self.clear()
            # Re-add
            for filepath, pixmap in stored:
                thumb = ImageThumbnail(filepath, pixmap)
                thumb.clicked.connect(self.image_clicked.emit)
                idx = len(self.images)
                row = idx // self._columns
                col = idx % self._columns
                self.grid_layout.addWidget(thumb, row, col)
                self.images.append((filepath, pixmap))
