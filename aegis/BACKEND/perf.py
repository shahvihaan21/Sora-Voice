"""Lightweight perf timer. Enable with SORA_PERF=1 env. No overhead when disabled."""
import os
import time
import functools

ENABLED = os.getenv("SORA_PERF", "0").strip().lower() in ("1", "true", "yes", "on")
_last = {}


def mark(label: str) -> float:
    now = time.perf_counter()
    if ENABLED:
        prev = _last.get("__prev__")
        if prev is not None:
            try:
                from BACKEND.logger import log
                log.info(f"[PERF] {label}: {(now - prev) * 1000:.0f} ms since last mark")
            except Exception:
                pass
        _last["__prev__"] = now
    else:
        _last["__prev__"] = now
    return now


def span(label: str):
    def deco(fn):
        @functools.wraps(fn)
        async def aw(*a, **k):
            t0 = time.perf_counter()
            try:
                return await fn(*a, **k)
            finally:
                if ENABLED:
                    try:
                        from BACKEND.logger import log
                        log.info(f"[PERF] {label}: {(time.perf_counter() - t0) * 1000:.0f} ms")
                    except Exception:
                        pass

        @functools.wraps(fn)
        def sw(*a, **k):
            t0 = time.perf_counter()
            try:
                return fn(*a, **k)
            finally:
                if ENABLED:
                    try:
                        from BACKEND.logger import log
                        log.info(f"[PERF] {label}: {(time.perf_counter() - t0) * 1000:.0f} ms")
                    except Exception:
                        pass
        import asyncio as _a
        if _a.iscoroutinefunction(fn):
            return aw
        return sw
    return deco
