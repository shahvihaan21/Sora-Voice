import asyncio
import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QHBoxLayout, QTextEdit, QLineEdit, QFrame
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject
from PyQt6.QtGui import QTextCursor

from ui.styles import MAIN_STYLE
from ui.widgets.glass_panel import GlassPanel
from ui.widgets.visualizer import AudioVisualizer, VisualizerMode
from core.config import config

class MainWindow(QMainWindow):
    user_command_submitted = pyqtSignal(str)
    voice_trigger_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        # Setup frameless and transparent window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.resize(760, 630)
        self.setMinimumSize(620, 520)
        
        # Apply global stylesheet
        self.setStyleSheet(MAIN_STYLE)
        
        # Central widget and layout
        self.central_widget = QWidget()
        self.central_widget.setObjectName("MainWindow")
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Glass Panel Container
        self.glass_panel = GlassPanel()
        main_layout.addWidget(self.glass_panel)
        
        self.setup_ui(self.glass_panel.layout)
        
        # Window dragging state
        self.drag_position = QPoint()

    def setup_ui(self, layout):
        # 1. Header Area & Sleek Window Controls
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(4, 0, 4, 0)
        
        self.lbl_title = QLabel("SORA")
        self.lbl_title.setObjectName("HeaderBrand")
        header_layout.addWidget(self.lbl_title)
        
        self.lbl_status = QLabel("● STANDBY")
        self.lbl_status.setObjectName("StatusBadge")
        self.lbl_status.setProperty("mode", VisualizerMode.IDLE)
        header_layout.addWidget(self.lbl_status)
        
        self.lbl_hint = QLabel("Ready • Say 'Hey Sora' or type below")
        self.lbl_hint.setObjectName("ActionHint")
        self.lbl_hint.setStyleSheet("margin-left: 8px;")
        header_layout.addWidget(self.lbl_hint)
        
        header_layout.addStretch()
        
        # Window Controls (— □ ✕)
        self.btn_min = QPushButton("—")
        self.btn_min.setProperty("class", "WindowControl")
        self.btn_min.setFixedSize(30, 26)
        self.btn_min.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_min.clicked.connect(self.showMinimized)
        header_layout.addWidget(self.btn_min)
        
        self.btn_max = QPushButton("□")
        self.btn_max.setProperty("class", "WindowControl")
        self.btn_max.setFixedSize(30, 26)
        self.btn_max.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max.clicked.connect(self.toggle_maximize)
        header_layout.addWidget(self.btn_max)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("BtnClose")
        self.btn_close.setProperty("class", "WindowControl")
        self.btn_close.setFixedSize(30, 26)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.close)
        header_layout.addWidget(self.btn_close)
        
        layout.addLayout(header_layout)
        
        # 2. Siri / Apple Intelligence Harmonic Fluid Wave Visualizer
        self.visualizer = AudioVisualizer()
        layout.addWidget(self.visualizer)
        
        # 3. Conversation Log Display
        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("ChatDisplay")
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display, stretch=1)
        
        # 4. Replicated Bottom Pill Input Bar
        self.pill_container = QFrame()
        self.pill_container.setObjectName("PillInputContainer")
        self.pill_container.setFixedHeight(56)
        self.pill_container.setProperty("mode", VisualizerMode.IDLE)
        
        pill_layout = QHBoxLayout(self.pill_container)
        pill_layout.setContentsMargins(8, 6, 8, 6)
        pill_layout.setSpacing(10)
        
        # Left '+' Action Button
        self.btn_plus = QPushButton("+")
        self.btn_plus.setObjectName("BtnPlus")
        self.btn_plus.setFixedSize(40, 40)
        self.btn_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_plus.setToolTip("Click to trigger voice listening mode")
        self.btn_plus.clicked.connect(self.on_plus_clicked)
        pill_layout.addWidget(self.btn_plus)
        
        # Center Text Input with Context Placeholder
        self.input_cmd = QLineEdit()
        self.input_cmd.setObjectName("PillInput")
        self.input_cmd.setPlaceholderText("Write your prompt here..")
        self.input_cmd.returnPressed.connect(self.on_send_command)
        pill_layout.addWidget(self.input_cmd, stretch=1)
        
        # Right Circular Gradient '↑' Send Button
        self.btn_send = QPushButton("↑")
        self.btn_send.setObjectName("BtnSendGradient")
        self.btn_send.setFixedSize(40, 40)
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self.on_send_command)
        pill_layout.addWidget(self.btn_send)
        
        layout.addWidget(self.pill_container)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def set_system_status(self, text: str, mode: str = VisualizerMode.IDLE):
        """Update the status label badge, visualizer mode, action hint, and container cues."""
        status_map = {
            VisualizerMode.IDLE: ("● STANDBY", "Ready • Say 'Hey Sora' or write below"),
            VisualizerMode.LISTENING: ("🎙 LISTENING...", "Listening to your voice... Speak now"),
            VisualizerMode.THINKING: ("✦ THINKING...", "Sora is processing your request..."),
            VisualizerMode.SPEAKING: ("🔊 SPEAKING...", "Sora is speaking..."),
        }
        
        label_text, hint_text = status_map.get(mode, (text.upper(), ""))
        self.lbl_status.setText(label_text)
        self.lbl_hint.setText(hint_text)
        
        self.lbl_status.setProperty("mode", mode)
        self.pill_container.setProperty("mode", mode)
        
        is_listening = (mode == VisualizerMode.LISTENING)
        self.btn_plus.setProperty("active", "true" if is_listening else "false")
        self.btn_plus.setText("🎙" if is_listening else "+")
        
        if is_listening:
            self.input_cmd.setPlaceholderText("Listening to your voice...")
        elif mode == VisualizerMode.THINKING:
            self.input_cmd.setPlaceholderText("Formulating response...")
        else:
            self.input_cmd.setPlaceholderText("Write your prompt here..")
            
        # Re-apply stylesheet state
        for widget in [self.lbl_status, self.pill_container, self.btn_plus]:
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            
        self.visualizer.set_mode(mode)

    def append_message(self, sender: str, text: str):
        """Append a formatted message to the chat transcript."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        if sender.lower() in ["sora", "aegis", "jarvis"]:
            formatted = (
                f"<div style='margin-bottom: 10px;'>"
                f"<span style='color: #c084fc; font-weight: 700;'>[ Sora ]</span> "
                f"<span style='color: #64748b; font-size: 11px;'>{timestamp}</span><br>"
                f"<span style='color: #f8fafc; font-size: 13px; line-height: 1.5;'>{text}</span>"
                f"</div>"
            )
        else:
            formatted = (
                f"<div style='margin-bottom: 10px; text-align: right;'>"
                f"<span style='color: #38bdf8; font-weight: 700;'>[ You ]</span> "
                f"<span style='color: #64748b; font-size: 11px;'>{timestamp}</span><br>"
                f"<span style='color: #e2e8f0; font-size: 13px; line-height: 1.5;'>{text}</span>"
                f"</div>"
            )
        self.chat_display.append(formatted)
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

    def on_plus_clicked(self):
        """Handle '+' button click to toggle instant voice listening."""
        self.voice_trigger_requested.emit()

    def on_send_command(self):
        text = self.input_cmd.text().strip()
        if text:
            self.input_cmd.clear()
            self.user_command_submitted.emit(text)

    # --- Frameless Window Dragging ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
