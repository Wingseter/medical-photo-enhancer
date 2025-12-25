"""
Main Window - Hosts the tabbed interface with Runner and Editor pages.
"""
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QIcon

from node_editor.main_app.tab_container import DetachableTabWidget
from node_editor.main_app.runner_page import WorkflowRunnerPage
from node_editor.main_app.editor_page import NodeEditorPage
from node_editor.main_app.compare_page import ImageComparePage


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Node-Based Image Processor")
        self.setGeometry(100, 100, 1600, 900)

        # Create tab container
        self.tab_container = DetachableTabWidget()
        self.setCentralWidget(self.tab_container)

        # Create pages
        self.runner_page = WorkflowRunnerPage()
        self.editor_page = NodeEditorPage()
        self.compare_page = ImageComparePage()

        # Add tabs (Runner first as default)
        self.tab_container.addTab(
            self.runner_page,
            QIcon("node_editor/icons/play.svg"),
            "Workflow Runner"
        )
        self.tab_container.addTab(
            self.editor_page,
            QIcon("node_editor/icons/tune.svg"),
            "Node Editor"
        )
        self.tab_container.addTab(
            self.compare_page,
            QIcon("node_editor/icons/compare.svg"),
            "Image Compare"
        )

        # Connect signals
        self.runner_page.new_workflow_requested.connect(self._switch_to_editor)
        self.runner_page.edit_workflow_requested.connect(self._edit_workflow)
        self.editor_page.workflow_saved.connect(self._on_workflow_saved)

        self.create_menus()

    def create_menus(self):
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        new_workflow_action = QAction("New Workflow", self)
        new_workflow_action.setShortcut("Ctrl+N")
        new_workflow_action.triggered.connect(self._switch_to_editor)
        file_menu.addAction(new_workflow_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = menu_bar.addMenu("View")

        runner_action = QAction("Workflow Runner", self)
        runner_action.setShortcut("Ctrl+1")
        runner_action.triggered.connect(lambda: self.tab_container.setCurrentWidget(self.runner_page))
        view_menu.addAction(runner_action)

        editor_action = QAction("Node Editor", self)
        editor_action.setShortcut("Ctrl+2")
        editor_action.triggered.connect(lambda: self.tab_container.setCurrentWidget(self.editor_page))
        view_menu.addAction(editor_action)

        compare_action = QAction("Image Compare", self)
        compare_action.setShortcut("Ctrl+3")
        compare_action.triggered.connect(lambda: self.tab_container.setCurrentWidget(self.compare_page))
        view_menu.addAction(compare_action)

    @Slot()
    def _switch_to_editor(self):
        """Switch to the editor tab."""
        self.tab_container.setCurrentWidget(self.editor_page)

    @Slot(str)
    def _edit_workflow(self, filepath):
        """Load a workflow in the editor for editing."""
        self.editor_page.load_workflow_from_file(filepath)
        self.tab_container.setCurrentWidget(self.editor_page)

    @Slot()
    def _on_workflow_saved(self):
        """Refresh runner page when a workflow is saved."""
        self.runner_page.refresh_workflows()

    def closeEvent(self, event):
        """Cleanup when closing the app."""
        self.tab_container.close_all_detached()
        self.runner_page.cleanup()
        self.editor_page.cleanup()
        event.accept()
