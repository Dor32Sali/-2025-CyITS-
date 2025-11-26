import time
from .sensors import Sensors
from ..states.vehicle_sim import VehicleSimulation
from ..states.traffic_light import TrafficLight
from ..api.client import NodeAPIClient
from pprint import pprint

class IntersectionNode:
    def __init__(self,
                 intersection_id=None,
                 block_brain_url="http://localhost:5000",
                 telemetry_interval=1.0,
                 lights = {'N' :'GREEN', 'S' : 'GREEN', 'E' : 'RED', 'W' : 'RED'}):
        self.id = intersection_id 
        self.telemetry_interval = telemetry_interval  
        self.sensors = Sensors()
        self.vehicle_sim = VehicleSimulation()
        self.light = TrafficLight(lights)
        self.client = NodeAPIClient(block_brain_url)

    def generate_telemetry(self):
        return {
            "intersection_id": self.id,
            "timestamp": int(time.time()),
            "phase": self.light.state,
            "cars": {
                "north": self.sensors.vehicle_count('N', self.light.state['N']),
                "south": self.sensors.vehicle_count('S', self.light.state['S']),
                "east": self.sensors.vehicle_count('E', self.light.state['E']),
                "west": self.sensors.vehicle_count('W', self.light.state['W'])
            },
            "pedestrians_waiting": bool(self.sensors.pedestrian_button),
            "emergency_vehicle": bool(self.sensors.emergency_vehicle_flag()),
        }
         
    def run_once(self):
        self.light.update()
        self.vehicle_sim.update(self.light.state)
        telemetry = self.generate_telemetry()
        self.client.send_telemetry(telemetry)
        return telemetry

    def run(self):
        while True:
            telemetry = self.run_once()
            pprint(telemetry)
            print()

            self.sensors.pedestrian_button = False
            time.sleep(self.telemetry_interval)
