# Sora Voice — Local Windows Assistant

Sora is a local-first Windows desktop assistant. It combines a futuristic PyQt HUD, dynamic-VAD speech input, interruptible Edge-TTS/pyttsx3 speech output, Ollama conversation, and local execution fallback capability.

---

## Features

- **100% Local AI Intelligence**: Powered by Ollama (`jarvis-ft:latest`, `llama3.2:3b`, or any installed Ollama model) — private, responsive, and offline-capable with instant fallback.
- **Sleek Context-Accurate UI**: Modern dark HUD aesthetic with floating rounded glassmorphism window, custom minimalist controls, and state indicators.
- **Fluid Multi-Layer Harmonic Waveform**: Translucent gradient sine ribbons that dynamically pulse and react to speech, thinking, listening, and idle states.
- **Floating Pill Input Bar**: Complete with microphone toggle/stop button, prompt input, and send action.
- **Ultra-Fast Zero-Lag Speech Pipeline**:
  - **Dynamic Voice Activity Detection (VAD)**: Detects speech termination in real-time (~0.7s silence) instead of waiting on fixed duration timers.
  - **Clause & Sentence Streaming**: Yields early tokens to Text-to-Speech immediately for near-zero time to first speech.
  - **Cinematic Neural Voice Pack**: Edge-TTS neural voice with fallback to local offline pyttsx3/SAPI5 TTS.
- **One-Click Launcher**: Launch easily with `python run.py`.

---

## Requirements & Prerequisites

- **OS**: Windows 10/11 (Linux/macOS supported in headless or windowed mode).
- **Python**: Python 3.10, 3.11, or 3.12.
- **Audio Hardware**: Microphone and sound output device (optional for text-only mode).
- **Ollama**: Download and install from [ollama.com](https://ollama.com).

---

## Installation and Quick Start

### 1. Clone & Setup Environment

```bash
# Clone the repository
git clone https://github.com/user/sora-voice.git
cd sora-voice

# Create and activate virtual environment
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Copy `.env.example` to `.env` if you want to customize the model, Ollama host, wake words, or voice parameters:

```bash
cp .env.example .env
```

### 3. Start Ollama and Pull a Model

Install [Ollama](https://ollama.com), then start the Ollama server and pull your desired model (e.g., `llama3.2:3b` or custom fine-tune `jarvis-ft:latest`):

```bash
# Pull llama3.2:3b (or set OLLAMA_MODEL=llama3.2:3b in .env)
ollama pull llama3.2:3b
```

### 4. Launch Assistant

```bash
python run.py
```

---

## Testing and Diagnostics

Run unit tests and system diagnostics:

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
aegis/
├── BACKEND/
│   ├── config.py             # App configuration, env loading & defaults
│   ├── logger.py             # Loguru logger with UTF-8 file & console logging
│   ├── intelligence/
│   │   └── llm.py            # Ollama streaming engine + fast local fallback
│   └── speech/
│       ├── stt.py            # Dynamic VAD speech recognition & wake word loop
│       └── tts.py            # Accelerated Edge-TTS + pyttsx3/SAPI5 offline fallback
├── UI/
│   ├── main_window.py        # Dark HUD window, pill bar & chat transcript
│   ├── styles.py             # Modern dark QSS stylesheet
│   └── widgets/
│       ├── glass_panel.py    # Rounded glass container
│       └── visualizer.py     # Siri-style multi-layer fluid harmonic visualizer
└── main.py                   # Async controller, command queue & microphone lifecycle
run.py                        # Root Python launcher
test_system.py                # System diagnostic suite
```
