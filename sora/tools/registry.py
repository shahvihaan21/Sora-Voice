"""Tool registry + confirmation manager.

The registry is the single gate between the LLM and system actions:
`registry.execute(name, args)` validates arguments, enforces permission
levels (confirmation for destructive operations) and returns structured
`ToolResult`s. New tools can be registered without touching the core loop.
"""
import time
from typing import Callable, Dict, List, Optional

from sora.tools.base import Tool, ToolError, ToolResult, PermissionLevel
from sora.utils.logging import log


class PendingConfirmation:
    """A destructive action awaiting explicit user approval."""

    def __init__(self, tool_name: str, args: Dict, prompt: str, expires_at: float):
        self.tool_name = tool_name
        self.args = args
        self.prompt = prompt
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        return time.monotonic() > self.expires_at


class ToolRegistry:
    def __init__(self, confirmation_timeout: float = 20.0):
        self._tools: Dict[str, Tool] = {}
        self._pending: Optional[PendingConfirmation] = None
        self.confirmation_timeout = confirmation_timeout

    # -- registration ------------------------------------------------
    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ToolError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def register_fn(self, name: str, description: str, schema: Dict,
                    handler: Callable, permission: PermissionLevel = PermissionLevel.SAFE,
                    aliases: Optional[List[str]] = None) -> None:
        self.register(Tool(name, description, schema, handler, permission, aliases or []))

    # -- lookup ------------------------------------------------------
    def get(self, name: str) -> Optional[Tool]:
        name = (name or "").strip().lower()
        tool = self._tools.get(name)
        if tool:
            return tool
        for t in self._tools.values():
            if name in [a.lower() for a in t.aliases]:
                return t
        return None

    def names(self) -> List[str]:
        return sorted(self._tools.keys())

    def all_tools(self) -> List[Tool]:
        return list(self._tools.values())

    # -- execution ----------------------------------------------------
    def execute(self, tool_name: str, **args) -> ToolResult:
        """Validate and run a tool. Destructive tools require confirmation."""
        tool = self.get(tool_name)
        if tool is None:
            return ToolResult.fail(f"I don't have a tool called '{tool_name}'.", error="unknown_tool")
        try:
            validated = tool.validate_args(args)
        except ToolError as exc:
            log.warning(f"Validation failed for {tool.name}: {exc}")
            return ToolResult.fail(f"That request was invalid: {exc}", error="invalid_arguments")

        start = time.perf_counter()
        try:
            if tool.permission == PermissionLevel.DESTRUCTIVE:
                result = self._request_confirmation(tool, validated)
            else:
                result = tool.execute(**validated)
        except ToolError as exc:
            result = ToolResult.fail(str(exc), error="invalid_arguments")
        except Exception as exc:  # noqa: BLE001 — tools must never crash the loop
            log.exception(f"Tool '{tool.name}' crashed")
            result = ToolResult.fail(
                f"Sorry, '{tool.name}' failed to run.", error="tool_crash", detail=type(exc).__name__
            )
        duration_ms = (time.perf_counter() - start) * 1000
        log.info(f"Tool '{tool.name}' -> success={result.success} in {duration_ms:.1f}ms "
                 f"error={result.error or 'none'}")
        return result

    def _request_confirmation(self, tool: Tool, args: Dict) -> ToolResult:
        prompt = f"Are you sure you want me to {tool.description.rstrip('.')}?"
        self._pending = PendingConfirmation(
            tool.name, args, prompt, time.monotonic() + self.confirmation_timeout
        )
        log.info(f"Confirmation required for '{tool.name}' with {args}")
        return ToolResult.confirm(tool.name, prompt, args)

    # -- confirmation flow ---------------------------------------------
    @property
    def pending_confirmation(self) -> Optional[PendingConfirmation]:
        if self._pending and self._pending.is_expired():
            log.info("Pending confirmation expired.")
            self._pending = None
        return self._pending

    def confirm(self) -> ToolResult:
        pending = self.pending_confirmation
        if pending is None:
            return ToolResult.ok("There is nothing waiting for confirmation.")
        self._pending = None
        tool = self.get(pending.tool_name)
        if tool is None:
            return ToolResult.fail("That action is no longer available.", error="unknown_tool")
        start = time.perf_counter()
        try:
            result = tool.execute(**pending.args)
        except ToolError as exc:
            result = ToolResult.fail(str(exc), error="invalid_arguments")
        except Exception:  # noqa: BLE001
            log.exception("Confirmed tool crashed")
            result = ToolResult.fail("Sorry, that action failed.", error="tool_crash")
        log.info(f"Confirmed tool '{tool.name}' -> success={result.success} "
                 f"in {(time.perf_counter() - start) * 1000:.1f}ms")
        return result

    def cancel(self) -> ToolResult:
        if self._pending is None:
            return ToolResult.ok("There was nothing to cancel.")
        self._pending = None
        return ToolResult.ok("Cancelled. I won't do that.")


def build_default_registry(confirmation_timeout: float = 20.0) -> ToolRegistry:
    """Assemble the full default toolset."""
    from sora.tools.audio import register_audio_tools
    from sora.tools.display import register_display_tools
    from sora.tools.applications import register_application_tools
    from sora.tools.system import register_system_tools
    from sora.tools.files import register_file_tools
    from sora.tools.diagnostics import register_diagnostics_tools

    registry = ToolRegistry(confirmation_timeout=confirmation_timeout)
    register_audio_tools(registry)
    register_display_tools(registry)
    register_application_tools(registry)
    register_system_tools(registry)
    register_file_tools(registry)
    register_diagnostics_tools(registry)
    return registry
