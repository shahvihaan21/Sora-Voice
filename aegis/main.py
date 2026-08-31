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
    active_response_task = None

    # Initial greeting
    window.set_system_status("Online", VisualizerMode.IDLE)
    welcome_msg = "jarvis voice online- how may i assist you"
    window.append_message("Jarvis", welcome_msg)
    
    # Non-blocking voice greeting
    asyncio.create_task(tts.speak(welcome_msg))

    async def trigger_listening():
        """Capture one command while the microphone toggle is enabled."""
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
            cmd = await stt.listen_for_command()
            if cmd:
                log.info(f"Spoken command recognized: {cmd}")
                await command_queue.put(cmd)
            else:
                window.set_system_status("Online", VisualizerMode.IDLE)

    async def voice_listener_task():
        """Keep the mic active after the first press and accept wake words."""
        while mic_enabled:
            try:
                detected = await stt.listen_for_wake_word()
                if detected and mic_enabled:
                    await trigger_listening()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.error(f"Error in voice listener loop: {e}")
                await asyncio.sleep(1.0)

    async def stop_all_operations():
        nonlocal mic_enabled, listener_task, active_response_task
        mic_enabled = False
        if listener_task and not listener_task.done():
            listener_task.cancel()
        stt.stop()
        if active_response_task and not active_response_task.done():
            active_response_task.cancel()
        while not command_queue.empty():
            try:
                command_queue.get_nowait()
                command_queue.task_done()
            except asyncio.QueueEmpty:
                break
        await tts.stop()
        window.set_system_status("Stopped", VisualizerMode.IDLE)

    def on_manual_voice_trigger():
        nonlocal mic_enabled, listener_task
        if mic_enabled:
            asyncio.create_task(stop_all_operations())
            return
        mic_enabled = True
        window.set_system_status("Listening...", VisualizerMode.LISTENING)
        asyncio.create_task(trigger_listening())
        listener_task = asyncio.create_task(voice_listener_task())

    window.voice_trigger_requested.connect(on_manual_voice_trigger)

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
            
            # Generate the complete response before displaying/speaking it.
            # This avoids chopped chat bubbles and overlapping TTS sentences.
            async def process_response():
                response_parts = []
                async for sentence in llm.generate_response_stream(command):
                    if sentence:
                        response_parts.append(sentence.strip())
                response = " ".join(response_parts).strip()
                if response:
                    window.append_message("Jarvis", response)
                    await tts.speak(response)

            active_response_task = asyncio.create_task(process_response())
            try:
                await active_response_task
            except asyncio.CancelledError:
                log.info("Active Jarvis response cancelled by microphone stop.")
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
