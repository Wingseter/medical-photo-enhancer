"""
Image Compare Page - Compare two images with difference detection and synchronized zoom.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QFrame, QFileDialog, QScrollArea, QSplitter,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem,
    QScrollBar
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QPen, QBrush
import cv2
import numpy as np


class MiniMap(QLabel):
    """Minimap showing full image with viewport indicator."""

    position_clicked = Signal(float, float)  # normalized x, y (0-1)
    viewport_changed = Signal(float, float, float, float)  # x, y, w, h (normalized)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(120, 90)
        self.setMaximumSize(200, 150)
        self.setStyleSheet("""
            QLabel {
                background: #252836;
                border: 1px solid #4A4F6A;
                border-radius: 4px;
            }
        """)
        self.setAlignment(Qt.AlignCenter)

        self.pixmap_original = None
        self.viewport_rect = QRectF(0, 0, 1, 1)  # normalized (0-1)

    def set_image(self, np_image):
        """Set image from numpy array."""
        if np_image is None:
            self.clear()
            return

        h, w = np_image.shape[:2]

        if len(np_image.shape) == 2:
            bytes_per_line = w
            fmt = QImage.Format_Grayscale8
        else:
            bytes_per_line = w * 3
            fmt = QImage.Format_RGB888

        q_image = QImage(np_image.data, w, h, bytes_per_line, fmt)
        self.pixmap_original = QPixmap.fromImage(q_image.copy())
        self._update_display()

    def set_viewport(self, x, y, w, h):
        """Set viewport rectangle (normalized 0-1)."""
        self.viewport_rect = QRectF(x, y, w, h)
        self._update_display()

    def _update_display(self):
        if self.pixmap_original is None:
            return

        # Scale pixmap to fit
        scaled = self.pixmap_original.scaled(
            self.size() - QPixmap(4, 4).size(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # Draw viewport rectangle
        result = QPixmap(scaled.size())
        result.fill(Qt.transparent)

        painter = QPainter(result)
        painter.drawPixmap(0, 0, scaled)

        # Draw viewport indicator
        rect = QRectF(
            self.viewport_rect.x() * scaled.width(),
            self.viewport_rect.y() * scaled.height(),
            self.viewport_rect.width() * scaled.width(),
            self.viewport_rect.height() * scaled.height()
        )

        # Semi-transparent overlay outside viewport
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
        painter.setPen(Qt.NoPen)

        # Top
        painter.drawRect(QRectF(0, 0, scaled.width(), rect.top()))
        # Bottom
        painter.drawRect(QRectF(0, rect.bottom(), scaled.width(), scaled.height() - rect.bottom()))
        # Left
        painter.drawRect(QRectF(0, rect.top(), rect.left(), rect.height()))
        # Right
        painter.drawRect(QRectF(rect.right(), rect.top(), scaled.width() - rect.right(), rect.height()))

        # Viewport border
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(124, 134, 203), 2))
        painter.drawRect(rect)

        painter.end()

        self.setPixmap(result)

    def mousePressEvent(self, event):
        self._handle_click(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self._handle_click(event.pos())

    def _handle_click(self, pos):
        if self.pixmap_original is None:
            return

        # Calculate normalized position
        pixmap = self.pixmap()
        if pixmap is None:
            return

        # Get the actual drawing area
        label_size = self.size()
        pixmap_size = pixmap.size()

        # Center offset
        offset_x = (label_size.width() - pixmap_size.width()) / 2
        offset_y = (label_size.height() - pixmap_size.height()) / 2

        # Adjust for offset
        x = pos.x() - offset_x
        y = pos.y() - offset_y

        if 0 <= x <= pixmap_size.width() and 0 <= y <= pixmap_size.height():
            nx = x / pixmap_size.width()
            ny = y / pixmap_size.height()
            self.position_clicked.emit(max(0, min(1, nx)), max(0, min(1, ny)))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_display()


class ZoomableImageView(QGraphicsView):
    """Zoomable image view with scroll synchronization."""

    scroll_changed = Signal(float, float)  # normalized scroll position (0-1)
    viewport_changed = Signal(float, float, float, float)  # x, y, w, h (normalized)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setStyleSheet("""
            QGraphicsView {
                background: #252836;
                border: 1px solid #4A4F6A;
                border-radius: 6px;
            }
        """)

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.pixmap_item = None
        self.image = None
        self.image_size = (0, 0)
        self.zoom_factor = 1.0
        self._is_syncing = False

        # Connect scroll bars
        self.horizontalScrollBar().valueChanged.connect(self._on_scroll_changed)
        self.verticalScrollBar().valueChanged.connect(self._on_scroll_changed)

    def set_image(self, np_image):
        """Set image from numpy array."""
        if np_image is None:
            return

        self.image = np_image.copy()
        h, w = self.image.shape[:2]
        self.image_size = (w, h)

        if len(self.image.shape) == 2:
            bytes_per_line = w
            fmt = QImage.Format_Grayscale8
        else:
            bytes_per_line = w * 3
            fmt = QImage.Format_RGB888

        q_image = QImage(self.image.data, w, h, bytes_per_line, fmt)
        pixmap = QPixmap.fromImage(q_image.copy())

        self.scene.clear()
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))
        self._apply_zoom()

    def set_zoom(self, factor):
        """Set zoom level."""
        self.zoom_factor = factor
        self._apply_zoom()

    def _apply_zoom(self):
        self.resetTransform()
        self.scale(self.zoom_factor, self.zoom_factor)
        self._emit_viewport()

    def center_on_normalized(self, nx, ny):
        """Center view on normalized coordinates (0-1)."""
        if self.pixmap_item is None:
            return

        self._is_syncing = True
        rect = self.sceneRect()
        x = nx * rect.width()
        y = ny * rect.height()
        self.centerOn(x, y)
        self._is_syncing = False
        self._emit_viewport()

    def set_scroll_normalized(self, nx, ny):
        """Set scroll position using normalized values (0-1)."""
        if self._is_syncing:
            return

        self._is_syncing = True

        h_bar = self.horizontalScrollBar()
        v_bar = self.verticalScrollBar()

        if h_bar.maximum() > 0:
            h_bar.setValue(int(nx * h_bar.maximum()))
        if v_bar.maximum() > 0:
            v_bar.setValue(int(ny * v_bar.maximum()))

        self._is_syncing = False
        self._emit_viewport()

    def _on_scroll_changed(self):
        if self._is_syncing:
            return

        h_bar = self.horizontalScrollBar()
        v_bar = self.verticalScrollBar()

        nx = h_bar.value() / max(1, h_bar.maximum()) if h_bar.maximum() > 0 else 0
        ny = v_bar.value() / max(1, v_bar.maximum()) if v_bar.maximum() > 0 else 0

        self.scroll_changed.emit(nx, ny)
        self._emit_viewport()

    def _emit_viewport(self):
        """Emit current viewport rectangle."""
        if self.pixmap_item is None or self.image_size[0] == 0:
            return

        # Get visible rect in scene coordinates
        visible = self.mapToScene(self.viewport().rect()).boundingRect()
        scene_rect = self.sceneRect()

        if scene_rect.width() > 0 and scene_rect.height() > 0:
            x = visible.x() / scene_rect.width()
            y = visible.y() / scene_rect.height()
            w = visible.width() / scene_rect.width()
            h = visible.height() / scene_rect.height()

            # Clamp values
            x = max(0, min(1, x))
            y = max(0, min(1, y))
            w = max(0, min(1 - x, w))
            h = max(0, min(1 - y, h))

            self.viewport_changed.emit(x, y, w, h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._emit_viewport()


class ImagePanel(QWidget):
    """Panel containing image view and minimap."""

    scroll_changed = Signal(float, float)
    position_clicked = Signal(float, float)

    def __init__(self, title="Image", parent=None):
        super().__init__(parent)
        self.title = title
        self.image = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header with title and load button
        header = QHBoxLayout()

        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #7986CB; font-size: 12px; font-weight: bold;")
        header.addWidget(title_label)

        header.addStretch()

        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #6B7394; font-size: 10px;")
        header.addWidget(self.info_label)

        self.load_btn = QPushButton("Load Image")
        self.load_btn.setStyleSheet("""
            QPushButton {
                background: #3D4259;
                color: #E8EAF0;
                border: 1px solid #4A4F6A;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #4A4F6A;
                border-color: #5C6BC0;
            }
        """)
        self.load_btn.clicked.connect(self._browse_image)
        header.addWidget(self.load_btn)

        layout.addLayout(header)

        # Main view and minimap
        content = QHBoxLayout()
        content.setSpacing(8)

        # Zoom view (main)
        self.zoom_view = ZoomableImageView()
        self.zoom_view.scroll_changed.connect(self._on_scroll_changed)
        self.zoom_view.viewport_changed.connect(self._on_viewport_changed)
        content.addWidget(self.zoom_view, 1)

        # Minimap
        self.minimap = MiniMap()
        self.minimap.position_clicked.connect(self._on_minimap_clicked)
        content.addWidget(self.minimap)

        layout.addLayout(content)

    def _browse_image(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if filepath:
            self._load_image(filepath)

    def _load_image(self, filepath):
        img = cv2.imread(filepath)
        if img is not None:
            self.image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.set_image(self.image)

    def set_image(self, np_image):
        """Set image from numpy array."""
        self.image = np_image.copy() if np_image is not None else None
        self.zoom_view.set_image(self.image)
        self.minimap.set_image(self.image)

        if self.image is not None:
            h, w = self.image.shape[:2]
            self.info_label.setText(f"{w} × {h}")
        else:
            self.info_label.setText("")

    def set_zoom(self, factor):
        self.zoom_view.set_zoom(factor)

    def center_on_normalized(self, nx, ny):
        self.zoom_view.center_on_normalized(nx, ny)

    def set_scroll_normalized(self, nx, ny):
        self.zoom_view.set_scroll_normalized(nx, ny)

    def _on_scroll_changed(self, nx, ny):
        self.scroll_changed.emit(nx, ny)

    def _on_viewport_changed(self, x, y, w, h):
        self.minimap.set_viewport(x, y, w, h)

    def _on_minimap_clicked(self, nx, ny):
        self.zoom_view.center_on_normalized(nx, ny)
        self.position_clicked.emit(nx, ny)


class ImageComparePage(QWidget):
    """Page for comparing two images."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()

        title = QLabel("Image Compare")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #E8EAF0;")
        header.addWidget(title)

        header.addStretch()

        # Zoom controls
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("color: #9BA3C2; font-size: 12px;")
        header.addWidget(zoom_label)

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(100, 2000)
        self.zoom_slider.setValue(400)
        self.zoom_slider.setFixedWidth(150)
        self.zoom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #3D4259;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #7986CB;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #5C6BC0;
                border-radius: 3px;
            }
        """)
        self.zoom_slider.valueChanged.connect(self._on_zoom_changed)
        header.addWidget(self.zoom_slider)

        self.zoom_value_label = QLabel("4.0x")
        self.zoom_value_label.setStyleSheet("color: #7986CB; font-size: 12px; min-width: 40px;")
        header.addWidget(self.zoom_value_label)

        # Find differences button
        self.diff_btn = QPushButton("Find Differences")
        self.diff_btn.setStyleSheet("""
            QPushButton {
                background: #5C6BC0;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7986CB;
            }
            QPushButton:pressed {
                background: #3F51B5;
            }
            QPushButton:disabled {
                background: #4A4F6A;
                color: #6B7394;
            }
        """)
        self.diff_btn.clicked.connect(self._find_differences)
        self.diff_btn.setEnabled(False)
        header.addWidget(self.diff_btn)

        # Reset button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: #3D4259;
                color: #E8EAF0;
                border: 1px solid #4A4F6A;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #4A4F6A;
                border-color: #5C6BC0;
            }
        """)
        self.reset_btn.clicked.connect(self._reset_images)
        header.addWidget(self.reset_btn)

        layout.addLayout(header)

        # Main content - side by side panels
        panels_layout = QHBoxLayout()
        panels_layout.setSpacing(16)

        # Left panel
        self.panel_left = ImagePanel("Image A (Reference)")
        self.panel_left.scroll_changed.connect(self._on_left_scroll)
        self.panel_left.position_clicked.connect(self._on_left_position)
        self.panel_left.zoom_view.viewport_changed.connect(lambda *_: self._update_diff_button())
        panels_layout.addWidget(self.panel_left)

        # Right panel
        self.panel_right = ImagePanel("Image B (Compare)")
        self.panel_right.scroll_changed.connect(self._on_right_scroll)
        self.panel_right.position_clicked.connect(self._on_right_position)
        self.panel_right.zoom_view.viewport_changed.connect(lambda *_: self._update_diff_button())
        panels_layout.addWidget(self.panel_right)

        layout.addLayout(panels_layout, 1)

        # Difference result panel (hidden by default)
        self.diff_panel = QFrame()
        self.diff_panel.setStyleSheet("""
            QFrame {
                background: #353849;
                border: 1px solid #4A4F6A;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        self.diff_panel.setVisible(False)
        self.diff_panel.setMaximumHeight(60)

        diff_layout = QHBoxLayout(self.diff_panel)

        self.diff_info = QLabel("")
        self.diff_info.setStyleSheet("color: #E8EAF0; font-size: 12px;")
        diff_layout.addWidget(self.diff_info)

        diff_layout.addStretch()

        self.show_diff_btn = QPushButton("Show Difference Map")
        self.show_diff_btn.setStyleSheet("""
            QPushButton {
                background: #3D4259;
                color: #E8EAF0;
                border: 1px solid #5C6BC0;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #4A4F6A;
            }
        """)
        self.show_diff_btn.clicked.connect(self._show_diff_map)
        diff_layout.addWidget(self.show_diff_btn)

        self.restore_btn = QPushButton("Restore Original")
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background: #3D4259;
                color: #E8EAF0;
                border: 1px solid #4A4F6A;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #4A4F6A;
            }
        """)
        self.restore_btn.clicked.connect(self._restore_original)
        self.restore_btn.setVisible(False)
        diff_layout.addWidget(self.restore_btn)

        layout.addWidget(self.diff_panel)

        # Set initial zoom
        self._on_zoom_changed(400)

    def _update_diff_button(self):
        enabled = self.panel_left.image is not None and self.panel_right.image is not None
        self.diff_btn.setEnabled(enabled)

    def _on_zoom_changed(self, value):
        factor = value / 100.0
        self.zoom_value_label.setText(f"{factor:.1f}x")
        self.panel_left.set_zoom(factor)
        self.panel_right.set_zoom(factor)

    def _on_left_scroll(self, nx, ny):
        self.panel_right.set_scroll_normalized(nx, ny)

    def _on_right_scroll(self, nx, ny):
        self.panel_left.set_scroll_normalized(nx, ny)

    def _on_left_position(self, nx, ny):
        self.panel_right.center_on_normalized(nx, ny)

    def _on_right_position(self, nx, ny):
        self.panel_left.center_on_normalized(nx, ny)

    def _find_differences(self):
        img_left = self.panel_left.image
        img_right = self.panel_right.image

        if img_left is None or img_right is None:
            return

        # Resize right image to match left if needed
        h1, w1 = img_left.shape[:2]
        h2, w2 = img_right.shape[:2]

        if (h1, w1) != (h2, w2):
            img_right_resized = cv2.resize(img_right, (w1, h1))
        else:
            img_right_resized = img_right

        # Convert to grayscale for comparison
        if len(img_left.shape) == 3:
            gray_left = cv2.cvtColor(img_left, cv2.COLOR_RGB2GRAY)
        else:
            gray_left = img_left

        if len(img_right_resized.shape) == 3:
            gray_right = cv2.cvtColor(img_right_resized, cv2.COLOR_RGB2GRAY)
        else:
            gray_right = img_right_resized

        # Find absolute difference
        diff = cv2.absdiff(gray_left, gray_right)

        # Threshold to find significant differences
        _, thresh = cv2.threshold(diff, 10, 255, cv2.THRESH_BINARY)

        # Count different pixels
        diff_pixels = np.count_nonzero(thresh)
        total_pixels = w1 * h1
        diff_percent = (diff_pixels / total_pixels) * 100

        # Create difference map (highlight in magenta)
        if len(img_left.shape) == 3:
            diff_map = img_left.copy()
        else:
            diff_map = cv2.cvtColor(img_left, cv2.COLOR_GRAY2RGB)

        # Highlight differences in magenta
        diff_map[thresh > 0] = [255, 0, 255]

        self.diff_map = diff_map
        self.original_left = img_left.copy()

        # Show results
        self.diff_panel.setVisible(True)

        if diff_pixels == 0:
            self.diff_info.setText("✓ Images are identical")
            self.diff_info.setStyleSheet("color: #81C784; font-size: 12px;")
            self.show_diff_btn.setVisible(False)
        else:
            self.diff_info.setText(f"⚠ Found {diff_pixels:,} different pixels ({diff_percent:.2f}%)")
            self.diff_info.setStyleSheet("color: #FFB74D; font-size: 12px;")
            self.show_diff_btn.setVisible(True)

    def _show_diff_map(self):
        if hasattr(self, 'diff_map'):
            self.panel_left.set_image(self.diff_map)
            self.show_diff_btn.setVisible(False)
            self.restore_btn.setVisible(True)

    def _restore_original(self):
        if hasattr(self, 'original_left'):
            self.panel_left.set_image(self.original_left)
            self.show_diff_btn.setVisible(True)
            self.restore_btn.setVisible(False)

    def _reset_images(self):
        self.panel_left.set_image(None)
        self.panel_left.image = None
        self.panel_left.info_label.setText("")
        self.panel_left.zoom_view.scene.clear()
        self.panel_left.zoom_view.pixmap_item = None
        self.panel_left.minimap.clear()
        self.panel_left.minimap.pixmap_original = None

        self.panel_right.set_image(None)
        self.panel_right.image = None
        self.panel_right.info_label.setText("")
        self.panel_right.zoom_view.scene.clear()
        self.panel_right.zoom_view.pixmap_item = None
        self.panel_right.minimap.clear()
        self.panel_right.minimap.pixmap_original = None

        self.diff_panel.setVisible(False)
        self.diff_btn.setEnabled(False)

        if hasattr(self, 'diff_map'):
            del self.diff_map
        if hasattr(self, 'original_left'):
            del self.original_left
