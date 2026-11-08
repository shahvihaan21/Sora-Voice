import sys
import asyncio
from pathlib import Path

# Setup Python path to include current directory so modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))

import qasync
from PyQt6.QtWidgets import QApplication

from BACKEND.logger import log
from BACKEND.config import config
from UI.main_window import MainWindow
from UI.widgets.visualizer import VisualizerMode
from BACKEND.speech.stt import SpeechToText
from BACKEND.speech.tts import TextToSpeech
from BACKEND.intelligence.llm import IntelligenceEngine

async def main_controller(window: MainWindow):
    """
    Main controller orchestrating UI, Speech, and Intelligence.
    Handles voice-only commands and microphone lifecycle.
    """
    log.info("Jarvis controller started.")
    
    # Initialize Core Modules
    stt = SpeechToText()
    tts = TextToSpeech()
    llm = IntelligenceEngine()
    
    # Set TTS State Callbacks
    def _on_tts_start():
        window.set_system_status("Speaking...", VisualizerMode.SPEAKING)
    def _on_tts_end():
        window.set_system_status("Online", VisualizerMode.IDLE)
        
    tts.on_start_callback = _on_tts_start
    tts.on_end_callback = _on_tts_end
    
    # Voice command queue and lifecycle state.
    command_queue = asyncio.Queue()
    voice_trigger_lock = asyncio.Lock()
    mic_enabled = False
    listener_task = None
    recording_task = None
    active_response_task = None

    # Initial greeting & active model
    window.set_active_model(llm.model_id)
    window.set_system_status("Online", VisualizerMode.IDLE)
    welcome_msg = "jarvis voice online- how may i assist you"
    window.append_message("Jarvis", welcome_msg)
    
    # Non-blocking voice greeting
    asyncio.create_task(tts.speak(welcome_msg))

    async def trigger_listening():
        """Capture one command while the microphone toggle is enabled."""
        nonlocal recording_task
        if voice_trigger_lock.locked():
            return
        async with voice_trigger_lock:
            if not mic_enabled:
                return
            if not stt.has_microphone:
                window.append_message("Jarvis", "Microphone not detected. Check your input device.")
                window.set_system_status("Offline", VisualizerMode.IDLE)
                return
            window.set_system_status("Listening...", VisualizerMode.LISTENING)
            try:
                cmd = await stt.listen_for_command()
                if cmd:
                    log.info(f"Spoken command recognized: {cmd}")
                    await command_queue.put(cmd)
                else:
                    if mic_enabled:
                        window.set_system_status("Online", VisualizerMode.IDLE)
            except asyncio.CancelledError:
                log.debug("Manual recording task cancelled.")
                raise
            finally:
                recording_task = None

    async def voice_listener_task():
        """Keep the mic active after the first press and accept wake words."""
        nonlocal recording_task
        while mic_enabled:
            try:
                detected = await stt.listen_for_wake_word()
                if detected and mic_enabled:
                    if recording_task is None or recording_task.done():
                        recording_task = asyncio.create_task(trigger_listening())
                        await recording_task
                else:
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"Error in voice listener loop: {e}")
                await asyncio.sleep(0.5)

    is_stopping = False

    async def stop_all_operations():
        nonlocal mic_enabled, listener_task, recording_task, active_response_task, is_stopping
        if is_stopping:
            return
        is_stopping = True
        try:
            mic_enabled = False
            stt.stop()

            if recording_task and not recording_task.done():
                recording_task.cancel()
                try:
                    await recording_task
                except (asyncio.CancelledError, Exception):
                    pass
                recording_task = None

            if listener_task and not listener_task.done():
                listener_task.cancel()
                try:
                    await listener_task
                except (asyncio.CancelledError, Exception):
                    pass
                listener_task = None

            if active_response_task and not active_response_task.done():
                active_response_task.cancel()
                try:
                    await active_response_task
                except (asyncio.CancelledError, Exception):
                    pass
                active_response_task = None

            while not command_queue.empty():
                try:
                    command_queue.get_nowait()
                    command_queue.task_done()
                except Exception:
                    break

            await tts.stop()
            window.set_system_status("Online", VisualizerMode.IDLE)
        finally:
            is_stopping = False

    def on_manual_voice_trigger():
        nonlocal mic_enabled, listener_task, recording_task
        if mic_enabled:
            asyncio.create_task(stop_all_operations())
            return
        mic_enabled = True
        window.set_system_status("Listening...", VisualizerMode.LISTENING)
        stt.reset_cancellation()
        if listener_task and not listener_task.done():
            listener_task.cancel()
        if recording_task and not recording_task.done():
            recording_task.cancel()
        listener_task = asyncio.create_task(voice_listener_task())
        recording_task = asyncio.create_task(trigger_listening())

    window.voice_trigger_requested.connect(on_manual_voice_trigger)

    def _on_text(t):
        try:
            command_queue.put_nowait(t)
        except Exception:
            pass

    try:
        window.text_submit_requested.connect(_on_text)
    except Exception:
        pass

    def _on_cancel():
        asyncio.create_task(stop_all_operations())

    try:
        window.cancel_requested.connect(_on_cancel)
        window.stop_speech_requested.connect(_on_cancel)
    except Exception:
        pass

    def _on_model_changed(model_name: str):
        llm.set_model(model_name)
        log.info(f"Model switched to {model_name}")

    try:
        window.model_changed.connect(_on_model_changed)
    except Exception:
        pass

    def _on_mute_toggled(muted: bool):
        tts.is_muted = muted
        if muted:
            asyncio.create_task(tts.stop())

    try:
        window.mute_toggled.connect(_on_mute_toggled)
    except Exception:
        pass

    def _on_clear_requested():
        llm.conversation_history.clear()

    try:
        window.clear_requested.connect(_on_clear_requested)
    except Exception:
        pass

    async def _health():
        import httpx as _hx
        _hc = _hx.AsyncClient(timeout=2.5)
        try:
            while True:
                try:
                    mic = bool(getattr(stt, "has_microphone", False))
                    try:
                        host = getattr(config, "ollama_host", "http://localhost:11434")
                        r = await _hc.get(host.rstrip("/") + "/api/tags")
                        ai = (r.status_code == 200)
                        if ai:
                            data = r.json()
                            models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                            if models:
                                window.set_available_models(models, llm.model_id)
                    except Exception:
                        ai = False
                    window.set_health(mic=mic, ai=ai, voice=True, local=True)
                    window.set_ollama_status(ai)
                except Exception:
                    pass
                await asyncio.sleep(15.0)
        finally:
            try:
                await _hc.aclose()
            except Exception:
                pass

    asyncio.create_task(_health())

    from BACKEND.perf import mark as _mark
    asyncio.create_task(llm.prewarm())
    asyncio.create_task(tts.prewarm())
    try:
        await asyncio.to_thread(stt.prewarm)
    except Exception:
        pass
    _mark("startup: modules ready")

    # Process Commands from Queue
    while True:
        try:
            window.set_system_status("Online", VisualizerMode.IDLE)
            command = await command_queue.get()
            
            if not command or not command.strip():
                command_queue.task_done()
                continue
                
            # Log user command in UI
            window.append_message("User", command)
            
            # Update status to Thinking
            window.set_system_status("Thinking...", VisualizerMode.THINKING)
            
            # Stream: render + speak each clause as it arrives (no full wait).
            async def process_response():
                from BACKEND.perf import mark as _m
                response_parts = []
                first_chunk = True
                async for sentence in llm.generate_response_stream(command):
                    s = (sentence or "").strip()
                    if not s:
                        continue
                    if first_chunk:
                        first_chunk = False
                        _m("LLM first chunk")
                        window.set_system_status("Speaking...", VisualizerMode.SPEAKING)
                    response_parts.append(s)
                    spoken = " ".join(response_parts)
                    window.show_response(spoken)
                    await tts.speak_stream(s)
                response = " ".join(response_parts).strip()
                if response:
                    window.append_message("Jarvis", response)
                    _m("LLM complete, TTS queued")
                await tts.flush()

            active_response_task = asyncio.create_task(process_response())
            try:
                await active_response_task
            except asyncio.CancelledError:
                log.info("Active Jarvis response cancelled.")
                await tts.stop()
            finally:
                active_response_task = None
                command_queue.task_done()
        except Exception as e:
            log.error(f"Error executing command loop: {e}")
            window.set_system_status("Error", VisualizerMode.IDLE)
            await asyncio.sleep(0.5)

def main():
    log.info("Starting Jarvis Assistant...")
    try:
        app = QApplication(sys.argv)
        app.setApplicationName(config.app_name)
        app.setQuitOnLastWindowClosed(True)
        
        # Initialize qasync event loop
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        def exception_handler(loop, context):
            msg = context.get("exception", context.get("message"))
            log.error(f"Asyncio loop exception: {msg}")
            
        loop.set_exception_handler(exception_handler)
        
        # Create and display main window
        window = MainWindow()
        window.show()
        log.info("Jarvis UI successfully initialized.")
        
        # Schedule main asynchronous controller
        loop.create_task(main_controller(window))
        
        # Run the event loop
        with loop:
            loop.run_forever()
    except Exception as e:
        log.critical(f"Fatal error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
