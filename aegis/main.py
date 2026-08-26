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
    Handles both spoken voice commands and typed text commands.
    """
    log.info("Sora controller started.")
    
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
    
    # Command Queue for handling typed or spoken inputs
    command_queue = asyncio.Queue()

    def handle_user_command_submission(command_text: str):
        log.info(f"Received user input: {command_text}")
        command_queue.put_nowait(command_text)

    window.user_command_submitted.connect(handle_user_command_submission)

    # Initial greeting
    window.set_system_status("Online", VisualizerMode.IDLE)
    welcome_msg = "Sora 2.0 system online and operational. How may I assist you?"
    window.append_message("Sora", welcome_msg)
    
    # Non-blocking voice greeting
    asyncio.create_task(tts.speak(welcome_msg))

    async def trigger_listening():
        """Triggered either by wake word or '+' button."""
        if not stt.has_microphone:
            window.append_message("Sora", "Microphone not detected. Please type your prompt.")
            return
        
        window.set_system_status("Listening...", VisualizerMode.LISTENING)
        cmd = await stt.listen_for_command()
        if cmd:
            log.info(f"Spoken command recognized: {cmd}")
            await command_queue.put(cmd)
        else:
            window.set_system_status("Online", VisualizerMode.IDLE)

    def on_manual_voice_trigger():
        asyncio.create_task(trigger_listening())

    window.voice_trigger_requested.connect(on_manual_voice_trigger)

    async def voice_listener_task():
        """Listens continuously for wake words if microphone is available."""
        if not stt.has_microphone:
            log.warning("No microphone detected. Voice trigger loop is disabled.")
            return

        while True:
            try:
                # Wait for wake word
                detected = await stt.listen_for_wake_word()
                if detected:
                    await trigger_listening()
            except Exception as e:
                log.error(f"Error in voice listener loop: {e}")
                await asyncio.sleep(1.5)

    # Launch background voice listener
    asyncio.create_task(voice_listener_task())

    # Create a queue for TTS to play sentences sequentially
    tts_queue = asyncio.Queue()

    async def tts_worker():
        while True:
            sentence = await tts_queue.get()
            if sentence is None:
                tts_queue.task_done()
                continue
            await tts.speak(sentence)
            tts_queue.task_done()

    asyncio.create_task(tts_worker())

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
            
            # Generate AI response
            first_sentence = True
            async for sentence in llm.generate_response_stream(command):
                if sentence:
                    window.append_message("Sora", sentence)
                    await tts_queue.put(sentence)
                    first_sentence = False
            
            command_queue.task_done()
        except Exception as e:
            log.error(f"Error executing command loop: {e}")
            window.set_system_status("Error", VisualizerMode.IDLE)
            await asyncio.sleep(0.5)

def main():
    log.info("Starting Sora AI Assistant...")
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Sora AI")
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
        log.info("Sora UI successfully initialized.")
        
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
