import random
import math
import time
from typing import Dict, Tuple, Optional, List
from src.utils.logger import log_robot_action

class Robot:
    def __init__(self, robot_id: int, initial_position: Tuple[float, float]):
        self.id = robot_id
        self.position = initial_position
        self.destination = None
        self.path = []  # For visualization (coordinates)
        self.path_indices = []  # For traffic management (vertex indices)
        self.current_path_index = 0
        self.speed = 0.05
        self.status = "idle"
        self.color = self._generate_random_color()
        self.waiting_since = None
        log_robot_action(self.id, "Robot spawned", f"at position {initial_position}")

    def _generate_random_color(self) -> str:
        colors = ["red", "green", "blue", "orange", "purple", "cyan", "magenta"]
        return random.choice(colors)
    
    def set_destination(self, destination: Tuple[float, float], path_indices: List[int]):
        self.destination = destination
        self.path_indices = path_indices
        self.current_path_index = 0
        self.status = "moving"
        self.waiting_since = None
        log_robot_action(self.id, "Destination set", f"to {destination} via path {path_indices}")

    def update_position(self, traffic_manager) -> bool:
        if not self.path_indices or self.status != "moving":
            return False
        
        if self.current_path_index >= len(self.path_indices) - 1:
            self.status = "idle"
            log_robot_action(self.id, "Reached destination", f"at {self.position}")
            return True
        
        current_vertex_idx = self.path_indices[self.current_path_index]
        next_vertex_idx = self.path_indices[self.current_path_index + 1]
        lane = (current_vertex_idx, next_vertex_idx)
        
        # Check lane availability
        if not traffic_manager.request_lane(self.id, lane):
            if self.status != "waiting":
                self.status = "waiting"
                self.waiting_since = time.time()
                traffic_manager.add_waiting_robot(self.id, lane)
                log_robot_action(self.id, "Waiting at vertex", f"for lane {lane}")
            return False
        
        # Get the actual segment coordinates
        current_vertex = self.path[self.current_path_index]
        next_vertex = self.path[self.current_path_index + 1]
        
        # Calculate direction vector
        dx = next_vertex[0] - current_vertex[0]
        dy = next_vertex[1] - current_vertex[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 0.0001:  # Vertices are coincident
            self.current_path_index += 1
            return False
        
        # Calculate movement along the segment
        step_x = (dx / distance) * self.speed
        step_y = (dy / distance) * self.speed
        
        # Calculate remaining distance to next vertex
        remaining_x = next_vertex[0] - self.position[0]
        remaining_y = next_vertex[1] - self.position[1]
        remaining_dist = math.sqrt(remaining_x**2 + remaining_y**2)
        
        if remaining_dist <= self.speed:
            # Reached next vertex
            self.position = next_vertex
            self.current_path_index += 1
            # Release the previous lane
            prev_lane = (self.path_indices[self.current_path_index - 1], 
                        self.path_indices[self.current_path_index])
            traffic_manager.release_lane(prev_lane)
            log_robot_action(self.id, "Reached waypoint", f"{self.current_path_index}/{len(self.path_indices)}")
        else:
            # Move along the segment
            self.position = (
                self.position[0] + step_x,
                self.position[1] + step_y
            )
        
        return False
            
    def set_status(self, status: str):
        old_status = self.status
        self.status = status
        if old_status != status:
            log_robot_action(self.id, "Status changed", f"from {old_status} to {status}")