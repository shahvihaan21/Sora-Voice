# SORA HUD stylesheet — restrained graphite + cyan/violet state accents.
"""
Sora HUD Palette & QSS Stylesheet.
Defines color constants and PyQt QSS style rules for glassmorphism HUD windows,
status badges, chat controls, and pill input containers.
"""

HUD_ACCENT_CYAN = "#38bdf8"
HUD_ACCENT_TEAL = "#22d3ee"
HUD_ACCENT_INDIGO = "#818cf8"
HUD_ACCENT_PURPLE = "#c4b5fd"
HUD_ACCENT_AMBER = "#fcd34d"
HUD_ACCENT_RED = "#fca5a5"

MAIN_STYLE = """
QWidget { color: #e2e8f0; font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif; }
#MainWindow { background-color: transparent; }
#GlassPanel { background-color: rgba(8, 11, 20, 0.96); border-radius: 20px; border: 1px solid rgba(148,163,184,0.22); }
QLabel#HeaderBrand { color: #f1f5f9; font-size: 16px; font-weight: 700; letter-spacing: 4px; }
QLabel#HeaderSub { color: #64748b; font-size: 10px; letter-spacing: 2px; }
QLabel#StatusBadge { border-radius: 10px; padding: 3px 12px; font-size: 11px; font-weight: 700; letter-spacing: 1px; }
QLabel#StatusBadge[mode="IDLE"] { background: rgba(56,189,248,0.12); color: #7dd3fc; border: 1px solid rgba(56,189,248,0.35); }
QLabel#StatusBadge[mode="LISTENING"] { background: rgba(34,211,238,0.14); color: #22d3ee; border: 1px solid rgba(34,211,238,0.55); }
QLabel#StatusBadge[mode="THINKING"] { background: rgba(129,140,248,0.14); color: #a5b4fc; border: 1px solid rgba(129,140,248,0.55); }
QLabel#StatusBadge[mode="SPEAKING"] { background: rgba(167,139,250,0.14); color: #c4b5fd; border: 1px solid rgba(167,139,250,0.55); }
QLabel#StatusBadge[mode="EXECUTING"] { background: rgba(129,140,248,0.14); color: #a5b4fc; border: 1px solid rgba(129,140,248,0.55); }
QLabel#StatusBadge[mode="CONFIRMATION_REQUIRED"] { background: rgba(251,191,36,0.12); color: #fcd34d; border: 1px solid rgba(251,191,36,0.5); }
QLabel#StatusBadge[mode="ERROR"] { background: rgba(248,113,113,0.12); color: #fca5a5; border: 1px solid rgba(248,113,113,0.5); }
QLabel#ActionHint { color: #64748b; font-size: 11px; }
QLabel#StateLabel { color: #94a3b8; font-size: 12px; font-weight: 600; letter-spacing: 5px; }
QLabel#ResponseLabel { color: #e2e8f0; font-size: 14px; }
QLabel#SysDot { color: #475569; font-size: 10px; letter-spacing: 1px; }
QLabel#SysDot[on="true"] { color: #22d3ee; }
QLabel#SysDot[warn="true"] { color: #f59e0b; }
QPushButton.WindowControl { background: transparent; border: none; color: #64748b; font-size: 13px; border-radius: 6px; }
QPushButton.WindowControl:hover { background: rgba(255,255,255,0.08); color: #fff; }
QPushButton#BtnClose:hover { background: rgba(239,68,68,0.35); color: #fca5a5; }
QTextEdit#ChatDisplay { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; color: #e2e8f0; font-size: 13px; padding: 12px 14px; selection-background-color: #0ea5e9; }
QScrollBar:vertical { background: transparent; width: 6px; margin: 4px 0; }
QScrollBar::handle:vertical { background: rgba(148,163,184,0.25); min-height: 24px; border-radius: 3px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
#PillInputContainer { background: rgba(255,255,255,0.04); border: 1px solid rgba(148,163,184,0.25); border-radius: 26px; }
#PillInputContainer:focus-within { border: 1px solid rgba(56,189,248,0.6); }
#PillInputContainer[mode="LISTENING"] { border: 1px solid rgba(34,211,238,0.6); }
#PillInputContainer[mode="THINKING"] { border: 1px solid rgba(129,140,248,0.6); }
#PillInputContainer[mode="SPEAKING"] { border: 1px solid rgba(167,139,250,0.6); }
#PillInputContainer[mode="ERROR"] { border: 1px solid rgba(248,113,113,0.6); }
QLineEdit#CmdInput { background: transparent; border: none; color: #f1f5f9; font-size: 14px; padding: 6px 4px; }
QPushButton#BtnMic { background: rgba(56,189,248,0.12); border: 1px solid rgba(56,189,248,0.35); border-radius: 18px; color: #7dd3fc; font-size: 13px; font-weight: 700; }
QPushButton#BtnMic:hover { background: rgba(56,189,248,0.22); color: #fff; }
QPushButton#BtnMic[active="true"] { background: rgba(34,211,238,0.25); border: 1px solid rgba(34,211,238,0.7); color: #fff; }
QPushButton#BtnSend { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0ea5e9, stop:1 #8b5cf6); border: none; border-radius: 18px; color: #fff; font-size: 15px; font-weight: 700; }
QPushButton#BtnSend:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #38bdf8, stop:1 #a78bfa); }
QPushButton#BtnSend:pressed { background: #0c4a6e; }
"""
