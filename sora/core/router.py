"Hybrid router: deterministic common commands, then local LLM tool JSON."""
import re
from sora.intelligence.llm import IntelligenceEngine, LLMDecision
from sora.tools.registry import ToolRegistry
class ToolRouter:
    def __init__(self, registry: ToolRegistry, llm: IntelligenceEngine):
        self.registry, self.llm = registry, llm
        self.llm.set_tools(registry.all_tools())
    async def decide(self, text: str) -> LLMDecision:
        q = text.lower().strip()
        if re.search(r'\b(volume|sound)\b', q) and re.search(r'\b(up|increase|louder)\b', q): return LLMDecision('volume_up', {'step': 10})
        if re.search(r'\b(volume|sound)\b', q) and re.search(r'\b(down|decrease|lower|quieter)\b', q): return LLMDecision('volume_down', {'step': 10})
        match = re.search(r'(?:volume|sound).{0,12}(?:to|at)\s*(\d{1,3})', q)
        if match: return LLMDecision('set_volume', {'percent': int(match.group(1))})
        if 'unmute' in q: return LLMDecision('unmute', {})
        if re.search(r'\bmute\b', q): return LLMDecision('mute', {})
        if re.search(r'brightness|brighter|dimmer', q):
            if re.search(r'brighter|increase|up', q): return LLMDecision('brightness_up', {'step': 10})
            if re.search(r'dimmer|decrease|down', q): return LLMDecision('brightness_down', {'step': 10})
        match = re.search(r'brightness.{0,12}(?:to|at)\s*(\d{1,3})', q)
        if match: return LLMDecision('set_brightness', {'percent': int(match.group(1))})
        if 'diagnostic' in q or 'system doing' in q or 'what is wrong' in q or 'system health' in q: return LLMDecision('run_diagnostic', {})
        if 'ram' in q or 'memory usage' in q: return LLMDecision('get_ram', {})
        if 'storage' in q or 'disk space' in q: return LLMDecision('get_disk', {})
        if 'is ollama' in q or 'ollama working' in q: return LLMDecision('run_diagnostic', {})
        if 'lock' in q and ('pc' in q or 'computer' in q): return LLMDecision('lock_computer', {})
        if 'shut down' in q or 'shutdown' in q: return LLMDecision('shutdown_computer', {})
        if 'restart' in q and ('computer' in q or 'pc' in q): return LLMDecision('restart_computer', {})
        for verb, tool in (('open','open_app'),('launch','open_app'),('close','close_app'),('restart','restart_app')):
            match = re.search(rf'\b{verb}\s+(.+)', q)
            if match and match.group(1).strip() not in ('settings','task manager','file explorer'):
                return LLMDecision(tool, {'name': match.group(1).strip()})
        for folder in ('downloads','documents','desktop','pictures','music','videos'):
            if re.search(rf'\b(open|go to)\s+{folder}\b', q): return LLMDecision('open_folder', {'name': folder})
        return await self.llm.generate_decision(text)
