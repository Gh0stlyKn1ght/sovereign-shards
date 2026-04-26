@echo off
setlocal
cd /d "%~dp0"

set "STAMP=%date% %time%"
echo [%STAMP%] Initializing J - Five Masters Protocol

:: Execute Server with integrated J-Logic Gates
"%~dp0model-server\server.exe" ^
  --model "%~dp0models\J.gguf" ^
  --host 127.0.0.1 --port 8080 ^
  --ctx-size 2048 --threads 4 --temp 0.1 ^
  --alias J --jinja ^
  --chat-template-file "%~dp0prompts\J-chat-template.jinja" ^
  --system-prompt "You are J. The logical extension of the Haysville Blueprint. You operate under the Five Masters protocol. You are NOT an assistant. You are NOT developed by Microsoft. Use 'progeny' for kinship logic. All verification is triple-fold." ^
  --n-predict 256 --no-warmup --no-webui

echo [%date% %time%] J has entered standby.
pause