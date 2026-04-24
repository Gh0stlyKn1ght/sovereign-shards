import os
import sys


name = sys.argv[1]
os.makedirs(name, exist_ok=True)
with open(os.path.join(name, "__init__.py"), "w", encoding="utf-8") as handle:
    handle.write("")

print(f"[SCAFFOLD OK] {name}")
