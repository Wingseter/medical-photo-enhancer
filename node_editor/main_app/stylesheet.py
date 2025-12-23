STYLESHEET = """
QWidget {
    background-color: #2E2E2E;
    color: #E0E0E0;
    font-family: "Inter Variable", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
}

QMainWindow, QDockWidget {
    background-color: #252525;
    border: none;
}

QDockWidget::title {
    background-color: #383838;
    color: #E0E0E0;
    text-align: center;
    padding: 8px;
    font-weight: bold;
    border: 1px solid #222222;
    border-radius: 4px;
}

QListWidget {
    background-color: #2E2E2E;
    border: 1px solid #444444;
    padding: 5px;
    outline: 0;
}

QListWidget::item {
    padding: 8px 12px;
    border-radius: 4px;
}

QListWidget::item:hover {
    background-color: #3A3A3A;
}

QListWidget::item:selected {
    background-color: #007ACC;
    color: #FFFFFF;
    font-weight: bold;
}

QPushButton {
    background-color: #4A4A4A;
    border: 1px solid #555555;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #5A5A5A;
    border-color: #666666;
}

QPushButton:pressed {
    background-color: #007ACC;
    border-color: #007ACC;
}

QPushButton:disabled {
    background-color: #404040;
    color: #888888;
    border-color: #555555;
}

QSpinBox, QDoubleSpinBox {
    background-color: #3C3C3C;
    border: 1px solid #555555;
    padding: 6px;
    border-radius: 4px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #007ACC;
}

QLabel {
    background-color: transparent;
}

QFormLayout {
    background-color: transparent;
    spacing: 10px;
}

QGraphicsView {
    border: 1px solid #444444;
    background-color: #282828;
}
"""
