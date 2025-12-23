from PySide6.QtWidgets import QGraphicsItem, QGraphicsObject, QGraphicsSceneMouseEvent
from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QFont, QPainterPathStroker

PORT_SIZE = 12
NODE_HEADER_HEIGHT = 25
NODE_WIDTH = 150
NODE_HEIGHT = 100

# --- Color Palette ---
COLOR_BACKGROUND = QColor("#222222")
COLOR_NODE_BODY = QColor("#3A3A3A")
COLOR_NODE_HEADER = QColor("#007ACC")
COLOR_NODE_BORDER = QColor("#555555")
COLOR_NODE_BORDER_SELECTED = QColor("#00A8FF")
COLOR_PORT = QColor("#FFAA00")
COLOR_EDGE = QColor("#FFAA00")
COLOR_TEXT = QColor("#DDDDDD")

class NodePort(QGraphicsObject):
    def __init__(self, parent, is_output=False):
        super().__init__(parent)
        self.is_output, self.hovered = is_output, False
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setToolTip("Input" if not is_output else "Output")

    def boundingRect(self): return QRectF(-PORT_SIZE/2, -PORT_SIZE/2, PORT_SIZE, PORT_SIZE)
    def paint(self, p, o, w):
        p.setPen(QPen(COLOR_NODE_BORDER, 2))
        p.setBrush(COLOR_PORT.lighter(120) if self.hovered else COLOR_PORT)
        p.drawEllipse(self.boundingRect())
    def hoverEnterEvent(self, e): self.hovered = True; self.update(); super().hoverEnterEvent(e)
    def hoverLeaveEvent(self, e): self.hovered = False; self.update(); super().hoverLeaveEvent(e)

class NodeWidget(QGraphicsObject):
    node_selected = Signal(str)
    def __init__(self, node_id, node_name):
        super().__init__()
        self.node_id, self.node_name = node_id, node_name
        self.width, self.height = NODE_WIDTH, NODE_HEIGHT
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.input_port = NodePort(self, False); self.input_port.setPos(self.width/2, NODE_HEADER_HEIGHT)
        self.output_port = NodePort(self, True); self.output_port.setPos(self.width/2, self.height)

    def boundingRect(self): return QRectF(0,0,self.width,self.height).adjusted(-2,-2,2,2)
    def paint(self, p, o, w):
        p.setRenderHint(QPainter.Antialiasing)
        
        # Main body
        body_rect = QRectF(0, 0, self.width, self.height)
        p.setBrush(COLOR_NODE_BODY)
        border_pen = QPen(COLOR_NODE_BORDER_SELECTED if self.isSelected() else COLOR_NODE_BORDER, 2)
        p.setPen(border_pen)
        p.drawRoundedRect(body_rect, 8, 8)

        # Header
        header_rect = QRectF(0, 0, self.width, NODE_HEADER_HEIGHT)
        header_path = QPainterPath()
        header_path.addRoundedRect(header_rect, 8, 8)
        header_path.addRect(0, NODE_HEADER_HEIGHT - 8, self.width, 8) # Mask bottom corners
        p.setBrush(COLOR_NODE_HEADER)
        p.setPen(Qt.NoPen)
        p.drawPath(header_path)
        
        # Text
        font = QFont("Arial", 10, QFont.Bold)
        p.setFont(font)
        p.setPen(COLOR_TEXT)
        p.drawText(header_rect, Qt.AlignCenter, self.node_name)

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
        p1 = self.start_port.scenePos()
        p2 = self.end_port.scenePos()
        
        path = QPainterPath(p1)
        
        # Bezier curve calculation
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        ctrl1 = QPointF(p1.x() + dx * 0.5, p1.y() + dy * 0.1)
        ctrl2 = QPointF(p1.x() + dx * 0.5, p1.y() + dy * 0.9)
        path.cubicTo(ctrl1, ctrl2, p2)
        
        self.path = path

    def boundingRect(self): return self.path.boundingRect()
    def shape(self):
        stroker = QPainterPathStroker()
        stroker.setWidth(10)
        return stroker.createStroke(self.path)
    def paint(self, p, o, w):
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(COLOR_EDGE, 2.5))
        p.setBrush(Qt.NoBrush)
        p.drawPath(self.path)