"""Tool abstractions.

Every capability exposed to the LLM is a registered `Tool` with a schema,
validation, a permission level, and a structured `ToolResult`. The LLM never
executes arbitrary shell commands — it may only name registered tools with
structured arguments.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class PermissionLevel(str, Enum):
    SAFE = "safe"            # read-only / non-destructive
    ELEVATED = "elevated"    # changes system state (volume, brightness, apps)
    DESTRUCTIVE = "destructive"  # requires explicit user confirmation


class ToolError(Exception):
    """Raised by tools when validation or execution fails."""


@dataclass
class ToolResult:
    success: bool
    spoken: str                     # human/voice-facing summary
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None     # machine-readable error category
    needs_confirmation: bool = False
    pending_action: Optional[str] = None   # tool name awaiting confirmation
    pending_args: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, spoken: str, **data: Any) -> "ToolResult":
        return cls(success=True, spoken=spoken, data=data)

    @classmethod
    def fail(cls, spoken: str, error: str = "execution_error", **data: Any) -> "ToolResult":
        return cls(success=False, spoken=spoken, error=error, data=data)

    @classmethod
    def confirm(cls, tool_name: str, spoken: str, args: Dict[str, Any]) -> "ToolResult":
        return cls(
            success=False,
            needs_confirmation=True,
            pending_action=tool_name,
            pending_args=args,
            spoken=spoken,
            error="confirmation_required",
        )


@dataclass
class Tool:
    name: str
    description: str
    schema: Dict[str, Any]          # {"type":"object","properties":{...},"required":[...]}
    handler: Callable[..., ToolResult]
    permission: PermissionLevel = PermissionLevel.SAFE
    aliases: List[str] = field(default_factory=list)

    def to_prompt(self) -> str:
        props = self.schema.get("properties", {})
        return f"- {self.name}: {self.description} | args: {props}"

    def validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and coerce arguments against the tool schema."""
        if not isinstance(args, dict):
            raise ToolError("Arguments must be a JSON object.")
        props: Dict[str, Any] = self.schema.get("properties", {})
        required: List[str] = self.schema.get("required", [])
        clean: Dict[str, Any] = {}
        for req in required:
            if req not in args or args[req] is None:
                raise ToolError(f"Missing required argument '{req}'.")
        for key, value in args.items():
            if key not in props:
                raise ToolError(f"Unknown argument '{key}' for tool '{self.name}'.")
            expected = props[key].get("type", "string")
            if expected in ("number", "integer"):
                try:
                    converted = int(value) if expected == "integer" else float(value)
                except (TypeError, ValueError):
                    raise ToolError(f"Argument '{key}' must be a number.")
                minimum, maximum = props[key].get("minimum"), props[key].get("maximum")
                if minimum is not None and converted < minimum:
                    raise ToolError(f"Argument '{key}' must be at least {minimum}.")
                if maximum is not None and converted > maximum:
                    raise ToolError(f"Argument '{key}' must be at most {maximum}.")
                clean[key] = converted
            elif expected == "boolean":
                if not isinstance(value, bool):
                    raise ToolError(f"Argument '{key}' must be true or false.")
                clean[key] = value
            else:
                if not isinstance(value, str):
                    value = str(value)
                if not value.strip():
                    raise ToolError(f"Argument '{key}' must not be empty.")
                clean[key] = value.strip()
        return clean

    def execute(self, **args: Any) -> ToolResult:
        validated = self.validate_args(args)
        return self.handler(**validated)
