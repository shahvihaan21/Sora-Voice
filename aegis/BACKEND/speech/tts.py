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
        self._sentence_queue: asyncio.Queue = asyncio.Queue()
        self._player_task = None
        self._started = False

    async def stop(self):
        """Stop Windows playback immediately when the user disables the mic."""
        # drop queued sentences so interruption is instant
        try:
            while not self._sentence_queue.empty():
                try:
                    self._sentence_queue.get_nowait()
                    self._sentence_queue.task_done()
                except Exception:
                    break
        except Exception:
            pass
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

    async def _ensure_player(self):
        if self._player_task is None or self._player_task.done():
            self._player_task = asyncio.create_task(self._player_loop())
        if not self._started:
            self._started = True

    async def _player_loop(self):
        while True:
            item = await self._sentence_queue.get()
            if item is None:  # flush sentinel
                self._sentence_queue.task_done()
                continue
            try:
                await self._speak_one(item)
            finally:
                self._sentence_queue.task_done()

    async def speak_stream(self, text: str):
        """Enqueue one clause/sentence for immediate playback (non-blocking)."""
        if not text or not text.strip():
            return
        await self._ensure_player()
        await self._sentence_queue.put(text.strip())

    async def flush(self):
        try:
            await self._sentence_queue.join()
        except Exception:
            pass

    async def speak(self, text: str):
        if not text or not text.strip():
            return
        await self._ensure_player()
        # keep old API: full-text speak goes through the same player
        await self._sentence_queue.put(text.strip())
        await self.flush()

    async def prewarm(self):
        """Warm TTS engine + edge-tts import off the critical path (call at startup)."""
        try:
            await asyncio.to_thread(self._get_offline_engine)
        except Exception:
            pass
        try:
            await asyncio.to_thread(__import__("importlib").import_module, "edge_tts")
        except Exception:
            pass

    async def _speak_one(self, text: str):
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
