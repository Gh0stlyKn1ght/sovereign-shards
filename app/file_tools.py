from pathlib import Path

BASE = Path.cwd()

def read_file(path: str) -> str:
    p = BASE / path
    if not p.exists():
        return f"[ERROR] File not found: {path}"
    return p.read_text(encoding="utf-8", errors="ignore")

def write_file(path: str, content: str) -> str:
    p = BASE / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"[OK] Wrote {len(content)} bytes to {path}"

def list_dir(path: str) -> str:
    p = BASE / path
    if not p.exists():
        return f"[ERROR] Directory not found: {path}"
    return "\n".join(str(x.name) for x in p.iterdir())
