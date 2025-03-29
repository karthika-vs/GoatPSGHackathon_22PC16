import random
import math
from typing import Dict, Tuple, Optional, List

class Robot:
    def __init__(self, robot_id: int, initial_position: Tuple[float, float]):
        self.id = robot_id
        self.position = initial_position
        self.destination = None
        self.path: List[Tuple[float, float]] = []
        self.current_path_index = 0
        self.speed = 0.05  # Movement speed (units per frame)
        self.status = "idle"  # idle, moving, charging, waiting
        self.color = self._generate_random_color()
    
    def _generate_random_color(self) -> str:
        colors = ["red", "green", "blue", "orange", "purple", "cyan", "magenta"]
        return random.choice(colors)
    
    def set_destination(self, destination: Tuple[float, float], path: List[Tuple[float, float]]):
        """Set destination and path for the robot"""
        self.destination = destination
        self.path = path
        self.current_path_index = 0
        self.status = "moving"
    
    def update_position(self) -> bool:
        """Update robot position along the path. Returns True if reached destination."""
        if not self.path or self.status != "moving":
            return False
        
        if self.current_path_index >= len(self.path):
            self.status = "idle"
            return True
        
        target = self.path[self.current_path_index]
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.speed:
            self.position = target
            self.current_path_index += 1
        else:
            self.position = (
                self.position[0] + (dx / distance) * self.speed,
                self.position[1] + (dy / distance) * self.speed
            )
        
        return False
    
    def get_info(self) -> Dict:
        return {
            "id": self.id,
            "position": self.position,
            "destination": self.destination,
            "status": self.status,
            "color": self.color
        }