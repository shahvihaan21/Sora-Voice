"""Reusable diagnostics service.

Collects structured system health information (CPU/RAM/disk/battery/network/
Ollama/mic/TTS/uptime). Both the UI panel and the tool layer consume this
service — the logic lives here, not in the interface.
"""
import datetime
import os
import platform
import sys
import time
from typing import Any, Dict, Optional

from sora.config.settings import config
from sora.tools.base import ToolResult
from sora.utils.logging import log

_STARTED_AT = time.monotonic()


def uptime_seconds() -> float:
    return time.monotonic() - _STARTED_AT


def _psutil():
    try:
        import psutil
        return psutil
    except ImportError:
        return None


def cpu_usage() -> Optional[float]:
    psutil = _psutil()
    if not psutil:
        return None
    try:
        return psutil.cpu_percent(interval=0.15)
    except Exception:  # noqa: BLE001
        return None


def ram_usage() -> Optional[Dict[str, Any]]:
    psutil = _psutil()
    if not psutil:
        return None
    try:
        mem = psutil.virtual_memory()
        return {
            "percent": mem.percent,
            "used_gb": round(mem.used / 1e9, 1),
            "total_gb": round(mem.total / 1e9, 1),
        }
    except Exception:  # noqa: BLE001
        return None


def disk_usage() -> Optional[Dict[str, Any]]:
    psutil = _psutil()
    if not psutil:
        return None
    try:
        root = "C:\\" if platform.system() == "Windows" else "/"
        usage = psutil.disk_usage(root)
        return {
            "percent": usage.percent,
            "free_gb": round(usage.free / 1e9, 1),
            "total_gb": round(usage.total / 1e9, 1),
        }
    except Exception:  # noqa: BLE001
        return None


def battery() -> Optional[Dict[str, Any]]:
    psutil = _psutil()
    if not psutil:
        return None
    try:
        bat = psutil.sensors_battery()
        if bat is None:
            return None
        return {"percent": round(bat.percent), "plugged_in": bool(bat.power_plugged)}
    except Exception:  # noqa: BLE001
        return None


def network_status() -> bool:
    import socket
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=1.5)
        return True
    except OSError:
        return False


def ollama_status() -> Dict[str, Any]:
    """Blocking availability check — run via asyncio.to_thread when async."""
    import httpx
    try:
        with httpx.Client(timeout=2.0) as client:
            res = client.get(f"{config.ollama_host.rstrip('/')}/api/tags")
            if res.status_code == 200:
                models = [m.get("name", "") for m in res.json().get("models", [])]
                active = config.ollama_model in models
                return {"available": True, "model": config.ollama_model, "model_loaded": active}
            return {"available": False, "model": config.ollama_model, "model_loaded": False}
    except Exception:  # noqa: BLE001
        return {"available": False, "model": config.ollama_model, "model_loaded": False}


def microphone_status() -> Dict[str, Any]:
    try:
        import sounddevice as sd
        inputs = [d for d in sd.query_devices() if d.get("max_input_channels", 0) > 0]
        if inputs:
            return {"available": True, "device": inputs[0].get("name", "Default Mic")}
        return {"available": False, "device": None}
    except Exception:  # noqa: BLE001
        return {"available": False, "device": None}


def tts_status() -> Dict[str, Any]:
    try:
        import pyttsx3  # noqa: F401
        return {"available": True, "engine": "pyttsx3/edge-tts"}
    except ImportError:
        return {"available": False, "engine": None}


def full_diagnostics() -> Dict[str, Any]:
    """Collect everything into one structured snapshot."""
    snapshot: Dict[str, Any] = {
        "os": f"{platform.system()} {platform.release()}",
        "python": sys.version.split()[0],
        "assistant_uptime_seconds": round(uptime_seconds()),
        "network": network_status(),
        "ollama": ollama_status(),
        "microphone": microphone_status(),
        "tts": tts_status(),
    }
    cpu = cpu_usage()
    if cpu is not None:
        snapshot["cpu_percent"] = round(cpu, 1)
    ram = ram_usage()
    if ram:
        snapshot["ram"] = ram
    disk = disk_usage()
    if disk:
        snapshot["disk"] = disk
    bat = battery()
    if bat:
        snapshot["battery"] = bat
    return snapshot


def summarize(snapshot: Dict[str, Any]) -> str:
    """Turn a snapshot into a concise spoken summary."""
    parts = []
    if "cpu_percent" in snapshot:
        parts.append(f"CPU at {snapshot['cpu_percent']} percent")
    ram = snapshot.get("ram")
    if ram:
        parts.append(f"RAM at {ram['percent']} percent")
    disk = snapshot.get("disk")
    if disk:
        parts.append(f"disk {disk['percent']} percent full with {disk['free_gb']} gigabytes free")
    bat = snapshot.get("battery")
    if bat:
        power = "charging" if bat["plugged_in"] else "on battery"
        parts.append(f"battery {bat['percent']} percent {power}")
    parts.append("network is " + ("up" if snapshot.get("network") else "down"))
    ollama = snapshot.get("ollama", {})
    parts.append("Ollama is " + ("online" if ollama.get("available") else "offline"))
    mic = snapshot.get("microphone", {})
    parts.append("microphone is " + ("ready" if mic.get("available") else "not detected"))
    return ". ".join(parts) + "."


def run_diagnostic() -> ToolResult:
    try:
        snapshot = full_diagnostics()
    except Exception as exc:  # noqa: BLE001
        log.exception("Diagnostics failed")
        return ToolResult.fail("The diagnostic run failed.", error="diagnostics_failed")
    return ToolResult.ok("Here's what I found: " + summarize(snapshot), **snapshot)


def register_diagnostics_tools(registry) -> None:
    from sora.tools.base import PermissionLevel

    registry.register_fn(
        "run_diagnostic", "run a full system diagnostic and report health",
        {"type": "object", "properties": {}},
        run_diagnostic,
    )
    registry.register_fn(
        "get_cpu", "report CPU usage", {"type": "object", "properties": {}},
        lambda: (
            ToolResult.ok(f"CPU is at {cpu_usage()} percent.", cpu_percent=cpu_usage())
            if cpu_usage() is not None
            else ToolResult.fail("I couldn't read CPU usage.", error="unavailable")
        ),
    )
    registry.register_fn(
        "get_ram", "report RAM usage", {"type": "object", "properties": {}},
        lambda: (
            (lambda r: ToolResult.ok(
                f"RAM is at {r['percent']} percent — {r['used_gb']} of {r['total_gb']} gigabytes in use.", **r
            ))(ram_usage())
            if ram_usage() is not None
            else ToolResult.fail("I couldn't read memory usage.", error="unavailable")
        ),
    )
    registry.register_fn(
        "get_disk", "report disk usage and free space", {"type": "object", "properties": {}},
        lambda: (
            (lambda d: ToolResult.ok(
                f"Disk is {d['percent']} percent full with {d['free_gb']} gigabytes free.", **d
            ))(disk_usage())
            if disk_usage() is not None
            else ToolResult.fail("I couldn't read disk usage.", error="unavailable")
        ),
    )
    registry.register_fn(
        "get_battery", "report battery status", {"type": "object", "properties": {}},
        lambda: (
            (lambda b: ToolResult.ok(
                f"Battery is at {b['percent']} percent and "
                f"{'charging' if b['plugged_in'] else 'on battery'}.", **b
            ))(battery())
            if battery() is not None
            else ToolResult.fail("There's no battery on this machine.", error="unavailable")
        ),
    )
    registry.register_fn(
        "get_network", "report network connectivity", {"type": "object", "properties": {}},
        lambda: (
            ToolResult.ok("The network is up.", network=True)
            if network_status()
            else ToolResult.fail("The network appears to be down.", network=False)
        ),
    )
