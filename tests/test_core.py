import pytest
import asyncio
import sys
import os

if sys.platform.startswith("linux") and not os.getenv("DISPLAY") and not os.getenv("QT_QPA_PLATFORM"):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

from aegis.BACKEND.config import AppConfig
from aegis.BACKEND.intelligence.llm import IntelligenceEngine
from aegis.BACKEND.speech.stt import SpeechToText
from aegis.BACKEND.speech.tts import TextToSpeech
from aegis.UI.main_window import MainWindow
from aegis.UI.widgets.core import AICore
from aegis.UI.widgets.visualizer import VisualizerMode
from PyQt6.QtWidgets import QApplication


def test_config_defaults_and_env_override(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    cfg = AppConfig()
    assert cfg.ollama_model == "llama3.2:3b"
    assert cfg.ollama_host == "http://127.0.0.1:11434"


@pytest.mark.asyncio
async def test_llm_offline_fallback():
    engine = IntelligenceEngine()
    response = await engine.generate_response("what time is it?")
    assert "currently" in response.lower() or "time" in response.lower()

    response_calc = await engine.generate_response("calculate 25 * 4")
    assert "100" in response_calc


@pytest.mark.asyncio
async def test_llm_streaming_clauses():
    engine = IntelligenceEngine()
    chunks = []
    async for chunk in engine.generate_response_stream("calculate 10 + 10"):
        chunks.append(chunk)
    assert len(chunks) > 0
    joined = " ".join(chunks)
    assert "20" in joined


@pytest.mark.asyncio
async def test_stt_lifecycle_and_cancellation():
    stt = SpeechToText()
    stt.stop()
    assert stt._stop_event.is_set()

    # Wake check should immediately return False when stop event is set
    wake_res = await stt.listen_for_wake_word()
    assert wake_res is False


@pytest.mark.asyncio
async def test_tts_stop_and_interruption():
    tts = TextToSpeech()
    await tts.speak_stream("First clause.")
    await tts.speak_stream("Second clause.")
    await tts.stop()
    assert tts.is_speaking is False
    assert tts._sentence_queue.empty()


def test_ai_core_widget():
    app = QApplication.instance() or QApplication(sys.argv)
    core = AICore()
    core.set_mode("THINKING")
    assert core.mode == "THINKING"
    core.set_level(0.8)
    assert core._target == 0.8


def test_main_window_ui_and_status_transitions():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()

    window.set_system_status("Online", VisualizerMode.IDLE)
    assert window.lbl_status.text() == "ONLINE"

    window.set_system_status("Listening...", VisualizerMode.LISTENING)
    assert window.lbl_status.text() == "LISTENING"

    window.show_response("Test Response")
    assert window.lbl_response.text() == "Test Response"

    window.append_message("User", "Hello Sora")
    assert "Hello Sora" in window.chat_display.toPlainText()


def test_main_window_health_indicator():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.set_health(mic=True, ai=False, voice=True, local=True)
    assert "+" in window.dot_mic.text()
    assert "-" in window.dot_ai.text()
