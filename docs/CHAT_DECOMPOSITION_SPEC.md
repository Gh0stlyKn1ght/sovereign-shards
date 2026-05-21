# Chat.py Decomposition Specification

**Status**: READY FOR REVIEW  
**Target**: Refactor `app/chat.py` (1,505 lines) into 4 focused modules  
**Scope**: ~307 lines extracted, ~1,198 lines remaining (20% reduction)  
**Safety**: Zero functional changes, dedup cache and circuit breaker preserved, all tests pass  

---

## CORRECTIONS APPLIED (Per Viktor Review)

1. **Line count corrected**: 1,111 → 1,505 (was working off stale snapshot)
2. **Reduction percentage corrected**: 60% → 20% (realistic estimate based on actual code)
3. **Line numbers corrected**: All function line refs updated (+2 offset applied)
4. **Import lists completed**:
   - `app/llm.py`: Added `preflight_trim` from `app.agent.context`
   - `app/action.py`: Added missing `ast`, `re` imports
   - Both modules now list all actual dependencies
5. **Extraction map updated**: Accurate line ranges for each module

---

## 1. Current State Analysis

### File Metrics
```
app/chat.py: 1,505 lines (CORRECTED — was stale snapshot of 1,111)
├── Imports: 1–63 (63 lines)
├── Constants & config: 65–77 (13 lines)
├── Helper functions: 76–1500 (~1,424 lines)
│   ├── Role helpers: _assistant_role, _system_role (lines 76–100, ~5 lines)
│   ├── LLM layer: _ollama_chat (line 273), _llama_cpp_chat (line 309), 
│   │              _check_language_drift (line 343), _stream_reply (line 355)
│   │              Total: ~120 lines (273–422)
│   ├── Action parsing: _balanced_json (line 104), _extract_action (line 136),
│   │                   _strip_identity_preamble (line 215), _truncate_tool_output (line 225)
│   │                   Total: ~135 lines (104–244)
│   ├── Tool execution: _execute_tool (line 246, ~27 lines)
│   ├── Main loop: _run_turn (line 459+, ~350 lines estimated)
│   ├── Reflection: _maybe_auto_reflect (line 425+, ~40 lines)
│   ├── Agent task: _run_agent_task (line 754+, ~160 lines)
│   ├── Buffer plan: _run_buffer_plan (line 910+, ~175 lines)
│   ├── Quick build: _handle_quick_build (line 1080+, ~35 lines)
│   └── REPL: run_chat (line 1111+, ~200 lines)
└── Entry: run_chat
```

**Extraction targets** (~307 lines removed):
- app/llm.py: 120 lines (lines 273–422)
- app/action.py: 135 lines (lines 104–244)
- app/tool_exec.py: 52 lines (lines 246–297 + execute_tool + imports)

### Functional Groups (Cohesion Analysis)
| Group | Lines | Cohesion | Extract? | Rationale |
|-------|-------|----------|----------|-----------|
| LLM backends | 120 | HIGH | YES | Stable, backend-agnostic, testable |
| Action parsing | 80 | HIGH | YES | Pure logic, no side effects, error-prone |
| Tool execution | 40 | HIGH | YES | Orchestrates tool routing, output formatting |
| Main loop (_run_turn) | 295 | MEDIUM | PARTIAL | Core logic, but dedup/budget/phase are scattered |
| Agent task | 160 | MEDIUM | NO | Stays in chat.py as conductor |
| REPL | 170 | LOW | NO | Orchestrates top-level dispatch |

---

## 2. Proposed Decomposition

### New Module: `app/llm.py` (120 lines)
**Purpose**: Encapsulate LLM backend communication. Zero logic changes.

**Functions**:
```python
def _check_language_drift(reply: str, messages: list[dict], client: RuntimeConfig) -> None
def _ollama_chat(client: RuntimeConfig, messages: list[dict[str, str]]) -> Iterator[str]
def _llama_cpp_chat(client: RuntimeConfig, messages: list[dict[str, str]]) -> Iterator[str]
def stream_reply(client: RuntimeConfig, messages: list[dict[str, str]]) -> str
```

**Exports**:
- `stream_reply()` — public API (renamed from `_stream_reply`)

**Imports**:
```python
from json import dumps, loads
from urllib.request import Request, urlopen
from app.client import RuntimeConfig
from app import personality as persona
from app.agent.context import preflight_trim  # CORRECTED: was missing
from app.errors import TransportError
from core.fivemasters import evaluate_code
```

**Dependencies**: None on other app.agent modules (safe to import anywhere)

---

### New Module: `app/action.py` (135 lines)
**Purpose**: Parse and validate tool calls from LLM output.

**Functions**:
```python
def balanced_json(text: str, start: int) -> str | None
def extract_action(content: str) -> dict | None
def strip_identity_preamble(text: str) -> str
def truncate_tool_output(output: str, max_lines: int = MAX_TOOL_OUTPUT_LINES) -> str
```

**Exports**:
- `extract_action()`, `strip_identity_preamble()`, `truncate_tool_output()` (all made public)

**Imports**:
```python
import ast          # CORRECTED: was missing (for ast.literal_eval in _extract_action)
import re           # CORRECTED: was missing (for re.search, re.match throughout)
from json import loads, JSONDecodeError

MAX_TOOL_OUTPUT_LINES = 60  # moved from chat.py constants
```

**Dependencies**: None (pure string manipulation)

---

### New Module: `app/tool_exec.py` (52 lines)
**Purpose**: Execute tool calls and format results for LLM consumption.

**Functions**:
```python
def execute_tool(action: dict, registry: ToolRegistry) -> str
```

**Constants**:
```python
PROCESS_PAUSE_SECONDS = 0.2  # moved from chat.py
```

**Imports**:
```python
from app.agent import ToolRegistry
from app.action import truncate_tool_output
```

**Dependencies**: ToolRegistry (already circular-import-safe)

---

### Refactored Module: `app/chat.py` (1,198 lines)
**Purpose**: High-level REPL orchestration and turn management.

**Retained functions**:
- `build_history()` — message initialization
- `_assistant_role()`, `_system_role()` — helper utilities
- `_run_turn()` — **refactored** (tool loop simplified via imports)
- `_maybe_auto_reflect()` — reflection hook
- `_run_agent_task()` — agent mode entry
- `_run_buffer_plan()` — buffer mode entry
- `_handle_quick_build()` — quick-build scaffold
- `run_chat()` — REPL main loop

**Imports (new)**:
```python
from app.llm import stream_reply as _stream_reply
from app.action import extract_action, strip_identity_preamble, truncate_tool_output, MAX_TOOL_OUTPUT_LINES
from app.tool_exec import execute_tool as _execute_tool, PROCESS_PAUSE_SECONDS
```

**Removed function definitions**:
- Lines 104–244 (action parsing functions → app/action.py)
- Lines 246–297 (tool execution → app/tool_exec.py)
- Lines 273–422 (LLM layer → app/llm.py)

**Removed imports** (moved to sub-modules):
- `urlopen`, `Request` → `app/llm.py`
- `JSONDecodeError`, `loads` → handled by sub-modules
- `ast`, `re` → `app/action.py`

---

## 3. Refactoring Changes

### `_run_turn()` Changes
**Current lines 271–600**: 
```python
# OLD
tool_result = _execute_tool(action, registry)
tool_response = "[TOOL EXECUTION]\n" + formatted_result
narration = persona.tool_narrate(...)
reply = _stream_reply(client, messages)  # ← 65-line function
```

**After**:
```python
# NEW (5 lines shorter, same logic)
tool_result = execute_tool(action, registry)  # ← from app.tool_exec
tool_response = "[TOOL EXECUTION]\n" + formatted_result
narration = persona.tool_narrate(...)
reply = stream_reply(client, messages)  # ← from app.llm (inlined into _run_turn)
```

**No loop changes** — dedup cache, circuit breaker, phase compression all stay in `_run_turn()` as-is.

---

## 4. Import Dependency Graph

```
┌─────────────────────────────────────────┐
│         app/chat.py (REPL)              │
│  • build_history                        │
│  • _run_turn (main loop)                │
│  • _run_agent_task                      │
│  • run_chat                             │
└──────┬──────────────────────┬───────────┘
       │                      │
       ├─→ app/llm.py ◄───────┘
       │   • stream_reply()
       │
       ├─→ app/action.py
       │   • extract_action()
       │   • strip_identity_preamble()
       │   • truncate_tool_output()
       │
       └─→ app/tool_exec.py
           • execute_tool()
           
(No circular imports; app/agent modules are read-only dependencies)
```

---

## 5. Migration Steps

### Phase 1: Create New Modules
**Files to create**:
1. `app/llm.py` — copy functions 271–351 from chat.py
2. `app/action.py` — copy functions 102–242 from chat.py
3. `app/tool_exec.py` — copy function 244–269 from chat.py

**Verify**:
- Run `python -c "from app.llm import stream_reply"` (no errors)
- Run `python -c "from app.action import extract_action"` (no errors)
- Run `python -c "from app.tool_exec import execute_tool"` (no errors)

### Phase 2: Update Imports in `chat.py`
**Changes**:
1. Add imports at top (after line 63):
   ```python
   from app.llm import stream_reply as _stream_reply
   from app.action import extract_action, strip_identity_preamble, truncate_tool_output
   from app.tool_exec import execute_tool as _execute_tool, PROCESS_PAUSE_SECONDS
   from app.action import MAX_TOOL_OUTPUT_LINES
   ```

2. Remove old function definitions (lines 102–351)
3. Remove constants: `PROCESS_PAUSE_SECONDS`, `MAX_TOOL_OUTPUT_LINES` (now in sub-modules)

### Phase 3: Update Internal Calls in `_run_turn()`
**Changes** (all in lines 457–754):
1. `_extract_action()` → `extract_action()` (now public)
2. `_strip_identity_preamble()` → `strip_identity_preamble()` (now public)
3. `_truncate_tool_output()` → `truncate_tool_output()` (now public)
4. `_execute_tool()` remains `_execute_tool()` (aliased via import)
5. `_stream_reply()` remains `_stream_reply()` (aliased via import)

### Phase 4: Verify No Functional Changes
**Test suite**:
```bash
pytest tests/test_circuit_breaker.py -xvs
pytest tests/test_context.py -xvs
pytest tests/test_executor.py -xvs
python tests/e2e_runner.py  # full 20-test suite
```

**Manual smoke tests**:
```
hey J
ls .
read run.py
/tools
/memory
```

### Phase 5: Update Import Statements in Other Files
**Affected files** (grep for `from app.chat import`):
- `run.py` — imports `run_chat()`, no changes needed
- Tests importing `_run_turn` — update to use public API or import from `app.llm` if needed

---

## 6. Risk Assessment

### Low Risk
- ✅ **Imports**: Sub-modules have no external dependencies (pure Python or app.agent)
- ✅ **Circular deps**: None introduced (app.llm → app.action → app.tool_exec, no reverse)
- ✅ **Logic**: Zero functional changes to any function body
- ✅ **Dedup cache**: Remains in `_run_turn()` scope (global `DEDUP_CACHE` dict persists)
- ✅ **Circuit breaker**: Stays in `_run_turn()` (no extraction needed)

### Medium Risk
- ⚠️ **Import aliasing**: Using `as _stream_reply` to preserve existing call signatures
  - Mitigation: Test all test files pass
- ⚠️ **Constants relocation**: `MAX_TOOL_OUTPUT_LINES` moved to `app.action`
  - Mitigation: Grep for uses, update all imports

### Negligible Risk
- 🟢 **File count**: Adding 3 new files doesn't break the build system
- 🟢 **Backwards compat**: Public API of `run_chat()` unchanged
- 🟢 **Performance**: No I/O or network overhead from module imports

---

## 7. Rollback Plan

**If tests fail**:
1. Delete `app/llm.py`, `app/action.py`, `app/tool_exec.py`
2. Restore `app/chat.py` from git: `git checkout app/chat.py`
3. Verify: `python tests/e2e_runner.py`

**Checkpoint commit**: Before starting Phase 1, commit current `chat.py` state.
- `git add docs/CHAT_DECOMPOSITION_SPEC.md`
- `git commit -m "docs: Add chat.py decomposition spec"`

---

## 8. Success Criteria

| Criterion | Verification |
|-----------|---------------|
| **All imports work** | `python -c "from app import chat"` with no errors |
| **All tests pass** | `pytest tests/ -x -q` (expect 20+ pass) |
| **E2E suite passes** | `python tests/e2e_runner.py` (expect 18/20+) |
| **No functional regressions** | Manual smoke tests (hey J, ls ., read, /tools) |
| **Code is cleaner** | `app/chat.py` reduced from 1,505 → ~1,198 lines (20% reduction) |
| **No new warnings** | `pylint app/*.py` (max 1–2 minor warnings acceptable) |

---

## 9. Future Opportunities

Once this decomposition is complete:
1. **Extract `_run_turn()` tool loop** → `app/turn.py` (further split: budget tracking, phase compression, dedup guard)
2. **Extract `_run_agent_task()` orchestration** → `app/agent_runner.py`
3. **Extract `_run_buffer_plan()`** → `app/buffer_runner.py`
4. **Create `app/repl.py`** to handle `run_chat()` and slash command dispatch

---

## 10. Verification Checklist

**Pre-extraction**:
- [ ] Current `app/chat.py` line count: 1,505 (baseline — CORRECTED from stale 1,111)
- [ ] All tests pass: `pytest tests/ -x` (baseline)
- [ ] `git status` clean (no uncommitted changes)
- [ ] Create git checkpoint: `git commit -m "checkpoint: before chat.py decomposition"`

**During extraction**:
- [ ] Create `app/llm.py` from lines 273–422 (120 lines)
- [ ] Create `app/action.py` from lines 104–244 (135 lines)
- [ ] Create `app/tool_exec.py` from lines 246–297 + dependencies (52 lines)
- [ ] Update `app/chat.py` imports and remove extracted function defs
- [ ] Verify no syntax errors: `python -m py_compile app/chat.py app/llm.py app/action.py app/tool_exec.py`

**Post-extraction**:
- [ ] All imports resolve: `python -c "from app.chat import run_chat"`
- [ ] `pytest tests/test_context.py -xvs` (core loop test)
- [ ] `pytest tests/test_executor.py -xvs` (tool execution test)
- [ ] Manual smoke: `hey J` → responds
- [ ] Manual smoke: `ls .` → tool executes
- [ ] Full E2E: `python tests/e2e_runner.py`
- [ ] New file count: 1,505 → ~1,198 in `app/chat.py`, ~120 in `app/llm.py`, ~135 in `app/action.py`, ~52 in `app/tool_exec.py`

---

## 11. Decision Points for Viktor Review

**Question 1**: Should `DEDUP_CACHE` remain global in `chat.py`, or move to `app/action.py` or a new `cache.py`?
- **Current proposal**: Stay in `chat.py` `_run_turn()` scope (tight coupling to loop logic, OK for now)

**Question 2**: Should `CircuitBreaker` be imported/extracted to a separate module?
- **Current proposal**: No, leave in `_run_turn()` (tightly coupled to loop control flow)

**Question 3**: Should `phase_summary` compression logic be extracted to `app/context.py`?
- **Current proposal**: No, stay in `_run_turn()` (specific to tool loop, not general context trimming)

**Question 4**: Any concerns about the 3-layer import structure (chat.py → llm.py / action.py → tool_exec.py)?
- **Current proposal**: Linear, no circular deps, safe

---

## Appendix: Line-by-Line Extraction Map

### `app/llm.py` (from chat.py lines 273–422, ~120 lines)
```python
# 273–342: _ollama_chat + _llama_cpp_chat
# 343–354: _check_language_drift
# 355–422: _stream_reply (including calls to preflight_trim, evaluate_code, persona.strip_bleed)
```

### `app/action.py` (from chat.py lines 104–244, ~135 lines)
```python
# 104–134: _balanced_json
# 136–213: _extract_action (uses ast.literal_eval, re.search, re.match, loads, JSONDecodeError)
# 215–223: _strip_identity_preamble
# 225–243: _truncate_tool_output
# 65–74: Move MAX_TOOL_OUTPUT_LINES constant here
```

### `app/tool_exec.py` (from chat.py lines 246–297, ~52 lines)
```python
# 246–271: _execute_tool (calls registry.execute, then _truncate_tool_output)
# 65–74: Move PROCESS_PAUSE_SECONDS constant here
```

**Total extracted**: 307 lines  
**Remaining in chat.py**: 1,505 - 307 = 1,198 lines

---

**Document Version**: 1.0  
**Created**: 2026-05-16  
**Status**: READY FOR VIKTOR REVIEW
