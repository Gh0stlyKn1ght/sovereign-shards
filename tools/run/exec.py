import subprocess
import sys


code = sys.stdin.read()

try:
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")
except Exception as error:
    print(f"[EXEC ERROR] {error}")
