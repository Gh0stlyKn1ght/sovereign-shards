"""Sandboxed shell command execution with timeout and output cap.

Usage: echo '<command>' | python bash.py [timeout_seconds]
Default timeout: 30s. Max output: 64 KB.
"""

import subprocess
import sys

MAX_OUTPUT = 64 * 1024  # 64 KB output cap
DEFAULT_TIMEOUT = 30


def main() -> None:
    command = sys.stdin.read().strip()
    if not command:
        print("[BASH ERROR] No command provided on stdin.")
        return

    timeout = DEFAULT_TIMEOUT
    if len(sys.argv) > 1:
        try:
            timeout = int(sys.argv[1])
        except ValueError:
            pass

    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"[BASH ERROR] Command timed out after {timeout}s: {command[:120]}")
        return
    except Exception as exc:
        print(f"[BASH ERROR] {exc}")
        return

    output = (result.stdout or "") + (result.stderr or "")
    output = output.strip()

    if len(output) > MAX_OUTPUT:
        output = output[:MAX_OUTPUT] + f"\n... [TRUNCATED at {MAX_OUTPUT} bytes]"

    if output:
        print(output)
    if result.returncode != 0:
        print(f"[exit code {result.returncode}]")
    elif not output:
        print("[BASH OK] Command completed with no output.")


if __name__ == "__main__":
    main()
