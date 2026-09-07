import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Find workspace root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOTENV_PATH = BASE_DIR / ".env"

if DOTENV_PATH.exists():
    load_dotenv(dotenv_path=DOTENV_PATH)
else:
    load_dotenv()

class AppConfig(BaseModel):
    app_name: str = "Jarvis"
    version: str = "2.0.0"
    debug: bool = True

    # UI Customization
    theme: str = "dark"
    accent_color: str = "#ff1744"  # Neon red accent
    secondary_color: str = "#ffea00" # Neon yellow highlight

    # Local AI (Ollama)
    ollama_host: str = Field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434").strip().rstrip("/"))
    ollama_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "jarvis-ft:latest").strip())
    ollama_timeout: float = Field(default_factory=lambda: float(os.getenv("OLLAMA_TIMEOUT", "15").strip()))

    # Speech & Voice
    wake_words: List[str] = Field(
        default_factory=lambda: [
            w.strip().lower()
            for w in os.getenv("WAKE_WORDS", "jarvis,hey jarvis").split(",")
            if w.strip()
        ]
    )
    tts_voice: str = Field(default_factory=lambda: os.getenv("TTS_VOICE", "").strip())
    tts_rate: str = Field(default_factory=lambda: os.getenv("TTS_RATE", "").strip())
    tts_pitch: str = Field(default_factory=lambda: os.getenv("TTS_PITCH", "").strip())
    tts_volume: str = Field(default_factory=lambda: os.getenv("TTS_VOLUME", "").strip())
    sample_rate: int = Field(default_factory=lambda: int(os.getenv("SAMPLE_RATE", "16000").strip()))
    vad_energy_threshold: float = Field(default_factory=lambda: float(os.getenv("VAD_ENERGY_THRESHOLD", "0.010").strip()))
    vad_silence_timeout: float = Field(default_factory=lambda: float(os.getenv("VAD_SILENCE_TIMEOUT", "0.7").strip()))
    max_command_seconds: float = Field(default_factory=lambda: float(os.getenv("MAX_COMMAND_SECONDS", "8").strip()))

    # Paths
    base_dir: Path = BASE_DIR
    logs_dir: Path = BASE_DIR / "logs"
    data_dir: Path = BASE_DIR / "data"

    def ensure_dirs(self):
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

config = AppConfig()
config.ensure_dirs()
