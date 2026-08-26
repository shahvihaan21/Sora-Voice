# QSS Stylesheet for Sora AI Desktop Assistant (Replicating Context Image)

MAIN_STYLE = """
/* Global Base */
QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
}

/* Main Frameless Window Base */
#MainWindow {
    background-color: transparent;
}

/* Glass Panel Widget - Rounded Obsidian Floating Window */
#GlassPanel {
    background-color: rgba(12, 16, 25, 0.96);
    border-radius: 22px;
    border: 1px solid rgba(255, 255, 255, 0.09);
}

/* Header Area & Window Controls */
QLabel#HeaderBrand {
    color: #f8fafc;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

QLabel#ActionHint {
    color: #94a3b8;
    font-size: 12px;
    font-style: italic;
}

/* Status Badges with Dynamic Mode Color Cues */
QLabel#StatusBadge {
    border-radius: 10px;
    padding: 3px 12px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
}

QLabel#StatusBadge[mode="IDLE"] {
    background-color: rgba(56, 189, 248, 0.12);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.35);
}

QLabel#StatusBadge[mode="LISTENING"] {
    background-color: rgba(34, 197, 94, 0.22);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.65);
}

QLabel#StatusBadge[mode="THINKING"] {
    background-color: rgba(168, 85, 247, 0.22);
    color: #c084fc;
    border: 1px solid rgba(168, 85, 247, 0.65);
}

QLabel#StatusBadge[mode="SPEAKING"] {
    background-color: rgba(6, 182, 212, 0.22);
    color: #22d3ee;
    border: 1px solid rgba(6, 182, 212, 0.65);
}

/* Minimalist Window Control Buttons (— □ ✕) */
QPushButton.WindowControl {
    background-color: transparent;
    border: none;
    color: #64748b;
    font-size: 13px;
    font-weight: bold;
    border-radius: 6px;
}

QPushButton.WindowControl:hover {
    background-color: rgba(255, 255, 255, 0.08);
    color: #ffffff;
}

QPushButton#BtnClose:hover {
    background-color: rgba(239, 68, 68, 0.35);
    color: #fca5a5;
}

/* Chat Transcript / Conversation View */
QTextEdit#ChatDisplay {
    background-color: rgba(15, 20, 31, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    color: #f1f5f9;
    font-size: 13px;
    padding: 12px 14px;
    selection-background-color: #8b5cf6;
}

/* Smooth Minimal Scrollbar */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 4px 0 4px 0;
}
QScrollBar::handle:vertical {
    background: rgba(148, 163, 184, 0.25);
    min-height: 24px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(168, 85, 247, 0.6);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Bottom Pill Input Container (Exact Reference Replica) */
#PillInputContainer {
    background-color: rgba(22, 28, 42, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 27px;
}

#PillInputContainer[mode="LISTENING"] {
    border: 1px solid rgba(34, 197, 94, 0.55);
    background-color: rgba(18, 36, 32, 0.95);
}

#PillInputContainer[mode="THINKING"] {
    border: 1px solid rgba(168, 85, 247, 0.55);
    background-color: rgba(28, 22, 44, 0.95);
}

#PillInputContainer[mode="SPEAKING"] {
    border: 1px solid rgba(6, 182, 212, 0.55);
    background-color: rgba(16, 30, 42, 0.95);
}

#PillInputContainer:focus-within {
    border: 1px solid rgba(168, 85, 247, 0.6);
    background-color: rgba(25, 32, 48, 0.98);
}

/* Left '+' Plus Action Button */
QPushButton#BtnPlus {
    background-color: transparent;
    border: none;
    color: #94a3b8;
    font-size: 22px;
    font-weight: 300;
    border-radius: 18px;
    padding-bottom: 2px;
}

QPushButton#BtnPlus[active="true"] {
    background-color: rgba(34, 197, 94, 0.25);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.6);
    font-size: 16px;
}

QPushButton#BtnPlus:hover {
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.08);
}

QPushButton#BtnPlus:pressed {
    color: #c084fc;
    background-color: rgba(168, 85, 247, 0.15);
}

/* Center Text Input */
QLineEdit#PillInput {
    background-color: transparent;
    border: none;
    color: #ffffff;
    font-size: 14px;
    padding: 0px 6px;
}

QLineEdit#PillInput::placeholder {
    color: #64748b;
    font-weight: 400;
}

/* Right Circular Gradient '↑' Send Button */
QPushButton#BtnSendGradient {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a855f7, stop:0.5 #818cf8, stop:1 #6366f1);
    border: none;
    border-radius: 20px;
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
}

QPushButton#BtnSendGradient:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #c084fc, stop:0.5 #9333ea, stop:1 #4f46e5);
}

QPushButton#BtnSendGradient:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9333ea, stop:1 #4338ca);
}
"""
