# Fleet Management System with Traffic Negotiation

## Overview

A Python-based Fleet Management System designed for managing multiple robots navigating through an environment while negotiating traffic and avoiding collisions. The system features an interactive GUI built with Tkinter that visualizes robot movements, statuses, and the navigation graph

## Features

-  **Interactive GUI** with zoom/pan capabilities
-  **Robot Management**:
        Spawn robots by clicking vertices,
        Assign destinations visually,
        Unique robot colors/IDs
-  **Traffic Negotiation**:
        Real-time collision avoidance,
        Lane reservation system,
        Visual waiting indicators
-  **Pathfinding** with A* algorithm
-  **Status Monitoring** panel
-  **Multi-level Support** for buildings

## Installation and Setup

1. Clone the repository:
    ```bash
    git clone [repository-url]
    cd fleet_management_system

2. Install Dependencies
    ```bash
    pip install -r requirements.txt

3. Run the application:
    ```bash
    python -m src.main