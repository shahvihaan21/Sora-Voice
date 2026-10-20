import datetime
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QTextEdit, QFrame
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QTextCursor
from UI.styles import MAIN_STYLE
from UI.widgets.glass_panel import GlassPanel
from UI.widgets.visualizer import AudioVisualizer, VisualizerMode
from UI.widgets.core import AICore


class MainWindow(QMainWindow):
    voice_trigger_requested = pyqtSignal()
    text_submit_requested = pyqtSignal(str)
    cancel_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(780, 860)
        self.setMinimumSize(600, 640)
        self.setStyleSheet(MAIN_STYLE)
        self.central_widget = QWidget()
        self.central_widget.setObjectName("MainWindow")
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.glass_panel = GlassPanel()
        main_layout.addWidget(self.glass_panel)
        self.setup_ui(self.glass_panel.layout)
        self.drag_position = QPoint()
        self._boot()

    def _boot(self):
        # Cheap fade: animate window opacity, no graphics effect left attached.
        self.setWindowOpacity(0.0)
        a = QPropertyAnimation(self, b"windowOpacity", self)
        a.setDuration(450)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start()
        self._boot_anim = a

    def setup_ui(self, layout):
        hl = QHBoxLayout()
        hl.setContentsMargins(4, 0, 4, 0)
        brand = QVBoxLayout()
        self.lbl_title = QLabel("SORA")
        self.lbl_title.setObjectName("HeaderBrand")
        brand.addWidget(self.lbl_title)
        self.lbl_sub = QLabel("LOCAL AI")
        self.lbl_sub.setObjectName("HeaderSub")
        brand.addWidget(self.lbl_sub)
        hl.addLayout(brand)
        hl.addSpacing(10)
        self.lbl_status = QLabel("ONLINE")
        self.lbl_status.setObjectName("StatusBadge")
        self.lbl_status.setProperty("mode", VisualizerMode.IDLE)
        hl.addWidget(self.lbl_status)
        self.lbl_hint = QLabel("Ready")
        self.lbl_hint.setObjectName("ActionHint")
        hl.addWidget(self.lbl_hint)
        hl.addStretch()
        self.btn_min = QPushButton("-")
        self.btn_min.setProperty("class", "WindowControl")
        self.btn_min.setFixedSize(30, 26)
        self.btn_min.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_min.clicked.connect(self.showMinimized)
        hl.addWidget(self.btn_min)
        self.btn_max = QPushButton("+")
        self.btn_max.setProperty("class", "WindowControl")
        self.btn_max.setFixedSize(30, 26)
        self.btn_max.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_max.clicked.connect(self.toggle_maximize)
        hl.addWidget(self.btn_max)
        self.btn_close = QPushButton("x")
        self.btn_close.setObjectName("BtnClose")
        self.btn_close.setProperty("class", "WindowControl")
        self.btn_close.setFixedSize(30, 26)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(self.close)
        hl.addWidget(self.btn_close)
        layout.addLayout(hl)
        self.core = AICore()
        self.core.setFixedSize(240, 240)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(self.core)
        row.addStretch()
        layout.addLayout(row)
        self.lbl_state = QLabel("READY")
        self.lbl_state.setObjectName("StateLabel")
        self.lbl_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_state)
        self.visualizer = AudioVisualizer()
        layout.addWidget(self.visualizer)
        self.lbl_response = QLabel("How can I help?")
        self.lbl_response.setObjectName("ResponseLabel")
        self.lbl_response.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_response.setWordWrap(True)
        layout.addWidget(self.lbl_response)
        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("ChatDisplay")
        self.chat_display.setReadOnly(True)
        self.chat_display.setFixedHeight(130)
        layout.addWidget(self.chat_display, stretch=0)
        self.pill_container = QFrame()
        self.pill_container.setObjectName("PillInputContainer")
        self.pill_container.setFixedHeight(56)
        self.pill_container.setProperty("mode", VisualizerMode.IDLE)
        pl = QHBoxLayout(self.pill_container)
        pl.setContentsMargins(8, 6, 8, 6)
        pl.setSpacing(8)
        self.btn_mic = QPushButton("MIC")
        self.btn_mic.setObjectName("BtnMic")
        self.btn_mic.setFixedSize(64, 38)
        self.btn_mic.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mic.clicked.connect(self.on_mic_clicked)
        pl.addWidget(self.btn_mic)
        self.txt_input = QLineEdit()
        self.txt_input.setObjectName("CmdInput")
        self.txt_input.setPlaceholderText("Ask Sora anything...")
        self.txt_input.returnPressed.connect(self.on_send_clicked)
        pl.addWidget(self.txt_input, stretch=1)
        self.btn_send = QPushButton(">")
        self.btn_send.setObjectName("BtnSend")
        self.btn_send.setFixedSize(44, 38)
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self.on_send_clicked)
        pl.addWidget(self.btn_send)
        layout.addWidget(self.pill_container)
        sl = QHBoxLayout()
        sl.addStretch()
        self.dot_mic = QLabel("MIC -")
        self.dot_mic.setObjectName("SysDot")
        sl.addWidget(self.dot_mic)
        self.dot_ai = QLabel("AI -")
        self.dot_ai.setObjectName("SysDot")
        sl.addWidget(self.dot_ai)
        self.dot_voice = QLabel("VOICE -")
        self.dot_voice.setObjectName("SysDot")
        sl.addWidget(self.dot_voice)
        self.dot_local = QLabel("LOCAL -")
        self.dot_local.setObjectName("SysDot")
        sl.addWidget(self.dot_local)
        sl.addStretch()
        layout.addLayout(sl)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def set_system_status(self, text, mode=VisualizerMode.IDLE):
        if mode == getattr(self, "_last_mode", None) and getattr(self, "_last_text", None) == text:
            return
        self._last_mode = mode
        self._last_text = text
        m = {VisualizerMode.IDLE: ("ONLINE", "Ready", "READY"),
             VisualizerMode.LISTENING: ("LISTENING", "Listening... speak now", "LISTENING"),
             VisualizerMode.THINKING: ("THINKING", "Processing...", "THINKING"),
             VisualizerMode.EXECUTING: ("WORKING", "Applying action...", "WORKING"),
             VisualizerMode.CONFIRMATION_REQUIRED: ("CONFIRM", "Confirm action", "CONFIRM"),
             VisualizerMode.ERROR: ("ERROR", text or "Error", "SYSTEM ERROR"),
             VisualizerMode.SPEAKING: ("SPEAKING", "Speaking...", "SPEAKING")}
        badge, hint, state = m.get(mode, ("ONLINE", text, "READY"))
        self.lbl_status.setText(badge)
        self.lbl_hint.setText(hint)
        self.lbl_state.setText(state)
        self.lbl_status.setProperty("mode", mode)
        self.pill_container.setProperty("mode", mode)
        listening = (mode == VisualizerMode.LISTENING)
        self.btn_mic.setProperty("active", "true" if listening else "false")
        self.btn_mic.setText("STOP" if listening else "MIC")
        for w in [self.lbl_status, self.pill_container, self.btn_mic]:
            w.style().unpolish(w)
            w.style().polish(w)
        self.visualizer.set_mode(mode)
        self.core.set_mode(mode)

    def set_health(self, mic=None, ai=None, voice=None, local=None):
        for lbl, val in [(self.dot_mic, mic), (self.dot_ai, ai), (self.dot_voice, voice), (self.dot_local, local)]:
            if val is None:
                continue
            name = lbl.text().split(" ")[0]
            lbl.setText(name + (" +" if val else " -"))
            if getattr(self, "_health_cache", {}).get(lbl) == val:
                continue
            if not hasattr(self, "_health_cache"):
                self._health_cache = {}
            self._health_cache[lbl] = val
            lbl.setProperty("on", "true" if val else "false")
            lbl.style().unpolish(lbl)
            lbl.style().polish(lbl)

    def show_response(self, text):
        self.lbl_response.setText(text)

    def append_message(self, sender, text):
        import time as _t
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        you = sender.lower() not in ["sora", "aegis", "jarvis"]
        if not you:
            now = _t.monotonic()
            if now - getattr(self, "_resp_ts", 0.0) >= 0.05 or len(text) < 60:
                self._resp_ts = now
                self.show_response(text)
        try:
            if self.chat_display.document().blockCount() > 120:
                cur = self.chat_display.textCursor()
                cur.movePosition(QTextCursor.MoveOperation.Start)
                cur.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor, 20)
                cur.removeSelectedText()
        except Exception:
            pass
        tag = "You" if you else "Sora"
        color = "#7dd3fc" if you else "#c4b5fd"
        align = "right" if you else "left"
        safe = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if len(safe) > 1200:
            safe = safe[:1200] + "…"
        self.chat_display.append(f"<div style='margin-bottom:8px;text-align:{align};'><span style='color:{color};font-weight:700;'>[{tag}]</span> <span style='color:#64748b;font-size:11px;'>{ts}</span><br><span style='color:#e2e8f0;font-size:13px;'>{safe}</span></div>")
        self.chat_display.moveCursor(QTextCursor.MoveOperation.End)

    def on_mic_clicked(self):
        self.voice_trigger_requested.emit()

    def on_send_clicked(self):
        t = self.txt_input.text().strip()
        if not t:
            return
        self.txt_input.clear()
        self.text_submit_requested.emit(t)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_requested.emit()
            event.accept()
            return
        if event.key() == Qt.Key.Key_Space and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.voice_trigger_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if child in (None, self.central_widget, self.glass_panel) or isinstance(child, QLabel):
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_position = QPoint()
        super().mouseReleaseEvent(event)
