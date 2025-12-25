from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTreeWidget, QTreeWidgetItem,
    QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon


class NodePalette(QWidget):
    """A searchable, categorized node palette widget."""

    node_double_clicked = Signal(str)  # Emits node name

    # Category display order and icons
    CATEGORY_ORDER = [
        ("Basic I/O", "node_editor/icons/image.svg"),
        ("Image Processing", "node_editor/icons/tune.svg"),
        ("AI / Machine Learning", "node_editor/icons/brain.svg"),
    ]

    def __init__(self, node_categories, parent=None):
        super().__init__(parent)
        self.node_categories = node_categories
        self.all_items = []  # Store references for search
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search nodes...")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.textChanged.connect(self._filter_nodes)
        layout.addWidget(self.search_box)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(16)
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree.setExpandsOnDoubleClick(False)
        layout.addWidget(self.tree)

        self._populate_tree()

    def _populate_tree(self):
        """Populate the tree with categorized nodes."""
        self.tree.clear()
        self.all_items = []
        self.category_items = {}

        # Add categories in defined order
        for category_name, icon_path in self.CATEGORY_ORDER:
            if category_name not in self.node_categories:
                continue

            category_item = QTreeWidgetItem([category_name])
            category_item.setIcon(0, QIcon(icon_path))
            category_item.setFlags(category_item.flags() & ~Qt.ItemIsSelectable)
            category_item.setExpanded(True)

            # Add nodes under this category
            for node_name in sorted(self.node_categories[category_name]):
                node_item = QTreeWidgetItem([node_name])
                node_item.setData(0, Qt.UserRole, node_name)
                category_item.addChild(node_item)
                self.all_items.append((node_item, node_name.lower(), category_item))

            self.tree.addTopLevelItem(category_item)
            self.category_items[category_name] = category_item

        # Add any uncategorized nodes
        remaining = set(self.node_categories.keys()) - {c[0] for c in self.CATEGORY_ORDER}
        for category_name in remaining:
            category_item = QTreeWidgetItem([category_name])
            category_item.setFlags(category_item.flags() & ~Qt.ItemIsSelectable)
            category_item.setExpanded(True)

            for node_name in sorted(self.node_categories[category_name]):
                node_item = QTreeWidgetItem([node_name])
                node_item.setData(0, Qt.UserRole, node_name)
                category_item.addChild(node_item)
                self.all_items.append((node_item, node_name.lower(), category_item))

            self.tree.addTopLevelItem(category_item)
            self.category_items[category_name] = category_item

    def _filter_nodes(self, text):
        """Filter nodes based on search text."""
        search_text = text.lower().strip()

        if not search_text:
            # Show all items
            for item, _, category in self.all_items:
                item.setHidden(False)
            for cat_item in self.category_items.values():
                cat_item.setHidden(False)
                cat_item.setExpanded(True)
            return

        # Hide non-matching items
        visible_categories = set()
        for item, name, category in self.all_items:
            matches = search_text in name
            item.setHidden(not matches)
            if matches:
                visible_categories.add(category)
                category.setExpanded(True)

        # Hide empty categories
        for cat_item in self.category_items.values():
            cat_item.setHidden(cat_item not in visible_categories)

    def _on_item_double_clicked(self, item, column):
        """Handle node item double-click."""
        node_name = item.data(0, Qt.UserRole)
        if node_name:  # Not a category header
            self.node_double_clicked.emit(node_name)

    def refresh(self, node_categories):
        """Refresh the palette with new categories."""
        self.node_categories = node_categories
        self._populate_tree()
