"Compatibility adapter for the original interruptible Edge-TTS/SAPI pipeline."""
import sys
from pathlib import Path
_AEGIS = Path(__file__).resolve().parents[2] / "aegis"
if str(_AEGIS) not in sys.path:
    sys.path.insert(0, str(_AEGIS))
from BACKEND.speech.tts import TextToSpeech
__all__ = ["TextToSpeech"]
