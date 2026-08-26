import asyncio
import os
import tempfile
import ctypes
import threading
from typing import Callable, Optional
from core.logger import log
from core.config import config

class TextToSpeech:
    def __init__(self, voice: Optional[str] = None):
        self.voice = voice or config.tts_voice
        self.rate = getattr(config, "tts_rate", "+15%")
        self.is_speaking = False
        self._lock = asyncio.Lock()
        self.on_start_callback: Optional[Callable[[], None]] = None
        self.on_end_callback: Optional[Callable[[], None]] = None
        self._pyttsx3_engine = None

    def _get_offline_engine(self):
        if self._pyttsx3_engine is None:
            try:
                import pyttsx3
                self._pyttsx3_engine = pyttsx3.init()
                self._pyttsx3_engine.setProperty('rate', 190)
            except Exception as e:
                log.warning(f"Could not initialize pyttsx3 offline TTS engine: {e}")
        return self._pyttsx3_engine

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

            log.info(f"Sora speaking: {text}")
            success = False

            # 1. Try High Quality Edge-TTS with accelerated speech rate
            try:
                import edge_tts
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                temp_file.close()

                communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
                await communicate.save(temp_file.name)

                # Play via Windows MCI
                alias = f"sora_audio_{abs(hash(text))}_{os.getpid()}"
                ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
                
                open_cmd = f'open "{temp_file.name}" alias {alias}'
                res = ctypes.windll.winmm.mciSendStringW(open_cmd, None, 0, None)
                
                if res == 0:
                    ctypes.windll.winmm.mciSendStringW(f'play {alias}', None, 0, None)
                    
                    status_buf = ctypes.create_unicode_buffer(256)
                    while True:
                        ctypes.windll.winmm.mciSendStringW(f'status {alias} mode', status_buf, 256, None)
                        if status_buf.value != "playing":
                            break
                        await asyncio.sleep(0.04)
                        
                    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
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
