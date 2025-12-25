from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter

class NodeEditorView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self._pan_start_mouse_pos = None

    def wheelEvent(self, event):
        # Zoom in/out with Ctrl + Wheel
        if event.modifiers() == Qt.ControlModifier:
            zoom_factor = 1.25
            if event.angleDelta().y() > 0:
                self.scale(zoom_factor, zoom_factor)
            else:
                self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton: # Middle button for panning
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._pan_start_mouse_pos = event.pos()
            event.accept()
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        # If panning, update the view manually
        if self.dragMode() == QGraphicsView.ScrollHandDrag and self._pan_start_mouse_pos is not None:
            delta = event.pos() - self._pan_start_mouse_pos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self._pan_start_mouse_pos = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton: # Stop panning
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self._pan_start_mouse_pos = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        # Delete selected edges with Delete or Backspace key
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.scene().delete_selected_edges()
            event.accept()
        else:
            super().keyPressEvent(event)
