from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

HOST = "0.0.0.0"
PORT = 5000

DATA_FROM_DIR = BASE_DIR / "data_from_intersections"
DATA_TO_DIR = BASE_DIR / "data_to_front"