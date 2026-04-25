@echo off
setlocal
cd /d "%~dp0"
set "STAMP=%date% %time%"
echo [%STAMP%] Starting Sovereign Shard
"%~dp0python.exe" run.py %*
