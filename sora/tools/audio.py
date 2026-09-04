"""Volume/mute control through the Windows Core Audio API (pycaw)."""
import ctypes
import platform
from typing import Any, Optional

from sora.tools.base import ToolError, ToolResult
from sora.utils.logging import log

_IS_WINDOWS = platform.system() == "Windows"
_cast = None  # lazy


def _get_volume_interface() -> Any:
    """Return the IAudioEndpointVolume for the default render device."""
    global _cast
    try:
        from comtypes import CLSCTX_ALL, GUID
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    except ImportError as exc:
        raise ToolError("Audio control backend (pycaw) is not installed.") from exc

    if _cast is None:
        from comtypes import IUnknown
        _cast = IUnknown

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))


def get_volume_state() -> dict:
    """Return {'volume': int percent, 'muted': bool}."""
    vol = _get_volume_interface()
    level = float(vol.GetMasterVolumeLevelScalar()) * 100.0
    muted = bool(vol.GetMute())
    return {"volume": round(level), "muted": muted}


def set_volume(percent: float) -> ToolResult:
    percent = max(0, min(100, int(percent)))
    vol = _get_volume_interface()
    vol.SetMasterVolumeLevelScalar(percent / 100.0, None)
    # If adjusting volume while muted, unmute so the change is audible.
    if vol.GetMute():
        vol.SetMute(False, None)
    return ToolResult.ok(f"Volume set to {percent} percent.", volume=percent, muted=False)


def adjust_volume(delta: int) -> ToolResult:
    state = get_volume_state()
    new_level = max(0, min(100, state["volume"] + delta))
    return set_volume(new_level)


def set_muted(muted: bool) -> ToolResult:
    vol = _get_volume_interface()
    vol.SetMute(muted, None)
    word = "Muted" if muted else "Unmuted"
    return ToolResult.ok(f"{word}.", muted=muted)


def register_audio_tools(registry) -> None:
    from sora.tools.base import PermissionLevel

    registry.register_fn(
        "volume_up", "increase the system volume", {
            "type": "object",
            "properties": {"step": {"type": "integer", "description": "percent to increase, default 10"}},
        },
        lambda step: adjust_volume(int(step)), PermissionLevel.ELEVATED,
        aliases=["increase_volume"],
    )
    registry.register_fn(
        "volume_down", "decrease the system volume", {
            "type": "object",
            "properties": {"step": {"type": "integer", "description": "percent to decrease, default 10"}},
        },
        lambda step: adjust_volume(-int(step)), PermissionLevel.ELEVATED,
        aliases=["decrease_volume"],
    )
    registry.register_fn(
        "set_volume", "set the system volume to a percentage", {
            "type": "object",
            "properties": {"percent": {"type": "integer", "description": "0-100", "minimum": 0, "maximum": 100}},
            "required": ["percent"],
        },
        lambda percent: set_volume(int(percent)), PermissionLevel.ELEVATED,
    )
    registry.register_fn(
        "mute", "mute the system audio", {"type": "object", "properties": {}},
        lambda: set_muted(True), PermissionLevel.ELEVATED,
    )
    registry.register_fn(
        "unmute", "unmute the system audio", {"type": "object", "properties": {}},
        lambda: set_muted(False), PermissionLevel.ELEVATED,
    )
    registry.register_fn(
        "get_volume", "report the current volume level", {"type": "object", "properties": {}},
        lambda: (
            (lambda s: ToolResult.ok(
                f"Volume is {s['volume']} percent and {'muted' if s['muted'] else 'unmuted'}.", **s
            ))(get_volume_state())
        ),
    )
