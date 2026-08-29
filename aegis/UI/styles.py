# QSS Stylesheet for Jarvis Desktop Assistant

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
    background-color: rgba(15, 5, 10, 0.97);
    border-radius: 22px;
    border: 1px solid rgba(255, 23, 68, 0.28);
}

/* Header Area & Window Controls */
QLabel#HeaderBrand {
    color: #ff1744;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

QLabel#ActionHint {
    color: #ff8a9f;
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
    background-color: rgba(255, 23, 68, 0.14);
    color: #ff526f;
    border: 1px solid rgba(255, 23, 68, 0.5);
}

QLabel#StatusBadge[mode="LISTENING"] {
    background-color: rgba(255, 234, 0, 0.16);
    color: #ffea00;
    border: 1px solid rgba(255, 234, 0, 0.7);
}

QLabel#StatusBadge[mode="THINKING"] {
    background-color: rgba(255, 23, 68, 0.22);
    color: #ff6b81;
    border: 1px solid rgba(255, 23, 68, 0.7);
}

QLabel#StatusBadge[mode="SPEAKING"] {
    background-color: rgba(255, 234, 0, 0.2);
    color: #fff176;
    border: 1px solid rgba(255, 234, 0, 0.7);
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
    background-color: rgba(25, 5, 12, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    color: #f1f5f9;
    font-size: 13px;
    padding: 12px 14px;
    selection-background-color: #d50032;
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
    background-color: rgba(35, 7, 15, 0.97);
    border: 1px solid rgba(255, 23, 68, 0.3);
    border-radius: 27px;
}

#PillInputContainer[mode="LISTENING"] {
    border: 1px solid rgba(255, 234, 0, 0.65);
    background-color: rgba(40, 32, 4, 0.95);
}

#PillInputContainer[mode="THINKING"] {
    border: 1px solid rgba(255, 23, 68, 0.65);
    background-color: rgba(48, 7, 17, 0.95);
}

#PillInputContainer[mode="SPEAKING"] {
    border: 1px solid rgba(255, 234, 0, 0.65);
    background-color: rgba(40, 32, 4, 0.95);
}

#PillInputContainer:focus-within {
    border: 1px solid rgba(255, 23, 68, 0.8);
    background-color: rgba(50, 8, 18, 0.98);
}

/* Left '+' Plus Action Button */
QPushButton#BtnPlus {
    background-color: transparent;
    border: none;
    color: #ff8a9f;
    font-size: 22px;
    font-weight: 300;
    border-radius: 18px;
    padding-bottom: 2px;
}

QPushButton#BtnPlus[active="true"] {
    background-color: rgba(255, 234, 0, 0.25);
    color: #ffea00;
    border: 1px solid rgba(255, 234, 0, 0.7);
    font-size: 16px;
}

QPushButton#BtnPlus:hover {
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.08);
}

QPushButton#BtnPlus:pressed {
    color: #ff1744;
    background-color: rgba(255, 23, 68, 0.18);
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
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff1744, stop:0.5 #ff5252, stop:1 #ffea00);
    border: none;
    border-radius: 20px;
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
}

QPushButton#BtnSendGradient:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff4569, stop:0.5 #ff1744, stop:1 #fff000);
}

QPushButton#BtnSendGradient:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #d50032, stop:1 #ffea00);
}
"""
