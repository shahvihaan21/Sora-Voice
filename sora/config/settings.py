"""Central configuration for Sora.

All settings are read from environment variables (optionally a `.env` file in
the project root). Every setting has a sensible default so a clean install
works with minimal configuration.
"""
import os
from pathlib import Path
from typing import Dict, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOTENV_PATH = BASE_DIR / ".env"

if DOTENV_PATH.exists():
    load_dotenv(dotenv_path=DOTENV_PATH)
else:
    load_dotenv()


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _app_aliases() -> Dict[str, str]:
    """Parse SORA_APP_ALIASES as `name=path;name=path`."""
    raw = _env("SORA_APP_ALIASES")
    aliases: Dict[str, str] = {}
    for pair in raw.split(";"):
        if "=" in pair:
            name, target = pair.split("=", 1)
            if name.strip() and target.strip():
                aliases[name.strip().lower()] = target.strip()
    return aliases


class AppConfig(BaseModel):
    app_name: str = "Sora"
    version: str = "3.0.0"
    debug: bool = Field(default_factory=lambda: _env("DEBUG", "False").lower() in ("1", "true", "yes"))

    # Local AI (Ollama)
    ollama_host: str = Field(default_factory=lambda: _env("OLLAMA_HOST", "http://localhost:11434"))
    ollama_model: str = Field(default_factory=lambda: _env("OLLAMA_MODEL", "llama3.2:3b"))
    ollama_timeout: float = Field(default_factory=lambda: float(_env("OLLAMA_TIMEOUT", "30")))

    # Speech & voice
    wake_words: List[str] = Field(
        default_factory=lambda: [
            w.strip().lower()
            for w in _env("WAKE_WORDS", "sora,hey sora").split(",")
            if w.strip()
        ]
    )
    tts_profile: str = Field(default_factory=lambda: _env("TTS_PROFILE", "sora_classic"))
    tts_voice: str = Field(default_factory=lambda: _env("TTS_VOICE"))
    tts_rate: str = Field(default_factory=lambda: _env("TTS_RATE"))
    tts_pitch: str = Field(default_factory=lambda: _env("TTS_PITCH"))
    tts_volume: str = Field(default_factory=lambda: _env("TTS_VOLUME"))
    sample_rate: int = Field(default_factory=lambda: int(_env("SAMPLE_RATE", "16000")))
    mic_energy_threshold: float = Field(default_factory=lambda: float(_env("MIC_ENERGY_THRESHOLD", "280")))

    # VAD / listening
    vad_energy_threshold: float = Field(default_factory=lambda: float(_env("VAD_ENERGY_THRESHOLD", "0.010")))
    vad_silence_timeout: float = Field(default_factory=lambda: float(_env("VAD_SILENCE_TIMEOUT", "0.7")))
    max_command_seconds: float = Field(default_factory=lambda: float(_env("MAX_COMMAND_SECONDS", "8")))

    # Tools
    app_aliases: Dict[str, str] = Field(default_factory=_app_aliases)
    confirmation_timeout: float = Field(default_factory=lambda: float(_env("CONFIRMATION_TIMEOUT", "20")))
    tool_timeout: float = Field(default_factory=lambda: float(_env("TOOL_TIMEOUT", "15")))

    # UI
    theme: str = "dark"
    accent_color: str = "#ff1744"
    secondary_color: str = "#ffea00"

    # Logging
    log_level: str = Field(default_factory=lambda: _env("LOG_LEVEL", "DEBUG"))

    # Paths
    base_dir: Path = BASE_DIR
    logs_dir: Path = BASE_DIR / "logs"
    data_dir: Path = BASE_DIR / "data"

    def ensure_dirs(self):
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)


config = AppConfig()
config.ensure_dirs()
