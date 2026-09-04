"Sora application entry point."""
import asyncio
import sys
from PyQt6.QtWidgets import QApplication
from sora.config.settings import config
from sora.core.assistant import Assistant
from sora.core.state import AssistantState
from sora.utils.logging import log

def main():
    try:
        import qasync
        from aegis.UI.main_window import MainWindow
        from aegis.UI.widgets.visualizer import VisualizerMode
        app = QApplication(sys.argv); app.setApplicationName(config.app_name)
        window = MainWindow(); window.show()
        loop = qasync.QEventLoop(app); asyncio.set_event_loop(loop)
        assistant = Assistant()
        listening = False
        listener_task = None
        def state_changed(state):
            mode = getattr(VisualizerMode, state.value, VisualizerMode.IDLE)
            window.set_system_status(state.value.title(), mode)
        assistant.events.on('state_changed', state_changed)
        assistant.events.on('response', lambda text: window.append_message('Sora', text))
        async def run():
            window.set_system_status('Online', VisualizerMode.IDLE)
            window.append_message('Sora', 'Sora is online. How may I help?')
            while True:
                await asyncio.sleep(0.2)
        async def capture_command():
            nonlocal listening
            if listening:
                assistant.stt.stop()
                await assistant.interrupt()
                listening = False
                return
            listening = True
            assistant.set_state(AssistantState.LISTENING)
            try:
                command = await assistant.stt.listen_for_command()
                if command:
                    window.append_message('User', command)
                    await assistant.handle_text(command)
                else:
                    assistant.set_state(AssistantState.IDLE)
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception('Voice capture failed')
                assistant.set_state(AssistantState.ERROR)
            finally:
                listening = False
        window.voice_trigger_requested.connect(lambda: asyncio.create_task(capture_command()))
        with loop:
            loop.create_task(run()); loop.run_forever()
    except Exception:
        log.exception('Fatal application startup failure')
        raise
if __name__ == '__main__': main()
