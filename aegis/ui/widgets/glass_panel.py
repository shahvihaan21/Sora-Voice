from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen

class GlassPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GlassPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 16, 20, 20)
        self.layout.setSpacing(12)
        
    def add_widget(self, widget):
        self.layout.addWidget(widget)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw sleek dark rounded container
        rect = self.rect().adjusted(1, 1, -1, -1)
        
        # Obsidian dark backdrop
        painter.setBrush(QBrush(QColor(11, 15, 23, 245)))
        # Subtle rim border
        pen = QPen(QColor(255, 255, 255, 22))
        pen.setWidth(1)
        painter.setPen(pen)
        
        painter.drawRoundedRect(rect, 22, 22)
