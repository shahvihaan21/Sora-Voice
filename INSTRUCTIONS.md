# Sora Voice — Complete Laptop Setup & Execution Guide

This document contains step-by-step instructions to get **Sora Voice** up and running on your personal laptop (Windows, macOS, or Linux).

---

## 1. System Requirements & Prerequisites

Before starting, ensure your system has:

1. **Python 3.10, 3.11, or 3.12**
   - Download from [python.org](https://www.python.org/downloads/).
   - **Crucial for Windows**: During installation, check the box **"Add Python to PATH"**.
2. **Ollama** (for local LLM inference)
   - Download and install from [ollama.com](https://ollama.com).
   - After installation, Ollama runs in the background as a local service at `http://localhost:11434`.
3. **Audio Hardware**:
   - Built-in or external microphone and speakers/headphones.
4. **Git** (optional, to clone or update the repository)
   - Download from [git-scm.com](https://git-scm.com/).

---

## 2. Quick Start (Windows Laptop)

### Method A: One-Click Startup Helper (`run.bat`)

If you are on Windows, a launcher script `run.bat` is provided in the repository root.

1. Double-click **`run.bat`** (or open Command Prompt / PowerShell and run `.\run.bat`).
2. The script will:
   - Detect or create a virtual environment (`venv`).
   - Install required packages from `requirements.txt` if needed.
   - Launch the Sora Voice desktop application.

---

### Method B: Manual Step-by-Step (Windows PowerShell)

Open PowerShell in the project folder:

```powershell
# 1. (Optional) Create and activate a Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# If PowerShell blocks script execution, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Upgrade pip and install Python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Pull the default Ollama model (ensure Ollama app is running)
ollama pull qwen3:1.7b

# (Optional vision model if using screenshot / screen queries)
ollama pull qwen2.5vl:7b

# 4. Copy the environment template (optional)
copy .env.example .env

# 5. Launch Sora Voice
python run.py
```

---

## 3. Quick Start (macOS / Linux Laptop)

### Step 1: System Audio Library (Linux only)

If you are on Ubuntu/Debian Linux, install PortAudio and speech packages:

```bash
sudo apt update
sudo apt install -y portaudio19-dev python3-pyaudio espeak espeak-ng
```

On macOS (using Homebrew):

```bash
brew install portaudio
```

### Step 2: Run Setup & Application

Using the provided shell script:

```bash
chmod +x run.sh
./run.sh
```

Or manually:

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Pull Ollama model
ollama pull qwen3:1.7b

# 4. Launch
python3 run.py
```

---

## 4. How to Use Sora Voice

Once the application window appears:

1. **Voice Input (Hands-free / Push-to-Talk)**:
   - Click the **MIC** button in the floating pill bar to begin listening.
   - Speak your prompt (or say wake words like *"Jarvis"* / *"Hey Jarvis"*).
   - Sora uses dynamic Voice Activity Detection (VAD) to sense when you finish speaking (~0.7s silence).
2. **Text Input**:
   - Type any question or command into the input pill capsule (`Ask Sora anything...`) and press **Enter** or click **>**.
3. **Stop Speech / Cancel**:
   - Click the **STOP** button to immediately halt ongoing speech playback or cancel ongoing generation.
4. **Mute / Unmute**:
   - Click the **MUTE** button in the top bar to toggle audio speech output on/off.
5. **Switch AI Models Dynamically**:
   - Use the model dropdown in the top controls bar to switch between installed Ollama models (`qwen3:1.7b`, `jarvis-ft:latest`, `gemma4-local:latest`, etc.) without restarting.
6. **Clear Conversation**:
   - Click the **CLEAR** button to wipe previous turns and reset conversation context.

---

## 5. Web Preview Mode (Alternative Lightweight Interface)

If you wish to preview the interactive futuristic HUD in your web browser (without running Python GUI or desktop audio drivers):

```bash
# 1. Install Node.js dependencies
npm install

# 2. Launch Vite local dev preview server
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## 6. Running Diagnostic Tests

To verify that your installation is healthy and all modules function properly:

```bash
# 1. Run unit test suite
python -m pytest

# 2. Run system diagnostic check
python test_system.py
```

---

## 7. Troubleshooting & Common Issues

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **"Microphone not detected" / STT warning** | Microphone permissions disabled or PortAudio missing. | Ensure your OS privacy settings allow apps to access the microphone. On Linux, ensure `portaudio19-dev` is installed. Text input works even without microphone. |
| **"Ollama server offline / fallback response"** | Ollama is not installed or service is not running. | Download Ollama from [ollama.com](https://ollama.com) and start the application. Run `ollama list` in terminal to confirm. |
| **"Model 'qwen3:1.7b' not found"** | Model has not been downloaded yet. | In a separate terminal, run `ollama pull qwen3:1.7b`. |
| **Edge-TTS audio errors** | No internet connection for Microsoft Edge neural voice. | Sora automatically falls back to your local offline voice (`pyttsx3` / Windows SAPI5). No action needed. |
| **PyQt screen error on Linux (headless)** | Missing X11/Wayland display server. | Run `export QT_QPA_PLATFORM=offscreen` before running tests or scripts headless. |
| **PowerShell script execution policy error** | Windows restricts unsigned script execution by default. | Run PowerShell as Administrator and execute `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`. |

---

Enjoy using **Sora Voice** on your laptop!
