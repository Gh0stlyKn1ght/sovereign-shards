# Sovereign Shards

Windows-first local developer shard for J., built to run as a standalone folder
from `E:\dev shard`.

Build timestamp: `2026-04-24T15:00:33.6018063-05:00`
Standalone runtime timestamp: `2026-04-24T19:20:01.0890088-05:00`

## What This Build Includes

- shard-local `python.exe`
- shard-local `llama.exe` and `server.exe`
- local `brain.gguf` model path inside `models/`
- automatic `llama.cpp` server boot from Python
- automatic hardware identity injection on boot
- timestamped session transcripts under `logs/sessions/`
- one-shot mode for quick validation
- local tool scripts under `tools/run/`

## Setup

Install the Python dependencies:

```powershell
py -m pip install -r requirements.txt
```

The default runtime is now local `llama.cpp` from inside this shard.

```env
RUNTIME_BACKEND=llama_cpp
LLAMA_HOST=127.0.0.1
LLAMA_PORT=8080
LLAMA_MODEL_ALIAS=brain
LLAMA_MODEL_PATH=models\brain.gguf
LLAMA_SERVER_BINARY=model-server\server.exe
LLAMA_CLI_BINARY=model-server\llama.exe
LLAMA_STARTUP_TIMEOUT=120
OLLAMA_NUM_PREDICT=256
OLLAMA_NUM_CTX=1024
OLLAMA_NUM_THREAD=2
OLLAMA_TEMPERATURE=0.2
REQUIRE_GPU=false
```

## Run

Interactive mode:

```powershell
.\python.exe run.py
```

One-shot mode:

```powershell
.\python.exe run.py --message "Report system status."
```

Show the exact local runtime paths:

```powershell
.\python.exe run.py --paths
```

Start the local server manually:

```powershell
.\start-server.bat
```

Run the local CLI manually:

```powershell
.\run-llama.bat
```

Each session writes a timestamped transcript and metadata file into `logs/sessions/`.
