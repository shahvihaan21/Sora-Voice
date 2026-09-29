"""SORA AI Core — central state visual. QPainter only, ~30fps."""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient
from PyQt6.QtCore import Qt, QTimer
import math, random


class AICore(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220, 220)
        self.mode = "IDLE"
        self.level = 0.0
        self._target = 0.0
        self.phase = 0.0
        self.ring_a = 0.0
        self.ring_b = 0.0
        self.pts = [{"ang": random.random() * math.tau,
                     "rad": random.uniform(0.62, 0.95),
                     "spd": random.uniform(0.008, 0.03),
                     "sz": random.uniform(1.2, 2.6)} for _ in range(24)]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(90)
        self._cached_size = None
        self._cached_geom = None

    def set_mode(self, mode: str):
        if mode == self.mode:
            return

    def set_level(self, v: float):
        self._target = max(0.0, min(1.0, v))

    def _tick(self):
        sp = {"IDLE": 0.020, "LISTENING": 0.055, "THINKING": 0.075,
              "EXECUTING": 0.085, "CONFIRMATION_REQUIRED": 0.03,
              "ERROR": 0.015, "SPEAKING": 0.065}
        self.phase += sp.get(self.mode, 0.025)
        self.ring_a += 0.012 + (0.03 if self.mode in ("THINKING", "EXECUTING") else 0.0)
        self.ring_b -= 0.009 + (0.02 if self.mode == "THINKING" else 0.0)
        self.level += (self._target - self.level) * 0.12
        if self.mode == "IDLE":
            self._target = 0.08 + 0.06 * (0.5 + 0.5 * math.sin(self.phase * 1.4))
        elif self.mode == "LISTENING":
            self._target = max(self._target, 0.45 + 0.3 * abs(math.sin(self.phase * 2.2)))
        elif self.mode == "SPEAKING":
            self._target = max(self._target, 0.40 + 0.35 * abs(math.sin(self.phase * 3.0)))
        if self.isVisible():
            self.update()

    def set_mode(self, mode: str):
        if mode == self.mode:
            return
        self.mode = mode
        # adaptive frame rate: idle/error slow, thinking medium, voice fast
        interval = {"IDLE": 90, "ERROR": 200, "CONFIRMATION_REQUIRED": 90,
                    "THINKING": 60, "EXECUTING": 50,
                    "LISTENING": 36, "SPEAKING": 36}.get(mode, 50)
        if self.timer.interval() != interval:
            self.timer.setInterval(interval)
        self._cached_size = None  # force geometry recache
        if self.isVisible():
            self.update()
    def _pal(self):
        m = {"IDLE": ((56,189,248),(129,140,248)),
             "LISTENING": ((34,211,238),(56,189,248)),
             "THINKING": ((96,165,250),(167,139,250)),
             "EXECUTING": ((96,165,250),(167,139,250)),
             "CONFIRMATION_REQUIRED": ((251,191,36),(251,113,133)),
             "SPEAKING": ((167,139,250),(34,211,238)),
             "ERROR": ((248,113,113),(248,113,113))}
        a, b = m.get(self.mode, m["IDLE"])
        return QColor(*a), QColor(*b)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())
        key = (int(w), int(h))
        if key != self._cached_size:
            self._cached_size = key
            self._cached_geom = (w / 2.0, h / 2.0, min(w, h) / 2.0 - 8.0)
        cx, cy, R = self._cached_geom
        br = 1.0 + 0.025 * math.sin(self.phase * 1.6)
        en = 1.0 + self.level * (0.14 if self.mode in ("LISTENING","SPEAKING") else 0.07)
        c1, c2 = self._pal()
        dim = 0.55 if self.mode == "IDLE" else 1.0
        hr = R * 1.02
        halo = QRadialGradient(cx, cy, hr)
        halo.setColorAt(0.0, QColor(0,0,0,0))
        halo.setColorAt(0.6, QColor(0,0,0,0))
        halo.setColorAt(1.0, QColor(c1.red(),c1.green(),c1.blue(),int(26*dim+self.level*40)))
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(halo))
        p.drawEllipse(int(cx-hr),int(cy-hr),int(hr*2),int(hr*2))
        rings = [(self.ring_a,0.98,46,1.2,2),(self.ring_b,0.82,60,1.4,2),(self.ring_a*0.6,0.66,80,1.1,3)]
        for ang,fr,al,wd,n in rings:
            rr = R*fr*br*en
            pen = QPen(QColor(148,163,184,int(al*dim+self.level*30))); pen.setWidthF(wd)
            p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(int(cx-rr),int(cy-rr),int(rr*2),int(rr*2))
            p.setPen(Qt.PenStyle.NoPen)
            for k in range(n):
                a = ang + k*(math.tau/n)
                dx,dy = math.cos(a)*rr, math.sin(a)*rr
                dc = c1 if k%2==0 else c2
                p.setBrush(QBrush(QColor(dc.red(),dc.green(),dc.blue(),int(150*dim+self.level*80))))
                s = 3.2 if n==3 else 2.6
                p.drawEllipse(int(cx+dx-s/2),int(cy+dy-s/2),int(s),int(s))
        p.setPen(Qt.PenStyle.NoPen)
        for pt in self.pts:
            pt["ang"] += pt["spd"]*(0.6 if self.mode=="IDLE" else 1.6)
            rf = pt["rad"]
            if self.mode in ("THINKING","EXECUTING"):
                rf = 0.55+0.35*(0.5+0.5*math.sin(self.phase*2+pt["ang"]))
            rr = R*rf
            x = cx+math.cos(pt["ang"])*rr; y = cy+math.sin(pt["ang"])*rr*0.92
            p.setBrush(QBrush(QColor(c2.red(),c2.green(),c2.blue(),70)))
            s = pt["sz"]; p.drawEllipse(int(x),int(y),int(s),int(s))
        cr = R*0.48*br*en
        g = QRadialGradient(cx-cr*0.25, cy-cr*0.3, cr*1.6)
        g.setColorAt(0.0,QColor(226,232,240,int(210*dim+30)))
        g.setColorAt(0.25,QColor(c1.red(),c1.green(),c1.blue(),int(150*dim+self.level*60)))
        g.setColorAt(0.65,QColor(c2.red(),c2.green(),c2.blue(),int(90*dim+self.level*50)))
        g.setColorAt(1.0,QColor(2,6,16,0))
        p.setBrush(QBrush(g)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(cx-cr*1.25),int(cy-cr*1.25),int(cr*2.5),int(cr*2.5))
        dr = R*0.30*br*(1+self.level*0.12)
        d = QRadialGradient(cx-dr*0.3, cy-dr*0.35, dr*1.4)
        d.setColorAt(0.0,QColor(248,250,252,235))
        d.setColorAt(0.45,QColor(c1.red(),c1.green(),c1.blue(),200))
        d.setColorAt(1.0,QColor(8,12,24,230))
        p.setBrush(QBrush(d))
        rim = QPen(QColor(c1.red(),c1.green(),c1.blue(),int(120+self.level*100))); rim.setWidthF(1.3)
        p.setPen(rim)
        p.drawEllipse(int(cx-dr),int(cy-dr),int(dr*2),int(dr*2))

