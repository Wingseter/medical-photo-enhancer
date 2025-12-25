from PySide6.QtWidgets import (
    QGraphicsItem, QGraphicsObject, QGraphicsSceneMouseEvent,
    QGraphicsProxyWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSpinBox, QDoubleSpinBox, QSizePolicy
)
from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QSize
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QPainterPath, QFont,
    QPainterPathStroker, QLinearGradient, QRadialGradient, QFontMetrics,
    QPixmap, QImage
)
from pathlib import Path
import numpy as np

# --- Layout Constants ---
PORT_SIZE = 12
NODE_HEADER_HEIGHT = 28
NODE_WIDTH = 180
NODE_MIN_HEIGHT = 50
PARAM_ROW_HEIGHT = 26
PARAM_PADDING = 8

# Output node specific
OUTPUT_NODE_WIDTH = 280
OUTPUT_NODE_HEIGHT = 220
OUTPUT_PREVIEW_HEIGHT = 150

# --- Category Color Palette (Professional Theme) ---
CATEGORY_COLORS = {
    "Basic I/O": {
        "header": QColor("#2D7D46"),
        "header_gradient": QColor("#1E5C32"),
        "accent": QColor("#4CAF50"),
    },
    "Image Processing": {
        "header": QColor("#1565C0"),
        "header_gradient": QColor("#0D47A1"),
        "accent": QColor("#42A5F5"),
    },
    "AI / Machine Learning": {
        "header": QColor("#7B1FA2"),
        "header_gradient": QColor("#4A148C"),
        "accent": QColor("#AB47BC"),
    },
    "Uncategorized": {
        "header": QColor("#455A64"),
        "header_gradient": QColor("#37474F"),
        "accent": QColor("#78909C"),
    },
}

# --- Base Colors ---
COLOR_NODE_BODY = QColor("#2D2D2D")
COLOR_NODE_BODY_GRADIENT = QColor("#252525")
COLOR_NODE_BORDER = QColor("#1A1A1A")
COLOR_NODE_BORDER_SELECTED = QColor("#FFB300")  # Amber for selection
COLOR_PORT_INPUT = QColor("#4FC3F7")   # Light blue for inputs
COLOR_PORT_OUTPUT = QColor("#81C784")  # Light green for outputs
COLOR_PORT = QColor("#90CAF9")  # Default port color for edge dragging
COLOR_TEXT = QColor("#E0E0E0")
COLOR_SHADOW = QColor(0, 0, 0, 60)


class NodePort(QGraphicsObject):
    """A modern port widget with glow effect on hover."""

    def __init__(self, parent, is_output=False):
        super().__init__(parent)
        self.is_output = is_output
        self.hovered = False
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setToolTip("Output" if is_output else "Input")

    def boundingRect(self):
        # Larger bounding rect for glow effect
        return QRectF(-PORT_SIZE / 2 - 4, -PORT_SIZE / 2 - 4,
                      PORT_SIZE + 8, PORT_SIZE + 8)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        base_color = COLOR_PORT_OUTPUT if self.is_output else COLOR_PORT_INPUT

        # Glow effect when hovered
        if self.hovered:
            glow_rect = QRectF(-PORT_SIZE / 2 - 3, -PORT_SIZE / 2 - 3,
                               PORT_SIZE + 6, PORT_SIZE + 6)
            glow_gradient = QRadialGradient(0, 0, PORT_SIZE)
            glow_gradient.setColorAt(0, QColor(base_color.red(), base_color.green(),
                                               base_color.blue(), 150))
            glow_gradient.setColorAt(1, QColor(base_color.red(), base_color.green(),
                                               base_color.blue(), 0))
            painter.setBrush(glow_gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(glow_rect)

        # Main port circle with gradient
        port_rect = QRectF(-PORT_SIZE / 2, -PORT_SIZE / 2, PORT_SIZE, PORT_SIZE)

        port_gradient = QRadialGradient(0, -PORT_SIZE / 4, PORT_SIZE)
        port_gradient.setColorAt(0, base_color.lighter(130))
        port_gradient.setColorAt(1, base_color)

        painter.setBrush(port_gradient)
        painter.setPen(QPen(base_color.darker(120), 1.5))
        painter.drawEllipse(port_rect)

        # Inner highlight
        highlight_rect = QRectF(-PORT_SIZE / 4, -PORT_SIZE / 4,
                                PORT_SIZE / 2, PORT_SIZE / 2)
        painter.setBrush(QColor(255, 255, 255, 60))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(highlight_rect)

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)


class ResizeHandle(QGraphicsItem):
    """A resize handle at the bottom-right corner of a node."""

    HANDLE_SIZE = 12

    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.SizeFDiagCursor)
        self.hovered = False
        self.dragging = False
        self.drag_start_pos = None
        self.drag_start_size = None

    def boundingRect(self):
        return QRectF(0, 0, self.HANDLE_SIZE, self.HANDLE_SIZE)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw resize grip lines
        color = QColor("#888") if self.hovered else QColor("#555")
        painter.setPen(QPen(color, 1.5))

        # Draw diagonal lines
        for i in range(3):
            offset = i * 3 + 3
            painter.drawLine(
                QPointF(self.HANDLE_SIZE - offset, self.HANDLE_SIZE),
                QPointF(self.HANDLE_SIZE, self.HANDLE_SIZE - offset)
            )

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.scenePos()
            parent = self.parentItem()
            self.drag_start_size = (parent.width, parent.height)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.scenePos() - self.drag_start_pos
            parent = self.parentItem()

            new_width = max(NODE_WIDTH, self.drag_start_size[0] + delta.x())
            new_height = max(NODE_MIN_HEIGHT, self.drag_start_size[1] + delta.y())

            parent.resize(new_width, new_height)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class NodeWidget(QGraphicsObject):
    """A modern node widget with gradient background and category-based colors."""

    node_selected = Signal(str)
    parameter_changed = Signal(str, str, object)  # node_id, param_name, value
    file_select_requested = Signal(str, str)  # node_id, param_name
    save_requested = Signal(str)  # node_id

    def __init__(self, node_id, node_name, category="Uncategorized", parameters=None, is_output_node=False):
        super().__init__()
        self.node_id = node_id
        self.node_name = node_name
        self.category = category
        self.parameters = parameters or {}
        self.param_widgets = {}
        self.is_output_node = is_output_node
        self.preview_pixmap = None

        # Set size based on node type
        if is_output_node:
            self.width = OUTPUT_NODE_WIDTH
            self.height = OUTPUT_NODE_HEIGHT
        else:
            self.width = NODE_WIDTH
            # Calculate dynamic height based on parameters
            param_count = len(self.parameters)
            body_height = max(NODE_MIN_HEIGHT - NODE_HEADER_HEIGHT, param_count * PARAM_ROW_HEIGHT + PARAM_PADDING * 2)
            self.height = NODE_HEADER_HEIGHT + body_height

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        # Create ports (horizontal layout: input on left, output on right)
        self.input_port = NodePort(self, is_output=False)
        self.input_port.setPos(0, self.height / 2)

        self.output_port = NodePort(self, is_output=True)
        self.output_port.setPos(self.width, self.height / 2)

        # Create resize handle
        self.resize_handle = ResizeHandle(self)
        self._update_resize_handle_pos()

        # Create embedded parameter widgets or output preview
        if is_output_node:
            self._setup_output_widgets()
        else:
            self._setup_parameter_widgets()

    def _setup_output_widgets(self):
        """Setup widgets for Output node: preview area and save button."""
        # Save button at the bottom
        save_btn = QPushButton("Save Image")
        save_btn.setFixedSize(int(self.width - 20), 24)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #2D7D46; border: none;
                border-radius: 4px; color: #FFF; font-size: 10px; font-weight: bold;
            }
            QPushButton:hover { background: #3D8D56; }
            QPushButton:disabled { background: #555; color: #888; }
        """)
        save_btn.setEnabled(False)
        save_btn.clicked.connect(lambda: self.save_requested.emit(self.node_id))

        proxy = QGraphicsProxyWidget(self)
        proxy.setWidget(save_btn)
        proxy.setPos(10, self.height - 34)
        self.save_button = save_btn

    def set_preview_image(self, np_image):
        """Set the preview image for Output node."""
        if not self.is_output_node or np_image is None:
            return

        h, w = np_image.shape[:2]
        bytes_per_line = w * (1 if len(np_image.shape) == 2 else 3)
        fmt = QImage.Format_Grayscale8 if len(np_image.shape) == 2 else QImage.Format_RGB888

        # Make a copy of the image data to ensure it persists
        img_copy = np_image.copy()
        q_image = QImage(img_copy.data, w, h, bytes_per_line, fmt)
        self.preview_pixmap = QPixmap.fromImage(q_image.copy())

        # Enable save button
        self.save_button.setEnabled(True)
        self.update()

    def _update_resize_handle_pos(self):
        """Update resize handle position to bottom-right corner."""
        self.resize_handle.setPos(
            self.width - ResizeHandle.HANDLE_SIZE,
            self.height - ResizeHandle.HANDLE_SIZE
        )

    def resize(self, new_width, new_height):
        """Resize the node to new dimensions."""
        self.prepareGeometryChange()
        self.width = new_width
        self.height = new_height

        # Update port positions
        self.update_port_positions()

        # Update resize handle position
        self._update_resize_handle_pos()

        self.update()

    def set_size(self, width, height):
        """Set the node size (alias for resize, used when loading workflows)."""
        self.resize(width, height)

    def _setup_parameter_widgets(self):
        """Create embedded widgets for each parameter."""
        if not self.parameters:
            return

        y_offset = NODE_HEADER_HEIGHT + PARAM_PADDING

        for name, props in self.parameters.items():
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            layout = QHBoxLayout(container)
            layout.setContentsMargins(4, 0, 4, 0)
            layout.setSpacing(4)

            # Label
            label = QLabel(name[:8] + ":" if len(name) > 8 else name + ":")
            label.setStyleSheet("color: #AAA; font-size: 9px; background: transparent;")
            label.setFixedWidth(50)
            layout.addWidget(label)

            # Widget based on type
            widget = self._create_param_widget(name, props)
            if widget:
                layout.addWidget(widget)
                self.param_widgets[name] = widget

            container.setFixedSize(int(self.width - 20), PARAM_ROW_HEIGHT - 4)

            proxy = QGraphicsProxyWidget(self)
            proxy.setWidget(container)
            proxy.setPos(10, y_offset)

            y_offset += PARAM_ROW_HEIGHT

    def _create_param_widget(self, name, props):
        """Create appropriate widget for parameter type."""
        param_type = props.get('type')
        value = props.get('value')

        if param_type == 'int':
            widget = QSpinBox()
            widget.setFixedHeight(20)
            widget.setStyleSheet("""
                QSpinBox {
                    background: #3A3A3A; border: 1px solid #555;
                    border-radius: 3px; color: #DDD; font-size: 9px;
                }
            """)
            if 'range' in props:
                widget.setRange(*props['range'])
            if 'step' in props:
                widget.setSingleStep(props['step'])
            widget.setValue(value if value is not None else 0)
            widget.valueChanged.connect(
                lambda v, n=name: self.parameter_changed.emit(self.node_id, n, v)
            )
            return widget

        elif param_type == 'float':
            widget = QDoubleSpinBox()
            widget.setFixedHeight(20)
            widget.setStyleSheet("""
                QDoubleSpinBox {
                    background: #3A3A3A; border: 1px solid #555;
                    border-radius: 3px; color: #DDD; font-size: 9px;
                }
            """)
            if 'range' in props:
                widget.setRange(*props['range'])
            if 'step' in props:
                widget.setSingleStep(props['step'])
            widget.setValue(value if value is not None else 0.0)
            widget.valueChanged.connect(
                lambda v, n=name: self.parameter_changed.emit(self.node_id, n, v)
            )
            return widget

        elif param_type == 'filepath':
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.setSpacing(2)

            # File name label (elided)
            file_label = QLabel()
            file_label.setStyleSheet("color: #8CF; font-size: 9px; background: transparent;")
            if value:
                filename = Path(value).name
                # Elide if too long
                metrics = QFontMetrics(file_label.font())
                elided = metrics.elidedText(filename, Qt.ElideMiddle, 70)
                file_label.setText(elided)
                file_label.setToolTip(str(value))
            else:
                file_label.setText("No file")
            h_layout.addWidget(file_label)

            # Browse button
            btn = QPushButton("...")
            btn.setFixedSize(24, 18)
            btn.setStyleSheet("""
                QPushButton {
                    background: #4A4A4A; border: 1px solid #555;
                    border-radius: 3px; color: #DDD; font-size: 9px;
                }
                QPushButton:hover { background: #5A5A5A; }
            """)
            btn.clicked.connect(lambda _, n=name: self.file_select_requested.emit(self.node_id, n))
            h_layout.addWidget(btn)

            # Store reference to update later
            self.param_widgets[name + "_label"] = file_label
            return container

        return None

    def update_filepath_display(self, param_name, filepath):
        """Update the displayed filename after file selection."""
        label_key = param_name + "_label"
        if label_key in self.param_widgets:
            label = self.param_widgets[label_key]
            if filepath:
                filename = Path(filepath).name
                metrics = QFontMetrics(label.font())
                elided = metrics.elidedText(filename, Qt.ElideMiddle, 70)
                label.setText(elided)
                label.setToolTip(str(filepath))
            else:
                label.setText("No file")
                label.setToolTip("")

    def update_port_positions(self):
        """Update port positions after height change."""
        self.input_port.setPos(0, self.height / 2)
        self.output_port.setPos(self.width, self.height / 2)
        if self.scene():
            self.scene().update_edges_for_node(self)

    def boundingRect(self):
        # Include space for shadow
        return QRectF(-2, -2, self.width + 8, self.height + 8)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        colors = CATEGORY_COLORS.get(self.category, CATEGORY_COLORS["Uncategorized"])

        # 1. Draw shadow
        shadow_rect = QRectF(3, 3, self.width, self.height)
        painter.setBrush(COLOR_SHADOW)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(shadow_rect, 10, 10)

        # 2. Draw main body with gradient
        body_rect = QRectF(0, 0, self.width, self.height)
        body_gradient = QLinearGradient(0, 0, 0, self.height)
        body_gradient.setColorAt(0, COLOR_NODE_BODY)
        body_gradient.setColorAt(1, COLOR_NODE_BODY_GRADIENT)
        painter.setBrush(body_gradient)

        border_color = COLOR_NODE_BORDER_SELECTED if self.isSelected() else COLOR_NODE_BORDER
        border_width = 2 if self.isSelected() else 1
        painter.setPen(QPen(border_color, border_width))
        painter.drawRoundedRect(body_rect, 10, 10)

        # 3. Draw header with gradient
        header_rect = QRectF(0, 0, self.width, NODE_HEADER_HEIGHT)
        header_gradient = QLinearGradient(0, 0, 0, NODE_HEADER_HEIGHT)
        header_gradient.setColorAt(0, colors["header"])
        header_gradient.setColorAt(1, colors["header_gradient"])

        # Create header path with rounded top corners only
        header_path = QPainterPath()
        header_path.moveTo(0, NODE_HEADER_HEIGHT)
        header_path.lineTo(0, 10)
        header_path.arcTo(QRectF(0, 0, 20, 20), 180, -90)
        header_path.lineTo(self.width - 10, 0)
        header_path.arcTo(QRectF(self.width - 20, 0, 20, 20), 90, -90)
        header_path.lineTo(self.width, NODE_HEADER_HEIGHT)
        header_path.closeSubpath()

        painter.setBrush(header_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawPath(header_path)

        # 4. Draw accent line under header
        painter.setPen(QPen(colors["accent"], 2))
        painter.drawLine(
            QPointF(0, NODE_HEADER_HEIGHT),
            QPointF(self.width, NODE_HEADER_HEIGHT)
        )

        # 5. Draw node name
        font = QFont("Inter", 10, QFont.DemiBold)
        if not font.exactMatch():
            font = QFont("Segoe UI", 10, QFont.DemiBold)
        painter.setFont(font)
        painter.setPen(COLOR_TEXT)

        text_rect = QRectF(8, 0, self.width - 16, NODE_HEADER_HEIGHT)
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, self.node_name)

        # 6. Draw category indicator (small colored dot)
        dot_rect = QRectF(self.width - 14, 8, 6, 6)
        painter.setBrush(colors["accent"])
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(dot_rect)

        # 7. Draw preview image for Output node
        if self.is_output_node:
            preview_rect = QRectF(10, NODE_HEADER_HEIGHT + 8, self.width - 20, OUTPUT_PREVIEW_HEIGHT)

            if self.preview_pixmap:
                # Draw the scaled preview image
                scaled_pixmap = self.preview_pixmap.scaled(
                    int(preview_rect.width()), int(preview_rect.height()),
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                # Center the image in the preview area
                x_offset = (preview_rect.width() - scaled_pixmap.width()) / 2
                y_offset = (preview_rect.height() - scaled_pixmap.height()) / 2
                painter.drawPixmap(
                    int(preview_rect.x() + x_offset),
                    int(preview_rect.y() + y_offset),
                    scaled_pixmap
                )
            else:
                # Draw placeholder
                painter.setBrush(QColor("#1A1A1A"))
                painter.setPen(QPen(QColor("#333"), 1))
                painter.drawRoundedRect(preview_rect, 6, 6)
                painter.setPen(QColor("#666"))
                painter.setFont(QFont("Inter", 9))
                painter.drawText(preview_rect, Qt.AlignCenter, "No Preview\nRun to see output")

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            self.scene().update_edges_for_node(self)
        return super().itemChange(change, value)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        self.node_selected.emit(self.node_id)
        super().mousePressEvent(event)


class EdgeWidget(QGraphicsObject):
    """A modern edge widget with gradient color from output to input."""

    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        self.setZValue(-1)

        # Make edge selectable
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        self.hovered = False

        self.update_path()

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def update_path(self):
        self.prepareGeometryChange()
        p1 = self.start_port.scenePos()
        p2 = self.end_port.scenePos()

        path = QPainterPath(p1)

        # Horizontal Bezier curve calculation
        dx = abs(p2.x() - p1.x())
        offset = min(dx * 0.5, 100)

        ctrl1 = QPointF(p1.x() + offset, p1.y())
        ctrl2 = QPointF(p2.x() - offset, p2.y())
        path.cubicTo(ctrl1, ctrl2, p2)

        self.path = path

    def boundingRect(self):
        return self.path.boundingRect().adjusted(-5, -5, 5, 5)

    def shape(self):
        stroker = QPainterPathStroker()
        stroker.setWidth(12)
        return stroker.createStroke(self.path)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        p1 = self.start_port.scenePos()
        p2 = self.end_port.scenePos()

        # Draw selection/hover highlight
        if self.isSelected():
            highlight_pen = QPen(QColor("#FFB300"), 4)
            highlight_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(highlight_pen)
            painter.drawPath(self.path)
        elif self.hovered:
            highlight_pen = QPen(QColor(255, 255, 255, 80), 4)
            highlight_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(highlight_pen)
            painter.drawPath(self.path)

        # Draw shadow
        shadow_pen = QPen(QColor(0, 0, 0, 30), 5)
        shadow_pen.setCapStyle(Qt.RoundCap)
        shadow_path = QPainterPath(self.path)
        shadow_path.translate(1.5, 1.5)
        painter.setPen(shadow_pen)
        painter.drawPath(shadow_path)

        # Draw gradient edge (output color to input color)
        edge_gradient = QLinearGradient(p1, p2)
        edge_gradient.setColorAt(0, COLOR_PORT_OUTPUT)
        edge_gradient.setColorAt(1, COLOR_PORT_INPUT)

        edge_pen = QPen(QBrush(edge_gradient), 2.5)
        edge_pen.setCapStyle(Qt.RoundCap)
        edge_pen.setJoinStyle(Qt.RoundJoin)

        painter.setPen(edge_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path)
