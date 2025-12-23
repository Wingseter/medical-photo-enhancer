from PySide6.QtWidgets import QGraphicsScene, QGraphicsLineItem, QGraphicsView
from PySide6.QtCore import Qt, QLineF
from PySide6.QtGui import QPen, QColor

from node_editor.widgets.node_items import NodePort, EdgeWidget, COLOR_PORT

class NodeEditorScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QColor("#333333"))
        self.line = None
        self.start_port = None
    
    def get_view(self):
        """Helper to get the first QGraphicsView associated with this scene."""
        views = self.views()
        return views[0] if views else None

    def update_edges_for_node(self, node_widget):
        for item in self.items():
            if isinstance(item, EdgeWidget):
                if item.start_port.parentItem() == node_widget or \
                   item.end_port.parentItem() == node_widget:
                    item.update_path()

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), self.get_view().transform())
        if isinstance(item, NodePort) and item.is_output:
            self.start_port = item
            self.line = QGraphicsLineItem(QLineF(self.start_port.scenePos(), event.scenePos()))
            self.line.setPen(QPen(COLOR_PORT, 2))
            self.addItem(self.line)
            
            # Temporarily disable rubber band drag while connecting
            view = self.get_view()
            if view:
                view.setDragMode(QGraphicsView.NoDrag)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.line:
            self.line.setLine(QLineF(self.start_port.scenePos(), event.scenePos()))
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Restore rubber band drag mode
        view = self.get_view()
        if view:
            view.setDragMode(QGraphicsView.RubberBandDrag)

        if self.line:
            self.removeItem(self.line)
            self.line = None
            
            start_item = self.start_port
            end_item = self.itemAt(event.scenePos(), self.get_view().transform())

            if isinstance(end_item, NodePort) and not end_item.is_output and end_item != start_item:
                edge = EdgeWidget(start_item, end_item)
                self.addItem(edge)
                
                start_node_widget = start_item.parentItem()
                end_node_widget = end_item.parentItem()
                
                self.parent().graph.connect(start_node_widget.node_id, end_node_widget.node_id)
        
        super().mouseReleaseEvent(event)