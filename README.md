# Sora Voice — Local Windows Assistant

Sora is a local-first Windows desktop assistant. It combines the existing PyQt HUD, dynamic-VAD speech input, interruptible Edge-TTS/pyttsx3 speech output, Ollama conversation, and a validated tool layer for safe system actions. Cloud speech fallbacks remain optional legacy compatibility paths; Sora never gives the LLM arbitrary shell access.

---

## Features

- **100% Local AI Intelligence**: Powered by Ollama with `jarvis-ft:latest` — private, blazing fast, and offline-capable with instant fallbacks.
- **Sleek Context-Accurate UI**: Replicating the modern Apple Intelligence / Siri dark HUD aesthetic with floating rounded window, custom minimalist controls, and glassmorphism.
- **Fluid Multi-Layer Harmonic Waveform**: Translucent gradient sine ribbons (cyan, blue, purple, magenta) that dynamically pulse and react to speech and thinking states.
- **Floating Pill Input Bar**: Complete with `+` voice trigger action button, clean prompt input, and glowing purple-to-blue gradient `↑` send button.
- **Ultra-Fast Zero-Lag Speech Pipeline**:
  - **Dynamic Voice Activity Detection (VAD)**: Detects speech termination in real-time (0.6s silence) instead of waiting on fixed duration timers.
  - **Clause & Sentence Streaming**: Yields early tokens to Text-to-Speech immediately for near-zero latency.
  - **Cinematic British Voice Pack**: British `en-GB-RyanNeural` voice, deliberate delivery, and lower pitch with Edge-TTS plus an offline fallback. It is an original neural-voice configuration, not a clone of the film performance.
- **One-Click Windows Launcher**: Automatic environment activation with `run.bat`.

---

## Installation and Quick Start

### 1. Start Ollama
Install [Ollama](https://ollama.com), then pull the configured model:
```bash
ollama pull llama3.2:3b
ollama run llama3.2:3b
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

To enable the voice pack, copy `.env.example` to `.env` and keep `TTS_PROFILE=cinematic_assistant`. `jarvis_classic` remains as a backward-compatible alias. Use `TTS_PROFILE=neutral` or set `TTS_VOICE`, `TTS_RATE`, `TTS_PITCH`, and `TTS_VOLUME` to customize it.

### 4. Launch Jarvis
```bash
python run.py
```

---

## Testing and diagnostics
Run the built-in automated test suite to verify all subsystems:
```bash
python test_system.py
```

---

## Architecture

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
