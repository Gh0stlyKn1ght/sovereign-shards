"""Git operations wrapper. Safe subset of git commands.

Usage: python git.py <subcommand> [args...]
Allowed: status, diff, log, add, commit, branch, checkout, stash, show, reset.
"""

import subprocess
import sys

ALLOWED = {
    "status", "diff", "log", "add", "commit", "branch", "checkout",
    "stash", "show", "reset", "rev-parse", "remote",
}
MAX_OUTPUT = 64 * 1024


def main() -> None:
    if len(sys.argv) < 2:
        print(f"[GIT ERROR] Usage: git.py <subcommand> [args...]\n"
              f"Allowed: {', '.join(sorted(ALLOWED))}")
        return

    subcommand = sys.argv[1]
    if subcommand not in ALLOWED:
        print(f"[GIT ERROR] Subcommand '{subcommand}' not allowed.\n"
              f"Allowed: {', '.join(sorted(ALLOWED))}")
        return

    cmd = ["git", subcommand] + sys.argv[2:]

    try:
        result = subprocess.run(
            cmd, text=True, capture_output=True, timeout=30,
        )
    except subprocess.TimeoutExpired:
        print(f"[GIT ERROR] Timed out: {' '.join(cmd)}")
        return
    except FileNotFoundError:
        print("[GIT ERROR] git is not installed or not on PATH.")
        return

    output = (result.stdout or "") + (result.stderr or "")
    output = output.strip()
    if len(output) > MAX_OUTPUT:
        output = output[:MAX_OUTPUT] + "\n... [TRUNCATED]"

    if output:
        print(output)
    elif result.returncode == 0:
        print(f"[GIT OK] {' '.join(cmd)}")
    else:
        print(f"[GIT ERROR] exit code {result.returncode}")


if __name__ == "__main__":
    main()
