import random
from .constants import DIRECTIONS

class VehicleSimulation:
    def __init__(self):
        self.direction_queues = {
            direction : 0 for direction in DIRECTIONS
        }
        
    def update(self, light_states):
        for direct in light_states:
            if light_states[direct] == "GREEN":
                self.direction_queues[direct] = max(0, self.direction_queues[direct] - random.randint(3, 8))
            else:
                self.direction_queues[direct] += random.randint(1, 5)

        return self.direction_queues
