"""Dynamic tool registry with schema validation and side-effect labels.

Merges the best of both branches:
- Auto-discovery of tools/run/*.py scripts (version-1.0)
- Schema validation + side-effect labels (working-shard-pieces)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

from app.file_tools import list_dir, read_file, write_file
from app.system_tools import get_system_snapshot


ToolFn = Callable[..., str]


@dataclass(frozen=True)
class ToolSpec:
    """Metadata for one callable tool."""

    name: str
    description: str = ""
    args: list[str] = field(default_factory=list)
    side_effect: str = "read"  # read | write | exec | network
    timeout_seconds: int = 30


@dataclass
class ScriptTool:
    """Subprocess wrapper for tools/run/*.py scripts."""

    name: str
    script_path: Path
    spec: ToolSpec | None = None

    def run(self, *args: Any) -> str:
        str_args = [str(a) for a in args]
        stdin_data = ""

        # Tools that expect JSON or content on stdin
        if self.name in ("str_replace",) and str_args:
            stdin_data = str_args[0]
            str_args = []
        elif self.name in ("write", "bash", "exec") and str_args:
            if self.name == "write" and len(str_args) >= 2:
                stdin_data = str_args[1]
                str_args = [str_args[0]]
            elif self.name in ("bash", "exec"):
                stdin_data = str_args[0]
                str_args = str_args[1:]

        timeout = self.spec.timeout_seconds if self.spec else 30

        try:
            result = subprocess.run(
                [sys.executable, str(self.script_path), *str_args],
                input=stdin_data,
                text=True,
                capture_output=True,
                check=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return f"[TOOL ERROR] Script tool '{self.name}' timed out after {timeout}s."
        except Exception as error:
            return f"[TOOL ERROR] Script tool '{self.name}' failed to start: {error}"

        output = (result.stdout or "") + (result.stderr or "")
        output = output.strip()
        if result.returncode != 0:
            return f"[TOOL ERROR] Script tool '{self.name}' exited {result.returncode}: {output}"
        return output or f"[OK] Script tool '{self.name}' completed"


class ToolRegistry:
    """Register built-in Python tools and auto-discover script tools."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.tools: dict[str, ToolFn] = {}
        self.specs: dict[str, ToolSpec] = {}
        self._register_builtin_tools()
        self._register_script_tools()

    def _register_builtin_tools(self) -> None:
        builtins = {
            "read_file": (read_file, ToolSpec("read_file", "Read a file with chunking support.", ["path"], "read")),
            "write_file": (write_file, ToolSpec("write_file", "Write content to a file (FAT32-safe).", ["path", "content"], "write")),
            "list_dir": (list_dir, ToolSpec("list_dir", "List directory contents.", ["path"], "read")),
            "system_snapshot": (get_system_snapshot, ToolSpec("system_snapshot", "Get hardware/OS vitals.", [], "read")),
        }
        for name, (fn, spec) in builtins.items():
            self.tools[name] = fn
            self.specs[name] = spec

    def _register_script_tools(self) -> None:
        scripts_dir = self.base_dir / "tools" / "run"
        if not scripts_dir.exists():
            return

        # Load optional metadata manifest
        manifest: dict[str, Any] = {}
        manifest_path = scripts_dir / "registry.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        for script in sorted(scripts_dir.glob("*.py")):
            name = script.stem
            tool_name = f"run_{name}"
            meta = manifest.get(tool_name, {})
            spec = ToolSpec(
                name=tool_name,
                description=meta.get("description", f"Script tool: {name}"),
                args=meta.get("args", []),
                side_effect=meta.get("side_effect", "exec"),
                timeout_seconds=meta.get("timeout_seconds", 30),
            )
            runner = ScriptTool(name=name, script_path=script, spec=spec)
            self.tools[tool_name] = runner.run
            self.specs[tool_name] = spec

    def execute(self, tool_name: str, tool_args: list) -> str:
        tool = self.tools.get(tool_name)
        if tool is None:
            known = ", ".join(sorted(self.tools))
            return f"[TOOL ERROR] Unknown tool: {tool_name}. Available: {known}"
        try:
            return str(tool(*tool_args))
        except Exception as error:
            return f"[TOOL ERROR] {tool_name} failed: {error}"

    def get_side_effect(self, tool_name: str) -> str:
        """Return the side-effect class for a tool (read/write/exec/network)."""
        spec = self.specs.get(tool_name)
        return spec.side_effect if spec else "exec"

    def describe(self) -> str:
        """Human-readable tool listing with descriptions."""
        lines = []
        for name in sorted(self.specs):
            spec = self.specs[name]
            args_str = ", ".join(spec.args) if spec.args else ""
            effect = f"[{spec.side_effect}]"
            lines.append(f"- {name}({args_str}) {effect} — {spec.description}")
        return "\n".join(lines)
