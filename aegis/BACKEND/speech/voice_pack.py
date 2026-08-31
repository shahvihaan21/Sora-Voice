"""Configurable, JARVIS-inspired speech profiles.

These profiles tune a hosted neural voice; they do not clone a performer.
"""
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class VoicePack:
    name: str
    voice: str
    rate: str
    pitch: str
    volume: str
    offline_rate: int


VOICE_PACKS = {
    # Original cinematic British assistant profile. The legacy key remains
    # supported so existing .env files continue to work.
    "cinematic_assistant": VoicePack("Cinematic British assistant", "en-GB-RyanNeural", "-10%", "-5Hz", "+0%", 175),
    "jarvis_classic": VoicePack("Cinematic British assistant", "en-GB-RyanNeural", "-10%", "-5Hz", "+0%", 175),
    "neutral": VoicePack("Neutral assistant", "en-US-GuyNeural", "+0%", "+0Hz", "+0%", 190),
}


def get_voice_pack() -> VoicePack:
    selected = os.getenv("TTS_PROFILE", "jarvis_classic").strip().lower()
    pack = VOICE_PACKS.get(selected, VOICE_PACKS["jarvis_classic"])
    custom_voice = os.getenv("TTS_VOICE", "").strip()
    if custom_voice:
        pack = VoicePack(pack.name, custom_voice, pack.rate, pack.pitch, pack.volume, pack.offline_rate)
    return pack
