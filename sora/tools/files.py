"""Safe, validated file/folder tools.

Only whitelisted user folders and explicitly-validated paths may be opened.
Paths cannot escape the user profile; nothing is ever deleted by the LLM.
"""
import os
from pathlib import Path
from typing import Optional

from sora.tools.base import ToolError, ToolResult
from sora.utils.logging import log


def _resolve_safe_path(path: str) -> Path:
    """Resolve a user-supplied path and ensure it stays inside the profile."""
    raw = Path(os.path.expandvars(path.strip().strip('"')))
    if not raw.is_absolute():
        raw = Path(os.getenv("USERPROFILE", str(Path.home()))) / raw
    try:
        resolved = raw.resolve()
        profile = Path(os.getenv("USERPROFILE", str(Path.home()))).resolve()
        resolved.relative_to(profile)
    except ValueError:
        raise ToolError("I can only open paths inside your user profile.")
    return resolved


def open_path(path: str) -> ToolResult:
    try:
        resolved = _resolve_safe_path(path)
    except ToolError as exc:
        return ToolResult.fail(str(exc), error="path_not_allowed")
    if not resolved.exists():
        return ToolResult.fail("That path doesn't exist.", error="not_found")
    try:
        os.startfile(str(resolved))  # noqa: S606 — validated path
    except OSError as exc:
        log.warning(f"os.startfile failed for {resolved}: {exc}")
        return ToolResult.fail("I couldn't open that path.", error="open_failed")
    label = "folder" if resolved.is_dir() else "file"
    return ToolResult.ok(f"Opening the {label} {resolved.name}.", path=str(resolved))


def path_exists(path: str) -> ToolResult:
    try:
        resolved = _resolve_safe_path(path)
    except ToolError as exc:
        return ToolResult.fail(str(exc), error="path_not_allowed")
    if resolved.exists():
        kind = "folder" if resolved.is_dir() else "file"
        return ToolResult.ok(f"Yes, that {kind} exists.", exists=True)
    return ToolResult.ok("No, that path doesn't exist.", exists=False)


def register_file_tools(registry) -> None:
    from sora.tools.base import PermissionLevel

    registry.register_fn("open_path", "open a file or folder inside the user profile",
                         {"type": "object", "properties": {"path": {"type": "string"}},
                          "required": ["path"]},
                         open_path, PermissionLevel.ELEVATED)
    registry.register_fn("path_exists", "check whether a path inside the user profile exists",
                         {"type": "object", "properties": {"path": {"type": "string"}},
                          "required": ["path"]},
                         path_exists)
