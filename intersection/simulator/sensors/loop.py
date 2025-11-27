import numpy as np
# Note: pandas is implicitly required by create_timestamp_index
import pandas as pd
from datetime import datetime
from abc import ABC, abstractmethod

# --- Base Components ---
# Assuming these are available either via a local file or defined in the package scope.
# Including minimal definitions for context, but relying on the relative import for resolution.

class SensorData(ABC):
    """Base class providing the abstract interface."""
    @abstractmethod
    def get_latest_data(self):
        pass

def create_timestamp_index():
    """Generates the current timestamp formatted as a Pandas index."""
    return pd.to_datetime(datetime.now())




class LoopSensor(SensorData):
    """
    Handles data specific to Inductive Loop Detectors by generating a single,
    synthetic data point for the current time step.
    
    This data reflects vehicle presence, count, and speed over the loop.
    """
    LABEL = "LOOP_DETECTOR_METRICS"
    
    def __init__(self):
        # Assuming SensorData has a simple or no __init__
        # super().__init__() 
        pass

    def get_latest_data(self):
        """
        Generates and returns a single, new synthetic loop detector data point 
        as a dictionary, including the sensor's LABEL.
        
        The metrics simulated are based on common inductive loop outputs.
        """
        
        # 1. Base Data Generation (mimicking the columns from test_loop_final.csv)
        data = {}
        
        # Binary flags for special conditions
        data['Is_All_Red'] = np.random.choice([0, 1], p=[0.9, 0.1])
        data['Edge_Blackhole_NS'] = np.random.choice([0, 1], p=[0.98, 0.02])
        data['Edge_Blackhole_EW'] = np.random.choice([0, 1], p=[0.98, 0.02])
        
        # Core metrics
        data['Avg_Presence_Time_s'] = round(np.random.uniform(0.1, 1.5), 4)
        data['Loop_Occupancy_Ratio'] = round(np.random.uniform(0.01, 0.20), 4)
        data['Loop_Vehicle_Count'] = np.random.randint(100, 500)
        data['Loop_Avg_Speed'] = round(np.random.uniform(50.0, 75.0), 4)
        data['Truck_Ratio'] = round(np.random.uniform(0.05, 0.25), 4)
        
        # 2. Add Metadata
        data['Sensor_Label'] = self.LABEL
        data['Timestamp'] = create_timestamp_index()

        return data
    
    def get_vehicle_count(self):
        """Returns the current vehicle count as reported by the loop."""
        return self.get_latest_data()['Loop_Vehicle_Count']