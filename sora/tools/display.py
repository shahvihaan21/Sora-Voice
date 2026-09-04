"""Display brightness control via the Windows WMI monitor API.

Uses a small PowerShell WMI query so no extra dependency is required.
Laptop panels that expose WmiMonitorBrightnessMethods work; external monitors
without DDC/CI report an "unavailable capability" result instead of failing.
"""
import json
import platform
import subprocess
from typing import Optional

from sora.tools.base import ToolError, ToolResult
from sora.utils.logging import log

_IS_WINDOWS = platform.system() == "Windows"


def _ps(command: str, timeout: float = 8.0) -> str:
    """Run a PowerShell one-liner without a shell wrapper."""
    exe = "powershell" if _IS_WINDOWS else "pwsh"
    proc = subprocess.run(
        [exe, "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True, text=True, timeout=timeout,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if proc.returncode != 0:
        raise ToolError(proc.stderr.strip() or "PowerShell command failed.")
    return proc.stdout.strip()


def get_brightness() -> Optional[int]:
    if not _IS_WINDOWS:
        return None
    try:
        out = _ps(
            "(Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness)"
            ".CurrentBrightness"
        )
        return int(float(out))
    except (ToolError, ValueError) as exc:
        log.debug(f"Brightness query unavailable: {exc}")
        return None


def set_brightness(percent: int) -> ToolResult:
    percent = max(0, min(100, int(percent)))
    if not _IS_WINDOWS:
        return ToolResult.fail("Brightness control is only available on Windows.", error="unsupported_platform")
    try:
        _ps(
            "(Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods)"
            f".WmiSetBrightness(1,{percent})"
        )
    except ToolError:
        return ToolResult.fail(
            "I couldn't change brightness — this display doesn't expose software control.",
            error="capability_unavailable",
        )
    return ToolResult.ok(f"Brightness set to {percent} percent.", brightness=percent)


def register_display_tools(registry) -> None:
    from sora.tools.base import PermissionLevel

    def _up(step: int = 10) -> ToolResult:
        current = get_brightness()
        if current is None:
            return ToolResult.fail("Brightness is not controllable on this display.", error="capability_unavailable")
        return set_brightness(current + int(step))

    def _down(step: int = 10) -> ToolResult:
        current = get_brightness()
        if current is None:
            return ToolResult.fail("Brightness is not controllable on this display.", error="capability_unavailable")
        return set_brightness(current - int(step))

    def _set(percent: int) -> ToolResult:
        return set_brightness(int(percent))

    def _get() -> ToolResult:
        current = get_brightness()
        if current is None:
            return ToolResult.fail("I can't read brightness on this display.", error="capability_unavailable")
        return ToolResult.ok(f"Brightness is {current} percent.", brightness=current)

    registry.register_fn("brightness_up", "increase the screen brightness",
                         {"type": "object", "properties": {"step": {"type": "integer"}}},
                         _up, PermissionLevel.ELEVATED, aliases=["increase_brightness"])
    registry.register_fn("brightness_down", "decrease the screen brightness",
                         {"type": "object", "properties": {"step": {"type": "integer"}}},
                         _down, PermissionLevel.ELEVATED, aliases=["decrease_brightness"])
    registry.register_fn("set_brightness", "set the screen brightness to a percentage",
                         {"type": "object",
                          "properties": {"percent": {"type": "integer", "minimum": 0, "maximum": 100}},
                          "required": ["percent"]},
                         _set, PermissionLevel.ELEVATED)
    registry.register_fn("get_brightness", "report the current screen brightness",
                         {"type": "object", "properties": {}}, _get)
