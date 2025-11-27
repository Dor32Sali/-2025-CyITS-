import json
from datetime import datetime
from pathlib import Path
import os 
from typing import Dict, Any, List
import csv # Core library for CSV manipulation

# --- Configuration (Local Directory) ---
# We use Path(os.getcwd()) to find the current directory, then create a subdirectory for output.
BASE = Path(os.getcwd()) / "data_output"
BASE.mkdir(parents=True, exist_ok=True)

# The file that holds the complete, latest JSON payload (overwritten every time)
JSON_FILE_PATH = BASE / "latest_event.json" 

# --- CSV Output File Paths (Ensuring all paths are correctly defined) ---
CAMERA_CSV_FILE = BASE / "test_camera.csv"
RCU_CSV_FILE = BASE / "test_rcu.csv"
LOOP_CSV_FILE = BASE / "test_loop.csv"


def _append_row(path: Path, row: dict):
    """Append a single row to CSV, create file with header if needed."""
    
    file_exists = path.exists()
    
    # Ensure all dictionary keys are strings (Timestamp objects have already been converted in process_and_split)
    stringified_row = {str(k): v for k, v in row.items()}
    
    with path.open("a", newline="", encoding="utf-8") as f:
        # Use the row keys for fieldnames, ensuring consistency
        # NOTE: fieldnames must be calculated on every call because sensor data columns might shift slightly
        writer = csv.DictWriter(f, fieldnames=stringified_row.keys())
        
        if not file_exists:
            writer.writeheader()
        
        try:
            writer.writerow(stringified_row)
        except ValueError as e:
            # This happens if a row has keys the header didn't expect (which shouldn't happen here)
            print(f"ERROR writing CSV row: Missing field names or data mismatch for {path.name}. Error: {e}")


def _process_and_split_to_csv(event: dict):
    """
    Takes the raw event dict (the JSON from the intersection) and appends rows 
    to separate sensor-specific CSV files (test_camera.csv, test_rcu.csv, test_loop.csv).
    """

    # Extract top-level metadata
    timestamp = event.get("timestamp")
    intersection_id = event.get("intersection_id")
    block_id = event.get("block_id")

    # The actual sensor readings dictionary
    sensors = event.get("sensor_readings", {})

    # Helper function to prepare row and convert Timestamp to string (if needed)
    def prepare_row(sensor_data):
        row = {
            "timestamp": timestamp,
            "intersection_id": intersection_id,
            "block_id": block_id,
            **sensor_data
        }
        # Ensure Timestamp objects are converted to strings if they somehow survived serialization earlier
        if 'Timestamp' in row and not isinstance(row['Timestamp'], (str, int, float)):
             row['Timestamp'] = row['Timestamp'].isoformat()
        return row

    # --- CAMERA ---
    cam = sensors.get("CAMERA_DATA") 
    if cam:
        cam_row = prepare_row(cam)
        _append_row(CAMERA_CSV_FILE, cam_row) 

    # --- RCU ---
    rcu = sensors.get("RCU_DATA") 
    if rcu:
        rcu_row = prepare_row(rcu)
        _append_row(RCU_CSV_FILE, rcu_row) 

    # --- LOOP ---
    loop = sensors.get("LOOP_DATA") 
    if loop:
        loop_row = prepare_row(loop)
        _append_row(LOOP_CSV_FILE, loop_row) 


def save_incoming(data: dict):
    """
    Deletes the old master JSON file, writes the new complete payload, 
    and splits the sensor data into separate, continuous CSV log files.
    """
    
    # 1. Prepare the full entry dictionary (includes timestamp_received)
    entry = {"timestamp_received": datetime.utcnow().isoformat(), **data}
    
    # --- JSON LOGGING (OVERWRITE) ---
    try:
        # Explicitly delete the old master JSON file
        if JSON_FILE_PATH.exists():
            os.remove(JSON_FILE_PATH)
        
        # Write the new, complete payload
        with JSON_FILE_PATH.open("w", encoding="utf-8") as f:
            f.write(json.dumps(entry, indent=4))
            
    except Exception as e:
        print(f"ERROR: Could not perform file operation on JSON file ({JSON_FILE_PATH}). {e}")
        # Continue to CSV logging even if JSON fails

    # --- CSV LOGGING (SPLIT AND APPEND) ---
    try:
        # Call the integrated function to process the event and append to CSV files
        _process_and_split_to_csv(entry)
    except Exception as e:
        print(f"CSV conversion failed: {e}")