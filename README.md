# Sora Voice — Local Windows Desktop Assistant

Sora is a local-first Windows desktop voice assistant. It combines a futuristic dark PyQt HUD, dynamic-VAD speech input, interruptible Edge-TTS/pyttsx3 speech output, dynamic Ollama conversation, and local execution fallback capability.

---

## Features

- **100% Local AI Intelligence**: Powered by Ollama with `qwen3:1.7b` by default, supporting dynamic discovery and runtime switching among local models (`qwen3:1.7b`, `jarvis-ft:latest`, `gemma4-local:latest`, and `qwen2.5vl:7b` for vision/screen tasks).
- **Sleek Context-Accurate UI**: Modern dark HUD aesthetic with floating rounded glassmorphism window, custom minimalist controls, Ollama connection indicator, active model label, and settings controls (model selector, mute toggle, clear chat).
- **Fluid Multi-Layer Harmonic Waveform & AI Core**: Translucent gradient sine ribbons and concentric particle core that dynamically pulse and react to speech, thinking, listening, and idle states (~30 FPS active, throttled to 10–15 FPS when idle).
- **Floating Pill Input Capsule**: Complete with microphone toggle/stop button, prompt text input, dedicated stop speaking control, and send action.
- **Ultra-Fast Zero-Lag Speech Pipeline**:
  - **Dynamic Voice Activity Detection (VAD)**: Detects speech termination in real-time (~0.7s silence) instead of waiting on fixed duration timers.
  - **Clause & Sentence Streaming**: Yields early tokens to Text-to-Speech immediately for near-zero time to first speech without waiting for full generation.
  - **Cinematic Neural Voice Pack**: Edge-TTS neural voice with fallback to local offline pyttsx3/SAPI5 TTS.
- **Interactive Live Web Preview**: Browser-based UI preview in `web-preview/` for GitHubBox / CodeSandbox without requiring Python GUI or local desktop display.

---

## Requirements & Prerequisites

- **OS**: Windows 10/11 (Linux/macOS supported in headless or windowed mode).
- **Python**: Python 3.10, 3.11, or 3.12.
- **Audio Hardware**: Microphone and sound output device (optional for text-only mode).
- **Ollama**: Download and install from [ollama.com](https://ollama.com).

---

## Installation and Quick Start (Windows)

### 1. Clone & Setup Environment

Open Windows PowerShell:

```powershell
# Clone the repository
git clone https://github.com/shahvihaan21/Sora-Voice.git
cd Sora-Voice

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Copy `.env.example` to `.env` if you want to customize the default model or host:

```powershell
copy .env.example .env
```

### 3. Start Ollama and Pull the Default Model

Ensure Ollama is running, then pull the default conversational model:

```powershell
ollama pull qwen3:1.7b
```

If you have additional models installed (`jarvis-ft:latest`, `gemma4-local:latest`, `qwen2.5vl:7b`), Sora will discover them automatically.

### 4. Launch Desktop Assistant

```powershell
python run.py
```

---

## Switching Models and Vision Routing

- **Dynamic Model Selection**: Select any installed model from the dropdown menu in the settings bar at runtime without restarting the application.
- **Vision Query Routing**: When screenshot or image understanding is requested (e.g. "look at my screen", "screenshot"), Sora automatically routes inference to `qwen2.5vl:7b`. Normal voice conversations use the selected general model (default: `qwen3:1.7b`).

---

## Live Web Preview (GitHubBox / CodeSandbox)

To preview the Sora-Voice futuristic assistant interface live in a browser:

```bash
# Install web preview dependencies
npm install

# Start development server on 0.0.0.0:3000
npm run dev
```

---

## Testing and Diagnostics

Run the automated pytest test suite and system self-diagnostics:

```bash
# Automated pytest suite
python -m pytest

# System Subsystem Diagnostic Suite
python test_system.py
```

---

## Known Limitations & Local vs Network Features

- **Local Ollama LLM**: Performs completely offline when Ollama server is running locally on `http://localhost:11434`.
- **Edge-TTS**: Uses Microsoft's online Edge-TTS service for high-quality speech synthesis when internet is available. If offline or unreachable, Sora automatically falls back to local offline TTS (`pyttsx3` / `SAPI5` on Windows).
- **Google STT**: Default speech recognizer uses online Google STT API. If unreachable or audio hardware is missing, text prompt input remains fully operational.

---

## Architecture

```
Sora-Voice/
├── aegis/
│   ├── BACKEND/
│   │   ├── config.py             # App configuration, model defaults & env loading
│   │   ├── logger.py             # Loguru logger with UTF-8 file & console logging
│   │   ├── intelligence/
│   │   │   └── llm.py            # Ollama streaming engine, model discovery & fast local fallback
│   │   └── speech/
│   │       ├── stt.py            # Dynamic VAD speech recognition & wake word loop
│   │       └── tts.py            # Accelerated Edge-TTS + pyttsx3/SAPI5 offline fallback & mute support
│   ├── UI/
│   │   ├── main_window.py        # Dark HUD window, model selector, mute toggle, pill bar & chat transcript
│   │   ├── styles.py             # Modern dark QSS stylesheet
│   │   └── widgets/
│   │       ├── glass_panel.py    # Rounded glass container
│   │       ├── visualizer.py     # Fluid harmonic visualizer with 30fps/12fps throttling
│   │       └── core.py           # Animated central AI core with frame throttling
│   └── main.py                   # Async controller, command queue & lifecycle management
├── web-preview/                  # Self-contained browser interface preview
│   ├── index.html                # Web HUD layout & controls
│   ├── styles.css                # Obsidian glassmorphism CSS
│   └── app.js                    # Core animation & state simulation logic
├── package.json                  # Web preview Vite server configuration
├── run.py                        # Root Python launcher
├── test_system.py                # System diagnostic suite
└── requirements.txt              # Python desktop dependencies
```
