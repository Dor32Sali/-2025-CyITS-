# data/outgoing_data.py
import json
from datetime import datetime
from pathlib import Path
from config import DATA_TO_DIR

BASE = Path(str(DATA_TO_DIR))

BASE.mkdir(parents=True, exist_ok=True)  # ✅ correct

FILE_PATH = BASE / "events.jsonl"


def save_outgoing(data: dict):
    entry = {"timestamp": datetime.utcnow().isoformat(), **data}
    with FILE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
