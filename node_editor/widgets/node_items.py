from PySide6.QtWidgets import QGraphicsItem, QGraphicsObject, QGraphicsSceneMouseEvent
from PySide6.QtCore import Qt, QPointF, QRectF, QLineF, Signal, Slot
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath

PORT_SIZE = 10
PORT_COLOR = QColor("#FFAA00")

class NodePort(QGraphicsObject):
    def __init__(self, parent, is_output=False):
        super().__init__(parent)
        self.is_output, self.hovered = is_output, False
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def boundingRect(self): return QRectF(-PORT_SIZE/2, -PORT_SIZE/2, PORT_SIZE, PORT_SIZE)
    def paint(self, p, o, w): p.setPen(Qt.NoPen); p.setBrush(PORT_COLOR.lighter(150) if self.hovered else PORT_COLOR); p.drawEllipse(self.boundingRect())
    def hoverEnterEvent(self, e): self.hovered = True; self.update(); super().hoverEnterEvent(e)
    def hoverLeaveEvent(self, e): self.hovered = False; self.update(); super().hoverLeaveEvent(e)

class NodeWidget(QGraphicsObject):
    node_selected = Signal(str)
    def __init__(self, node_id, node_name):
        super().__init__()
        self.node_id, self.node_name = node_id, node_name
        self.width, self.height = 120, 80
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.input_port = NodePort(self, False); self.input_port.setPos(self.width/2, 0)
        self.output_port = NodePort(self, True); self.output_port.setPos(self.width/2, self.height)

    def boundingRect(self): return QRectF(0,0,self.width,self.height).adjusted(-5,-5,5,5)
    def paint(self, p, o, w):
        rect = QRectF(0, 0, self.width, self.height)
        bg_color = QColor("#1E3D59").lighter(130) if self.isSelected() else QColor("#1E3D59")
        p.setBrush(bg_color); p.setPen(QPen(Qt.white, 2)); p.drawRoundedRect(rect, 10, 10)
        p.setPen(Qt.white); p.drawText(rect, Qt.AlignCenter, self.node_name)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            self.scene().update_edges_for_node(self)
        return super().itemChange(change, value)
    
    def mousePressEvent(self, e: QGraphicsSceneMouseEvent):
        self.node_selected.emit(self.node_id)
        super().mousePressEvent(e)

class EdgeWidget(QGraphicsObject):
    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port, self.end_port = start_port, end_port
        self.setZValue(-1)
        self.update_path()

    def update_path(self):
        self.prepareGeometryChange()
        # Map points to scene coordinates first, then to this item's coordinates
        p1_scene = self.start_port.scenePos()
        p2_scene = self.end_port.scenePos()
        self.path = QPainterPath(self.mapFromScene(p1_scene))
        self.path.lineTo(self.mapFromScene(p2_scene))

    def boundingRect(self): return self.path.boundingRect()
    def shape(self): return self.path
    def paint(self, p, o, w): p.setPen(QPen(PORT_COLOR, 2)); p.drawPath(self.path)
