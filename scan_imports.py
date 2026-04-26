import os

root = r"E:\dev shard\app"
imports = set()

for dirpath, _, filenames in os.walk(root):
    for f in filenames:
        if f.endswith(".py"):
            with open(os.path.join(dirpath, f), "r", errors="ignore") as file:
                for line in file:
                    line = line.strip()
                    if line.startswith("import ") or line.startswith("from "):
                        imports.add(line)

for i in sorted(imports):
    print(i)
