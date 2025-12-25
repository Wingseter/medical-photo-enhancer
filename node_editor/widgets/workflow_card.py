"""
Workflow Card Widget - A clickable card displaying workflow thumbnail and info.
"""
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
import base64


class WorkflowCard(QFrame):
    """A clickable card displaying workflow thumbnail and info."""

    clicked = Signal(object)  # workflow_data
    edit_clicked = Signal(object)  # workflow_data
    delete_clicked = Signal(object)  # workflow_data

    def __init__(self, workflow_data, parent=None):
        super().__init__(parent)
        self.workflow_data = workflow_data
        self._is_selected = False
        self._setup_ui()
        self._apply_style()
        self.setCursor(Qt.PointingHandCursor)

    def _apply_style(self):
        if self._is_selected:
            self.setStyleSheet("""
                WorkflowCard {
                    background: #404040;
                    border: 2px solid #007ACC;
                    border-radius: 8px;
                    padding: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                WorkflowCard {
                    background: #3A3A3A;
                    border: 1px solid #555;
                    border-radius: 8px;
                    padding: 8px;
                }
                WorkflowCard:hover {
                    border-color: #007ACC;
                    background: #404040;
                }
            """)

    def set_selected(self, selected):
        self._is_selected = selected
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)

        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(140, 90)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet("""
            background: #2A2A2A;
            border-radius: 4px;
            color: #666;
            font-size: 10px;
        """)

        # Load thumbnail from base64 if available
        thumb_data = self.workflow_data.get('metadata', {}).get('thumbnail')
        if thumb_data:
            pixmap = self._decode_thumbnail(thumb_data)
            if pixmap and not pixmap.isNull():
                self.thumbnail_label.setPixmap(pixmap.scaled(
                    140, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            else:
                self.thumbnail_label.setText("No Preview")
        else:
            self.thumbnail_label.setText("No Preview")

        layout.addWidget(self.thumbnail_label, alignment=Qt.AlignCenter)

        # Name
        name = self.workflow_data.get('metadata', {}).get('name', 'Untitled')
        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-weight: bold; color: #E0E0E0; font-size: 11px;")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        # Node count
        node_count = len(self.workflow_data.get('nodes', []))
        count_label = QLabel(f"{node_count} nodes")
        count_label.setStyleSheet("color: #888; font-size: 9px;")
        count_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(count_label)

    def _decode_thumbnail(self, base64_str):
        """Decode base64 thumbnail to QPixmap."""
        if not base64_str or not base64_str.startswith("data:image"):
            return None
        try:
            _, data = base64_str.split(",", 1)
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(data))
            return pixmap
        except Exception:
            return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.workflow_data)
        super().mousePressEvent(event)
