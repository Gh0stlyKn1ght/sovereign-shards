import sys


path = sys.argv[1]
data = sys.stdin.read()

with open(path, "w", encoding="utf-8") as handle:
    handle.write(data)

print(f"[WRITE OK] {path}")
