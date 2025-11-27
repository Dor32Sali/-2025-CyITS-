import numpy as np
import pandas as pd
from datetime import datetime
from abc import ABC, abstractmethod

# --- START FIX: Base Components Defined Locally (Resolves missing sensor_data.py import) ---

class SensorData(ABC):
    """
    Base class for all sensor data handling.
    Abstract classes ensure subclasses implement the data generation logic.
    """
    @abstractmethod
    def get_latest_data(self):
        """Must be implemented by all subclasses."""
        pass

def create_timestamp_index():
    """Generates the current timestamp formatted as a Pandas index."""
    return pd.to_datetime(datetime.now())

# --- END FIX: Base Components Defined Locally ---


class CameraSensor(SensorData):
    """
    Handles data specific to traffic camera sensors by generating a single,
    synthetic data point for the current time step.
    
    This sensor simulates vehicle counts, queue metrics, and analytical insights, 
    including a ground truth anomaly flag.
    """
    LABEL = "CAMERA_TRAFFIC_FLOW"
    
    def __init__(self):
        super().__init__() 
        self.directions = ['North_Cars', 'South_Cars', 'East_Cars', 'West_Cars']

    def get_latest_data(self):
        """
        Generates and returns a single, new synthetic traffic camera sensor 
        data point as a dictionary, including all missing analytical metrics 
        and the Anomaly Ground Truth flag.
        """
        
        # Determine the current time information
        current_dt = create_timestamp_index()
        current_hour = current_dt.hour
        
        # 1. Directional Car Counts (Base data)
        north_cars = np.random.randint(50, 200)
        south_cars = np.random.randint(50, 200)
        east_cars = np.random.randint(20, 100)
        west_cars = np.random.randint(20, 100)
        
        # 2. Metrics Generation (Base data)
        queue_length = np.random.randint(0, 30)
        avg_speed = round(np.random.uniform(40.0, 75.0), 2)
        blocked_cars = np.random.randint(0, 10) # Max 10 blocked cars
        
        total_cars_in_period = north_cars + south_cars + east_cars + west_cars
        
        # 3. ADDED MISSING METRICS (Analytical/Time)
        
        # Hour of Day (0-23)
        hour_of_day = current_hour
        
        # Delta Metrics (Simulated changes since last cycle)
        delta_queue = np.random.randint(-5, 5)
        delta_speed = round(np.random.uniform(-5.0, 5.0), 2)
        
        # Directional Metrics
        max_direction_cars = max(north_cars, south_cars, east_cars, west_cars)
        
        # Simple directional imbalance proxy (e.g., N/S vs E/W traffic skew)
        ns_total = north_cars + south_cars
        ew_total = east_cars + west_cars
        direction_imbalance = round(abs(ns_total - ew_total) / (ns_total + ew_total + 1), 4)
        
        # Pedestrian Waiting Flag
        ped_waiting = np.random.choice([0, 1], p=[0.85, 0.15])
        
    
        
        
        # 5. Final Data Dictionary
        data = {
            # Time Metric
            'Hour_of_Day': hour_of_day,
            
            # Directional Car Counts
            'North_Cars': north_cars,
            'South_Cars': south_cars,
            'East_Cars': east_cars,
            'West_Cars': west_cars,
            
            # Base Metrics
            'Queue_Length': queue_length,
            'Avg_Speed': avg_speed,
            'Blocked_Cars': blocked_cars,
            
            # Analytical/Delta Metrics
            'Delta_Queue': delta_queue,
            'Delta_Speed': delta_speed,
            'Ped_Waiting': ped_waiting,
            'Max_Direction_Cars': max_direction_cars,
            'Direction_Imbalance': direction_imbalance,
            
            # Derived Metric
            'Blocked_to_Served_Ratio': round(blocked_cars / (total_cars_in_period + 1), 4),
             

            # Metadata
            'Sensor_Label': self.LABEL,
            'Timestamp': current_dt
        }
        
        return data

    def get_car_count_by_direction(self, direction_initial):
        """
        Fetches the current car count for a specific direction (N, S, E, W).
        """
        latest_data = self.get_latest_data() 
        key_map = {'N': 'North_Cars', 'S': 'South_Cars', 'E': 'East_Cars', 'W': 'West_Cars'}
        return latest_data.get(key_map.get(direction_initial), 0)

    def get_queue_and_blocked(self):
        """Returns the raw queue and blocked metrics from the latest reading."""
        latest_data = self.get_latest_data()
        return {
            'Queue_Length': latest_data['Queue_Length'],
            'Blocked_Cars': latest_data['Blocked_Cars'],
            'Blocked_to_Served_Ratio': latest_data['Blocked_to_Served_Ratio']
        }