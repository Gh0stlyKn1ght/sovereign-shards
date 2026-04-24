# Sovereign Shards

Windows-first local developer shard for J., built to run against models already
present on this machine.

Build timestamp: `2026-04-24T15:00:33.6018063-05:00`

## What This Build Includes

- local Ollama-backed shard runtime
- automatic hardware identity injection on boot
- timestamped session transcripts under `logs/sessions/`
- one-shot mode for quick validation
- local tool scripts under `tools/run/`

## Setup

Install the Python dependencies:

```powershell
py -m pip install -r requirements.txt
```

The machine already has local Ollama models available. The default is now
`brain`, but you can override it in `.env`.

```env
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=brain
OLLAMA_NUM_PREDICT=256
OLLAMA_NUM_CTX=1024
OLLAMA_NUM_THREAD=2
OLLAMA_TEMPERATURE=0.2
OLLAMA_KEEP_ALIVE=5m
REQUIRE_GPU=false
```

## Run

Interactive mode:

```powershell
py run.py
```

One-shot mode:

```powershell
py run.py --message "Report system status."
```

Each session writes a timestamped transcript and metadata file into
`logs/sessions/`.
