from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QConicalGradient


class LoadingSpinner(QWidget):
    """An animated circular loading spinner."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(64, 64)
        self._angle = 0
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.timer.setInterval(16)  # ~60 FPS

    def _rotate(self):
        self._angle = (self._angle + 6) % 360
        self.update()

    def start(self):
        self._angle = 0
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Center the spinner
        side = min(self.width(), self.height())
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._angle)

        # Draw spinning arc with gradient
        gradient = QConicalGradient(0, 0, 0)
        gradient.setColorAt(0, QColor("#007ACC"))
        gradient.setColorAt(0.7, QColor("#007ACC"))
        gradient.setColorAt(1, QColor(0, 122, 204, 0))

        pen = QPen(gradient, 5)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(
            int(-side / 2 + 8), int(-side / 2 + 8),
            int(side - 16), int(side - 16),
            0, 270 * 16
        )


class LoadingOverlay(QWidget):
    """A semi-transparent overlay with spinner, progress bar, and message."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background-color: rgba(30, 30, 30, 220);")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)

        self.spinner = LoadingSpinner()
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        self.message_label = QLabel("Processing...")
        self.message_label.setStyleSheet("""
            color: #E0E0E0;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        """)
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(300)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #444;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #007ACC;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        # Percent label
        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet("""
            color: #007ACC;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)
        self.percent_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.percent_label)

        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("""
            color: #888888;
            font-size: 12px;
            background: transparent;
        """)
        self.detail_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.detail_label)

        self.hide()

    def show_loading(self, message="Processing...", detail=""):
        self.message_label.setText(message)
        self.detail_label.setText(detail)
        self.progress_bar.setValue(0)
        self.percent_label.setText("0%")
        self.spinner.start()
        self.show()
        self.raise_()

    def hide_loading(self):
        self.spinner.stop()
        self.hide()

    def set_message(self, message):
        self.message_label.setText(message)

    def set_detail(self, detail):
        self.detail_label.setText(detail)

    def set_progress(self, percent):
        """Set the progress bar value (0-100)."""
        self.progress_bar.setValue(percent)
        self.percent_label.setText(f"{percent}%")
