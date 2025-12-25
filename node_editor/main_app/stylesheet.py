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

/* Tree Widget for Node Palette */
QTreeWidget {
    background-color: #2E2E2E;
    border: 1px solid #444444;
    border-radius: 4px;
    outline: 0;
    padding: 4px;
}

QTreeWidget::item {
    padding: 6px 8px;
    border-radius: 4px;
    margin: 1px 0;
}

QTreeWidget::item:hover {
    background-color: #3A3A3A;
}

QTreeWidget::item:selected {
    background-color: #007ACC;
    color: #FFFFFF;
}

QTreeWidget::branch {
    background-color: transparent;
}

QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {
    image: url(node_editor/icons/chevron-right.svg);
}

QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {
    image: url(node_editor/icons/chevron-down.svg);
}

/* Search Box */
QLineEdit {
    background-color: #3C3C3C;
    border: 1px solid #555555;
    padding: 8px 12px;
    border-radius: 6px;
    selection-background-color: #007ACC;
}

QLineEdit:focus {
    border-color: #007ACC;
}

QLineEdit::placeholder {
    color: #888888;
}

/* List Widget (fallback) */
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

/* Buttons */
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

/* Spinboxes */
QSpinBox, QDoubleSpinBox {
    background-color: #3C3C3C;
    border: 1px solid #555555;
    padding: 6px;
    border-radius: 4px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #007ACC;
}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #4A4A4A;
    border: none;
    width: 16px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #5A5A5A;
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

/* Scrollbars */
QScrollBar:vertical {
    background-color: #2E2E2E;
    width: 12px;
    margin: 0;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #555555;
    min-height: 30px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
    background: none;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background-color: #2E2E2E;
    height: 12px;
    margin: 0;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #555555;
    min-width: 30px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #666666;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
    background: none;
}

/* Tooltip */
QToolTip {
    background-color: #3C3C3C;
    color: #E0E0E0;
    border: 1px solid #555555;
    padding: 6px 10px;
    border-radius: 4px;
}

/* Splitter */
QSplitter::handle {
    background-color: #444444;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #007ACC;
}

/* Message Box */
QMessageBox {
    background-color: #2E2E2E;
}

QMessageBox QLabel {
    color: #E0E0E0;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* Menu Bar */
QMenuBar {
    background-color: #2E2E2E;
    border-bottom: 1px solid #444444;
}

QMenuBar::item {
    padding: 6px 12px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #3A3A3A;
}

QMenu {
    background-color: #2E2E2E;
    border: 1px solid #444444;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #007ACC;
}
"""
