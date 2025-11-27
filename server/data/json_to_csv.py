# data/json_to_csv.py

import csv
from pathlib import Path

# Use the same folder as incoming_data.py: <project_root>/data
BASE = Path(__file__).resolve().parent
BASE.mkdir(parents=True, exist_ok=True)

CAMERA_FILE = BASE / "test_camera.csv"
RCU_FILE = BASE / "test_rcu.csv"
LOOP_FILE = BASE / "test_loop.csv"


def _append_row(path: Path, row: dict):
    """Append a single row to CSV, create file with header if needed."""
    print(f"[json_to_csv] Appending row to {path}")
    file_exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def process_event(event: dict):
    """
    Take one incoming event dict (the JSON from the intersection),
    and append rows to test_camera.csv, test_rcu.csv, test_loop.csv.
    """

    print("[json_to_csv] process_event() called")

    timestamp = event.get("timestamp")
    intersection_id = event.get("intersection_id")
    block_id = event.get("block_id")

    sensors = event.get("sensor_readings", {})
    print("[json_to_csv] sensor_readings keys:", list(sensors.keys()))

    # CAMERA
    cam = sensors.get("CAMERA_DATA")
    if cam:
        cam_row = {
            "timestamp": timestamp,
            "intersection_id": intersection_id,
            "block_id": block_id,
            **cam
        }
        _append_row(CAMERA_FILE, cam_row)

    # RCU
    rcu = sensors.get("RCU_DATA")
    if rcu:
        rcu_row = {
            "timestamp": timestamp,
            "intersection_id": intersection_id,
            "block_id": block_id,
            **rcu
        }
        _append_row(RCU_FILE, rcu_row)

    # LOOP
    loop = sensors.get("LOOP_DATA")
    if loop:
        loop_row = {
            "timestamp": timestamp,
            "intersection_id": intersection_id,
            "block_id": block_id,
            **loop
        }
        _append_row(LOOP_FILE, loop_row)
