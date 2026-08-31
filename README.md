# ⚡ Jarvis (v2.0) - Next-Gen AI Desktop Assistant

A sleek, ultra-responsive voice-only desktop assistant named **Jarvis**, powered locally by **Ollama (`jarvis-ft:latest`)**, featuring a modern fluid harmonic waveform, microphone start/stop control, low-latency dynamic VAD voice processing, and neural speech synthesis.

---

## 🌟 Key Features

- **100% Local AI Intelligence**: Powered by Ollama with `jarvis-ft:latest` — private, blazing fast, and offline-capable with instant fallbacks.
- **Sleek Context-Accurate UI**: Replicating the modern Apple Intelligence / Siri dark HUD aesthetic with floating rounded window, custom minimalist controls, and glassmorphism.
- **Fluid Multi-Layer Harmonic Waveform**: Translucent gradient sine ribbons (cyan, blue, purple, magenta) that dynamically pulse and react to speech and thinking states.
- **Floating Pill Input Bar**: Complete with `+` voice trigger action button, clean prompt input, and glowing purple-to-blue gradient `↑` send button.
- **Ultra-Fast Zero-Lag Speech Pipeline**:
  - **Dynamic Voice Activity Detection (VAD)**: Detects speech termination in real-time (0.6s silence) instead of waiting on fixed duration timers.
  - **Clause & Sentence Streaming**: Yields early tokens to Text-to-Speech immediately for near-zero latency.
  - **Accelerated Neural Speech**: Enhanced speech rate (+15%) with Edge-TTS and instant Win32 SAPI5 / pyttsx3 offline fallback.
- **One-Click Windows Launcher**: Automatic environment activation with `run.bat`.

---

## 🚀 Quick Start

### 1. Start Ollama
Ensure you have [Ollama](https://ollama.com) installed and pull the `jarvis-ft:latest` model:
```bash
ollama run jarvis-ft:latest
```

### 2. Simple One-Click Run (Windows)
Double-click `run.bat` or run in terminal:
```cmd
run.bat
```

### 3. Manual Setup
Activate your Python environment and install dependencies:
```bash
pip install -r requirements.txt
```

### 4. Launch Jarvis
```bash
python run.py
```

---

## 🧪 Self-Diagnostic Suite
Run the built-in automated test suite to verify all subsystems:
```bash
python test_system.py
```

---

## 📁 Project Architecture

```
Jarvis/
├── aegis/
│   ├── BACKEND/
│   │   ├── config.py             # App configuration, wake words & voice settings
│   │   ├── logger.py             # Loguru logger with UTF-8 file & console logging
│   │   ├── intelligence/
│   │   │   └── llm.py            # Jarvis Ollama engine (jarvis-ft:latest) + Fast Fallback
│   │   └── speech/
│   │       ├── stt.py            # Dynamic VAD speech recognition & wake word detection
│   │       └── tts.py            # Accelerated Edge-TTS + Offline SAPI5 TTS
│   ├── UI/
│   │   ├── main_window.py        # Dark HUD window, pill bar & chat transcript
│   │   ├── styles.py             # Modern obsidian dark QSS stylesheet
│   │   └── widgets/
│   │       ├── glass_panel.py    # Rounded obsidian glass container
│   │       └── visualizer.py     # Siri-style multi-layer fluid harmonic visualizer
│   └── main.py                   # Async controller, command queue & event loop
├── run.py                        # Root Python launcher
├── run.bat                       # Windows double-click launcher
├── test_system.py                # Automated 6-part test suite
├── requirements.txt              # Project dependencies
├── .env.example                  # Environment configuration template
└── logs/                         # Application logs
```
