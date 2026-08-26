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
    app_name: str = "Sora AI"
    version: str = "2.0.0"
    debug: bool = True
    
    # UI Customization
    theme: str = "dark"
    accent_color: str = "#a855f7"  # Purple/Violet gradient accent
    secondary_color: str = "#38bdf8" # Cyan/Blue
    
    # Local AI (Ollama)
    ollama_host: str = Field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434").strip())
    ollama_model: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2:3b").strip())
    
    # Speech & Voice
    wake_words: List[str] = Field(
        default_factory=lambda: [
            w.strip().lower() 
            for w in os.getenv("WAKE_WORDS", "sora,hey sora").split(",") 
            if w.strip()
        ]
    )
    tts_voice: str = Field(default_factory=lambda: os.getenv("TTS_VOICE", "en-US-AriaNeural").strip())
    tts_rate: str = Field(default_factory=lambda: os.getenv("TTS_RATE", "+15%").strip())
    sample_rate: int = 16000
    
    # Paths
    base_dir: Path = BASE_DIR
    logs_dir: Path = BASE_DIR / "logs"
    data_dir: Path = BASE_DIR / "data"
    
    def ensure_dirs(self):
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

config = AppConfig()
config.ensure_dirs()
