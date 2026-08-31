import asyncio
import os
import tempfile
import ctypes
import threading
from typing import Callable, Optional
from BACKEND.logger import log
from BACKEND.config import config
from BACKEND.speech.voice_pack import get_voice_pack

class TextToSpeech:
    def __init__(self, voice: Optional[str] = None):
        self.voice_pack = get_voice_pack()
        self.voice = voice or config.tts_voice or self.voice_pack.voice
        self.rate = getattr(config, "tts_rate", "") or self.voice_pack.rate
        self.pitch = getattr(config, "tts_pitch", "") or self.voice_pack.pitch
        self.volume = getattr(config, "tts_volume", "") or self.voice_pack.volume
        self.is_speaking = False
        self._lock = asyncio.Lock()
        self.on_start_callback: Optional[Callable[[], None]] = None
        self.on_end_callback: Optional[Callable[[], None]] = None
        self._pyttsx3_engine = None
        self._active_alias = None

    async def stop(self):
        """Stop Windows playback immediately when the user disables the mic."""
        alias = self._active_alias
        if alias and hasattr(ctypes, "windll"):
            try:
                ctypes.windll.winmm.mciSendStringW(f"stop {alias}", None, 0, None)
                ctypes.windll.winmm.mciSendStringW(f"close {alias}", None, 0, None)
            except Exception as e:
                log.debug(f"Could not stop active speech: {e}")
        self._active_alias = None
        self.is_speaking = False
        if self._pyttsx3_engine:
            try:
                self._pyttsx3_engine.stop()
            except Exception:
                pass

    def _get_offline_engine(self):
        if self._pyttsx3_engine is None:
            try:
                import pyttsx3
                self._pyttsx3_engine = pyttsx3.init()
                self._pyttsx3_engine.setProperty('rate', self.voice_pack.offline_rate)
                self._select_male_offline_voice(self._pyttsx3_engine)
            except Exception as e:
                log.warning(f"Could not initialize pyttsx3 offline TTS engine: {e}")
        return self._pyttsx3_engine

    @staticmethod
    def _select_male_offline_voice(engine):
        """Prefer a male Windows voice while remaining compatible with any install."""
        try:
            voices = engine.getProperty("voices") or []
            male_terms = ("david", "mark", "guy", "george", "male", "daniel")
            for voice in voices:
                details = " ".join(str(getattr(voice, attr, "")) for attr in ("id", "name", "gender")).lower()
                if any(term in details for term in male_terms):
                    engine.setProperty("voice", voice.id)
                    log.info(f"Offline male voice selected: {getattr(voice, 'name', voice.id)}")
                    return
        except Exception as e:
            log.debug(f"Could not select an offline male voice: {e}")

    def _speak_offline(self, text: str):
        """Fallback local offline text to speech using pyttsx3 or SAPI5."""
        try:
            engine = self._get_offline_engine()
            if engine:
                engine.say(text)
                engine.runAndWait()
                return True
        except Exception as e:
            log.warning(f"pyttsx3 speech failed: {e}")

        # Direct Windows SAPI.SpVoice COM fallback
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Rate = 2  # Slightly faster
            speaker.Speak(text)
            return True
        except Exception:
            pass

        return False

    async def speak(self, text: str):
        if not text or not text.strip():
            return

        async with self._lock:
            self.is_speaking = True
            if self.on_start_callback:
                try:
                    self.on_start_callback()
                except Exception:
                    pass

            log.info(f"Jarvis speaking: {text}")
            success = False

            # 1. Try High Quality Edge-TTS with accelerated speech rate
            try:
                import edge_tts
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                temp_file.close()

                communicate = edge_tts.Communicate(
                    text, voice=self.voice, rate=self.rate,
                    volume=self.volume, pitch=self.pitch,
                )
                await communicate.save(temp_file.name)

                # Play via Windows MCI
                alias = f"jarvis_audio_{abs(hash(text))}_{os.getpid()}"
                self._active_alias = alias
                ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
                
                open_cmd = f'open "{temp_file.name}" alias {alias}'
                res = ctypes.windll.winmm.mciSendStringW(open_cmd, None, 0, None)
                
                if res == 0:
                    ctypes.windll.winmm.mciSendStringW(f'play {alias}', None, 0, None)
                    
                    # MCI can return an empty status briefly during startup.
                    # Wait for a real state so audio is not cut off early.
                    status_buf = ctypes.create_unicode_buffer(256)
                    for _ in range(25):
                        ctypes.windll.winmm.mciSendStringW(f'status {alias} mode', status_buf, 256, None)
                        if status_buf.value:
                            break
                        await asyncio.sleep(0.04)
                    while status_buf.value == "playing":
                        status_buf.value = ""
                        ctypes.windll.winmm.mciSendStringW(f'status {alias} mode', status_buf, 256, None)
                        await asyncio.sleep(0.04)
                        
                    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
                    self._active_alias = None
                    success = True

                # Clean up temporary mp3
                try:
                    os.unlink(temp_file.name)
                except Exception:
                    pass

            except Exception as e:
                log.warning(f"Edge TTS encountered an issue: {e}. Switching to offline speech synthesizer.")

            # 2. Fallback to offline TTS if Edge-TTS failed
            if not success:
                try:
                    await asyncio.to_thread(self._speak_offline, text)
                except Exception as e2:
                    log.error(f"All TTS options failed: {e2}")

            self.is_speaking = False
            if self.on_end_callback:
                try:
                    self.on_end_callback()
                except Exception:
                    pass
