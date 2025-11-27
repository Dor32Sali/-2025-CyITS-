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

# --- END FIX ---


class RcuSensor(SensorData):
    """
    Handles data specific to Roadside Control Unit (RCU) / Traffic Light.
    Generates a single, synthetic data point for the current time step.
    
    This sensor simulates the operational state of the intersection's light controller.
    """
    LABEL = "RCU_LIGHT_STATE"
    
    def __init__(self):
        super().__init__() 
        self.phases = ['NS_GREEN', 'EW_GREEN', 'ALL_RED', 'NS_YELLOW', 'EW_YELLOW']

    def get_latest_data(self):
        """
        Generates and returns a single, new synthetic RCU sensor data point 
        as a dictionary, including the sensor's LABEL, and includes all missing operational metrics.
        """
        
        # 1. Base Data Generation (Standard traffic phase, health, emergency)
        phase = np.random.choice(self.phases, p=[0.3, 0.3, 0.25, 0.075, 0.075])
        emergency_flag = np.random.choice([0, 1], p=[0.95, 0.05])
        health_flag = np.random.choice([1, 0], p=[0.90, 0.10])
        
        # 2. Operational Metrics (Simulated from training_rcu.csv columns)
        # Note: These are simulated to be mostly normal, unless an error flag is set.
        
        # Warning/Error Rates (usually low floats)
        csw_warn_rate = round(np.random.uniform(0.0, 0.05), 4) 
        spat_tx_rate = round(np.random.uniform(0.7, 1.0), 4) # Should be near 1.0 (100% transmission rate)
        im_fwd_drop_rate = round(np.random.uniform(0.0, 0.05), 4) # Should be near 0.0
        
        # Message/Signal Counts (integers)
        msg_rx_rate = np.random.randint(50, 150)
        preempt_call_count = np.random.randint(0, 5) # Number of emergency preempts requested
        
        # Binary Flags (0 or 1)
        dms_update_flag = np.random.choice([0, 1], p=[0.98, 0.02])
        tim_sent_flag = np.random.choice([0, 1], p=[0.95, 0.05])
        log_error_flag = np.random.choice([0, 1], p=[0.90, 0.10])
        
        # 3. Logical Correlation (Error/Emergency state)
        if emergency_flag == 1:
            phase = 'ALL_RED'
            health_flag = 0 
            spat_tx_rate = round(np.random.uniform(0.0, 0.3), 4) # Transmission drops
            log_error_flag = 1
        
        if log_error_flag == 1:
            csw_warn_rate = round(np.random.uniform(0.1, 0.5), 4) # Warning rate increases
            
        data = {
            'Phase': phase,
            'Emergency_Flag': emergency_flag,
            'Health_Flag': health_flag,
            
            # --- ADDED MISSING METRICS ---
            'CSW_Warn_Rate': csw_warn_rate,
            'DMS_Update_Flag': dms_update_flag,
            'SPAT_TX_Rate': spat_tx_rate,
            'IM_Fwd_Drop_Rate': im_fwd_drop_rate,
            'Msg_Rx_Rate': msg_rx_rate,
            'Preempt_Call_Count': preempt_call_count,
            'TIM_Sent_Flag': tim_sent_flag,
            'Log_Error_Flag': log_error_flag,
            # -----------------------------
            
            'Sensor_Label': self.LABEL,
            'Timestamp': create_timestamp_index()
        }

        return data

    def is_emergency_vehicle(self):
        """Checks the latest reading for an emergency vehicle event (Emergency_Flag == 1)."""
        return self.get_latest_data()['Emergency_Flag'] == 1
    
    def get_traffic_phase_and_health(self):
        """Returns the current signal phase and health flag."""
        latest_data = self.get_latest_data()
        return {
            'Phase': latest_data['Phase'],
            'Health_Flag': latest_data['Health_Flag']
        }