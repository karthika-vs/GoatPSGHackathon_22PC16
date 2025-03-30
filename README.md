# Fleet Management System with Traffic Negotiation

## Overview

A Python-based Fleet Management System designed for managing multiple robots navigating through an environment while negotiating traffic and avoiding collisions. The system features an interactive GUI built with Tkinter that visualizes robot movements, statuses, and the navigation graph

## Features

### Core Functionality
- **Interactive Map**: Click vertices to spawn robots and assign destinations
- **Robot Management**: 
  - Unique colored robots with IDs
  - Visual path highlighting
  - Status indicators (moving/waiting/idle)
  
### Traffic Control
- **Smart Navigation**: A* pathfinding algorithm
- **Collision Avoidance**: 
  - Lane reservation system
  - Automatic waiting at busy lanes
  - Visual queue indicators

### System Features
- **Multi-level Support**: Switch between building floors
- **View Controls**: Zoom, pan and reset view
- **Real-time Monitoring**: 
  - Selected robot info panel
  - System status display
- **Comprehensive Logging**: All actions logged with timestamps

### Technical Highlights
- Smooth 50ms animation updates
- Bi-directional lane collision detection
- Automatic path recalculation

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

## Usage Guide

### Basic Controls
- **Spawn Robot**: Click on any vertex (circle)
- **Assign Destination**:
  1. Click on a robot to select it
  2. Click on destination vertex
- **View Controls**:
  - Mouse wheel: Zoom in/out
  - Right-click + drag: Pan view
  - "Reset View" button: Reset zoom/pan

### Interface Elements
**Left Panel**:
- Interactive map with:
  - Robots (colored circles with IDs)
  - Paths (colored lines)
  - Vertices (location markers)

**Right Panel**:
- Robot information (selected robot):
  - ID
  - Status
  - Position
  - Destination
- System status display
- Level selection dropdown
- Control buttons:
  - Zoom in/out
  - Reset view
  - Clear selection

## Output video link
https://drive.google.com/drive/folders/1wbLfgHOd1R6qKz3FQMwufsTuXcoPjQFi