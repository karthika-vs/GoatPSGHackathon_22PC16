from src.utils.logger import log_robot_action, log_system_event
from typing import Dict, List, Tuple
from src.models.robot import Robot
from src.controllers.traffic_manager import TrafficManager

class FleetManager:
    def __init__(self):
        self.robots: Dict[int, Robot] = {}
        self.next_robot_id = 1
        self.traffic_manager = TrafficManager()
        log_system_event("FleetManager initialized", "With TrafficManager")

    def spawn_robot(self, position: Tuple[float, float]) -> Robot:
        robot = Robot(self.next_robot_id, position)
        self.robots[self.next_robot_id] = robot
        self.next_robot_id += 1
        log_system_event("Robot spawned", f"ID: {robot.id} at {position}")
        return robot

    def assign_destination(self, robot_id: int, destination: Tuple[float, float], path_indices: List[int]):
        if robot_id in self.robots:
            self.robots[robot_id].set_destination(destination, path_indices)
            log_system_event("Destination assigned", f"Robot {robot_id} to {destination} via {path_indices}")

    def update_robots(self):
        """Update all robot positions and handle traffic"""
        # First pass: update all moving robots
        for robot in self.robots.values():
            if robot.status == "moving":
                robot.update_position(self.traffic_manager)
        
        # Second pass: check waiting robots
        for robot in self.robots.values():
            if robot.status == "waiting":
                # Check if their lane is now available
                if robot.current_path_index < len(robot.path_indices) - 1:
                    current_idx = robot.path_indices[robot.current_path_index]
                    next_idx = robot.path_indices[robot.current_path_index + 1]
                    lane = (current_idx, next_idx)
                    
                    # Check if lane is free
                    lane_free = True
                    for reserved_lane, reserved_robot in self.traffic_manager.reserved_lanes.items():
                        if (reserved_lane == lane or reserved_lane == (lane[1], lane[0])) and reserved_robot != robot.id:
                            lane_free = False
                            break
                    
                    if lane_free:
                        robot.status = "moving"
                        log_robot_action(robot.id, "Resuming movement", f"on lane {lane}")