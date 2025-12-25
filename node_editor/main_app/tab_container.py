"""
Detachable Tab Widget that allows tabs to be dragged out into separate windows.
"""
from PySide6.QtWidgets import QTabWidget, QTabBar, QMainWindow
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon


class DetachableTabBar(QTabBar):
    """Custom tab bar that allows dragging tabs to detach them."""

    detach_requested = Signal(int)  # tab index

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self._drag_start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start_pos is None:
            return super().mouseMoveEvent(event)

        # Check if dragged outside tab bar bounds
        if not self.rect().contains(event.pos()):
            tab_index = self.tabAt(self._drag_start_pos)
            if tab_index >= 0:
                self.detach_requested.emit(tab_index)
                self._drag_start_pos = None
                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None
        super().mouseReleaseEvent(event)


class DetachedWindow(QMainWindow):
    """Window for a detached tab."""

    reattach_requested = Signal(object, str, object)  # widget, title, icon

    def __init__(self, widget, title, icon, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        if icon:
            self.setWindowIcon(icon)
        self.setCentralWidget(widget)
        self.resize(1400, 800)
        self._widget = widget
        self._title = title
        self._icon = icon

    def closeEvent(self, event):
        # On close, reattach to main window
        self.reattach_requested.emit(self._widget, self._title, self._icon)
        event.accept()


class DetachableTabWidget(QTabWidget):
    """Tab widget that allows tabs to be detached into separate windows."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Use custom tab bar
        self._tab_bar = DetachableTabBar(self)
        self.setTabBar(self._tab_bar)
        self._tab_bar.detach_requested.connect(self._detach_tab)

        # Track detached windows
        self._detached_windows = []

        # Store tab icons
        self._tab_icons = {}

    def addTab(self, widget, *args):
        """Override to store icon for later reattachment."""
        if len(args) == 2:
            icon, text = args
            self._tab_icons[id(widget)] = icon
            return super().addTab(widget, icon, text)
        else:
            return super().addTab(widget, *args)

    def _detach_tab(self, index):
        """Detach a tab into a separate window."""
        if self.count() <= 1:
            return  # Keep at least one tab

        widget = self.widget(index)
        title = self.tabText(index)
        icon = self._tab_icons.get(id(widget), QIcon())

        self.removeTab(index)

        window = DetachedWindow(widget, title, icon, self.window())
        window.reattach_requested.connect(self._reattach_tab)
        window.show()

        self._detached_windows.append(window)

    def _reattach_tab(self, widget, title, icon):
        """Reattach a widget from a closed detached window."""
        sender = self.sender()
        if sender in self._detached_windows:
            self._detached_windows.remove(sender)

        if icon:
            self._tab_icons[id(widget)] = icon
            self.addTab(widget, icon, title)
        else:
            self.addTab(widget, title)

    def close_all_detached(self):
        """Close all detached windows without reattaching."""
        for window in self._detached_windows[:]:
            window.reattach_requested.disconnect()
            window.close()
        self._detached_windows.clear()
