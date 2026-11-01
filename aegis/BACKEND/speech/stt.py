import asyncio
import tempfile
import os
import threading
from typing import List, Optional, Callable
import numpy as np
from BACKEND.logger import log
from BACKEND.config import config

class SpeechToText:
    def __init__(self, wake_words: Optional[List[str]] = None):
        self.wake_words = wake_words or config.wake_words
        self.sample_rate = config.sample_rate
        self.has_microphone = False
        self._recognizer = None
        # Prevent the wake-word loop and the manual trigger from recording at
        # the same time. Concurrent microphone streams are unreliable on Windows.
        self._command_lock = asyncio.Lock()
        self._stop_event = threading.Event()

        self.on_listening_callback: Optional[Callable[[], None]] = None
        self.on_processing_callback: Optional[Callable[[], None]] = None

        self._check_audio_hardware()

    def _check_audio_hardware(self):
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            input_devices = [d for d in devices if d.get('max_input_channels', 0) > 0]
            if input_devices:
                self.has_microphone = True
                log.info(f"Microphone detected: {input_devices[0].get('name', 'Default Mic')}")
            else:
                self.has_microphone = False
                log.warning("No audio input device detected. Voice wake word will be paused.")
        except Exception as e:
            self.has_microphone = False
            log.warning(f"Could not initialize audio input devices: {e}")

    @property
    def recognizer(self):
        if self._recognizer is None:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            self._recognizer.energy_threshold = 220
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.8
            self._recognizer.non_speaking_duration = 0.35
        return self._recognizer

    def stop(self):
        """Request immediate release of an active recording stream."""
        self._stop_event.set()

    def prewarm(self):
        """Import heavy STT deps once at startup, off the critical path."""
        try:
            _ = self.recognizer
        except Exception:
            pass
        for mod in ("sounddevice", "soundfile", "speech_recognition"):
            try:
                __import__("importlib").import_module(mod)
            except Exception:
                pass

    def _array_to_audio_data(self, audio_array: np.ndarray):
        """Convert float32 numpy audio array directly into SpeechRecognition AudioData without disk I/O."""
        import speech_recognition as sr
        int16_data = np.clip(audio_array * 32767.0, -32768, 32767).astype(np.int16)
        raw_bytes = int16_data.tobytes()
        return sr.AudioData(raw_bytes, self.sample_rate, 2)

    async def listen_for_wake_word(self) -> bool:
        """
        Listens in short dynamic chunks for Jarvis wake words with zero disk I/O.
        """
        if not self.has_microphone or self._stop_event.is_set():
            return False

        loop = asyncio.get_running_loop()

        def _record_and_check() -> bool:
            if self._stop_event.is_set():
                return False
            import sounddevice as sd
            import speech_recognition as sr
            import time

            duration = 1.8  # Quick window
            try:
                recording = sd.rec(
                    int(duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='float32'
                )
                elapsed = 0.0
                step = 0.1
                while elapsed < duration:
                    if self._stop_event.is_set():
                        try:
                            sd.stop()
                        except Exception:
                            pass
                        return False
                    time.sleep(step)
                    elapsed += step

                if self._stop_event.is_set():
                    return False

                max_amp = float(np.max(np.abs(recording)))
                if max_amp < 0.012:
                    return False

                try:
                    audio_data = self._array_to_audio_data(recording)
                    text = self.recognizer.recognize_google(audio_data).lower()
                    log.debug(f"Wake check heard: '{text}'")

                    for ww in self.wake_words:
                        if ww in text:
                            return True
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    log.debug(f"Google STT network notice: {e}")
                except Exception as e:
                    log.debug(f"STT recognition notice: {e}")

            except Exception as e:
                log.debug(f"Wake capture notice: {e}")

            return False

        if self._command_lock.locked():
            return False

        try:
            detected = await loop.run_in_executor(None, _record_and_check)
            if detected and not self._stop_event.is_set():
                log.info("Jarvis wake word recognized!")
                return True
        except Exception as e:
            log.debug(f"Wake loop error: {e}")

        return False

    async def listen_for_command(self) -> str:
        """
        Listens dynamically for the user's spoken command with silence detection.
        Converts in-memory float PCM directly into AudioData without disk file writes.
        """
        if not self.has_microphone:
            return ""

        if self.on_listening_callback:
            try:
                self.on_listening_callback()
            except Exception:
                pass

        loop = asyncio.get_event_loop()

        def _record_command_dynamic() -> str:
            import sounddevice as sd
            import speech_recognition as sr
            import time

            chunk_duration = 0.1  # 100ms chunks
            chunk_samples = int(chunk_duration * self.sample_rate)
            max_recording_time = config.max_command_seconds
            silence_timeout = config.vad_silence_timeout
            energy_threshold = config.vad_energy_threshold
            log.debug(
                f"Voice capture started (max={max_recording_time}s, "
                f"silence={silence_timeout}s, threshold={energy_threshold})"
            )

            audio_chunks = []
            speech_started = False
            silence_start_time = None
            start_time = time.time()

            try:
                with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32') as stream:
                    while time.time() - start_time < max_recording_time and not self._stop_event.is_set():
                        chunk, _ = stream.read(chunk_samples)
                        audio_chunks.append(chunk)

                        # Optimized single-pass VAD check on absolute max amplitude
                        max_val = float(np.max(np.abs(chunk)))
                        if max_val >= energy_threshold:
                            speech_started = True
                            silence_start_time = None
                        elif speech_started:
                            if silence_start_time is None:
                                silence_start_time = time.time()
                            elif time.time() - silence_start_time > silence_timeout:
                                log.debug("Dynamic VAD detected end of speech.")
                                break

                if not audio_chunks or not speech_started:
                    return ""

                full_audio = np.concatenate(audio_chunks, axis=0)

                try:
                    if self.on_processing_callback:
                        self.on_processing_callback()

                    audio_data = self._array_to_audio_data(full_audio)
                    text = self.recognizer.recognize_google(audio_data)
                    return text.strip()
                except sr.UnknownValueError:
                    log.debug("Speech was not intelligible.")
                    return ""
                except sr.RequestError as e:
                    log.warning(f"STT recognition request error: {e}")
                    return ""

            except Exception as e:
                log.warning(f"Voice recognition error: {e}")
                return ""

        async with self._command_lock:
            self._stop_event.clear()
            return await loop.run_in_executor(None, _record_command_dynamic)
