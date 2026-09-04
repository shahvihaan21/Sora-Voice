"Small framework-independent event bus for assistant state updates."""
from collections import defaultdict
from typing import Callable, DefaultDict, List, Any
class EventBus:
    def __init__(self): self._handlers: DefaultDict[str, List[Callable]] = defaultdict(list)
    def on(self, event: str, handler: Callable): self._handlers[event].append(handler)
    def emit(self, event: str, *args: Any, **kwargs: Any):
        for handler in tuple(self._handlers.get(event, ())):
            try: handler(*args, **kwargs)
            except Exception: pass
    def clear(self): self._handlers.clear()
