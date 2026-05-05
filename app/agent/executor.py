"""Executor: walk AgentSteps one at a time, calling tools via the registry.

The executor sends each step to the LLM as a focused sub-prompt,
collects tool calls, runs them through the ToolRegistry, and records results.
Respects autonomy mode: in 'semi', side-effects require confirmation.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from app.agent.contracts import AgentStep, AgentTask, ToolCall, ToolResult

if TYPE_CHECKING:
    from app.agent.tool_registry import ToolRegistry

PROCESS_PAUSE_SECONDS = 0.2


def build_step_prompt(step: AgentStep, tool_listing: str) -> str:
    """Build a focused prompt for one step."""
    return (
        f"[CURRENT STEP] {step.id}: {step.goal}\n"
        f"[SUCCESS CRITERIA] {step.success_criteria}\n\n"
        f"Available tools:\n{tool_listing}\n\n"
        "If you need a tool, respond with:\n"
        "ACTION:\n"
        '{"tool": "<name>", "args": [...]}\n\n'
        "Otherwise, respond with your result directly."
    )


def needs_confirmation(tool_name: str, registry: "ToolRegistry", mode: str) -> bool:
    """Return True if this tool call requires user confirmation."""
    if mode in ("auto-safe", "auto-full"):
        if mode == "auto-safe" and registry.get_side_effect(tool_name) == "exec":
            return True  # auto-safe blocks shell exec
        return False
    if mode == "semi":
        effect = registry.get_side_effect(tool_name)
        return effect in ("write", "exec")
    return True  # manual mode: always confirm


def execute_tool_call(
    call: ToolCall,
    registry: "ToolRegistry",
) -> ToolResult:
    """Execute a single validated tool call and return the result."""
    time.sleep(PROCESS_PAUSE_SECONDS)
    output = registry.execute(call.name, list(call.args.values()) if isinstance(call.args, dict) else list(call.args))

    ok = not output.startswith("[TOOL ERROR]")
    error = output if not ok else ""
    return ToolResult(
        name=call.name,
        ok=ok,
        output=output if ok else "",
        error=error,
    )


def format_tool_result(result: ToolResult) -> str:
    """Format a ToolResult for injection back into the conversation."""
    status = "OK" if result.ok else "ERROR"
    content = result.output if result.ok else result.error
    return (
        f"[TOOL {status}] {result.name}\n"
        f"{content}"
    )
