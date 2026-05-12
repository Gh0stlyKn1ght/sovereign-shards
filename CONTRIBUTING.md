# Contributing to Sovereign Shards

## Getting Started

1. Clone the repo: `git clone https://github.com/s4ndm4n33-spec/sovereign-shards.git`
2. Read `docs/MIGRATION_LOG.md` — this is the engineering diary. It tells you exactly what was built, what broke, and why every decision was made.
3. Read `docs/ROADMAP.md` — this is the phase plan. Find the current phase, check the gate criteria.
4. Read `docs/NEXT_10_STEPS.md` — this is your immediate task list.

## Architecture Principles

These are non-negotiable. Every contribution must follow them.

### 1. The LLM Does as Little Reasoning as Possible

The framework handles routing, tool execution, context management, memory, and security. The LLM does language and judgment. If you can solve it deterministically, don't ask the model.

### 2. Two Dependencies Maximum

The project uses `python-dotenv` and `psutil`. That's it. Everything else is Python stdlib. If your change needs a new package, it needs an extremely strong justification.

### 3. 2048-Token Context Ceiling

The target hardware has a hard 2048-token context window. Every feature must work within this constraint. Don't design for larger contexts — design for smaller ones.

### 4. USB-Portable, FAT32-Safe

All file operations must be atomic (write to temp, then rename). No symlinks. No files > 4GB. No filenames with special characters. The shard runs from a Kingston USB 2.0 on FAT32.

### 5. Zero Cloud Dependencies

No API keys. No internet at runtime. No phone-home. No telemetry. The shard is sovereign.

## Code Style

- Python 3.11+ (embedded portable Python)
- Type hints on all public functions
- Docstrings on all modules and public functions
- `from __future__ import annotations` at the top of every file
- Error messages must say WHAT failed, WHY, and WHAT TO DO
- Windows-compatible paths (use `pathlib.Path`, not hardcoded `/`)

## Tool Development

Tools live in `tools/run/`. Each tool is a standalone Python script.

**Template:**
```python
"""Short description of what the tool does.

Usage: python tool_name.py [args]
"""

import os
import sys
from pathlib import Path

# Constants
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def main():
    if len(sys.argv) < 2:
        print("[ERROR] Usage: python tool_name.py <arg>")
        sys.exit(1)
    
    # Tool logic here

if __name__ == "__main__":
    main()
```

**Registration:** Add the tool to `tools/run/registry.json` with description, args, and side_effect.

## Testing

- Unit tests: `python -m pytest tests/`
- E2E tests: `python tests/e2e_runner.py` (requires running llama.cpp server)
- Smoke test: boot J, run 5 basic commands, verify identity

## Git Workflow

- All work happens on `main` (this is a single-developer project for now)
- Commit messages follow conventional commits: `feat:`, `fix:`, `docs:`, `tests:`, `refactor:`
- Update `docs/MIGRATION_LOG.md` at the end of every session with what you built, what broke, and what's next

## The Five Masters

The codebase is governed by Five Masters — AST-based code quality checks:

1. **Korotkevich** — Algorithmic efficiency
2. **Ritchie** — Clean naming and structure
3. **Hamilton** — Error handling and fault tolerance
4. **Knuth** — Performance optimization
5. **Torvalds** — Systems clarity and maintainability

Run `/optimize <file>` to check a file against all five. Run `/sandbox` for a full project audit.

## Questions?

Read the docs first:
- `docs/USER_MANUAL.md` — complete command reference
- `docs/MIGRATION_LOG.md` — engineering diary (1400+ lines)
- `docs/ROADMAP.md` — 5-phase product plan
- `docs/NEXT_10_STEPS.md` — immediate task list
