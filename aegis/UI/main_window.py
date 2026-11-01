import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QTextEdit, QFrame,
    QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QTextCursor
try:
    from UI.styles import MAIN_STYLE
    from UI.widgets.glass_panel import GlassPanel
    from UI.widgets.visualizer import AudioVisualizer, VisualizerMode
    from UI.widgets.core import AICore
except ImportError:
    from aegis.UI.styles import MAIN_STYLE
    from aegis.UI.widgets.glass_panel import GlassPanel
    from aegis.UI.widgets.visualizer import AudioVisualizer, VisualizerMode
    from aegis.UI.widgets.core import AICore


class MainWindow(QMainWindow):
    voice_trigger_requested = pyqtSignal()
    text_submit_requested = pyqtSignal(str)
    cancel_requested = pyqtSignal()
    model_changed = pyqtSignal(str)
    mute_toggled = pyqtSignal(bool)
    clear_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(780, 880)
        self.setMinimumSize(620, 680)
        self.setStyleSheet(MAIN_STYLE)
        self.central_widget = QWidget()
        self.central_widget.setObjectName("MainWindow")
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.glass_panel = GlassPanel()
        main_layout.addWidget(self.glass_panel)
        self.is_muted = False
        self.setup_ui(self.glass_panel.layout)
        self.drag_position = QPoint()
        self._boot()

    def _boot(self):
        self.setWindowOpacity(0.0)
        a = QPropertyAnimation(self, b"windowOpacity", self)
        a.setDuration(450)
        a.setStartValue(0.0)
        a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start()
        self._boot_anim = a

    def setup_ui(self, layout):
        # 1. Top Bar
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

        # Ollama connection indicator & active model
        self.lbl_ollama = QLabel("OLLAMA OFFLINE")
        self.lbl_ollama.setObjectName("OllamaIndicator")
        self.lbl_ollama.setProperty("online", "false")
        hl.addWidget(self.lbl_ollama)

        self.lbl_active_model = QLabel("qwen3:1.7b")
        self.lbl_active_model.setObjectName("ActiveModelLabel")
        hl.addWidget(self.lbl_active_model)

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

        # 2. Settings Area (Model Selector, Mute, Clear)
        settings_frame = QFrame()
        settings_frame.setObjectName("SettingsArea")
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(6, 4, 6, 4)
        settings_layout.setSpacing(8)

        lbl_model_tag = QLabel("MODEL:")
        lbl_model_tag.setObjectName("SettingsTag")
        settings_layout.addWidget(lbl_model_tag)

        self.combo_model = QComboBox()
        self.combo_model.setObjectName("ModelSelector")
        self.combo_model.addItems(["qwen3:1.7b", "jarvis-ft:latest", "gemma4-local:latest", "qwen2.5vl:7b"])
        self.combo_model.currentTextChanged.connect(self._on_model_changed)
        settings_layout.addWidget(self.combo_model)

        settings_layout.addStretch()

        self.btn_mute = QPushButton("MUTE")
        self.btn_mute.setProperty("class", "SettingsBtn")
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mute.clicked.connect(self._on_mute_clicked)
        settings_layout.addWidget(self.btn_mute)

        self.btn_clear = QPushButton("CLEAR CHAT")
        self.btn_clear.setProperty("class", "SettingsBtn")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.clicked.connect(self._on_clear_clicked)
        settings_layout.addWidget(self.btn_clear)

        layout.addWidget(settings_frame)

        # 3. Main Area: Central Core & Waveform
        self.core = AICore()
        self.core.setFixedSize(220, 220)
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

        # Conversation transcript
        self.chat_display = QTextEdit()
        self.chat_display.setObjectName("ChatDisplay")
        self.chat_display.setReadOnly(True)
        self.chat_display.setFixedHeight(130)
        layout.addWidget(self.chat_display, stretch=0)

        # 4. Bottom Input Area (Pill Capsule)
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
        self.txt_input.setPlaceholderText("Ask Sora anything or switch models...")
        self.txt_input.returnPressed.connect(self.on_send_clicked)
        pl.addWidget(self.txt_input, stretch=1)

        self.btn_stop_speech = QPushButton("STOP")
        self.btn_stop_speech.setObjectName("BtnStopSpeech")
        self.btn_stop_speech.setFixedSize(60, 38)
        self.btn_stop_speech.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop_speech.clicked.connect(self.on_stop_speech_clicked)
        pl.addWidget(self.btn_stop_speech)

        self.btn_send = QPushButton(">")
        self.btn_send.setObjectName("BtnSend")
        self.btn_send.setFixedSize(44, 38)
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self.on_send_clicked)
        pl.addWidget(self.btn_send)
        layout.addWidget(self.pill_container)

        # Subsystem indicators
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

    def _on_model_changed(self, model_name: str):
        if model_name:
            self.lbl_active_model.setText(model_name)
            self.model_changed.emit(model_name)

    def _on_mute_clicked(self):
        self.is_muted = not self.is_muted
        self.btn_mute.setText("UNMUTE" if self.is_muted else "MUTE")
        self.btn_mute.setProperty("active", "true" if self.is_muted else "false")
        self.btn_mute.style().unpolish(self.btn_mute)
        self.btn_mute.style().polish(self.btn_mute)
        self.mute_toggled.emit(self.is_muted)

    def _on_clear_clicked(self):
        self.clear_chat()
        self.clear_requested.emit()

    def clear_chat(self):
        self.chat_display.clear()
        self.lbl_response.setText("How can I help?")

    def set_active_model(self, model_name: str):
        if not model_name:
            return
        self.lbl_active_model.setText(model_name)
        idx = self.combo_model.findText(model_name)
        if idx >= 0:
            self.combo_model.blockSignals(True)
            self.combo_model.setCurrentIndex(idx)
            self.combo_model.blockSignals(False)

    def set_available_models(self, models: list, current_model: str = ""):
        if not models:
            return
        self.combo_model.blockSignals(True)
        self.combo_model.clear()
        self.combo_model.addItems(models)
        target = current_model or self.lbl_active_model.text()
        idx = self.combo_model.findText(target)
        if idx >= 0:
            self.combo_model.setCurrentIndex(idx)
            self.lbl_active_model.setText(target)
        elif self.combo_model.count() > 0:
            self.lbl_active_model.setText(self.combo_model.currentText())
        self.combo_model.blockSignals(False)

    def set_ollama_status(self, online: bool):
        self.lbl_ollama.setText("OLLAMA ONLINE" if online else "OLLAMA OFFLINE")
        self.lbl_ollama.setProperty("online", "true" if online else "false")
        self.lbl_ollama.style().unpolish(self.lbl_ollama)
        self.lbl_ollama.style().polish(self.lbl_ollama)

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
        m = {VisualizerMode.IDLE: ("ONLINE", text or "Ready", "READY"),
             VisualizerMode.LISTENING: ("LISTENING", text or "Listening... speak now", "LISTENING"),
             VisualizerMode.THINKING: ("THINKING", text or "Processing...", "THINKING"),
             VisualizerMode.EXECUTING: ("WORKING", text or "Applying action...", "WORKING"),
             VisualizerMode.CONFIRMATION_REQUIRED: ("CONFIRM", text or "Confirm action", "CONFIRM"),
             VisualizerMode.ERROR: ("ERROR", text or "System error", "SYSTEM ERROR"),
             VisualizerMode.SPEAKING: ("SPEAKING", text or "Speaking...", "SPEAKING")}
        badge, hint, state = m.get(mode, ("ONLINE", text or "Ready", "READY"))
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

    def on_stop_speech_clicked(self):
        self.cancel_requested.emit()

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
