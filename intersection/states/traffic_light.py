from .constants import DIRECTIONS

class TrafficLight:
    def __init__(self, lights):
        self.state = {
            direction : lights[direction] for direction in DIRECTIONS
            }
        self.time_left = 10

    def update(self):
        self.time_left -= 1
        if self.time_left <= 0:
            for direct in self.state.keys():
                if self.state[direct] == "RED":
                    self.state[direct] = "GREEN"; 
                else:
                    self.state[direct] = "RED"; 
            self.time_left = 10
