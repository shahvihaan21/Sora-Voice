"""Application launch/close/query tools backed by an explicit registry.

The LLM can only refer to apps by alias; every target is validated against
`KNOWN_APPS` plus user-configured aliases from `SORA_APP_ALIASES`. There is no
path to arbitrary process creation from the model.
"""
import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from sora.config.settings import config
from sora.tools.base import ToolError, ToolResult
from sora.utils.logging import log

_IS_WINDOWS = platform.system() == "Windows"

# name -> list of candidate executables (absolute paths or PATH names)
KNOWN_APPS: Dict[str, List[str]] = {
    "chrome": ["chrome.exe", "google-chrome"],
    "edge": ["msedge.exe"],
    "firefox": ["firefox.exe"],
    "spotify": ["spotify.exe"],
    "vs code": ["code.cmd", "code"],
    "vscode": ["code.cmd", "code"],
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "terminal": ["wt.exe"],
    "cmd": ["cmd.exe"],
    "powershell": ["powershell.exe"],
    "task manager": ["taskmgr.exe"],
    "discord": ["discord.exe"],
    "steam": ["steam.exe"],
    "word": ["winword.exe"],
    "excel": ["excel.exe"],
    "vlc": ["vlc.exe"],
}

# well-known folders usable via the `open_path` tool
KNOWN_FOLDERS: Dict[str, str] = {
    "downloads": "{USERPROFILE}\\Downloads",
    "documents": "{USERPROFILE}\\Documents",
    "desktop": "{USERPROFILE}\\Desktop",
    "pictures": "{USERPROFILE}\\Pictures",
    "music": "{USERPROFILE}\\Music",
    "videos": "{USERPROFILE}\\Videos",
}

# process image names so we can query/close even when launch used PATH lookup
PROCESS_ALIASES: Dict[str, List[str]] = {
    "chrome": ["chrome.exe"],
    "edge": ["msedge.exe"],
    "firefox": ["firefox.exe"],
    "spotify": ["spotify.exe"],
    "vs code": ["code.exe"],
    "vscode": ["code.exe"],
    "notepad": ["notepad.exe"],
    "calculator": ["calculatorapp.exe", "calculator.exe", "applicationframehost.exe"],
    "discord": ["discord.exe"],
    "steam": ["steam.exe"],
    "vlc": ["vlc.exe"],
    "word": ["winword.exe"],
    "excel": ["excel.exe"],
}

_LOCAL_APPDATA = os.getenv("LOCALAPPDATA", "")
_PROGRAM_FILES = os.getenv("ProgramFiles", "")
_PROGRAM_FILES_X86 = os.getenv("ProgramFiles(x86)", "")
_APPDATA = os.getenv("APPDATA", "")

# extra search locations for common GUI apps on Windows
SEARCH_PATHS: List[Path] = [
    Path(_LOCAL_APPDATA) / "Google" / "Chrome" / "Application",
    Path(_PROGRAM_FILES) / "Google" / "Chrome" / "Application",
    Path(_LOCAL_APPDATA) / "Microsoft" / "Edge" / "Application",
    Path(_PROGRAM_FILES_X86) / "Microsoft" / "Edge" / "Application",
    Path(_APPDATA) / "Spotify",
    Path(_LOCAL_APPDATA) / "Discord",
    Path(_LOCAL_APPDATA) / "Programs",
]


def _normalize(name: str) -> str:
    return (name or "").strip().lower().replace(".exe", "").strip()


def resolve_app(name: str) -> str:
    """Resolve an alias to a launchable target. Raises ToolError if unknown."""
    normalized = _normalize(name)
    for alias, target in config.app_aliases.items():
        if _normalize(alias) == normalized:
            if os.path.isdir(target) or os.path.isfile(target):
                return target
            raise ToolError(f"The alias '{alias}' points to something that doesn't exist.")
    candidates = KNOWN_APPS.get(normalized)
    if not candidates:
        # allow direct known-folder style names too
        raise ToolError(f"'{name}' isn't in my application registry.")
    for cand in candidates:
        if os.path.isabs(cand) and os.path.exists(cand):
            return cand
        found = _find_in_paths(cand)
        if found:
            return str(found)
        if _which(cand):
            return cand
    raise ToolError(f"I found '{name}' in my registry but couldn't locate its executable.")


def _find_in_paths(executable: str) -> Optional[Path]:
    for base in SEARCH_PATHS:
        if base.exists():
            match = base / executable
            if match.exists():
                return match
    return None


def _which(exe: str) -> Optional[str]:
    from shutil import which
    return which(exe)


def _process_names(name: str) -> List[str]:
    normalized = _normalize(name)
    names = PROCESS_ALIASES.get(normalized)
    if names:
        return names
    resolved_alias = config.app_aliases.get(normalized)
    if resolved_alias and os.path.isfile(resolved_alias):
        return [Path(resolved_alias).name]
    return [f"{normalized}.exe"]


def _running_processes(image_names: List[str]) -> List[str]:
    """Return image names from the list that are currently running."""
    if not _IS_WINDOWS:
        return []
    try:
        out = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True,
            timeout=10, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        ).stdout.lower()
        return [n for n in image_names if f'"{n.lower()}"' in out]
    except (subprocess.TimeoutExpired, OSError) as exc:
        log.warning(f"tasklist failed: {exc}")
        return []


def launch_app(name: str) -> ToolResult:
    target = resolve_app(name)
    display_name = _normalize(name).title()
    try:
        if os.path.isdir(target):
            os.startfile(target)  # noqa: S606 — validated path, no shell
        else:
            subprocess.Popen([target], cwd=os.path.dirname(target) or None,
                             creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
    except OSError as exc:
        log.warning(f"Launch failed for {target}: {exc}")
        return ToolResult.fail(f"I couldn't open {display_name}.", error="launch_failed")
    return ToolResult.ok(f"Opening {display_name}.", app=display_name, target=target)


def close_app(name: str) -> ToolResult:
    names = _process_names(name)
    running = _running_processes(names)
    if not running:
        return ToolResult.ok(f"{_normalize(name).title()} isn't running.")
    try:
        subprocess.run(
            ["taskkill", "/IM", running[0]] , capture_output=True, timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (subprocess.TimeoutExpired, OSError):
        return ToolResult.fail(f"I couldn't close {_normalize(name).title()}.", error="close_failed")
    return ToolResult.ok(f"Closing {_normalize(name).title()}.", app=name)


def is_app_running(name: str) -> ToolResult:
    names = _process_names(name)
    running = _running_processes(names)
    label = _normalize(name).title()
    if running:
        return ToolResult.ok(f"Yes, {label} is running.", running=True)
    return ToolResult.ok(f"No, {label} isn't running right now.", running=False)


def restart_app(name: str) -> ToolResult:
    close_result = close_app(name)
    if not close_result.success:
        return close_result
    return launch_app(name)


def open_known_folder(name: str) -> ToolResult:
    key = _normalize(name)
    template = KNOWN_FOLDERS.get(key)
    if not template:
        return ToolResult.fail(f"I don't know the folder '{name}'.", error="unknown_folder")
    path = template.format(USERPROFILE=os.getenv("USERPROFILE", ""))
    if not os.path.isdir(path):
        return ToolResult.fail(f"The folder '{key}' doesn't exist.", error="missing_folder")
    try:
        os.startfile(path)  # noqa: S606 — validated known folder
    except OSError:
        return ToolResult.fail(f"I couldn't open {key}.", error="open_failed")
    return ToolResult.ok(f"Opening {key}.", folder=key)


def register_application_tools(registry) -> None:
    from sora.tools.base import PermissionLevel

    registry.register_fn("open_app", "open an application by name",
                         {"type": "object", "properties": {"name": {"type": "string"}},
                          "required": ["name"]},
                         launch_app, PermissionLevel.ELEVATED, aliases=["launch_app"])
    registry.register_fn("close_app", "close an application by name",
                         {"type": "object", "properties": {"name": {"type": "string"}},
                          "required": ["name"]},
                         close_app, PermissionLevel.ELEVATED)
    registry.register_fn("app_running", "check whether an application is running",
                         {"type": "object", "properties": {"name": {"type": "string"}},
                          "required": ["name"]},
                         is_app_running)
    registry.register_fn("restart_app", "restart an application by name",
                         {"type": "object", "properties": {"name": {"type": "string"}},
                          "required": ["name"]},
                         restart_app, PermissionLevel.ELEVATED)
    registry.register_fn("open_folder", "open a known user folder like Downloads or Documents",
                         {"type": "object", "properties": {"name": {"type": "string"}},
                          "required": ["name"]},
                         open_known_folder)
    registry.register_fn("list_apps", "list applications Sora knows how to open",
                         {"type": "object", "properties": {}},
                         lambda: ToolResult.ok(
                             "I can open: " + ", ".join(sorted(KNOWN_APPS.keys())) + ".",
                             apps=sorted(KNOWN_APPS.keys()),
                         ))
