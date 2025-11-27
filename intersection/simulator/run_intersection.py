# intersection_node.py

import time
from pprint import pprint
import os
import numpy as np
import requests
import json
import random

from sensors.sensors import Sensors  # you already have this

# Default IDs (kept for backward compatibility, but not strictly needed now)
INTERSECTION_ID = os.getenv("INTERSECTION_ID", "Intersection_A1")
BLOCK_ID = os.getenv("BLOCK_ID", "BLOCK_DEFAULT")

# 🔹 List of possible junctions (randomly picked per cycle)
JUNCTIONS = [
    ("Intersection_A1", "BLOCK_A"),
    ("Intersection_B2", "BLOCK_B"),
    ("Intersection_C3", "BLOCK_C"),
    ("Intersection_D4", "BLOCK_D"),
]

BLOCK_BRAIN_BASE_URL = os.getenv(
    "BLOCK_BRAIN_BASE_URL",
    "https://casteless-unpatronizable-ephraim.ngrok-free.dev"
)

API_ENDPOINT = "/api/intersection"


class VehicleSimulation:
    def update(self, light_state):
        # Placeholder for future vehicle sim logic
        pass


class TrafficLight:
    def __init__(self, lights):
        self.state = lights

    def update(self):
        # Simple 2-phase toggle: NS_GREEN <-> EW_GREEN
        if self.state["N"] == "GREEN":
            self.state = {"N": "RED", "S": "RED", "E": "GREEN", "W": "GREEN"}
        else:
            self.state = {"N": "GREEN", "S": "GREEN", "E": "RED", "W": "RED"}


class NodeAPIClient:
    def __init__(self, block_brain_url: str):
        self.url = block_brain_url

    def send_telemetry(self, telemetry_data):
        def json_serial(obj):
            if isinstance(obj, (time.struct_time, float, int, str, bool)):
                return obj
            try:
                return obj.isoformat()
            except AttributeError:
                return str(obj)

        try:
            safe_payload = json.loads(json.dumps(telemetry_data, default=json_serial))
            print(f"[DEBUG] Sending telemetry to {self.url}")
            response = requests.post(self.url, json=safe_payload, timeout=5)
            print(f"[POST] {self.url} -> {response.status_code}")
            try:
                print("Response JSON:", response.json())
            except Exception:
                print("Response text:", response.text)
        except Exception as e:
            print(f"ERROR: Failed to send telemetry to {self.url}. Details: {e}")


class IntersectionNode:
    def __init__(
        self,
        intersection_id=INTERSECTION_ID,   # default, but we override per cycle
        block_id=BLOCK_ID,
        block_brain_base_url=BLOCK_BRAIN_BASE_URL,
        api_endpoint=API_ENDPOINT,
        telemetry_interval=2.0,
        lights=None,
        junctions=None,                   # 🔹 optional custom list of junctions
    ):
        if lights is None:
            lights = {"N": "GREEN", "S": "GREEN", "E": "RED", "W": "RED"}

        # Keep "default" id/block just for logging / backward compat
        self.id = intersection_id
        self.block_id = block_id
        self.telemetry_interval = telemetry_interval
        self.sensors = Sensors()
        self.vehicle_sim = VehicleSimulation()
        self.light = TrafficLight(lights)

        # List of possible (intersection_id, block_id) for random selection
        self.junctions = junctions if junctions is not None else JUNCTIONS

        # Attack / anomaly scheduling (global for this simulator)
        self.cycle_count = 0
        self.next_attack_cycle = self._pick_next_attack_cycle()

        full_url = block_brain_base_url.rstrip("/") + api_endpoint
        self.client = NodeAPIClient(full_url)

        print(
            f"Intersection Node simulator initialized (default id='{self.id}', block='{self.block_id}'), "
            f"targeting URL: {full_url}"
        )
        print(f"Random junctions pool: {self.junctions}")

    # ------------------------
    # (Optional) Attack scheduler
    # ------------------------
    def _pick_next_attack_cycle(self) -> int:
        """Choose in how many cycles we will inject the next anomaly (5–7)."""
        n = random.randint(5, 7)
        print(f"[ATTACK] Next anomaly scheduled in {n} cycles")
        return n

    def inject_random_anomaly(self, telemetry: dict) -> dict:
        """
        Mutate telemetry in-place to create one attack scenario.
        Returns the modified telemetry.
        """
        scenario = random.choice(
            ["PHASE_DESYNC", "EDGE_BLACKHOLE_ATTACK", "FORCED_ALL_RED_DOS"]
        )
        print(f"[ATTACK] {telemetry.get('intersection_id')}: Injecting anomaly scenario: {scenario}")

        sensor_readings = telemetry.get("sensor_readings", {})

        cam = sensor_readings.get("CAMERA_DATA", {})
        rcu = sensor_readings.get("RCU_DATA", {})
        loop = sensor_readings.get("LOOP_DATA", {})

        # 1) PHASE_DESYNC: phase vs lights mismatch
        if scenario == "PHASE_DESYNC":
            rcu["Phase"] = "NS_GREEN"
            telemetry["light_state"] = {"N": "RED", "S": "RED", "E": "GREEN", "W": "GREEN"}
            sensor_readings["RCU_DATA"] = rcu

        # 2) EDGE_BLACKHOLE_ATTACK: camera sees traffic, loop sees nothing
        elif scenario == "EDGE_BLACKHOLE_ATTACK":
            cam["North_Cars"] = 80
            cam["South_Cars"] = 70
            cam["East_Cars"] = 40
            cam["West_Cars"] = 30
            cam["Queue_Length"] = 25
            loop["Edge_Blackhole_NS"] = 1
            loop["Edge_Blackhole_EW"] = 1
            loop["Loop_Vehicle_Count"] = 0
            loop["Loop_Occupancy_Ratio"] = 0.0
            sensor_readings["CAMERA_DATA"] = cam
            sensor_readings["LOOP_DATA"] = loop

        # 3) FORCED_ALL_RED_DOS: stuck all-red with big queue, no emergency
        elif scenario == "FORCED_ALL_RED_DOS":
            telemetry["light_state"] = {"N": "RED", "S": "RED", "E": "RED", "W": "RED"}
            rcu["Phase"] = "ALL_RED"
            rcu["Emergency_Flag"] = 0
            rcu["Preempt_Call_Count"] = 0
            sensor_readings["RCU_DATA"] = rcu
            cam["Queue_Length"] = 35
            sensor_readings["CAMERA_DATA"] = cam
            loop["Is_All_Red"] = 1
            sensor_readings["LOOP_DATA"] = loop

        telemetry["sensor_readings"] = sensor_readings
        return telemetry

    # ------------------------
    # Telemetry generation
    # ------------------------
    def generate_telemetry(self, intersection_id: str, block_id: str):
        raw_readings_list = self.sensors.get_all_labeled_readings()
        processed_readings = {}

        for reading in raw_readings_list:
            # Convert numpy types to native Python
            for key, value in list(reading.items()):
                if isinstance(value, np.generic):
                    reading[key] = value.item()

            label = reading.pop("Sensor_Label", None)

            if label:
                sensor_type_name = label.split("_")[0]  # e.g. CAMERA_R1 -> CAMERA
                new_key = f"{sensor_type_name}_DATA"
                processed_readings[new_key] = reading

        return {
            "intersection_id": intersection_id,
            "block_id": block_id,
            "timestamp": int(time.time()),
            "light_state": self.light.state,
            "sensor_readings": processed_readings,
            "pedestrian_button_pressed": bool(self.sensors.pedestrian_button),
        }

    # ------------------------
    # Main cycle
    # ------------------------
    def run_once(self, intersection_id: str, block_id: str):
        # Update local simulation
        self.light.update()
        self.vehicle_sim.update(self.light.state)
        self.sensors.simulate_pedestrian_press()

        telemetry = self.generate_telemetry(intersection_id, block_id)

        # Optional: inject anomalies every 5–7 cycles
        self.cycle_count += 1
        if self.cycle_count >= self.next_attack_cycle:
            telemetry = self.inject_random_anomaly(telemetry)
            self.cycle_count = 0
            self.next_attack_cycle = self._pick_next_attack_cycle()

        # Send telemetry to block brain (your Flask server)
        self.client.send_telemetry(telemetry)

        # Reset pedestrian button for next round
        self.sensors.pedestrian_button = False

        return telemetry

    def run(self):
        print(f"\n--- Starting Intersection Simulation (random junctions, infinite) ---")
        cycle = 0

        while True:
            cycle += 1
            # 🔹 Pick a random junction for this cycle
            intersection_id, block_id = random.choice(self.junctions)
            print(f"\n[Cycle {cycle}] Using intersection '{intersection_id}' (block '{block_id}')")

            telemetry = self.run_once(intersection_id, block_id)
            pprint(telemetry)
            time.sleep(self.telemetry_interval)


if __name__ == "__main__":
    node = IntersectionNode(telemetry_interval=10.0)
    node.run()  # 👈 infinite loop, stop with Ctrl+C
