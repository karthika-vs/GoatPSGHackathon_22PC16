from src.utils.logger import log_robot_action, log_system_event
from typing import Dict, List, Tuple
from src.models.robot import Robot

class FleetManager:
    def __init__(self):
        self.robots: Dict[int, Robot] = {}
        self.next_robot_id = 1
        log_system_event("FleetManager initialized")

    def spawn_robot(self, position: Tuple[float, float]) -> Robot:
        robot = Robot(self.next_robot_id, position)
        self.robots[self.next_robot_id] = robot
        self.next_robot_id += 1
        log_system_event("Robot spawned", f"ID: {robot.id} at {position}")
        return robot

    def assign_destination(self, robot_id: int, destination: Tuple[float, float], path: List[Tuple[float, float]]):
        if robot_id in self.robots:
            self.robots[robot_id].set_destination(destination, path)
            log_system_event("Destination assigned", f"Robot {robot_id} to {destination}")