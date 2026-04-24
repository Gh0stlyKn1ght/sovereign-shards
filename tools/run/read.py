import os
import sys


path = sys.argv[1]
if os.path.exists(path):
    with open(path, encoding="utf-8") as handle:
        print(handle.read())
else:
    print(f"[READ ERROR] File not found: {path}")
