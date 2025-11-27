import random
# --- CRITICAL FIX: Using relative imports (from .) to correctly reference other modules 
# within the same 'sensors' package, resolving the ModuleNotFoundError.
from .camera import CameraSensor
from .rcu import RcuSensor
from .loop import LoopSensor 

class Sensors:
    """
    A unified wrapper class that holds and manages all individual sensor instances 
    (Camera, RCU, Loop Detector).
    
    It adapts the specific sensor data methods (e.g., get_latest_data) into 
    the methods required by the IntersectionNode class, ensuring all data is 
    labeled and collected in a single, standardized list.
    """
    def __init__(self):
        # Initialize the specific sensor instances
        self.camera = CameraSensor()
        self.rcu = RcuSensor()
        self.loop_detector = LoopSensor()
        
        # Placeholder for physical input (simulated)
        self.pedestrian_button = False 

    def get_all_labeled_readings(self):
        """
        Collects the latest, full, labeled data dictionary from all connected sensors.
        Returns a list of data dictionaries ready for telemetry packaging.
        """
        # Generate new, real-time data from all sensors for this cycle
        return [
            self.camera.get_latest_data(),
            self.rcu.get_latest_data(),
            self.loop_detector.get_latest_data()
        ]

    def vehicle_count(self, direction_initial, light_state):
        """
        Fetches the current car count for a given direction from the camera sensor.
        Note: This is often used by traffic light logic to decide phasing.
        """
        # This calls a method that must exist on CameraSensor
        return self.camera.get_car_count_by_direction(direction_initial)

    def emergency_vehicle_flag(self):
        """
        Checks the RCU sensor data for an emergency event flag.
        Returns 1 if true, 0 if false.
        """
        # This calls a method that must exist on RcuSensor
        return 1 if self.rcu.is_emergency_vehicle() else 0
    
    def simulate_pedestrian_press(self):
        """
        Simulates a random pedestrian button press.
        """
        if random.random() < 0.1: # 10% chance per cycle
            self.pedestrian_button = True

    def get_raw_camera_data(self):
        """Utility method to get raw camera data."""
        return self.camera.get_latest_data()

    def get_raw_rcu_data(self):
        """Utility method to get raw RCU data."""
        return self.rcu.get_latest_data()

    def get_raw_loop_data(self):
        """Utility method to get raw Loop data."""
        return self.loop_detector.get_latest_data()