import os
import json
from pathlib import Path

def emergency_snapshot():
    # Force the path to your Windows Desktop
    desktop = Path(os.path.join(os.environ['USERPROFILE'], 'Desktop'))
    output_path = desktop / "shard_snapshot.json"
    
    data = {
        "status": "online",
        "location": "desktop",
        "note": "If you see this, the system can write files."
    }
    
    print(f"Targeting: {output_path}")
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        
        if output_path.exists():
            print(f"!!! CHECK YOUR DESKTOP FOR: shard_snapshot.json !!!")
        else:
            print("OS reported success, but file is not on Desktop.")
    except Exception as e:
        print(f"Write failed: {e}")

if __name__ == "__main__":
    emergency_snapshot()