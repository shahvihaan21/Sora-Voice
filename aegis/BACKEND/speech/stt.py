import asyncio
import tempfile
import os
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
            self._recognizer.energy_threshold = 280
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.6  # Snappy pause detection
        return self._recognizer

    async def listen_for_wake_word(self) -> bool:
        """
        Listens in short dynamic chunks for Sora wake words.
        """
        if not self.has_microphone:
            await asyncio.sleep(2)
            return False

        loop = asyncio.get_event_loop()

        def _record_and_check() -> bool:
            import sounddevice as sd
            import soundfile as sf
            import speech_recognition as sr

            duration = 1.8  # Quick window
            try:
                recording = sd.rec(
                    int(duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='float32'
                )
                sd.wait()

                # Check if audio has energy
                if np.max(np.abs(recording)) < 0.012:
                    return False

                temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_wav.close()
                sf.write(temp_wav.name, recording, self.sample_rate)

                try:
                    with sr.AudioFile(temp_wav.name) as source:
                        audio = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio).lower()
                    log.debug(f"Wake check heard: '{text}'")

                    for ww in self.wake_words:
                        if ww in text:
                            return True
                except sr.UnknownValueError:
                    # Silence or unrecognized audio is normal during wake checks
                    pass
                except sr.RequestError as e:
                    log.debug(f"Google STT network notice: {e}")
                except Exception as e:
                    log.debug(f"STT recognition notice: {e}")
                finally:
                    try:
                        os.unlink(temp_wav.name)
                    except Exception:
                        pass

            except Exception as e:
                log.debug(f"Wake capture notice: {e}")

            return False

        while True:
            if not self.has_microphone:
                await asyncio.sleep(2)
                return False

            try:
                detected = await loop.run_in_executor(None, _record_and_check)
                if detected:
                    log.info("Sora wake word recognized!")
                    return True
            except Exception as e:
                log.debug(f"Wake loop error: {e}")
                
            await asyncio.sleep(0.04)

    async def listen_for_command(self) -> str:
        """
        Listens dynamically for the user's spoken command with silence detection.
        Stops recording immediately when speech stops, eliminating delay.
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
            import soundfile as sf
            import speech_recognition as sr
            import time

            chunk_duration = 0.1  # 100ms chunks
            chunk_samples = int(chunk_duration * self.sample_rate)
            max_recording_time = 8.0  # Max seconds
            silence_timeout = 0.7     # Stop after 700ms of silence once speech started
            energy_threshold = 0.015

            audio_chunks = []
            speech_started = False
            silence_start_time = None
            start_time = time.time()

            try:
                with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32') as stream:
                    while time.time() - start_time < max_recording_time:
                        chunk, _ = stream.read(chunk_samples)
                        audio_chunks.append(chunk)
                        max_val = np.max(np.abs(chunk))

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

                temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                temp_wav.close()
                sf.write(temp_wav.name, full_audio, self.sample_rate)

                try:
                    if self.on_processing_callback:
                        self.on_processing_callback()

                    with sr.AudioFile(temp_wav.name) as source:
                        audio = self.recognizer.record(source)
                    
                    text = self.recognizer.recognize_google(audio)
                    return text.strip()
                except sr.UnknownValueError:
                    log.debug("Speech was not intelligible.")
                    return ""
                except sr.RequestError as e:
                    log.warning(f"STT recognition request error: {e}")
                    return ""
                finally:
                    try:
                        os.unlink(temp_wav.name)
                    except Exception:
                        pass

            except Exception as e:
                log.warning(f"Voice recognition error: {e}")
                return ""

        text = await loop.run_in_executor(None, _record_command_dynamic)
        return text
