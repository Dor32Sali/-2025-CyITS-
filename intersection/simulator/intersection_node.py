import time
from pprint import pprint
import os
import numpy as np
import requests
from sensors.sensors import Sensors
import json 

INTERSECTION_ID = os.getenv("INTERSECTION_ID", "Junction_A1")
BLOCK_ID = os.getenv("BLOCK_ID", "BLOCK_DEFAULT")

class VehicleSimulation:
    def update(self, light_state):
        pass

class TrafficLight:
    def __init__(self, lights):
        self.state = lights

    def update(self):
        if self.state['N'] == 'GREEN':
            self.state = {'N': 'RED', 'S': 'RED', 'E': 'GREEN', 'W': 'GREEN'}
        else:
            self.state = {'N': 'GREEN', 'S': 'GREEN', 'E': 'RED', 'W': 'RED'}

class NodeAPIClient:
    def __init__(self, block_brain_url):
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
            response = requests.post(self.url, json=safe_payload, timeout=5)
            print(f"[POST] {self.url} -> {response.status_code}")
            try:
                print("Response JSON:", response.json())
            except Exception:
                print("Response text:", response.text)
        except Exception as e:
            print(f"ERROR: Failed to send telemetry to {self.url}. Details: {e}")

class IntersectionNode:
    def __init__(self,
                 intersection_id=INTERSECTION_ID,
                 block_id=BLOCK_ID,
                 block_brain_base_url="https://casteless-unpatronizable-ephraim.ngrok-free.dev",
                 api_endpoint="/api/intersection",
                 telemetry_interval=5.0,
                 lights={'N': 'GREEN', 'S': 'GREEN', 'E': 'RED', 'W': 'RED'}):

        self.id = intersection_id
        self.block_id = block_id
        self.telemetry_interval = telemetry_interval
        self.sensors = Sensors()
        self.vehicle_sim = VehicleSimulation()
        self.light = TrafficLight(lights)

        full_url = block_brain_base_url.rstrip('/') + api_endpoint
        self.client = NodeAPIClient(full_url)

        print(f"Intersection Node '{self.id}' initialized (Block: {self.block_id}), targeting URL: {full_url}")

    def generate_telemetry(self):
        raw_readings_list = self.sensors.get_all_labeled_readings()
        processed_readings = {}

        for reading in raw_readings_list:
            for key, value in reading.items():
                if isinstance(value, np.generic):
                    reading[key] = value.item()

            label = reading.pop('Sensor_Label', None)

            if label:
                sensor_type_name = label.split('_')[0]
                new_key = f"{sensor_type_name}_DATA"
                processed_readings[new_key] = reading

        return {
            "intersection_id": self.id,
            "block_id": self.block_id,
            "timestamp": int(time.time()),
            "light_state": self.light.state,
            "sensor_readings": processed_readings,
            "pedestrian_button_pressed": bool(self.sensors.pedestrian_button),
        }

    def run_once(self):
        self.light.update()
        self.vehicle_sim.update(self.light.state)
        self.sensors.simulate_pedestrian_press()

        telemetry = self.generate_telemetry()
        self.client.send_telemetry(telemetry)
        return telemetry

    def run(self, max_cycles=4):
        print(f"\n--- Starting Intersection Simulation for {max_cycles} cycles ---")

        for cycle in range(1, max_cycles + 1):
            self.run_once()
            self.sensors.pedestrian_button = False
            time.sleep(self.telemetry_interval)

        print("\n--- Simulation Complete ---")

if __name__ == '__main__':
    node = IntersectionNode(telemetry_interval=1.0)
    node.run(max_cycles=1)
