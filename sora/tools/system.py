"""Windows/system-level tools: lock, power, settings panels, system info.

Destructive operations (restart, shutdown, sleep) require explicit
confirmation through the registry's confirmation flow.
"""
import ctypes
import datetime
import os
import platform
import subprocess
import sys

from sora.tools.base import ToolError, ToolResult
from sora.utils.logging import log

_IS_WINDOWS = platform.system() == "Windows"
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _run(cmd, timeout: float = 10.0) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          creationflags=_NO_WINDOW)


def lock_workstation() -> ToolResult:
    if not _IS_WINDOWS:
        return ToolResult.fail("Locking is only available on Windows.", error="unsupported_platform")
    result = _run(["rundll32.exe", "user32.dll,LockWorkStation"])
    if result.returncode != 0:
        return ToolResult.fail("I couldn't lock the computer.", error="lock_failed")
    return ToolResult.ok("Locking the computer now.")


def sleep_computer() -> ToolResult:
    if not _IS_WINDOWS:
        return ToolResult.fail("Sleep is only available on Windows.", error="unsupported_platform")
    # FALSE for hibernate so this is a sleep, not hibernate.
    result = _run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
    if result.returncode != 0:
        return ToolResult.fail("I couldn't put the computer to sleep.", error="sleep_failed")
    return ToolResult.ok("Putting the computer to sleep.")


def restart_computer() -> ToolResult:
    result = _run(["shutdown", "/r", "/t", "5"])
    if result.returncode != 0:
        return ToolResult.fail("The restart command failed.", error="restart_failed")
    return ToolResult.ok("Restarting the computer in five seconds.")


def shutdown_computer() -> ToolResult:
    result = _run(["shutdown", "/s", "/t", "5"])
    if result.returncode != 0:
        return ToolResult.fail("The shutdown command failed.", error="shutdown_failed")
    return ToolResult.ok("Shutting down the computer in five seconds.")


def cancel_shutdown() -> ToolResult:
    result = _run(["shutdown", "/a"])
    if result.returncode != 0:
        return ToolResult.fail("There's no pending shutdown to cancel.", error="nothing_to_cancel")
    return ToolResult.ok("Cancelled the pending shutdown.")


def _open_shell_target(target: str, spoken: str) -> ToolResult:
    try:
        if target.startswith(("ms-settings:", "shell:")):
            os.startfile(target)  # noqa: S606
        else:
            _run(["cmd", "/c", "start", "", target])
    except (OSError, subprocess.SubprocessError) as exc:
        log.warning(f"Failed to open '{target}': {exc}")
        return ToolResult.fail(f"I couldn't open {spoken}.", error="open_failed")
    return ToolResult.ok(f"Opening {spoken}.")


def open_settings() -> ToolResult:
    return _open_shell_target("ms-settings:", "Windows Settings")


def open_task_manager() -> ToolResult:
    return _open_shell_target("taskmgr.exe", "Task Manager")


def open_device_manager() -> ToolResult:
    return _open_shell_target("devmgmt.msc", "Device Manager")


def open_control_panel() -> ToolResult:
    return _open_shell_target("control.exe", "Control Panel")


def open_file_explorer() -> ToolResult:
    return _open_shell_target("explorer.exe", "File Explorer")


def system_info() -> ToolResult:
    info = {
        "os": f"{platform.system()} {platform.release()}",
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python": sys.version.split()[0],
        "hostname": platform.node(),
    }
    spoken = (f"You're running {info['os']} on a {info['machine']} machine, "
              f"with Python {info['python']}.")
    return ToolResult.ok(spoken, **info)


def register_system_tools(registry) -> None:
    from sora.tools.base import PermissionLevel

    registry.register_fn("lock_computer", "lock the computer",
                         {"type": "object", "properties": {}},
                         lock_workstation, PermissionLevel.DESTRUCTIVE)
    registry.register_fn("sleep_computer", "put the computer to sleep",
                         {"type": "object", "properties": {}},
                         sleep_computer, PermissionLevel.DESTRUCTIVE)
    registry.register_fn("restart_computer", "restart the computer",
                         {"type": "object", "properties": {}},
                         restart_computer, PermissionLevel.DESTRUCTIVE)
    registry.register_fn("shutdown_computer", "shut down the computer",
                         {"type": "object", "properties": {}},
                         shutdown_computer, PermissionLevel.DESTRUCTIVE)
    registry.register_fn("cancel_shutdown", "cancel a pending shutdown or restart",
                         {"type": "object", "properties": {}},
                         cancel_shutdown)
    registry.register_fn("open_settings", "open Windows Settings",
                         {"type": "object", "properties": {}}, open_settings)
    registry.register_fn("open_task_manager", "open Task Manager",
                         {"type": "object", "properties": {}}, open_task_manager)
    registry.register_fn("open_device_manager", "open Device Manager",
                         {"type": "object", "properties": {}}, open_device_manager)
    registry.register_fn("open_control_panel", "open the Control Panel",
                         {"type": "object", "properties": {}}, open_control_panel)
    registry.register_fn("open_file_explorer", "open File Explorer",
                         {"type": "object", "properties": {}}, open_file_explorer)
    registry.register_fn("system_info", "report system information",
                         {"type": "object", "properties": {}}, system_info)
