"Ollama-backed intelligence with structured tool decisions and fallback."""
import datetime
import json
import re
from typing import AsyncGenerator, Dict, List, Optional
import httpx
from sora.config.settings import config
from sora.intelligence.prompts import build_system_prompt
from sora.tools.base import Tool
from sora.utils.logging import log
class LLMDecision:
    def __init__(self, tool: Optional[str] = None, args: Optional[Dict] = None, reply: Optional[str] = None):
        self.tool, self.args, self.reply = tool, args or {}, reply
    @property
    def is_tool_call(self): return self.tool is not None

def parse_llm_output(text: str) -> LLMDecision:
    text = (text or '').strip()
    try:
        payload = json.loads(text)
        if isinstance(payload, dict) and isinstance(payload.get('tool'), str):
            return LLMDecision(tool=payload['tool'], args=payload.get('args', {}))
        if isinstance(payload, dict) and isinstance(payload.get('reply'), str):
            return LLMDecision(reply=payload['reply'])
    except (json.JSONDecodeError, TypeError):
        pass
    return LLMDecision(reply=re.sub(r'[\\*_#`]', '', text))

class IntelligenceEngine:
    def __init__(self):
        self.host = config.ollama_host.rstrip('/')
        self.model_id = config.ollama_model
        self.conversation_history: List[Dict[str, str]] = []
        self.tools: List[Tool] = []

    def set_tools(self, tools: List[Tool]): self.tools = tools
    async def is_ollama_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                return (await client.get(f'{self.host}/api/tags')).status_code == 200
        except Exception: return False
    def _fallback(self, text: str) -> str:
        q = text.lower().strip(); now = datetime.datetime.now()
        if any(x in q for x in ('hello','hi','hey')): return "Hello, I'm Sora. How can I help?"
        if 'time' in q: return f"It's currently {now.strftime('%I:%M %p' )}."
        if 'date' in q or 'today' in q: return f"Today is {now.strftime('%A, %B %d, %Y')}."
        if 'who are you' in q or 'your name' in q: return "I'm Sora, your local desktop assistant."
        return f"Ollama is offline. Start it with 'ollama run {self.model_id}' for full responses."

    async def generate_decision(self, user_input: str) -> LLMDecision:
        chunks = [x async for x in self._stream(user_input)]
        return parse_llm_output(' '.join(chunks))

    async def generate_response(self, user_input: str) -> str:
        return ' '.join([x async for x in self.generate_response_stream(user_input)]).strip()

    async def generate_response_stream(self, user_input: str) -> AsyncGenerator[str, None]:
        async for chunk in self._stream(user_input): yield chunk
    async def _stream(self, user_input: str) -> AsyncGenerator[str, None]:
        if not user_input.strip(): return
        messages = [{'role':'system','content':build_system_prompt(self.tools)}]
        for turn in self.conversation_history[-6:]:
            messages += [{'role':'user','content':turn['user']},{'role':'assistant','content':turn['sora']}]
        messages.append({'role':'user','content':user_input})
        full = ''; chunk = ''
        try:
            async with httpx.AsyncClient(timeout=config.ollama_timeout) as client:
                async with client.stream('POST', f'{self.host}/api/chat', json={'model':self.model_id,'messages':messages,'stream':True,'options':{'temperature':.4,'num_predict':160}}) as response:
                    if response.status_code == 404:
                        yield f"The model {self.model_id} is not installed."; return
                    if response.status_code != 200: raise RuntimeError(f'HTTP {response.status_code}')
                    async for line in response.aiter_lines():
                        if not line: continue
                        try: token = json.loads(line).get('message',{}).get('content','')
                        except json.JSONDecodeError: continue
                        if token:
                            token = re.sub(r'[\\*_#`]', '', token); full += token; chunk += token
                            if chunk.strip().endswith(('.', '?', '!')) or len(chunk.split()) >= 15:
                                yield chunk.strip(); chunk = ''
                    if chunk.strip(): yield chunk.strip()
            if full: self._save_history(user_input, full)
            return
        except Exception as exc:
            log.warning(f'Ollama request failed: {type(exc).__name__}')
        fallback = self._fallback(user_input); self._save_history(user_input, fallback); yield fallback
    def _save_history(self, user: str, answer: str):
        self.conversation_history.append({'user':user,'sora':answer})
        del self.conversation_history[:-20]
