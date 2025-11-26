# data/incoming_data.py
import json
from datetime import datetime
from pathlib import Path
from config import DATA_FROM_DIR

# Convert to normal string path for Windows
BASE = Path(str(DATA_FROM_DIR))
BASE.mkdir(parents=True, exist_ok=True)

FILE_PATH = BASE / "events.jsonl"


def save_incoming(data: dict):
    entry = {"timestamp": datetime.utcnow().isoformat(), **data}
    with FILE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
