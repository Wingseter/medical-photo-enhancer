import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase
from node_editor.main_app.main_window import MainWindow
from node_editor.main_app.stylesheet import STYLESHEET

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    font_path = os.path.join(os.path.dirname(__file__), "node_editor/fonts/InterVariable.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id == -1:
        print(f"Warning: Could not load Inter font from {font_path}")
        
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
