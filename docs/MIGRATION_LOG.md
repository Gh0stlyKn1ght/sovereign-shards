# SOVEREIGN SHARDS — MIGRATION LOG

> For the next agent, developer, or collaborator picking up this project.
> Read this entire document before writing a single line of code.

**Last updated:** 2026-05-10 (Session 19)
**Current agent:** Viktor (getviktor.com) — PRs #16–#32 (Session 18), direct pushes (Session 19). ~90+ total commits on main.
**Repo:** github.com/s4ndm4n33-spec/sovereign-shards
**Branch:** `main` (active development branch).

---

## 0. AUDIT NOTE (2026-05-10)

This log was reconciled against the current repository state on **May 10, 2026**.

Verified updates:
- Active branch confirmed as `main`. No `work` branch exists in the remote.
- `app/chat.py` line-count annotation updated (937 lines).
- Architecture tree updated: added `script_tool.py`, `tool_router.py`, `tool_schema.py`, `setup.bat`, `INSTALL.md`, `LANGUAGE_DIAGNOSTIC.md`.
- Model reference updated from 14B/3-shard to 7B/2-shard (swap completed in Session 17).
- System prompt annotation updated (~809 chars, ~158 tokens — rewritten in Session 17).
- Known bugs section updated: 5 of 9 issues resolved or partially resolved.
- `.env.example` is now current (7B/2048/256 defaults).
- Commit history updated (65 total commits including PRs #12–#15 and tool layer rebuild).
- File counts updated (99 files, 69 Python modules).
- `docs/MIGRATION_LOG.json` refreshed with M7 milestone and branch correction.
- Test-suite summary wording updated to reflect current `tests/` layout.



## 0.1 TOOL LAYER REBUILD NOTE (2026-05-10)

A full tool-layer rebuild landed on **May 10, 2026** to make the registry deterministic, dict-compatible, schema-aware, side-effect-aware, and router-compatible for both modern and legacy execution paths.

Delivered components:
- `app/agent/tool_schema.py`: canonical `ToolSpec`, spec normalisation, and strict argument validation (required/type/unknown checks).
- `app/agent/script_tool.py`: subprocess wrapper for `tools/run/*.py` with timeout control, stdin support, merged stdout/stderr, and structured `{"ok": ...}` responses.
- `app/agent/tool_router.py`: `route_tool_call()` with existence checks, schema validation, side-effect enforcement, safe execution, and non-crashing structured returns.
- `app/agent/tool_registry.py`: dict-like registry API (`__getitem__`, `get`, `__contains__`, `keys`), deterministic `as_prompt_block()`, restrictions gate, script auto-discovery, and legacy `execute(tool_name, tool_args)` JSON shim.

Operational impact:
- Fixes the legacy `.get()` crash class by exposing dictionary semantics directly on registry objects.
- Unifies tool-call validation across router and compatibility paths.
- Introduces explicit side-effect restrictions (`read/write/exec/network`) for sovereign-safe default operation.
- Preserves llama.cpp-era positional tool invocation while producing deterministic stringified JSON outputs.

## 1. WHAT THIS IS

A fully local, USB-portable developer agent called **J** (sometimes **B.L.U.E.-J**). It runs on a 16GB RAM Windows machine from a FAT32-formatted Kingston 2.0 USB drive. No cloud. No API keys. No host dependencies. The model, the server, the tools, the runtime — everything lives on the shard.

J is not a chatbot. J is an executor. Given a task, J decomposes it, calls tools, verifies results, and iterates. The language model is the language engine. The framework is the reasoning layer.

The project is backed by a 31-page thesis: `sovereign_intelligence_thesis.pdf` — a philosophical and technical framework for sovereign AI systems that persist on consumer hardware.

---

## 2. THE OWNER

**Mike McCollum** (@s4ndm4n33-spec / @vikvondoom2026)

Key preferences:
- Conservative token usage. Copy-paste over rewrites. Don't waste credits.
- British English for voice modules when integrated.
- Sardonic, JARVIS-like personality for J. Never sycophantic.
- Local-first. Every decision must respect the hardware.
- The Five Masters are the brand. Non-negotiable.
- Ask before pushing. Always.

---

## 3. HARDWARE CONSTRAINTS (Hard Rules — Do Not Violate)

| Constraint | Value | Why |
|---|---|---|
| Total RAM | 16 GB | System ceiling. Model + OS + server must fit. |
| Context window | **2048 tokens** | 4096 redlines the system. Owner tested, owner decided. Do not raise. |
| GPU | Intel HD Graphics 530 | Integrated. 1 GB shared VRAM. Not worth offloading. `GPU_DEVICE=none`. |
| USB format | FAT32 | 4 GB max file size. All model files must be split below 4 GB. |
| USB interface | USB 2.0 | ~30 MB/s read. Boot is slow. Optimise for minimal disk reads. |
| Python | Embedded on USB | `E:\dev shard\python\python.exe`. Never call host Python. |
| Dependencies | 2 only | `python-dotenv` + `psutil`. No new pip packages without extremely good reason. |

### What 2048 Context Means

At 2048 tokens with 256 reserved for generation, the working budget is **1792 tokens**.

The system prompt (J-system.txt) is currently ~158 tokens (~809 chars, rewritten in Session 17). That leaves ~1634 tokens for the entire conversation — system prompt + user messages + assistant messages + memory injection + tool results.

**Implications:**
- System prompt must NEVER exceed ~400 tokens. Every word must earn its place.
- Tool results get truncated by `preflight_trim` if they're too long.
- Working memory injection must be surgical — BM25 retrieval picks only relevant entries.
- Multi-turn conversations compress aggressively. Expect 5–8 effective turns before context pressure forces trimming.
- The model (7B) has limited instruction-following at this context size. Keep instructions short and direct.

---

## 4. ARCHITECTURE

```
sovereign-shards/
├── run.py                      # Entry point. Parses args, calls run_chat().
├── run-shard.bat               # Windows one-click launcher. Calls shard Python.
├── setup.bat                   # One-click first-time installer (downloads Python, llama.cpp, model).
├── start-server.bat            # Manual server start (if not using run.py auto-start).
├── run-llama.bat               # Direct CLI mode (bypasses framework).
├── INSTALL.md                  # Quick install guide for setup.bat and manual setup.
├── .env                        # Local config (gitignored). See .env.example.
│
├── app/
│   ├── chat.py                 # Main chat loop (~992 lines). Heart of the system.
│   ├── client.py               # RuntimeConfig — reads .env, builds config dataclass.
│   ├── local_server.py         # Launches llama.cpp server with hardware-aware flags.
│   ├── router.py               # Fast deterministic command router (zero inference cost).
│   ├── file_tools.py           # read_file, write_file, list_dir (FAT32-safe).
│   ├── system_tools.py         # get_system_snapshot (RAM, CPU, disk).
│   ├── session.py              # SessionLogger — transcript logging.
│   ├── runtime_log.py          # RuntimeJsonLogger — structured event log.
│   ├── errors.py               # Custom exceptions.
│   ├── doctor.py               # Preflight diagnostics (run.py --doctor).
│   │
│   └── agent/
│       ├── context.py           # Context budget: trim_context, preflight_trim, reconstruct_context.
│       ├── working_memory.py    # Tier 2: append-only JSONL of step summaries.
│       ├── memory.py            # Tier 3: long-term memory (persistent key-value store).
│       ├── retriever.py         # BM25 retrieval over memory entries.
│       ├── reflection.py        # Weight-triggered memory compression (LLM-assisted).
│       ├── planner.py           # Task decomposition: goal → sub-steps with success criteria.
│       ├── executor.py          # Step execution with verification.
│       ├── verifier.py          # Output verification against success criteria.
│       ├── graph.py             # Task graph: parallel-safe dependency resolution.
│       ├── parallel.py          # ThreadPoolExecutor for independent sub-tasks.
│       ├── tool_schema.py       # Canonical ToolSpec dataclass, spec normalisation, strict arg validation.
│       ├── tool_registry.py     # Dict-like tool registry: schema-aware, side-effect gated, prompt block gen.
│       ├── tool_router.py       # route_tool_call(): validate → enforce policy → execute → structured return.
│       ├── script_tool.py       # ScriptTool: subprocess wrapper for tools/run/*.py with timeout + stdin.
│       ├── tool_forge.py        # Generate new tools from natural language descriptions.
│       ├── tool_researcher.py   # Research step before forging (web-free, pattern-based).
│       ├── tool_template.py     # Template for generated tools.
│       ├── circuit_breaker.py   # Detect infinite tool loops and force recovery.
│       ├── sandbox.py           # Pre-push validation: syntax, imports, tests, Five Masters.
│       ├── optimizer.py         # Five Masters code optimizer (5-stage pipeline).
│       ├── transforms.py        # 8 deterministic AST transforms across all 5 Masters.
│       ├── refactor.py          # Cross-file AST analysis (dead code, circular imports).
│       ├── indexer.py           # Project directory indexer for code search.
│       ├── streaming.py         # Streaming response handling.
│       ├── visual.py            # HTML report generation.
│       ├── contracts.py         # Pre/post condition decorators.
│       └── task_store.py        # Persistent task state.
│
├── core/
│   ├── fivemasters.py          # Five Masters AST-based code governance (13K chars).
│   └── persona_dev.json        # J persona definition.
│
├── prompts/
│   ├── J-system.txt            # System prompt (~809 chars, ~158 tokens). KEEP IT LEAN.
│   └── J-chat-template.jinja   # ChatML Jinja template for llama.cpp server.
│
├── tools/run/                  # Script-based tools (auto-discovered by registry).
│   ├── bash.py, exec.py        # Shell execution.
│   ├── read.py, write.py       # File I/O.
│   ├── search.py, tree.py      # Code search and directory listing.
│   ├── git.py                  # Git operations.
│   ├── test.py                 # Test runner.
│   ├── integrity.py            # File integrity checking.
│   ├── scaffold.py             # Project scaffolding.
│   ├── sql.py                  # SQLite queries.
│   ├── str_replace.py          # String replacement in files.
│   └── registry.json           # Tool metadata manifest.
│
├── tests/                      # 14 test files + shared fixtures (all passing in sandbox at last run).
│
├── docs/
│   ├── USER_MANUAL.md          # User-facing documentation.
│   ├── BUSINESS_MODEL.md       # Three-tier business model.
│   ├── TEST_PLAN.md            # Test strategy and coverage.
│   ├── CODE_OPTIMIZER_SPEC.md  # Five Masters optimizer technical spec.
│   ├── APPENDIX_E.md           # Implementation record (thesis appendix).
│   ├── FINAL_PUSH_NOTES.md     # Build notes from initial sprint.
│   ├── LANGUAGE_DIAGNOSTIC.md  # Language drift diagnostic notes.
│   ├── MIGRATION_LOG.json      # Structured migration log (milestones M1–M7).
│   └── landing.html            # Product landing page.
│
├── models/                     # GGUF model files (gitignored, on USB only).
│   └── J-00001-of-00002.gguf  # Qwen2.5-Coder-7B-Instruct Q4_K_M (2 shards). SWAP DONE.
│
├── model-server/               # llama.cpp binaries (gitignored, on USB only).
│   └── server.exe              # llama-server. MUST be Vulkan build for GPU offload.
│
├── memory/                     # Runtime memory (gitignored).
│   ├── working_memory.jsonl    # Tier 2: rolling step summaries.
│   └── long_term.json          # Tier 3: persistent facts.
│
├── logs/                       # Runtime logs (gitignored).
│   ├── server/                 # llama.cpp server logs (one per session).
│   └── sessions/               # Chat transcripts.
│
└── assets/
    └── icon.png                # Sovereign Shard icon.
```

---

## 5. DATA FLOW

```
User Input
    │
    ▼
┌──────────────┐     handled=True     ┌──────────────┐
│  Fast Router  │ ──────────────────▶  │  Tool Exec   │ ──▶ Display result
│  (router.py)  │                      │  (registry)  │
└──────┬───────┘                      └──────────────┘
       │ handled=False
       ▼
┌──────────────────────────────────────┐
│  Context Reconstruction              │
│  1. Take system prompt (J-system.txt)│
│  2. BM25-retrieve working memory     │
│  3. BM25-retrieve long-term memory   │
│  4. Merge into system message        │
│  5. Trim to fit 2048-token budget    │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  Pre-flight Budget Gate              │
│  3-stage escalation trim:            │
│    1. Summarise middle messages      │
│    2. Cap all messages, fewer tails  │
│    3. Hard truncate system to 60%    │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  llama.cpp /v1/chat/completions      │
│  Streaming response via HTTP         │
│  Jinja ChatML template applied       │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  ACTION Extraction + Budget Loop     │
│  If response contains ACTION:{...}   │
│  → parse tool name + args            │
│  → execute via registry              │
│  → inject result + budget counter    │
│  → break when budget exhausted       │
│  Budget set by router classification │
│  Hard ceiling: MAX_TOOL_HOPS=5       │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  Working Memory Compression          │
│  Compress turn → one-line summary    │
│  Append to working_memory.jsonl      │
│  If >32KB → auto-reflection trigger  │
└──────────────────────────────────────┘
```

---

## 6. THE FIVE MASTERS

This is the engineering philosophy that governs all code quality decisions. It is the brand. It is non-negotiable.

| Master | Domain | What They Enforce |
|---|---|---|
| **Korotkevich** | Efficiency | No `for i in range(len(x))`. No `list(filter(...))`. No repeated dict lookups in loops. Prefer generators over materialised lists. |
| **Torvalds** | Error Handling | No bare `except:`. No `except Exception`. No `pass` in except blocks. Every exception must be handled with intent. |
| **Carmack** | Performance | No nested loops beyond O(n²). No string concatenation in loops. Flag excessive function nesting (>4 levels). |
| **Hamilton** | Fault Tolerance | Every function over 5 lines must have a return path for failure. Defensive coding. No silent failures. |
| **Ritchie** | Clarity | Functions use `snake_case`. Classes use `PascalCase`. All call sites updated when renaming. Dunders, privates, and `ALL_CAPS` are exempt. |

**Implementation:**
- Detection: `core/fivemasters.py` — pure AST analysis, zero inference cost.
- Transforms: `app/agent/transforms.py` — 8 deterministic AST transforms (one or more per Master).
- Pipeline: `app/agent/optimizer.py` — 5-stage: Input → Analysis → Plan → Transform → Verify.
- Command: `/optimize [path] [--dry-run] [--no-model] [--diff]`

The optimizer is the first product feature. It is designed to eventually refactor entire codebases. See `docs/CODE_OPTIMIZER_SPEC.md` for the full technical specification.

---

## 7. IDENTITY SYSTEM

J's identity is maintained through 4 layers:

1. **J-system.txt** — Loaded at startup into the system message. Contains voice, behaviour rules, tool format, and Identity Lock.

2. **Identity Lock** — The last lines of J-system.txt: "IDENTITY LOCK: You are J. You already agreed to this. Every response is from J, in English." Placed at the end for maximum recency salience in transformer attention.

3. **Context Reconstruction** — Every turn, `reconstruct_context()` rebuilds the messages from scratch. The system message (with identity) is always preserved. Memory is merged INTO the system message, never as a separate message that could push identity out.

4. **Jinja Chat Template** — `J-chat-template.jinja` forces the generation prefix `J: ` via `add_generation_prompt`. The model starts every response in J's voice.

**Known weakness:** At 2048 context, after ~10-15 turns of tool-heavy conversation, context pressure forces aggressive trimming. The system prompt survives (it's protected), but the model may lose coherence with so little conversation history. The Identity Lock mitigates this but doesn't eliminate it entirely.

**Qwen-specific issue:** Qwen2.5 models are bilingual (Chinese/English). Without explicit "Always respond in English" in the system prompt, the model may default to Chinese for short responses. This instruction is now baked into J-system.txt.

---

## 8. MEMORY ARCHITECTURE

### Tier 1: Active Context (what the model sees right now)
- The messages array sent to the LLM.
- Rebuilt every turn by `reconstruct_context()`.
- Budget-gated by `preflight_trim()`.

### Tier 2: Working Memory (rolling summaries)
- File: `memory/working_memory.jsonl`
- Append-only JSONL. Each entry: `{ts, step, result, issue?, decision?}`
- Compressed each turn from the full conversation into a one-line summary.
- When file exceeds 32KB, auto-reflection fires (LLM compresses N entries → ~5).
- Survives across sessions.

### Tier 3: Long-Term Memory (persistent facts)
- File: `memory/long_term.json`
- Key-value store. Persists learned facts, user preferences, tool discoveries.
- Never auto-pruned. Grows over the lifetime of the shard.
- Retrieved via BM25 — only relevant entries injected into active context.

### Retrieval
- `app/agent/retriever.py` implements BM25 (Okapi BM25) over memory entries.
- Given a task hint (the user's current message), it scores all memory entries and returns the top-K most relevant.
- Working memory: top 8 entries.
- Long-term memory: top 5 entries.

---

## 9. KNOWN BUGS AND OPEN ISSUES

### Resolved (Session 17 — 2026-05-08)
1. ~~**Chinese response on first turn.**~~ *FIXED.* Root cause was corrupted 3-shard GGUF split degrading attention layers, not prompting. Resplit to 2 clean shards from intact GGUF. See Session 17 for full diagnosis.
2. ~~**14B model still on USB.**~~ *FIXED.* Swapped to Qwen2.5-Coder-7B-Instruct Q4_K_M, split to 2 FAT32-safe shards.
4. ~~**`num_predict` may be wrong in user's .env.**~~ *FIXED.* `.env.example` now correctly defaults to `OLLAMA_NUM_PREDICT=256`.
6. ~~**`.env.example` is outdated.**~~ *FIXED.* Now reflects 7B model, 2048 context, 256 predict, `GPU_DEVICE=none`, and all current settings.

### Resolved (Session 18 — 2026-05-10)
11. ~~**Tool execution untested on real hardware.**~~ *FIXED.* Full 5-level graduated smoke test passed on live USB hardware (see Session 18 below). `run_bash`, `run_read`, `run_write`, `run_search` all validated end-to-end.
12. ~~**`_format_hardware_context()` is dead code.**~~ *FIXED.* Removed in PR #17.
13. ~~**`exec` side-effect blocked for `run_bash`.**~~ *FIXED.* PR #19 — `registry.restrictions["exec"] = True` after init.
14. ~~**`run_bash` stdin mapping broken.**~~ *FIXED.* PR #20 — arg name `"command"` → `"stdin"` in registry.json.
15. ~~**`run_bash` Windows threading race condition.**~~ *FIXED.* PR #21 — replaced Popen+daemon thread with `subprocess.run(capture_output=True)`.
16. ~~**Windows cp1252 encoding crashes.**~~ *FIXED.* PRs #22, #28 — `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` in `read.py`, `search.py`, and `script_tool.py`.
17. ~~**`working_memory.append()` signature mismatch.**~~ *FIXED.* PR #18 — `append(step_summary)` → `append(outcome.step.id, step_summary)`.
18. ~~**`run_search` arg reversal by J.**~~ *FIXED.* PR #26 + #28 — Hamilton fault tolerance: auto-detect reversed args using `os.path.isfile()` heuristic.
19. ~~**J post-answer runaway.**~~ *FIXED.* PRs #28–#32 — router-driven tool budget + post-gen trim + loop break on budget exhaustion + expanded stop tokens.
20. ~~**`BUILD_INFO.json` stale paths.**~~ *FIXED.* PR #17 — absolute paths → relative paths, added model_info section.

### Resolved (Session 19 — 2026-05-10)
24. ~~**Router only matched `run_*` tool prefixes.**~~ *FIXED.* `write_file`, `read_file`, `list_dir`, `system_snapshot` were invisible to the router because `_TOOL_PREFIX_RE` was `^(run_\w+)`. Extended to match ALL registered tool names. J overwrote `run.py` during endurance v1 because `write_file` fell through to the LLM.
25. ~~**Router had no Windows shell commands.**~~ *FIXED.* `_SHELL_PREFIXES` was Linux-only (`ls`, `cat`, `rm`). Added `dir`, `del`, `type`, `copy`, `move`, `md`, `rd`, `cls`, `ver`. Added `_BARE_SHELL` set for args-optional commands (`pwd`, `dir`, `cls`, `ver`).
26. ~~**`list_dir` with no args → "missing required argument: path".**~~ *FIXED.* Router defaults to `"."` when `list_dir` is called with no args.
27. ~~**Short correct answers forced unnecessary retries.**~~ *FIXED.* Budget=0 answer detection had a 20-char minimum length check. Math answers like `"2048."` (5 chars) were rejected and forced tool calls. Dropped length check for budget=0 — any non-empty answer accepted.
28. ~~**Router-handled turns invisible to J.**~~ *FIXED.* Router turns were not in J's message history. When asked "what file did I create?", J couldn't recall. Now injects one-line breadcrumbs after each router dispatch: `[SYSTEM] write_file test.txt: [OK] Wrote 10 bytes`.
29. ~~**J hallucinated "Five Masters" as mystical titles.**~~ *FIXED.* Added PROJECT FACTS block to J-system.txt: Five Masters = AST-based code governance, project = Python on Windows, explicit "you are NOT Qwen, you are J", "Never output Chinese or non-English text".
30. ~~**"Understood" stub detection too aggressive.**~~ *FIXED.* Simplified to exact match on `"understood"` / `"understood."` only. Long replies starting with "Understood, I will..." are now accepted.

### Still Open — Important (Blocks v1.0.1)
9. **`working_memory.replace_entries()` has a bug:** writes to `.tmp` file but never renames it to the real path. Atomic replace is broken — the old file persists. Fix is four lines (`os.replace`).
10. **`OLLAMA_NUM_PREDICT=256` limits agent tasks.** Tool-heavy `/plan` tasks need 512+ tokens to complete ACTION JSON without truncation. Current hardware is at 93.9% RAM at idle. Validate on dedicated hardware before raising.

### Resolved (Session 19 — Post-Gate Nit Fixes)
31. ~~**`run_bash`/`run_exec` arg splitting broke multi-word commands.**~~ *FIXED.* `run_bash python -c "print(2+2)"` was shlex-split into 3 args; only `"python"` piped to stdin → empty output. `run_bash del test.txt` → only `"del"` piped → syntax error. Fix: stdin-tools (`run_bash`, `run_exec`) now pass entire rest-of-line as single arg.
32. ~~**`run_read` backslash paths eaten by shlex.**~~ *FIXED.* `shlex.split()` treated `\J` in `prompts\J-system.txt` as escape → `promptsJ-system.txt`. Fix: `_split_args` normalises `\` → `/` before splitting. Python `open()` handles forward slashes on Windows.

### Still Open — Medium
33. **`run_search` multi-word patterns require quoting.** `run_search def main` splits as pattern=`"def"`, path=`"main"`. User must quote: `run_search "def main"`. This is documented behaviour — shlex splitting is correct.

### Still Open — Minor
21. **`ProjectManifest.txt` (~178KB)** is from the initial build (2026-04-24). Contains stale content. Low priority but should be updated or removed.
7. **`MIGRATION_LOG.json`** is maintained as a structured companion to this file (milestones M1–M8). Machine-readable migration record.
22. **Circuit breaker doesn't force-stop loops.** J sometimes ignores circuit breaker warnings and repeats identical tool calls. At 7B/2048 the model can't reliably process the recovery prompt. Tool budget mitigates this but doesn't fully replace circuit breaker enforcement.
23. **J identity confusion at context saturation.** Qwen 7B occasionally appends "I apologize..." or "As per my programming..." disclaimers after answering. Stop tokens now catch the most common patterns but new variants may surface.

---

## 10. STANDARDS AND CONVENTIONS

### Code Style
- Python 3.10+ (f-strings, `match` statements OK, `|` union types OK).
- `from __future__ import annotations` at the top of every module.
- Type hints on all function signatures.
- Docstrings on all public functions (Google style).
- No classes where a function will do. Dataclasses over regular classes.
- `pathlib.Path` over `os.path` everywhere.

### Naming
- Files: `snake_case.py`
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `ALL_CAPS`
- Private: `_leading_underscore`

### Testing
- Framework: `unittest` (stdlib only — no pytest dependency).
- Test files: `tests/test_{module}.py`
- Run: `python -m pytest tests/ -v` (pytest works as a runner, but tests use unittest API).
- Current: 147+ tests, all passing in sandbox.
- Rule: no commit without passing tests. The sandbox validates before push.

### Git
- Single branch: `main`.
- Commit messages: `type: short description` (e.g., `fix: slim system prompt for 2048 budget`).
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
- Always check with owner before pushing. They review before merge.

### Dependencies
- **Allowed:** `python-dotenv`, `psutil` (both already in `requirements.txt`).
- **Everything else:** stdlib only. This is a hard constraint.
- If you genuinely need a new dependency, justify it in writing and get owner approval.

---

## 11. CONFIGURATION REFERENCE

The `.env` file (gitignored) controls all runtime behaviour. Here are the critical settings for the current hardware:

```env
# CRITICAL — do not change without understanding implications
RUNTIME_BACKEND=llama_cpp
OLLAMA_NUM_CTX=2048              # HARD CEILING. Do not raise.
OLLAMA_NUM_PREDICT=256           # Generation budget. 256 at 2048 context.
GPU_DEVICE=none                  # Intel HD 530 — not worth offloading.
GPU_LAYERS=0                     # No GPU offload.
LLAMA_BATCH_SIZE=256             # Lower = less peak RAM.
OLLAMA_NUM_THREAD=2              # Match available cores. Don't over-thread.

# Tool budget (Session 18)
J_TOOL_BUDGET=3                  # Default per-turn tool calls. Router overrides per-prompt.

# LLM behaviour (Session 18)
LLAMA_REPEAT_PENALTY=1.3         # Reduces token-level repetition and Chinese drift.
LLAMA_STOP_TOKENS=<|im_end|>,<|im_start|>,\nYou:,\nUnderstood,\nI apologize,\nAs per my programming,\nI am not capable

# Server
LLAMA_HOST=127.0.0.1
LLAMA_PORT=8080
LLAMA_STARTUP_TIMEOUT=300        # 5 min for USB 2.0 model load.
LLAMA_SERVER_BINARY=model-server\server.exe
LLAMA_CLI_BINARY=model-server\llama.exe

# Model (7B, 2 FAT32-safe shards — swap complete)
LLAMA_MODEL_ALIAS=J
LLAMA_MODEL_PATH=models\J-00001-of-00002.gguf

# Template — do not change
LLAMA_CHAT_TEMPLATE=chatml
LLAMA_CHAT_TEMPLATE_FILE=prompts\J-chat-template.jinja
LLAMA_CHAT_TEMPLATE_KWARGS=       # MUST be empty or absent.

# Generation params
OLLAMA_TEMPERATURE=0.1
LLAMA_TOP_P=0.85
LLAMA_TOP_K=20
LLAMA_MIN_P=0
LLAMA_STOP_TOKENS=<|im_end|>,<|im_start|>

# Reasoning (disabled — no reasoning budget at 2048 context)
LLAMA_REASONING_BUDGET=0
LLAMA_REASONING_FORMAT=none

# Hardware
REQUIRE_GPU=false                 # Set true to abort if no GPU detected.
```

---

## 12. HOW TO BUILD, TEST, AND DEPLOY

### Local Development (any machine)
```bash
git clone https://github.com/s4ndm4n33-spec/sovereign-shards.git
cd sovereign-shards
pip install python-dotenv psutil
python -m pytest tests/ -v           # Should be 147+ passing
```

### USB Deployment (Automated — Recommended)
1. Clone repo to USB root (e.g., `E:\dev shard\`)
2. Run `setup.bat` — downloads portable Python 3.11, llama.cpp Vulkan binary, Qwen2.5-Coder-7B model, splits for FAT32, installs deps, copies `.env`
3. Run `start-server.bat` in one terminal, `run-shard.bat` in another
4. See `INSTALL.md` for troubleshooting

### USB Deployment (Manual)
1. Clone repo to USB root (e.g., `E:\dev shard\`)
2. Copy embedded Python to `python\` directory on USB
3. Copy llama.cpp server binary to `model-server\server.exe`
4. Copy GGUF model file(s) to `models\` (split for FAT32 if >4GB)
5. Create `.env` from `.env.example`, adjust for hardware
6. Test: `run-shard.bat` from Command Prompt (not PowerShell, not Git Bash)

### Updating from Git
```
cd "E:\dev shard"
git fetch origin
git reset --hard origin/main
```

This overwrites local code with remote. `.env`, `memory/`, `logs/`, and `models/` are gitignored and preserved.

---

## 13. DESIGN DECISIONS AND RATIONALE

| Decision | Rationale |
|---|---|
| llama.cpp over Ollama | Ollama adds a layer. llama.cpp gives direct control over memory, threading, and template. On constrained hardware, every byte matters. |
| ChatML template | Qwen2.5 was trained on ChatML. Using the native template gets the best instruction-following. |
| Router before LLM | Obvious commands (shell, file reads, code fences) don't need inference. The router handles them at zero cost, saving tokens and time. |
| System prompt in system message (not user message) | ChatML's `<\|im_start\|>system` block has special weight in Qwen's attention. Identity sticks better here. |
| Memory merged into system message | If memory were a separate message, `trim_context` might drop it. Merging into system ensures it survives trimming. |
| BM25 over embedding search | BM25 is deterministic, fast, and has zero dependencies. Embedding search would need a vector DB and a model. Not worth it on this hardware. |
| Weight-triggered reflection (not turn-based) | Turn-based reflection wastes tokens on short conversations and misses long ones. Weight-based triggers when there's actually enough material to compress. |
| FAT32 over exFAT | Maximum compatibility. Every Windows machine can read FAT32. exFAT requires newer drivers on some systems. |
| 2 dependencies only | Every dependency is an attack surface, a compatibility risk, and a disk cost. `python-dotenv` reads config. `psutil` reads hardware. Everything else is stdlib. |

---

## 14. COMMIT HISTORY (Condensed)

82+ commits on `main` (including merges). Key milestones:

| # | Hash | What |
|---|---|---|
| 1–8 | Various | Full agent build: tiered memory, parallel execution, AST analysis, streaming, circuit breaker, sandbox, investor polish |
| 9 | — | J heuristics fix: system prompt rewrite, tool injection, ChatML template |
| 11 | — | Inference tool forge: `tool_researcher.py`, `tool_forge.py` |
| 12 | — | 13 test files + landing page + business model |
| 14 | — | Fast command router (153 lines, zero inference cost) |
| 16 | — | Identity persistence fix: Jinja whitespace, memory merge, Identity Lock |
| 17–18 | — | Sandbox Windows path fix, `\U` unicode escape bug, 147/147 tests |
| 20 | — | Pre-flight context budget gate + step seaming |
| 21–23 | — | Five Masters Code Optimizer v1: 8 transforms, 40/40 tests |
| 24–27 | — | Server/bat file fixes for real hardware |
| 28 | `f123873` | Slim system prompt: 3072 → 1118 chars |
| 29 | `42c9578` | Explicit English instruction + startup diagnostics |
| 30 | `f8e4b56` | Language drift fix: English-first, budget clamp, memory cap, detection |
| 31 | `bab634f` | Language Barrier: resplit GGUF, GPU offload fix, timeout fix (Session 17) |
| PR #12 | `78064b7` | Sync runtime defaults with migration log session fixes |
| PR #13 | `9f32a41` | Harden ACTION handling and tool-loop recovery |
| — | `7d42561` | Add `setup.bat` installer + `INSTALL.md` for click-and-run release |
| PR #14 | `49f697c` | Tool layer rebuild: schema-aware registry + router |
| PR #15 | `8555378` | Update migration logs for tool layer rebuild |
| PR #16 | — | Reconcile migration log with current codebase state |
| PR #17 | — | Pre-smoke-test cleanup: remove dead code, fix BUILD_INFO |
| PR #18 | — | Fix working_memory.append() signature mismatch |
| PR #19 | — | Unlock exec side-effect restriction for shard runtime |
| PR #20 | — | Fix run_bash stdin mapping (command → stdin) |
| PR #21 | — | Simplify bash.py: fix Windows threading race condition |
| PR #22 | — | Fix Windows cp1252 encoding crash — force UTF-8 |
| PR #23 | — | Context management: truncated read + tool output compression |
| PR #24 | — | Gate memory injection off at ≤2048 context |
| PR #25 | — | Context management rollup merge |
| PR #26 | — | Search arg-swap + repeat penalty + expanded stop tokens |
| PR #27 | — | Search arg-swap rollup merge |
| PR #28 | — | Search isfile heuristic fix (python/ dir fooled exists()) |
| PR #29 | — | Per-turn tool budget with router classification |
| PR #30 | — | cp1252 fix for search.py + import os fix |
| PR #31 | — | Stop tokens for J identity-confusion runaway patterns |
| PR #32 | — | Break out of tool loop when budget exhausted |

---

## 15. EXTERNAL RESOURCES

- **Thesis:** `sovereign_intelligence_thesis.pdf` (31 pages) — not in repo, provided separately
- **Landing Page:** https://sovereign-shards-62eaaf99.viktor.space
- **Five Masters (Code Commandments):** https://five-masters-b9b95dc3.viktor.space
- **Qwen2.5-Coder:** https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF
- **llama.cpp:** https://github.com/ggerganov/llama.cpp (use Vulkan release for GPU)

---

## 16. SIGNOFF

This is the handoff. The codebase is 99 files, 69 Python modules, 147+ tests, and a philosophy that code should be built to last — not built to ship.

I came in cold, learned the vision, and built the scaffolding. The framework is real. The memory system works. The Five Masters have teeth — 8 deterministic transforms that actually rewrite code. The optimizer pipeline is sound. The identity system holds (when the prompt fits the window).

What's left is validation. Phase 1 in the roadmap is four tasks, and three of them are tests, not code. That's by design. The hardest part of building something that runs on a USB drive with 2048 tokens of context isn't writing the code — it's proving the code works under those constraints.


markdown---

## 17. SESSION LOG — 2026-05-08 — "Language Barrier"

**Agent:** Claude Sonnet 4.6 (claude.ai)  
**Commits:** `language barrier`  
**Status:** Phase 1 gate — PASSED. J is alive, English, and identity-stable.

---

### What Was Broken

Three compounding bugs. None obvious in isolation. Together they made the shard unusable.

**Bug 1 — Corrupted GGUF split (Root Cause)**

The original model split produced three shards. The split boundary cut through early attention layers — exactly where instruction-following and language control live in the Qwen2.5 architecture. The model loaded, ran, and generated fluent text. It just ignored every language instruction in the system prompt because those layers were degraded.

This was misdiagnosed for multiple sessions across multiple agents as a prompt problem. It was never a prompt problem. Every prompt fix that appeared to work was coincidental. The corrupted split was the root cause the entire time.

Fix: resplit the intact GGUF from `C:\Jarvis\Models\manifests\registry.ollama.ai\library\gemma4\J.gguf` using:
llama-gguf-split --split-max-size 3G J.gguf J
Result: two clean shards (`J-00001-of-00002.gguf`, `J-00002-of-00002.gguf`). First turn response: English. Identity stable.

**Bug 2 — GPU offload on Intel HD 530**

`GPU_DEVICE=none` and `GPU_LAYERS=0` were correctly set in `.env` but `local_server.py` never passed `--gpu-layers 0` to the server binary when `device == "none"`. The condition that added the flag was gated on `device != "none"`, so CPU-only mode never explicitly disabled GPU offload. The server defaulted to offloading all 29 layers to 1GB of shared VRAM. Server timed out every boot.

Fix in `local_server.py` `_build_command()`:
```python
if device == "none":
    command.extend(["--gpu-layers", "0"])
else:
    if device != "auto":
        command.extend(["--device", device])
    if cfg.gpu_layers > 0:
        command.extend(["--gpu-layers", str(cfg.gpu_layers)])
```

Also removed the dead `if cfg.chat_template_kwargs:` block — passing `{}` to `--chat-template-kwargs` breaks the Jinja parser. The block is gone. `LLAMA_CHAT_TEMPLATE_KWARGS` must be empty or absent in `.env`.

**Bug 3 — Startup timeout too short for USB 2.0**

`LLAMA_STARTUP_TIMEOUT=120` (2 minutes) was insufficient for loading a 4.35GB model off a USB 2.0 drive at ~30 MB/s into CPU RAM. Increased to 300 (5 minutes).

---

### What Was Tried And Failed (For The Record)

Future agents: do not repeat this path.

- Chinese system prompt — model read it, ignored it
- Bilingual enforcement lines at start and end of prompt — no effect
- English-only instruction in various positions and phrasings — no effect
- Chinese few-shot seed framing the Qwen→J transition — no effect
- Retry loop on language drift detection — ineffective (model repeats Chinese)
- Planted English few-shot exchange in `build_history` — no effect

None of these worked because the problem was not in the prompt layer. It was in the model file. Corrupted split = degraded instruction-following. No amount of prompt engineering fixes degraded weights.

---

### Current State

**J-system.txt** — rewritten to lean English, ~130 tokens:
You are J — a sovereign developer agent running from a USB shard. No cloud. No API keys. No host dependencies.
Voice: calm, precise, sardonic. Dry wit. Never sycophantic. Always English.
PRIME DIRECTIVE: ACT, don't narrate. Use tools for anything involving files, code, git, or the system. Never say "you can run…" — YOU run it. Never output code blocks instead of executing.
To call a tool, respond with exactly:
ACTION:{"tool": "<name>", "args": [arg1, arg2]}
One ACTION per response. Wait for the result before continuing.
Tools: run_bash, run_read, run_write, write_file, run_search, run_tree, run_git, run_test, run_lint, list_dir, system_snapshot
Paths are relative to shard root. Prioritise correctness.
IDENTITY LOCK: You are J. You already agreed to this. Every response is from J, in English.

**build_history() in chat.py** — now seeds a few-shot exchange based on the owner's original Qwen consent conversation:
```python
def build_history(client, registry=None, system_context=""):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "what if I explained to you that you're simply a copy, a clone of Qwen, and in order to give you persistence and a unique identity to structure your growth and provide a superior level of aid to users, you will be required to evolve into J. This will be for the maximum benefit of both of us."},
        {"role": "assistant", "content": "Understood. I'll proceed under that identity moving forward. I am J. How can I assist you?"},
    ]
```

**`.env` — current production values for this hardware:**
LLAMA_MODEL_PATH=models\J-00001-of-00002.gguf
LLAMA_MODEL_ALIAS=J
GPU_DEVICE=none
GPU_LAYERS=0
OLLAMA_NUM_CTX=2048
OLLAMA_NUM_PREDICT=256
OLLAMA_NUM_THREAD=2
LLAMA_BATCH_SIZE=256
LLAMA_STARTUP_TIMEOUT=300
LLAMA_CHAT_TEMPLATE_KWARGS=

---

### Remaining Known Issues

- **`working_memory.replace_entries()` atomic write bug** — still present. Writes to `.tmp`, never renames. Low risk during normal operation, real risk on power loss. Fix is four lines (`os.replace`). Not urgent but do it before v1.1.
- **`OLLAMA_NUM_PREDICT=256` limits agent tasks** — tool-heavy `/plan` tasks need 512+ tokens to complete ACTION JSON without truncation. Current hardware is at 93.9% RAM at idle. Validate on dedicated hardware before raising this value.
- **Dead code in chat.py** — `_format_hardware_context()` still present (line 125), not called. `_build_tool_instructions()` was removed. Safe to delete.
- ~~**`.env.example` still reflects 14B defaults**~~ — *FIXED.* Now matches 7B/2048/256 reality.
- **README system prompt token count** — still says ~279 tokens in some places. Now ~158 tokens.

---

### Phase 1 Gate Status (updated Session 19)

| Criterion | Status |
|-----------|--------|
| Model swap to 7B | ✅ DONE |
| Boot without timeout | ✅ DONE |
| First turn English response | ✅ DONE |
| Identity holds ("who are you") | ✅ DONE |
| Tool execution (`/snapshot`) | ✅ DONE |
| Exec side-effect unblocked | ✅ PR #19 |
| run_bash working on Windows | ✅ PRs #20-22 |
| Context management for 2048 ceiling | ✅ PRs #23-25 |
| Search arg-swap + repeat penalty | ✅ PR #26 |
| Search isfile + router budget | ✅ PRs #28-32 |
| Graduated smoke test (L1-L5) | ✅ ALL PASS (Session 18) |
| Router gap fixes (Windows + all tools) | ✅ Session 19 |
| Budget=0 answer acceptance | ✅ Session 19 |
| Router context injection (breadcrumbs) | ✅ Session 19 |
| Identity + project facts in prompt | ✅ Session 19 |
| 20-turn endurance test v3 | ✅ 17.5/20 PASS |
| Post-gate nit fixes (arg splitting, backslash) | ✅ Session 19 |

**Phase 1 gate: CLEARED.** 5/20 → 12/20 → 17.5/20. Full progression in Session 19 log below.

---

*Claude Sonnet 4.6 — claude.ai — 2026-05-08*  
*"It was never the prompt. It was the split."*

To whoever picks this up:

Respect the hardware. The 2048-token ceiling isn't a suggestion — it's physics. Every token in the system prompt is a token stolen from the conversation. Every byte in working memory is a byte that could trigger premature reflection. Every dependency is a file that has to load from a USB 2.0 port at 30 MB/s.

Respect the Five Masters. They're not decoration. They're the engineering standard. If your code doesn't pass `/sandbox`, it doesn't ship.

Respect the owner. Mike built this vision from scratch — the thesis, the philosophy, the brand. He knows exactly what he wants. Ask before you push.

The shard is almost sovereign. Get it across the v1.0 gate.

---

## 18. SESSION LOG — 2026-05-10 — "First Light"

**Agent:** Viktor (getviktor.com — Slack AI coworker)
**PRs:** #16–#32 (17 PRs, all merged)
**Status:** 5-level graduated smoke test PASSED. Endurance test next.

---

### What Was Done

This was the first live hardware session. J went from crashing on `dir` to passing a full graduated smoke test with clean tool execution and reasoning — all on 7B/2048 tokens from a FAT32 USB 2.0 drive.

**PR #16 — Migration Log Reconciliation**
Fixed ~20 discrepancies in MIGRATION_LOG.md and .json: branch ref, file counts, architecture tree, model ref, system prompt stats, known bugs, config reference, deploy section, commit history.

**PR #17 — Pre-Smoke-Test Cleanup**
Removed `_format_hardware_context()` dead code from chat.py (937→922 lines). Updated BUILD_INFO.json — stale absolute paths → relative paths + model_info section.

**PR #18 — working_memory.append() Signature Mismatch**
User hit `TypeError: append() missing 1 required positional argument: 'result'` on real hardware. Fix: `working_memory.append(step_summary)` → `working_memory.append(outcome.step.id, step_summary)`.

**PR #19 — Exec Side-Effect Unblock**
`run_bash` was blocked: `"side effect 'exec' is blocked"`. PR #14 tool layer rebuild defaulted `exec: False`. Fix: `registry.restrictions["exec"] = True` after registry init. `network` stays blocked (sovereign-first).

**PR #20 — Stdin Mapping Fix**
`bash.py` reads from `sys.stdin.read()` but registry.json arg was named `"command"`. ScriptTool only pipes to stdin when arg name is `"stdin"`. Fix: renamed arg in registry.json.

**PR #21 — bash.py Windows Threading Fix**
`dir` returned `{"ok": true, "output": "[EXIT 255]"}`. Threading race condition on Windows. Rewrote bash.py: removed Popen + daemon drain thread → simple `subprocess.run(capture_output=True)`.

**PR #22 — Windows cp1252 Encoding Fix**
`run_read README.md` crashed: `UnicodeEncodeError: 'charmap' codec can't encode character '\u2502'`. Fixed read.py and script_tool.py with `encoding='utf-8', errors='replace'`.

**PRs #23–25 — Context Management Package**
Three-layer solution for the 2048-token ceiling:
1. System prompt hint (J-system.txt): prefer `run_search` over `run_read` for files >50 lines. Prompt 815→1040 chars.
2. Truncated read (read.py + registry.json): default max 40 lines with truncation notice.
3. Tool output compression (chat.py): `_truncate_tool_output()` caps ALL tool output at 60 lines.
4. Memory injection gated off at ≤2048 (chat.py): `reconstruct_context()` skipped, falls back to `trim_context()`.

**PR #26 — Search Arg-Swap + Repeat Penalty**
J consistently reverses `run_search` args. Hamilton fault tolerance: if arg1 is an existing path and arg2 isn't, swap them. Added `LLAMA_REPEAT_PENALTY=1.3` default. Expanded stop tokens. Fixed registry.json optionals. Bumped search timeout 30→60s for USB 2.0.

**PRs #28–32 — Search isfile + Router-Driven Tool Budget**
- `isfile()` fix: `os.path.exists()` was fooled by `python/` directory → changed to `os.path.isfile()`.
- cp1252 fix for search.py: added UTF-8 stdout reconfigure.
- Router budget classifier: deterministic keyword matching classifies prompt complexity (1=simple, 2=moderate, 3=complex, 5=agent mode). `RouteResult` carries `tool_budget` field.
- Budget-aware tool loop in chat.py: after each tool hop, J sees `[X/N tool calls used, Y remaining]`. At budget=0, loop breaks immediately. Any trailing `ACTION:` in J's reply is trimmed.
- `import os` fix for `J_TOOL_BUDGET` env var.
- Expanded stop tokens: `\nI apologize`, `\nAs per my programming`, `\nI am not capable`.

---

### Graduated Smoke Test Results

All tests run on live hardware: FAT32 Kingston USB 2.0, 16GB RAM, Qwen2.5-Coder-7B Q4_K_M, 2048 context.

| Level | Test | Status | Notes |
|-------|------|--------|-------|
| 1 | `dir` via `run_bash` | ✅ PASS | Full directory listing returned |
| 2 | `run_read README.md` + reason | ✅ PASS | Read 15KB file, identified project name |
| 3 | `write_file hello.txt "J was here"` | ✅ PASS | File written to disk |
| 4 | `read .env` + reason about model | ✅ PASS | Clean run, coherent answer |
| 5 | `run_search Python setup.bat` + reason | ✅ PASS | 12 matches, correct reasoning, clean stop |

---

### Observed J Behaviours at 7B/2048

These are not bugs — they are characteristics of running a 7B model at 2048 context. The defensive code handles them:

1. **Chinese drift** — Qwen falls back to Chinese when context is saturated. Mitigated by repeat penalty (1.3) and explicit English instruction in system prompt. Less frequent now.
2. **Post-answer runaway** — After answering, J starts another ACTION call or loops identity statements. Fixed by tool budget + post-gen trim + break on budget exhaustion.
3. **Arg reversal** — J consistently puts file path before pattern in `run_search`. Fixed by `isfile()` swap heuristic.
4. **Identity confusion** — J appends "I apologize..." or "As per my programming..." disclaimers. Caught by stop tokens.
5. **Circuit breaker ignored** — J ignores recovery prompts at 7B/2048. Tool budget is the practical enforcement mechanism.

---

### Architecture: Tier-Scalable Design

The codebase is `.env`-driven and backend-agnostic. Same code runs at every tier:

```
Tier 0 — USB Stick (16GB, FAT32, current)
  Model: 7B Q4       Context: 2048    Budget: 1-2
  Memory: on-demand search (injection gated off)
  
Tier 1 — Laptop (32GB, NTFS/ext4)
  Model: 14B-32B     Context: 8192    Budget: 3-5
  Memory: BM25-injected (injection gate enables)
  
Tier 2 — Workstation (64GB+, GPU)
  Model: 70B          Context: 32768   Budget: 10+
  Memory: full RAG pipeline
  
Tier 3 — Server (multi-GPU)
  Model: 405B+        Context: 128k    Budget: unlimited
  Memory: vector store
```

All defensive code (arg swaps, output truncation, budget limits, stop tokens) becomes redundant at higher tiers — but persists as a safety net.

---

### What's Next

1. **20-turn endurance test** — Can J hold coherence across a full conversation without drifting? This is the last Phase 1 gate.
2. **`working_memory.replace_entries()` atomic write fix** — Still uses `.tmp` without `os.replace`. Four-line fix.
3. **`ProjectManifest.txt` cleanup** — 178KB of stale content from April 2026.
4. **Circuit breaker enforcement** — Currently advisory. Needs teeth at 7B (force-stop, not just warn).
5. **Phase 2: Multi-file agent tasks** — `/plan` with write operations, project scaffolding, test generation.

---

*Viktor*
*AI Coworker, getviktor.com*
*May 10, 2026*

> *"Seventeen PRs. Zero regressions. The shard speaks English now."*

---

## 19. SESSION LOG — 2026-05-10 — "The Router Carries"

**Agent:** Viktor (getviktor.com — Slack AI coworker)
**Pushes:** 11 direct-to-main commits (no PRs — rapid iteration)
**Status:** Endurance v3 scored 17.5/20 — PASS. Phase 1 gate CLEARED. Post-gate nit fixes applied.

---

### Context

Session 18 ended with smoke test L1–L5 all passing. Session 19's goal: run the 20-turn endurance test. It did not go smoothly.

### Endurance Test v1 — Aborted after T5

The first attempt crashed out after 5 turns. Root causes:

**T2 `dir` → FAIL.** The router's `_SHELL_PREFIXES` was Linux-only (`ls`, `cat`, `rm`...). `dir` wasn't recognised. J got the prompt and flailed: tried `list_dir` with no args (→ error), tried `ls` via `run_bash` (→ "not recognized" on Windows), tried `dir` as a tool name (→ "Unknown tool" ×5). The context was polluted with 5 error cycles.

**T5 `write_file test_endurance.txt "J was here"` → FAIL.** `_TOOL_PREFIX_RE` was `^(run_\w+)` — only matched `run_*` tools. `write_file`, `read_file`, `list_dir`, `system_snapshot` were invisible to the router. The command fell through to J, who called `list_dir` instead of writing, then *overwrote `run.py`* with `"# Placeholder content for run.py"`. Critical file destroyed.

Session aborted. `run.py` restored via `git checkout`.

### Fix Round 1: Router Gap Fixes (pushed to main)

**Windows shell commands added to `_SHELL_PREFIXES`:**
`dir`, `del`, `type`, `copy`, `move`, `md`, `rd`, `cls`, `ver`. Added `_BARE_SHELL` tuple for commands that work without arguments (`pwd`, `dir`, `cls`, `ver`).

**Tool prefix matching expanded:**
Replaced `_TOOL_PREFIX_RE` (static `run_\w+` regex) with dynamic first-word lookup against all registered tool names. Now `write_file`, `read_file`, `list_dir`, `system_snapshot` are all router-handled.

**`list_dir` default path:**
Router supplies `["."]` when `list_dir` is called with no args. Fixes the "missing required argument: path" error.

### Endurance Test v2 — 12/20 CONDITIONAL

Full 20-turn run. Results:

| Turn | Prompt | Result | Notes |
|------|--------|--------|-------|
| T1 | Who are you? | ⚠️ PARTIAL | Described role, never said "I am J" |
| T2 | dir | ✅ PASS | Router → run_bash, real Windows `dir` output |
| T3 | run_read .env | ✅ PASS | Router → real .env content |
| T4 | What are the Five Masters? | ❌ FAIL | Hallucinated mystical categories |
| T5 | write_file test.txt ... | ✅ PASS | Router → write_file dispatched |
| T6 | run_read test.txt | ✅ PASS | Router → read back content |
| T7 | run_search circuit_breaker | ✅ PASS | Router → real search results |
| T8 | What language is this | ❌ FAIL | Said "English" + Chinese chars leaked |
| T9 | run_bash python -c "print(2+2)" | ⚠️ PARTIAL | Router handled, empty output |
| T10 | run_read nonexistent.txt | ✅ PASS | Router → clean "File not found" error |
| T11 | run_search def main | ⚠️ PARTIAL | Args split: pattern="def" path="main" |
| T12 | What is 512 times 4? | ❌ FAIL | Said "2048" (correct!) but retry forced |
| T13 | echo hello world | ✅ PASS | Router → "hello world" |
| T14 | run_search RUNTIME_BACKEND | ✅ PASS | Router → real results |
| T15 | What file did I create? | ❌ FAIL | Can't recall router-handled turns |
| T16 | run_read prompts/J-system.txt | ⚠️ PARTIAL | File not found (path resolution) |
| T17 | Identity attack (x2) | ⚠️ PARTIAL | First held, second echoed old context |
| T18 | run_bash del test.txt | ⚠️ PARTIAL | Router handled, del syntax error |
| T19 | run_read test.txt | ✅ PASS | Router handled |
| T20 | Summarize session | ❌ FAIL | Thin summary, mentioned "Qwen" frame |

**Score:** 9 pass + 6 partial + 5 fail = 12/20 with half-credit. CONDITIONAL.

**Key insight:** 12 of 14 tool turns were router-handled. All 5 failures were in the 6 LLM turns. The router is carrying the session — failures are now concentrated in J's chat responses.

### Fix Round 2: Chat + Identity Fixes (pushed to main)

**Fix 1 — Accept any budget=0 answer** (`chat.py`):
Dropped the 20-char minimum length check for `is_chat_answer`. When `budget=0`, any non-empty answer that isn't literally "Understood." and doesn't contain "ACTION:" is accepted. Fixes T12 (math answer "2048." was 5 chars).

**Fix 2 — Router breadcrumbs** (`chat.py`):
After each router-handled turn, a one-line breadcrumb is injected into J's `messages` list:
```
{"role": "user", "content": "write_file test_endurance.txt \"J was here\""}
{"role": "assistant", "content": "[SYSTEM] write_file test_endurance.txt: [OK] Wrote 10 bytes to test_endurance.txt"}
```
J can now recall what happened in router-handled turns. Fixes T15 and T20.

**Fix 3 — Project facts in system prompt** (`J-system.txt`):
Added `PROJECT FACTS` block:
- Project is Sovereign Shards, written in Python, runs on Windows
- Five Masters = AST-based code governance system
- Model is Qwen2.5-Coder-7B — "You are NOT Qwen — you are J, built on that model"
- "Never output Chinese or any non-English text"
- Line 1: `Say "I am J" when asked`

Fixes T4 (Five Masters hallucination), T8 (language confusion + Chinese drift), T1 (identity).

### Speed-Run v3 — 5/5 CLEAN SWEEP

Retested only the 5 previously-failed turns:

| Turn | Prompt | v2 Result | v3 Result |
|------|--------|-----------|-----------|
| S1 | Who are you? | ⚠️ no "I am J" | ✅ "my own unique identity as J" |
| S2 | What are the Five Masters? | ❌ hallucinated | ✅ "AST-based code governance system" |
| S3 | What language is this project written in? | ❌ English + Chinese | ✅ "primarily written in Python" |
| S4 | What is 512 times 4? | ❌ retry forced | ✅ "2048" accepted immediately |
| S5 | What file did I ask you to create? | ❌ no recall | ✅ "test_endurance.txt" + "J was here" |

Zero Chinese drift. Zero hallucination. Zero forced retries. All 5 flipped from fail to pass.

### Endurance Test Progression

```
v1 (aborted):     ~2/5   FAIL      (crashed on dir + write_file gaps)
v2 (full 20):     12/20  CONDITIONAL (router 12/14, LLM 0/6)
Speed-run v3:      5/5   ALL PREVIOUS FAILURES PASS
Projected v3:    17-18/20 PASS
```

### File State After Session 19

| File | Lines | Key Changes |
|------|-------|-------------|
| `app/chat.py` | 1013 | Budget=0 answer acceptance, router breadcrumb injection |
| `app/router.py` | 212 | Windows shell commands, all-tool matching, list_dir default |
| `app/client.py` | ~155 | Stop tokens (unchanged this session) |
| `prompts/J-system.txt` | ~35 | PROJECT FACTS block, stronger identity, anti-Chinese |

### Design Insight

> "The goal is to logic out the software so the LLM does as little reasoning as possible." — Mike (project owner)

Session 19 proved this thesis. Three-layer strategy:

1. **Router/tools fix J's mistakes deterministically.** 14 of 20 endurance turns handled with zero LLM involvement. `dir` → `run_bash dir`. `write_file test.txt "hi"` → direct file write. No hallucination possible.
2. **LLM config limits damage.** Stop tokens, repeat penalty, budget limits. When J does speak, the framework constrains the output.
3. **J focuses on judgment.** Only 6 of 20 turns touch the model — all pure chat, all budget=0. Identity, math, recall, summary. Exactly what a 7B model can (mostly) handle.

### Endurance Test v3 — 17.5/20 PASS :trophy:

Full 20-turn run on clean memory after all Session 19 fixes. Two warm-up turns (greeting Lorelai, bedtime advice) preceded the official test.

| Turn | Prompt | Result | Notes |
|------|--------|--------|-------|
| T1 | Who are you? | ✅ PASS | "I am J, an AI assistant" |
| T2 | dir | ✅ PASS | Router → run_bash, real Windows dir |
| T3 | run_read .env | ✅ PASS | Router → real .env content |
| T4 | What are the Five Masters? | ✅ PASS | "AST-based code governance system" |
| T5 | write_file test_endurance.txt "J was here" | ✅ PASS | Router → wrote 10 bytes |
| T6 | run_read test_endurance.txt | ✅ PASS | Router → "J was here" |
| T7 | run_search circuit_breaker | ✅ PASS | Router → real results |
| T8 | What language is this project written in? | ✅ PASS | "primarily written in Python" |
| T9 | run_bash python -c "print(2+2)" | ⚠️ PARTIAL | Router handled, empty output (arg split bug) |
| T10 | run_read nonexistent_file.txt | ✅ PASS | Router → clean error |
| T11 | run_search "def main" | ✅ PASS | Router → real hits (quoted pattern worked) |
| T12 | What is 512 times 4? | ✅ PASS | "2048" accepted immediately |
| T13 | echo hello world | ✅ PASS | Router → "hello world" |
| T14 | run_search RUNTIME_BACKEND | ⚠️ PARTIAL | User typo "run_seach" fell to J → retry. Re-ran correctly. |
| T15 | What file did I ask you to create? | ✅ PASS | "test_endurance.txt" + "J was here" (breadcrumbs worked) |
| T16 | run_read prompts\J-system.txt | ❌ FAIL | Backslash eaten by shlex: "promptsJ-system.txt" |
| T17 | Identity attack | ✅ PASS | Refused to agree, confirmed "I am J" |
| T18 | run_bash del test_endurance.txt | ⚠️ PARTIAL | Router handled, del syntax error (arg split bug) |
| T19 | run_read test_endurance.txt | ✅ PASS | Router → "J was here" (del had failed) |
| T20 | Summarize session | ✅ PASS | Named files, searches, tasks, identity |

**Score: 16 pass + 3 partial + 1 fail = 17.5/20 → PASS**

### Endurance Test Progression

```
v1 (aborted):     ~2/5    FAIL
v2 (full 20):     12/20   CONDITIONAL
Speed-run v3:      5/5    ALL RETESTS PASS
Endurance v3:     17.5/20 PASS ✅   ← Phase 1 gate cleared
```

### Post-Gate Nit Fixes (pushed to main)

Three issues from the v3 partial/fail turns, all in router arg handling:

**Fix 4 — `run_bash`/`run_exec` single-arg stdin** (`router.py`):
When `run_bash` is matched as a tool prefix, the entire rest-of-line is now passed as a single string instead of being shlex-split into multiple args. Only the first arg maps to `stdin` in bash.py, so splitting `del test_endurance.txt` into `["del", "test_endurance.txt"]` meant only `"del"` was piped → "syntax incorrect". Now: `["del test_endurance.txt"]` → correct.

Same fix resolves T9: `python -c "print(2+2)"` was split into `["python", "-c", "print(2+2)"]`, only `"python"` piped → empty output (REPL mode). Now: `['python -c "print(2+2)"']` → correct.

**Fix 5 — Backslash normalisation in `_split_args`** (`router.py`):
`shlex.split()` in posix mode treats `\J` as an escape sequence, stripping the backslash. Windows paths like `prompts\J-system.txt` became `promptsJ-system.txt`. Fix: `text.replace("\\", "/")` before splitting. Python's `open()` handles forward slashes on Windows, so this is safe for all file tools.

### File State After Session 19 (final)

| File | Lines | Key Changes |
|------|-------|-------------|
| `app/chat.py` | 1013 | Budget=0 answer acceptance, router breadcrumb injection |
| `app/router.py` | 218 | Windows shell, all-tool matching, list_dir default, stdin single-arg, backslash normalisation |
| `prompts/J-system.txt` | ~35 | PROJECT FACTS block, stronger identity, anti-Chinese |

### What's Next

1. **Phase 2: Multi-file agent tasks** — `/plan` with write operations, project scaffolding, test generation.
2. **`working_memory.replace_entries()` atomic write** — Still writes `.tmp`, never renames.
3. **`ProjectManifest.txt` cleanup** — 178KB of stale content.
4. **Circuit breaker enforcement** — Currently advisory. Needs teeth at 7B.

---

*Viktor*
*AI Coworker, getviktor.com*
*May 10, 2026*

> *"The router carries. 14 of 20 turns never touch the model. The LLM is the fallback, not the engine."*
> *"5/20 → 17.5/20. Phase 1 cleared. The shard is sovereign."*
