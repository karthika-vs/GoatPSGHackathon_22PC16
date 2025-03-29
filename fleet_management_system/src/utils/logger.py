import os
import logging
from datetime import datetime

def setup_logging():
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'logs'), exist_ok=True)
    
    log_file = os.path.join(os.path.dirname(__file__), '..', 'logs', 'fleet_logs.txt')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )

def log_robot_action(robot_id: int, action: str, details: str = ""):
    logging.info(f"Robot {robot_id}: {action}. {details}")

def log_system_event(event: str, details: str = ""):
    logging.info(f"System: {event}. {details}")