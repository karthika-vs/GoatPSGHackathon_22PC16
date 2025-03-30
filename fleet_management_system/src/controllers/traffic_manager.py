from typing import Dict, Set, Tuple, List
from src.utils.logger import log_system_event

class TrafficManager:
    def __init__(self):
        self.reserved_lanes: Dict[Tuple[int, int], int] = {}
        self.waiting_robots: Dict[int, Tuple[int, int]] = {}  
        log_system_event("TrafficManager initialized", "Ready to manage lane traffic")

    def request_lane(self, robot_id: int, lane: Tuple[int, int]) -> bool:
        """
        Request to reserve a lane for a robot.
        Returns True if granted, False if blocked.
        """
        for reserved_lane, reserved_robot in self.reserved_lanes.items():
            if reserved_lane == lane and reserved_robot != robot_id:
                return False
            if reserved_lane == (lane[1], lane[0]) and reserved_robot != robot_id:
                return False

        # If lane is free, reserve it
        self.reserved_lanes[lane] = robot_id
        if robot_id in self.waiting_robots:
            del self.waiting_robots[robot_id]
        log_system_event("Lane reserved", f"Robot {robot_id} reserved lane {lane}")
        return True

    def release_lane(self, lane: Tuple[int, int]):
        """Release a lane reservation and notify waiting robots"""
        if lane in self.reserved_lanes:
            released_robot = self.reserved_lanes[lane]
            del self.reserved_lanes[lane]
            # Check if any robots are waiting for this lane
            waiting_robots = self.get_waiting_robots(lane)
            for robot_id in waiting_robots:
                if robot_id in self.waiting_robots:
                    del self.waiting_robots[robot_id]
                    log_system_event("Lane available", f"Robot {robot_id} can now proceed on lane {lane}")
            
            log_system_event("Lane released", f"Lane {lane} is now available (was used by robot {released_robot})")

    def add_waiting_robot(self, robot_id: int, lane: Tuple[int, int]):
        """Add a robot to waiting queue for a lane"""
        self.waiting_robots[robot_id] = lane
        log_system_event("Robot waiting", f"Robot {robot_id} waiting for lane {lane}")

    def get_waiting_robots(self, lane: Tuple[int, int]) -> List[int]:
        """Get all robots waiting for a specific lane"""
        return [rid for rid, l in self.waiting_robots.items() if l == lane]