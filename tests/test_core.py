import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch

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
    monkeypatch.setenv("OLLAMA_MODEL", "qwen3:1.7b")
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    cfg = AppConfig()
    assert cfg.ollama_model == "qwen3:1.7b"
    assert cfg.ollama_host == "http://127.0.0.1:11434"


@pytest.mark.asyncio
async def test_llm_model_discovery_and_switching():
    engine = IntelligenceEngine()
    assert engine.model_id in ("qwen3:1.7b", "jarvis-ft:latest")

    # Test dynamic model switching
    engine.set_model("jarvis-ft:latest")
    assert engine.model_id == "jarvis-ft:latest"

    # Test mock model discovery and validation
    mock_models = ["qwen3:1.7b", "jarvis-ft:latest", "gemma4-local:latest", "qwen2.5vl:7b"]
    with patch.object(engine, "get_available_models", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_models
        is_valid = await engine.validate_model("qwen3:1.7b")
        assert is_valid is True
        is_invalid = await engine.validate_model("nonexistent-model")
        assert is_invalid is False


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


@pytest.mark.asyncio
async def test_tts_mute_toggle():
    tts = TextToSpeech()
    tts.is_muted = True
    await tts.speak("This is a muted sentence.")
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


def test_main_window_controls_and_model_selector():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()

    # Model selector and dynamic model list updates
    models = ["qwen3:1.7b", "jarvis-ft:latest", "gemma4-local:latest", "qwen2.5vl:7b"]
    window.set_available_models(models, "qwen3:1.7b")
    assert window.lbl_active_model.text() == "qwen3:1.7b"
    assert window.combo_model.count() == 4

    # Ollama status update
    window.set_ollama_status(True)
    assert "ONLINE" in window.lbl_ollama.text()
    window.set_ollama_status(False)
    assert "OFFLINE" in window.lbl_ollama.text()

    # Mute toggle button
    assert window.is_muted is False
    window.btn_mute.click()
    assert window.is_muted is True
    assert window.btn_mute.text() == "UNMUTE"

    # Clear chat
    window.append_message("User", "Test to clear")
    assert "Test to clear" in window.chat_display.toPlainText()
    window.btn_clear.click()
    assert window.chat_display.toPlainText() == ""


def test_main_window_health_indicator():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.set_health(mic=True, ai=False, voice=True, local=True)
    assert "+" in window.dot_mic.text()
    assert "-" in window.dot_ai.text()
