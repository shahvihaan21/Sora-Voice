"""
Sora AI (v2.0) - System Self-Diagnostic & Verification Suite
Reports PASS, FAIL, WARNING, and SKIP statuses accurately.
"""
import sys
import os
from pathlib import Path

# Set Qt offscreen platform if running headless on Linux/CI
if sys.platform.startswith("linux") and not os.getenv("DISPLAY") and not os.getenv("QT_QPA_PLATFORM"):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

root_dir = Path(__file__).resolve().parent
aegis_dir = root_dir / "aegis"
for p in (str(root_dir), str(aegis_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

import asyncio

results = {}

def check_config():
    print("[1/6] Testing Configuration & Environment...")
    try:
        from aegis.BACKEND.config import config
        assert config.app_name is not None
        assert config.base_dir.exists()
        assert config.logs_dir.exists()
        print(f"  -> App Name: {config.app_name}")
        print(f"  -> Ollama Host: {config.ollama_host}")
        print(f"  -> Ollama Model: {config.ollama_model}")
        print("  [PASS] Configuration Loaded Successfully.")
        results["Config"] = "PASS"
    except Exception as e:
        print(f"  [FAIL] Configuration error: {e}")
        results["Config"] = "FAIL"

def check_logger():
    print("[2/6] Testing Logger...")
    try:
        from aegis.BACKEND.logger import log
        log.info("Sora self-test logger message.")
        print("  [PASS] Logger initialized and writing successfully.")
        results["Logger"] = "PASS"
    except Exception as e:
        print(f"  [FAIL] Logger error: {e}")
        results["Logger"] = "FAIL"

async def check_intelligence():
    print("[3/6] Testing Intelligence Engine (Ollama & Offline Fallback)...")
    try:
        from aegis.BACKEND.intelligence import llm
        engine = llm.IntelligenceEngine()

        is_live = await engine.is_ollama_available()
        status_str = "ONLINE" if is_live else "OFFLINE (Using Local Fallback)"
        print(f"  -> Ollama Server Status: {status_str}")

        res_time = await engine.generate_response("what time is it?")
        assert len(res_time) > 0
        print(f"  -> Query Test Output: '{res_time}'")

        if is_live:
            print("  [PASS] Intelligence Engine (Ollama Live)")
            results["Intelligence"] = "PASS"
        else:
            print("  [WARNING] Ollama server offline; fallback generator functional.")
            results["Intelligence"] = "WARNING"
    except Exception as e:
        print(f"  [FAIL] Intelligence test error: {e}")
        results["Intelligence"] = "FAIL"

def check_stt():
    print("[4/6] Testing Speech-to-Text Module...")
    try:
        from aegis.BACKEND.speech.stt import SpeechToText
        stt = SpeechToText()
        if stt.has_microphone:
            print(f"  -> Mic Hardware Detected: True")
            print("  [PASS] Speech-to-Text ready.")
            results["STT"] = "PASS"
        else:
            print("  -> Mic Hardware Detected: False")
            print("  [WARNING] Audio input device not found or PortAudio unavailable.")
            results["STT"] = "WARNING"
    except Exception as e:
        print(f"  [FAIL] STT error: {e}")
        results["STT"] = "FAIL"

def check_tts():
    print("[5/6] Testing Text-to-Speech Engine...")
    try:
        from aegis.BACKEND.speech.tts import TextToSpeech
        tts = TextToSpeech()
        print(f"  -> Voice Configured: {tts.voice}")
        offline_avail = (tts._get_offline_engine() is not None)
        print(f"  -> Offline Fallback Engine: {offline_avail}")
        print("  [PASS] Text-to-Speech Engine initialized.")
        results["TTS"] = "PASS"
    except Exception as e:
        print(f"  [FAIL] TTS error: {e}")
        results["TTS"] = "FAIL"

def check_ui():
    print("[6/6] Testing UI Components & Styles...")
    try:
        from PyQt6.QtWidgets import QApplication
        from aegis.UI.main_window import MainWindow
        from aegis.UI.widgets.visualizer import VisualizerMode

        app = QApplication.instance() or QApplication(sys.argv)
        window = MainWindow()
        assert window is not None
        window.set_system_status("DIAGNOSTIC", VisualizerMode.SPEAKING)
        window.append_message("Sora", "Diagnostic test message.")
        print("  [PASS] UI components initialized successfully.")
        results["UI"] = "PASS"
    except Exception as e:
        print(f"  [FAIL] UI test error: {e}")
        results["UI"] = "FAIL"

async def run_all():
    print("==================================================")
    print("      SORA AI (v2.0) SYSTEM DIAGNOSTIC SUITE      ")
    print("==================================================")
    check_config()
    check_logger()
    await check_intelligence()
    check_stt()
    check_tts()
    check_ui()
    print("\n==================================================")
    print("                DIAGNOSTIC SUMMARY                ")
    print("==================================================")
    has_failure = False
    for sub, status in results.items():
        print(f"  - {sub:15s}: [{status}]")
        if status == "FAIL":
            has_failure = True
    print("==================================================")
    if has_failure:
        print(" [RESULT] SYSTEM DIAGNOSTICS COMPLETED WITH FAILURES")
        sys.exit(1)
    else:
        print(" [RESULT] ALL CRITICAL SUBSYSTEM DIAGNOSTICS PASSED")

if __name__ == "__main__":
    asyncio.run(run_all())
