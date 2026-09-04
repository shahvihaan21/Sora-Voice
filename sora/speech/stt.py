"Compatibility adapter for the proven dynamic-VAD STT implementation."""
import sys
from pathlib import Path
_AEGIS = Path(__file__).resolve().parents[2] / "aegis"
if str(_AEGIS) not in sys.path:
    sys.path.insert(0, str(_AEGIS))
from BACKEND.speech.stt import SpeechToText
__all__ = ["SpeechToText"]
