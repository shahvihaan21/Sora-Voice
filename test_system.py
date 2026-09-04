"""
Sora AI (v2.0) - System Self-Diagnostic & Verification Suite (Ollama Edition)
"""
import sys
import os
from pathlib import Path

# Add 'aegis' directory to sys.path
root_dir = Path(__file__).resolve().parent
aegis_dir = root_dir / "aegis"
if str(aegis_dir) not in sys.path:
    sys.path.insert(0, str(aegis_dir))

import asyncio

def check_config():
    print("[1/6] Testing Configuration & Environment...")
    from aegis.BACKEND.config import config
    assert config.app_name is not None
    assert config.base_dir.exists()
    assert config.logs_dir.exists()
    print("  -> Configuration Loaded Successfully.")
    print(f"  -> App Name: {config.app_name}")
    print(f"  -> Ollama Host: {config.ollama_host}")
    print(f"  -> Ollama Model: {config.ollama_model}")
    print(f"  -> Wake words: {config.wake_words}")

def check_logger():
    print("[2/6] Testing Logger...")
    from aegis.BACKEND.logger import log
    log.info("Sora self-test logger message.")
    print("  -> Logger initialized and writing successfully.")

async def check_intelligence():
    print("[3/6] Testing Intelligence Engine (Ollama & Offline Fallback)...")
    from aegis.BACKEND.intelligence import llm
    engine = llm.IntelligenceEngine()

    # Check Ollama server availability
    is_live = await engine.is_ollama_available()
    print(f"  -> Ollama Local Server Online: {is_live}")

    # Test time query (handles both live Ollama or fallback seamlessly)
    res_time = await engine.generate_response("what time is it?")
    assert len(res_time) > 0
    print(f"  -> Response (Time query): '{res_time}'")

    res_calc = await engine.generate_response("calculate 50 * 2")
    assert len(res_calc) > 0
    print(f"  -> Response (Math query): '{res_calc}'")

def check_stt():
    print("[4/6] Testing Speech-to-Text Module...")
    from aegis.BACKEND.speech.stt import SpeechToText
    stt = SpeechToText()
    print(f"  -> Mic Hardware Detected: {stt.has_microphone}")
    print(f"  -> Recognizer Ready: {stt.recognizer is not None}")

def check_tts():
    print("[5/6] Testing Text-to-Speech Engine...")
    from aegis.BACKEND.speech.tts import TextToSpeech
    tts = TextToSpeech()
    print(f"  -> Voice: {tts.voice}")
    print(f"  -> Speech Rate: {tts.rate}")
    print(f"  -> Offline fallback engine available: {tts._get_offline_engine() is not None}")

def check_ui():
    print("[6/6] Testing UI Components & Styles...")
    from PyQt6.QtWidgets import QApplication
    from aegis.UI.main_window import MainWindow
    from aegis.UI.widgets.visualizer import VisualizerMode

    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    assert window is not None
    window.set_system_status("DIAGNOSTIC", VisualizerMode.SPEAKING)
    window.append_message("Sora", "Diagnostic test message.")
    print("  -> UI Window, Siri Waveform, and Pill Input Bar initialized successfully.")

async def run_all():
    print("==================================================")
    print("      SORA AI (v2.0) SYSTEM DIAGNOSTIC SUITE      ")
    print("==================================================")
    try:
        check_config()
        check_logger()
        await check_intelligence()
        check_stt()
        check_tts()
        check_ui()
        print("==================================================")
        print(" [SUCCESS] ALL 6 SUBSYSTEM TESTS PASSED!         ")
        print("==================================================")
    except Exception as e:
        print(f"\n[ERROR] Diagnostic test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_all())
