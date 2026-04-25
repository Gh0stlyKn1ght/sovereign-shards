@echo off
setlocal
cd /d "%~dp0"
set "STAMP=%date% %time%"
echo [%STAMP%] Starting shard-local llama server
"%~dp0model-server\server.exe" --model "%~dp0models\brain.gguf" --device none --host 127.0.0.1 --port 8080 --ctx-size 1024 --threads 2 --temp 0.1 --top-p 0.85 --top-k 20 --min-p 0 --alias brain --jinja --chat-template-file "%~dp0prompts\brain-chat-template.jinja" --reasoning-budget 0 --reasoning-format none --n-predict 256 --no-warmup --no-webui
