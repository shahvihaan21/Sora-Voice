from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient,
    QPainterPath
)
from PyQt6.QtCore import Qt, QTimer
import math

class VisualizerMode:
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    EXECUTING = "EXECUTING"
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
    ERROR = "ERROR"
    SPEAKING = "SPEAKING"

class AudioVisualizer(QWidget):
    """
    Apple Intelligence / Siri-style fluid multi-layered harmonic wave visualizer.
    Renders overlapping translucent glowing ribbons with vibrant cyan, blue, purple, and magenta gradients.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 56)
        self.setFixedHeight(64)

        self.phase = 0.0
        self.mode = VisualizerMode.IDLE
        self.pulse = 0.0
        self.level = 0.12
        self._target = 0.12

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(90)
        self._cached_w = 0
        self._xs = []  # cached x-samples per width

    def set_mode(self, mode: str):
        if mode == self.mode:
            return
        self.mode = mode
        interval = {VisualizerMode.IDLE: 90, VisualizerMode.ERROR: 250,
                    VisualizerMode.CONFIRMATION_REQUIRED: 120,
                    VisualizerMode.THINKING: 60, VisualizerMode.EXECUTING: 50,
                    VisualizerMode.LISTENING: 36, VisualizerMode.SPEAKING: 36}.get(mode, 60)
        if self.timer.interval() != interval:
            self.timer.setInterval(interval)
        if self.isVisible():
            self.update()

    def set_level(self, v: float):
        try:
            self._target = max(0.0, min(1.0, float(v)))
        except Exception:
            pass

    def update_animation(self):
        speed_map = {
            VisualizerMode.IDLE: 0.05,
            VisualizerMode.LISTENING: 0.14,
            VisualizerMode.THINKING: 0.10,
            VisualizerMode.EXECUTING: 0.12,
            VisualizerMode.CONFIRMATION_REQUIRED: 0.06,
            VisualizerMode.ERROR: 0.03,
            VisualizerMode.SPEAKING: 0.16,
        }
        self.phase += speed_map.get(self.mode, 0.06)
        self.pulse = (math.sin(self.phase * 2.0) + 1.0) / 2.0
        self.level += (self._target - self.level) * 0.15
        base = {VisualizerMode.IDLE: 0.12, VisualizerMode.LISTENING: 0.55,
                VisualizerMode.THINKING: 0.35, VisualizerMode.EXECUTING: 0.45,
                VisualizerMode.CONFIRMATION_REQUIRED: 0.25,
                VisualizerMode.ERROR: 0.10, VisualizerMode.SPEAKING: 0.60}.get(self.mode, 0.15)
        if abs(self._target - base) < 0.4:
            self._target = max(0.05, base + 0.06 * math.sin(self.phase * 1.7))
        if self.isVisible():
            self.update()

    def _cols(self):
        m = {VisualizerMode.IDLE: ((56, 189, 248), (129, 140, 248)),
             VisualizerMode.LISTENING: ((34, 211, 238), (56, 189, 248)),
             VisualizerMode.THINKING: ((96, 165, 250), (167, 139, 250)),
             VisualizerMode.EXECUTING: ((96, 165, 250), (167, 139, 250)),
             VisualizerMode.CONFIRMATION_REQUIRED: ((251, 191, 36), (251, 113, 133)),
             VisualizerMode.SPEAKING: ((167, 139, 250), (34, 211, 238)),
             VisualizerMode.ERROR: ((248, 113, 113), (248, 113, 113))}
        return m.get(self.mode, m[VisualizerMode.IDLE])

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width = float(self.width())
        height = float(self.height())
        mid_y = height / 2.0
        (r1, g1, b1), (r2, g2, b2) = self._cols()
        layers = [
            {"amp": 8 + self.level * 22, "f1": 2.2, "pm": 1.0, "sa": 110, "wd": 1.8, "glow": True},
            {"amp": 11 + self.level * 28, "f1": 3.1, "pm": -0.8, "sa": 150, "wd": 2.2, "glow": False},
            {"amp": 6 + self.level * 15, "f1": 4.3, "pm": 1.3, "sa": 80, "wd": 1.2, "glow": False},
        ]
        # cache x-samples + envelope per width to avoid recompute
        if int(width) != self._cached_w or not self._xs:
            self._cached_w = int(width)
            step = 6 if width > 520 else 4
            self._xs = []
            x = 0
            while x <= int(width):
                nx = x / max(1.0, width)
                env = max(0.0, math.sin(nx * math.pi)) ** 2
                self._xs.append((x, nx, env))
                x += step
        for L in layers:
            path = QPainterPath()
            first = True
            for (x, nx, env) in self._xs:
                y = (math.sin(nx * L["f1"] * math.tau + self.phase * L["pm"]) + 0.45 * math.cos(nx * 2.0 * math.tau - self.phase * 0.7)) * L["amp"] * env
                if first:
                    path.moveTo(x, mid_y - y)
                    first = False
                else:
                    path.lineTo(x, mid_y - y)
            grad = QLinearGradient(0, 0, width, 0)
            grad.setColorAt(0.08, QColor(r1, g1, b1, 0))
            grad.setColorAt(0.3, QColor(r1, g1, b1, L["sa"]))
            grad.setColorAt(0.7, QColor(r2, g2, b2, L["sa"]))
            grad.setColorAt(0.92, QColor(r2, g2, b2, 0))

            # Render optional ambient glow pass behind primary wave line
            if L["glow"]:
                glow_pen = QPen(QBrush(grad), L["wd"] * 3.0)
                glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                glow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                painter.setPen(glow_pen)
                painter.drawPath(path)

            pen = QPen(QBrush(grad), L["wd"])
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)
