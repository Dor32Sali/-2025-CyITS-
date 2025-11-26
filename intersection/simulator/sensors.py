import random
from ..states.constants import DIRECTIONS

class Sensors:
    def __init__(self):
        self.vehicle_counts = {
          direction : random.randint(0, 40) for direction in DIRECTIONS
        }

        self.pedestrian_button = False

    def vehicle_count(self, direction, light):
        self._random_update(direction, light)
        
        return self.vehicle_counts.get(direction, 0)

    def emergency_vehicle_flag(self):
        return random.choice([0, 0, 0, 0, 1])

    def _random_update(self, direction, light):
        if light == 'RED':
            delta = random.randint(1, 3)
        else:
            delta = random.randint(-3, -1)
        new_value = self.vehicle_counts[direction] + delta
        self.vehicle_counts[direction] = max(new_value, 0)
