import pytest
import asyncio
import sys
import os

if sys.platform.startswith("linux") and not os.getenv("DISPLAY") and not os.getenv("QT_QPA_PLATFORM"):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

from aegis.BACKEND.intelligence.llm import IntelligenceEngine
from aegis.BACKEND.speech.tts import TextToSpeech
from aegis.UI.main_window import MainWindow
from aegis.UI.widgets.core import AICore
from aegis.UI.widgets.visualizer import VisualizerMode
from PyQt6.QtWidgets import QApplication


@pytest.mark.asyncio
async def test_llm_offline_fallback():
    engine = IntelligenceEngine()
    response = await engine.generate_response("what time is it?")
    assert "currently" in response.lower() or "time" in response.lower()

    response_calc = await engine.generate_response("calculate 25 * 4")
    assert "100" in response_calc


@pytest.mark.asyncio
async def test_tts_play_audio_file(tmp_path):
    tts = TextToSpeech()
    dummy_file = tmp_path / "dummy.mp3"
    dummy_file.write_bytes(b"")

    # Should safely return False or True without raising AttributeError on any platform
    res = await tts._play_audio_file(str(dummy_file), "test")
    assert isinstance(res, bool)


def test_ai_core_widget():
    app = QApplication.instance() or QApplication(sys.argv)
    core = AICore()
    core.set_mode("THINKING")
    assert core.mode == "THINKING"
    core.set_level(0.8)
    assert core._target == 0.8


def test_main_window_ui():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.set_system_status("Online", VisualizerMode.IDLE)
    assert window.lbl_status.text() == "ONLINE"

    window.show_response("Test Response")
    assert window.lbl_response.text() == "Test Response"

    window.append_message("User", "Hello Sora")
    assert "Hello Sora" in window.chat_display.toPlainText()
