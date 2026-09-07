"Async agent loop: understand, route, validate, execute, respond."""
import asyncio
from sora.core.events import EventBus
from sora.core.router import ToolRouter
from sora.core.state import AssistantState
from sora.speech.stt import SpeechToText
from sora.speech.tts import TextToSpeech
from sora.tools.registry import ToolRegistry
from sora.utils.logging import log
class Assistant:
    def __init__(self, stt=None, tts=None, llm=None, registry=None, events=None):
        from sora.intelligence.llm import IntelligenceEngine
        self.stt=stt or SpeechToText(); self.tts=tts or TextToSpeech(); self.llm=llm or IntelligenceEngine()
        self.registry=registry or __import__('sora.tools.registry', fromlist=['build_default_registry']).build_default_registry(); self.events=events or EventBus(); self.router=ToolRouter(self.registry,self.llm)
        self.state=AssistantState.IDLE; self._response_lock=asyncio.Lock()
    def set_state(self,state): self.state=state; self.events.emit('state_changed',state)
    async def interrupt(self): await self.tts.stop(); self.set_state(AssistantState.LISTENING)
    async def handle_text(self,text: str):
        if not text or not text.strip(): return None
        async with self._response_lock:
            try:
                pending=self.registry.pending_confirmation
                if pending and text.lower().strip() in ('yes','yeah','confirm','do it','sure'):
                    self.set_state(AssistantState.EXECUTING); result=self.registry.confirm()
                elif pending and text.lower().strip() in ('no','cancel','stop'):
                    result=self.registry.cancel()
                else:
                    self.set_state(AssistantState.THINKING)
                    decision=await self.router.decide(text)
                    if decision.is_tool_call:
                        self.set_state(AssistantState.EXECUTING)
                        # Keep the tool identifier separate from tool arguments.
                        result=self.registry.execute(decision.tool, **decision.args)
                    else:
                        result=None
                if result is not None:
                    response=result.spoken
                    if result.needs_confirmation: self.set_state(AssistantState.CONFIRMATION_REQUIRED)
                else: response=decision.reply or "I couldn't form a response."
                self.events.emit('response',response)
                self.set_state(AssistantState.SPEAKING); await self.tts.speak(response); self.set_state(AssistantState.IDLE)
                return response
            except asyncio.CancelledError: raise
            except Exception:
                log.exception('Assistant request failed'); self.set_state(AssistantState.ERROR)
                response='I could not complete that request.'; self.events.emit('response',response); return response
