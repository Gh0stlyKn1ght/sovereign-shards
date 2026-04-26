@echo off
cd /d "%~dp0"

.\model-server\llama-server.exe ^
  --model "models\J.gguf" ^
  --ctx-size 2048 ^
  --temperature 0.7 ^
  --top-p 0.9 ^
  --repeat-penalty 1.1
