"Compatibility export for the existing configurable voice profiles."""
import sys
from pathlib import Path
_AEGIS = Path(__file__).resolve().parents[2] / "aegis"
if str(_AEGIS) not in sys.path:
    sys.path.insert(0, str(_AEGIS))
from BACKEND.speech.voice_pack import VoicePack, VOICE_PACKS, get_voice_pack
__all__ = ["VoicePack", "VOICE_PACKS", "get_voice_pack"]
