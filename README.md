# Sovereign Shards — J

**A fully local developer agent that runs from a USB stick.**

J is a self-contained AI coding assistant built to operate on a 16 GB FAT32 Kingston USB 2.0 drive. No cloud. No API keys. No internet required. Plug in, launch, and build software.

## What It Does

J is a *developer agent* — not a chatbot. It reads files, writes code, runs tests, manages git, and plans multi-step tasks with dependency graphs. It uses a local GGUF language model as its brain and a structured tool loop (plan → execute → verify) to complete real engineering work.

```
You  ─→  J  ─→  Plan steps  ─→  Execute tools  ─→  Verify results
              ↕                 ↕                   ↕
         Working Memory     Tool Registry       Task Checkpoint
```

## Quick Start

```bash
# 1. Plug in the USB drive (e.g. E:\)
# 2. Navigate to the shard
cd "E:\sovereign-shards"

# 3. Preflight check
python run.py --doctor

# 4. Launch
python run.py
```

That's it. J starts the local model server, loads the GGUF brain, and drops you into an interactive session. See [docs/USER_MANUAL.md](docs/USER_MANUAL.md) for the full production guide.

## Architecture

| Layer | What | Files |
|-------|------|-------|
| **Runtime** | Dual-backend streaming (llama.cpp + Ollama), local server lifecycle, hardware identity | `app/client.py`, `app/local_server.py`, `app/system_tools.py` |
| **Brain** | Plan → Execute → Verify agent loop with DAG task graphs | `app/agent/planner.py`, `app/agent/executor.py`, `app/agent/verifier.py`, `app/agent/graph.py` |
| **Memory** | 3-tier active context reconstruction with BM25 retrieval | `app/agent/context.py`, `app/agent/working_memory.py`, `app/agent/memory.py`, `app/agent/retriever.py` |
| **Tools** | 10 auto-discovered dev tools (file, shell, git, search, test) | `tools/run/*.py`, `app/agent/tool_registry.py` |
| **Governance** | Five Masters code quality heuristics, sandbox mode | `core/fivemasters.py`, `app/chat.py` |
| **Logging** | Structured JSONL runtime logs, session transcripts, rotation | `app/runtime_log.py`, `app/session.py` |
| **Contracts** | Typed dataclasses, autonomy modes, error taxonomy | `app/agent/contracts.py`, `app/errors.py` |

## Hardware Requirements

| Spec | Minimum | Recommended |
|------|---------|-------------|
| Drive | 16 GB USB 2.0, FAT32 | Same |
| RAM | 8 GB | 16 GB |
| CPU | 4 cores | 8+ cores |
| GPU | Not required | Any with 6+ GB VRAM (optional) |
| OS | Windows 10+ | Windows 10/11 |
| Python | 3.10+ | 3.12+ |

## Dependencies

```
python-dotenv
psutil
```

That's it. Two packages. Everything else is stdlib.

## Project Stats

```
29 Python files  ·  3,089 lines  ·  2 dependencies  ·  zero network calls
```

## License

See repository for license terms.
