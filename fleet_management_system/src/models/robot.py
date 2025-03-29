import random
import math
from typing import Dict, Tuple, Optional, List
from src.utils.logger import log_robot_action

class Robot:
    def __init__(self, robot_id: int, initial_position: Tuple[float, float]):
        self.id = robot_id
        self.position = initial_position
        self.destination = None
        self.path: List[Tuple[float, float]] = []
        self.current_path_index = 0
        self.speed = 0.05
        self.status = "idle"
        self.color = self._generate_random_color()
        log_robot_action(self.id, "Robot spawned", f"at position {initial_position}")

    def _generate_random_color(self) -> str:
        colors = ["red", "green", "blue", "orange", "purple", "cyan", "magenta"]
        return random.choice(colors)
    
    def set_destination(self, destination: Tuple[float, float], path: List[Tuple[float, float]]):
        self.destination = destination
        self.path = path
        self.current_path_index = 0
        self.status = "moving"
        log_robot_action(self.id, "Destination set", f"to {destination} via path {path}")

    def update_position(self) -> bool:
        if not self.path or self.status != "moving":
            return False
        
        if self.current_path_index >= len(self.path):
            self.status = "idle"
            log_robot_action(self.id, "Reached destination", f"at {self.position}")
            return True
        
        target = self.path[self.current_path_index]
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.speed:
            self.position = target
            self.current_path_index += 1
            log_robot_action(self.id, "Reached waypoint", f"{self.current_path_index-1}/{len(self.path)}")
        else:
            self.position = (
                self.position[0] + (dx / distance) * self.speed,
                self.position[1] + (dy / distance) * self.speed
            )
        
        return False
    
    def set_status(self, status: str):
        old_status = self.status
        self.status = status
        if old_status != status:
            log_robot_action(self.id, "Status changed", f"from {old_status} to {status}")