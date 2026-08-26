from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient, 
    QRadialGradient, QPainterPath
)
from PyQt6.QtCore import Qt, QTimer
import math

class VisualizerMode:
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"

class AudioVisualizer(QWidget):
    """
    Apple Intelligence / Siri-style fluid multi-layered harmonic wave visualizer.
    Renders overlapping translucent glowing ribbons with vibrant cyan, blue, purple, and magenta gradients.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 160)
        self.setFixedHeight(170)
        
        self.phase = 0.0
        self.mode = VisualizerMode.IDLE
        self.pulse = 0.0
        
        # 60 FPS smooth rendering timer (~16ms)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

    def set_mode(self, mode: str):
        self.mode = mode
        self.update()

    def update_animation(self):
        speed_map = {
            VisualizerMode.IDLE: 0.025,
            VisualizerMode.LISTENING: 0.065,
            VisualizerMode.THINKING: 0.085,
            VisualizerMode.SPEAKING: 0.075,
        }
        self.phase += speed_map.get(self.mode, 0.03)
        self.pulse = (math.sin(self.phase * 2.0) + 1.0) / 2.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = float(self.width())
        height = float(self.height())
        mid_y = height / 2.0
        center_x = width / 2.0

        # 1. Soft Central Ambient Aura
        aura_rad = min(width, height) * 0.55
        aura_gradient = QRadialGradient(center_x, mid_y, aura_rad)
        
        if self.mode == VisualizerMode.LISTENING:
            glow_col = QColor(6, 182, 212, int(25 + 30 * self.pulse))   # Cyan glow
        elif self.mode == VisualizerMode.THINKING:
            glow_col = QColor(168, 85, 247, int(25 + 35 * self.pulse))  # Violet glow
        elif self.mode == VisualizerMode.SPEAKING:
            glow_col = QColor(139, 92, 246, int(35 + 40 * self.pulse))  # Electric purple glow
        else:
            glow_col = QColor(56, 189, 248, int(15 + 15 * self.pulse))  # Soft sky blue
            
        aura_gradient.setColorAt(0.0, glow_col)
        aura_gradient.setColorAt(0.7, QColor(glow_col.red(), glow_col.green(), glow_col.blue(), int(glow_col.alpha() * 0.3)))
        aura_gradient.setColorAt(1.0, QColor(0, 0, 0, 0))
        
        painter.setBrush(QBrush(aura_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(center_x - aura_rad), int(mid_y - aura_rad * 0.6), int(aura_rad * 2), int(aura_rad * 1.2))

        # Mode Amplitude Multipliers
        amp_map = {
            VisualizerMode.IDLE: 0.65,
            VisualizerMode.LISTENING: 1.5,
            VisualizerMode.THINKING: 1.2,
            VisualizerMode.SPEAKING: 1.85,
        }
        amp_global = amp_map.get(self.mode, 0.7)

        # 2. Render Layered Siri / Sora Waveform Ribbons per mode
        if self.mode == VisualizerMode.LISTENING:
            # Listening: Emerald / Aquamarine / Cyan acoustic sensitivity
            layers = [
                {
                    "freq1": 4.5, "freq2": 6.0, "amp": 28.0 * amp_global, "phase_mult": 1.4,
                    "col_start": QColor(16, 185, 129), "col_end": QColor(6, 182, 212),
                    "alpha_fill": 55, "alpha_stroke": 200, "stroke_w": 2.4
                },
                {
                    "freq1": 3.8, "freq2": 7.2, "amp": 34.0 * amp_global, "phase_mult": -1.3,
                    "col_start": QColor(52, 211, 153), "col_end": QColor(56, 189, 248),
                    "alpha_fill": 60, "alpha_stroke": 220, "stroke_w": 2.5
                },
                {
                    "freq1": 5.2, "freq2": 3.5, "amp": 38.0 * amp_global, "phase_mult": 1.0,
                    "col_start": QColor(6, 182, 212), "col_end": QColor(99, 102, 241),
                    "alpha_fill": 50, "alpha_stroke": 230, "stroke_w": 2.6
                },
            ]
        elif self.mode == VisualizerMode.THINKING:
            # Thinking: Violet / Purple / Magenta swirling neural processing
            layers = [
                {
                    "freq1": 3.0, "freq2": 5.5, "amp": 28.0 * amp_global, "phase_mult": 1.6,
                    "col_start": QColor(147, 51, 234), "col_end": QColor(217, 70, 239),
                    "alpha_fill": 60, "alpha_stroke": 210, "stroke_w": 2.5
                },
                {
                    "freq1": 4.2, "freq2": 2.8, "amp": 32.0 * amp_global, "phase_mult": -1.8,
                    "col_start": QColor(168, 85, 247), "col_end": QColor(236, 72, 153),
                    "alpha_fill": 65, "alpha_stroke": 230, "stroke_w": 2.6
                },
                {
                    "freq1": 2.4, "freq2": 6.2, "amp": 30.0 * amp_global, "phase_mult": 1.2,
                    "col_start": QColor(99, 102, 241), "col_end": QColor(192, 132, 252),
                    "alpha_fill": 55, "alpha_stroke": 220, "stroke_w": 2.4
                },
            ]
        elif self.mode == VisualizerMode.SPEAKING:
            # Speaking: High-energy Cyan / Sky Blue / Magenta expressive speech
            layers = [
                {
                    "freq1": 3.2, "freq2": 4.8, "amp": 28.0 * amp_global, "phase_mult": 1.0,
                    "col_start": QColor(37, 99, 235), "col_end": QColor(6, 182, 212),
                    "alpha_fill": 50, "alpha_stroke": 180, "stroke_w": 2.4
                },
                {
                    "freq1": 2.6, "freq2": 5.4, "amp": 34.0 * amp_global, "phase_mult": -1.2,
                    "col_start": QColor(99, 102, 241), "col_end": QColor(168, 85, 247),
                    "alpha_fill": 60, "alpha_stroke": 210, "stroke_w": 2.5
                },
                {
                    "freq1": 3.8, "freq2": 2.2, "amp": 30.0 * amp_global, "phase_mult": 0.85,
                    "col_start": QColor(147, 51, 234), "col_end": QColor(236, 72, 153),
                    "alpha_fill": 65, "alpha_stroke": 220, "stroke_w": 2.5
                },
                {
                    "freq1": 4.5, "freq2": 3.0, "amp": 38.0 * amp_global, "phase_mult": -0.95,
                    "col_start": QColor(0, 242, 254), "col_end": QColor(56, 189, 248),
                    "alpha_fill": 45, "alpha_stroke": 250, "stroke_w": 2.8
                },
            ]
        else:
            # Idle / Standby: Soft Sky Blue & Azure breathing wave
            layers = [
                {
                    "freq1": 2.8, "freq2": 4.2, "amp": 22.0 * amp_global, "phase_mult": 0.8,
                    "col_start": QColor(30, 64, 175), "col_end": QColor(56, 189, 248),
                    "alpha_fill": 35, "alpha_stroke": 140, "stroke_w": 2.0
                },
                {
                    "freq1": 3.4, "freq2": 2.5, "amp": 24.0 * amp_global, "phase_mult": -0.7,
                    "col_start": QColor(99, 102, 241), "col_end": QColor(6, 182, 212),
                    "alpha_fill": 40, "alpha_stroke": 160, "stroke_w": 2.2
                },
            ]

        # Draw translucent filled ribbons and glowing stroke outlines
        for layer in layers:
            self._draw_fluid_ribbon(painter, width, mid_y, layer)

        # 3. Soft Center Baseline Line
        line_pen = QPen(QColor(148, 163, 184, 30))
        line_pen.setWidth(1)
        painter.setPen(line_pen)
        painter.drawLine(int(width * 0.1), int(mid_y), int(width * 0.9), int(mid_y))

    def _draw_fluid_ribbon(self, painter: QPainter, width: float, mid_y: float, cfg: dict):
        step = 3
        points_top = []
        points_bot = []

        freq1 = cfg["freq1"]
        freq2 = cfg["freq2"]
        amp = cfg["amp"]
        phase_offset = self.phase * cfg["phase_mult"]
        
        for x in range(0, int(width) + step, step):
            norm_x = min(1.0, max(0.0, float(x) / max(1.0, width)))
            # Smooth window envelope (taper to 0 at both edges)
            sin_env = max(0.0, math.sin(norm_x * math.pi))
            envelope = sin_env * sin_env
            
            # Harmonic superposition for organic fluid wave
            w1 = math.sin(norm_x * freq1 * math.pi * 2.0 + phase_offset)
            w2 = math.cos(norm_x * freq2 * math.pi * 2.0 - phase_offset * 0.7) * 0.45
            w3 = math.sin(norm_x * 1.5 * math.pi + phase_offset * 0.5) * 0.2
            
            disp = float((w1 + w2 + w3) * amp * envelope)
            
            # Thickness modulation along wave
            thickness = max(2.0, float((math.sin(norm_x * math.pi + self.phase * 0.4) * 8.0 + 10.0) * envelope))
            
            y_top = float(mid_y - disp - (thickness / 2.0))
            y_bot = float(mid_y - disp + (thickness / 2.0))
            
            points_top.append((float(x), float(y_top)))
            points_bot.append((float(x), float(y_bot)))

        # Build closed path for filled ribbon
        ribbon_path = QPainterPath()
        if points_top:
            ribbon_path.moveTo(points_top[0][0], points_top[0][1])
            for pt in points_top[1:]:
                ribbon_path.lineTo(pt[0], pt[1])
            for pt in reversed(points_bot):
                ribbon_path.lineTo(pt[0], pt[1])
            ribbon_path.closeSubpath()

        # Create gradient across the width
        grad = QLinearGradient(0, mid_y - amp, width, mid_y + amp)
        c_start = cfg["col_start"]
        c_end = cfg["col_end"]
        
        fill_start = QColor(c_start.red(), c_start.green(), c_start.blue(), cfg["alpha_fill"])
        fill_end = QColor(c_end.red(), c_end.green(), c_end.blue(), cfg["alpha_fill"])
        grad.setColorAt(0.15, fill_start)
        grad.setColorAt(0.85, fill_end)

        # Draw filled ribbon
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(ribbon_path)

        # Draw glowing crest stroke
        stroke_start = QColor(c_start.red(), c_start.green(), c_start.blue(), cfg["alpha_stroke"])
        stroke_end = QColor(c_end.red(), c_end.green(), c_end.blue(), cfg["alpha_stroke"])
        stroke_grad = QLinearGradient(0, 0, width, 0)
        stroke_grad.setColorAt(0.15, stroke_start)
        stroke_grad.setColorAt(0.85, stroke_end)

        stroke_pen = QPen(QBrush(stroke_grad), cfg["stroke_w"])
        stroke_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        stroke_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(stroke_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        top_line_path = QPainterPath()
        top_line_path.moveTo(points_top[0][0], points_top[0][1])
        for pt in points_top[1:]:
            top_line_path.lineTo(pt[0], pt[1])
        painter.drawPath(top_line_path)
