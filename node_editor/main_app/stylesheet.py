STYLESHEET = """
QWidget {
    background-color: #2D3142;
    color: #E8EAF0;
    font-family: "Inter Variable", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 12pt;
}

QMainWindow, QDockWidget {
    background-color: #252836;
    border: none;
}

QDockWidget::title {
    background-color: #3D4259;
    color: #E8EAF0;
    text-align: center;
    padding: 8px;
    font-weight: bold;
    border: 1px solid #2A2D3E;
    border-radius: 4px;
}

/* Tree Widget for Node Palette */
QTreeWidget {
    background-color: #2D3142;
    border: 1px solid #3D4259;
    border-radius: 6px;
    outline: 0;
    padding: 4px;
}

QTreeWidget::item {
    padding: 10px 12px;
    border-radius: 4px;
    margin: 2px 0;
}

QTreeWidget::item:hover {
    background-color: #3D4259;
}

QTreeWidget::item:selected {
    background-color: #5C6BC0;
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
    background-color: #353849;
    border: 1px solid #4A4F6A;
    padding: 10px 14px;
    border-radius: 6px;
    selection-background-color: #5C6BC0;
    font-size: 12pt;
}

QLineEdit:focus {
    border-color: #7986CB;
}

QLineEdit::placeholder {
    color: #8890A8;
}

/* List Widget (fallback) */
QListWidget {
    background-color: #2D3142;
    border: 1px solid #3D4259;
    padding: 5px;
    outline: 0;
}

QListWidget::item {
    padding: 8px 12px;
    border-radius: 4px;
}

QListWidget::item:hover {
    background-color: #3D4259;
}

QListWidget::item:selected {
    background-color: #5C6BC0;
    color: #FFFFFF;
    font-weight: bold;
}

/* Buttons */
QPushButton {
    background-color: #3D4259;
    border: 1px solid #4A4F6A;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 12pt;
}

QPushButton:hover {
    background-color: #4A5175;
    border-color: #5C6BC0;
}

QPushButton:pressed {
    background-color: #5C6BC0;
    border-color: #7986CB;
}

QPushButton:disabled {
    background-color: #353849;
    color: #6B7394;
    border-color: #3D4259;
}

/* Spinboxes */
QSpinBox, QDoubleSpinBox {
    background-color: #353849;
    border: 1px solid #4A4F6A;
    padding: 6px;
    border-radius: 4px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #7986CB;
}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #3D4259;
    border: none;
    width: 16px;
}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #4A5175;
}

QLabel {
    background-color: transparent;
}

QFormLayout {
    background-color: transparent;
    spacing: 10px;
}

QGraphicsView {
    border: 1px solid #3D4259;
    background-color: #252836;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #2D3142;
    width: 12px;
    margin: 0;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #4A4F6A;
    min-height: 30px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5C6BC0;
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
    background-color: #2D3142;
    height: 12px;
    margin: 0;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #4A4F6A;
    min-width: 30px;
    border-radius: 6px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #5C6BC0;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
    background: none;
}

/* Tooltip */
QToolTip {
    background-color: #3D4259;
    color: #E8EAF0;
    border: 1px solid #5C6BC0;
    padding: 6px 10px;
    border-radius: 4px;
}

/* Splitter */
QSplitter::handle {
    background-color: #3D4259;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #7986CB;
}

/* Message Box */
QMessageBox {
    background-color: #2D3142;
}

QMessageBox QLabel {
    color: #E8EAF0;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* Menu Bar */
QMenuBar {
    background-color: #2D3142;
    border-bottom: 1px solid #3D4259;
}

QMenuBar::item {
    padding: 6px 12px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #3D4259;
}

QMenu {
    background-color: #2D3142;
    border: 1px solid #3D4259;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #5C6BC0;
}

/* Tab Widget */
QTabWidget::pane {
    border: none;
    background-color: #252836;
}

QTabBar {
    background-color: #2D3142;
}

QTabBar::tab {
    background-color: #353849;
    color: #9BA3C2;
    padding: 14px 28px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    min-width: 150px;
    font-size: 13pt;
}

QTabBar::tab:selected {
    background-color: #252836;
    color: #E8EAF0;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #3D4259;
    color: #C5CAE9;
}

/* Progress Bar */
QProgressBar {
    background-color: #353849;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #5C6BC0;
    border-radius: 4px;
}

/* Input Dialog */
QInputDialog {
    background-color: #2D3142;
}

QInputDialog QLabel {
    color: #E8EAF0;
}

QInputDialog QLineEdit {
    min-width: 300px;
}
"""
