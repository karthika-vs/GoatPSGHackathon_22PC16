import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Tuple, Any
from math import sqrt
from ..models.nav_graph import NavGraph
from ..models.robot import Robot
from src.utils.logger import log_robot_action, log_system_event

class FleetManagementGUI:
    def __init__(self, root: tk.Tk, nav_graph_file: str):
        self.root = root
        self.root.title("Fleet Management System")
        
        # Configure window
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Custom styling
        self.setup_styles()
        
        # Load navigation graph
        self.nav_graph = NavGraph(nav_graph_file)
        
        # Set current level
        self.current_level = self.nav_graph.get_level_names()[0]
        
        # Robot management
        self.robots = {}  # robot_id: Robot object
        self.next_robot_id = 1
        self.selected_robot = None
        
        # Create main frames with modern layout
        self.main_frame = ttk.Frame(root, style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas for visualization with shadow effect
        self.canvas_frame = ttk.Frame(self.main_frame, style='Canvas.TFrame')
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="#f5f5f5", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Create control panel with modern styling
        self.control_frame = ttk.Frame(self.main_frame, width=280, style='Control.TFrame')
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5))
        
        # Setup controls with improved layout
        self.setup_controls()
        
        # Initialize view parameters
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.pan_start_x = 0
        self.pan_start_y = 0
        
        # Store vertex positions for click detection
        self.vertex_positions = []
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.pan)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # For zoom with mouse wheel
        
        # Animation control
        self.animation_running = False
        self.after_id = None
        
        # Draw the initial graph
        self.draw_graph()
        
        # Start animation loop
        self.start_animation()
        log_system_event("System initialized", f"Loading graph from {nav_graph_file}")
    
    def setup_styles(self):
        """Configure custom styles for a professional look"""
        style = ttk.Style()
        
        # Configure main styles
        style.configure('Main.TFrame', background='#e1e5ed')
        style.configure('Canvas.TFrame', background='#ffffff', relief=tk.RAISED, borderwidth=1)
        style.configure('Control.TFrame', background='#ffffff', relief=tk.RAISED, borderwidth=1)
        
        # Button styles
        style.configure('TButton', font=('Segoe UI', 9), padding=6)
        style.map('TButton',
            foreground=[('pressed', 'white'), ('active', 'white')],
            background=[('pressed', '#4a6baf'), ('active', '#5c7cbf')]
        )
        
        # Label styles
        style.configure('Header.TLabel', font=('Segoe UI', 11, 'bold'), background='#ffffff', foreground='#2c3e50')
        style.configure('Subheader.TLabel', font=('Segoe UI', 10, 'bold'), background='#ffffff', foreground='#34495e')
        
        # Option menu style
        style.configure('TMenubutton', font=('Segoe UI', 9))
        
        # Robot info frame
        style.configure('Info.TLabelframe', font=('Segoe UI', 9, 'bold'), background='#ffffff')
        style.configure('Info.TLabelframe.Label', font=('Segoe UI', 9, 'bold'), background='#ffffff')
        style.configure('Info.TLabel', font=('Segoe UI', 9), background='#ffffff', padding=(5, 2))
    
    def setup_controls(self):
        """Set up the control panel with improved layout"""
        # Header
        header = ttk.Label(self.control_frame, text="FLEET CONTROLS", style='Header.TLabel')
        header.pack(pady=(15, 10), padx=10, anchor=tk.NW)
        
        # Level selection
        ttk.Label(self.control_frame, text="Environment Level:", style='Subheader.TLabel').pack(pady=(5, 0), padx=10, anchor=tk.NW)
        self.level_var = tk.StringVar(value=self.current_level)
        level_menu = ttk.OptionMenu(
            self.control_frame,
            self.level_var,
            self.current_level,
            *self.nav_graph.get_level_names(),
            command=self.change_level
        )
        level_menu.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        # View controls
        ttk.Label(self.control_frame, text="View Controls:", style='Subheader.TLabel').pack(pady=(5, 0), padx=10, anchor=tk.NW)
        zoom_frame = ttk.Frame(self.control_frame)
        zoom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(zoom_frame, text="Zoom In", command=self.zoom_in, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(zoom_frame, text="Zoom Out", command=self.zoom_out, width=8).pack(side=tk.LEFT)
        ttk.Button(zoom_frame, text="Reset View", command=self.reset_view).pack(side=tk.RIGHT)
        
        # Separator
        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15, padx=10)
        
        # Robot controls
        ttk.Label(self.control_frame, text="Robot Controls:", style='Subheader.TLabel').pack(pady=(5, 0), padx=10, anchor=tk.NW)
        ttk.Button(self.control_frame, text="Clear Selection", command=self.clear_selection).pack(fill=tk.X, padx=10, pady=5)
        
        # Separator
        ttk.Separator(self.control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15, padx=10)
        
        # Robot info display
        self.robot_info_frame = ttk.LabelFrame(self.control_frame, text="Selected Robot", style='Info.TLabelframe')
        self.robot_info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.robot_info_label = ttk.Label(
            self.robot_info_frame, 
            text="No robot selected\n\nClick on a vertex to spawn a robot\nor select an existing robot",
            style='Info.TLabel',
            justify=tk.LEFT
        )
        self.robot_info_label.pack(padx=10, pady=10, fill=tk.X)
        
        # System status
        ttk.Label(self.control_frame, text="System Status:", style='Subheader.TLabel').pack(pady=(5, 0), padx=10, anchor=tk.NW)
        self.status_label = ttk.Label(
            self.control_frame, 
            text="System ready\nRobots: 0",
            style='Info.TLabel',
            justify=tk.LEFT
        )
        self.status_label.pack(padx=10, pady=(0, 15), fill=tk.X)
    
    def draw_graph(self):
        """Draw the navigation graph with robots using improved visuals"""
        self.canvas.delete("all")
        
        # Draw a subtle grid background
        self.draw_grid()
        
        vertices = self.nav_graph.get_vertices(self.current_level)
        lanes = self.nav_graph.get_lanes(self.current_level)
        
        if not vertices:
            return
            
        # Calculate scaling and offsets
        x_coords = [v[0] for v in vertices]
        y_coords = [-v[1] for v in vertices]  # Invert y-axis for display
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        graph_width = max(1, max_x - min_x)
        graph_height = max(1, max_y - min_y)
        
        self.scale = min(
            (self.canvas.winfo_width() * 0.8) / graph_width,
            (self.canvas.winfo_height() * 0.8) / graph_height
        ) * self.zoom_level
        
        self.center_x = (self.canvas.winfo_width() / 2) - ((min_x + max_x) / 2) * self.scale + self.offset_x
        self.center_y = (self.canvas.winfo_height() / 2) - ((min_y + max_y) / 2) * self.scale + self.offset_y
        
        # Store vertex positions for click detection
        self.vertex_positions = []
        
        # Draw lanes with improved styling
        for lane in lanes:
            start_idx, end_idx = lane[0], lane[1]
            start = vertices[start_idx]
            end = vertices[end_idx]
            
            x1 = start[0] * self.scale + self.center_x
            y1 = -start[1] * self.scale + self.center_y
            x2 = end[0] * self.scale + self.center_x
            y2 = -end[1] * self.scale + self.center_y
            
            # Draw lane with gradient effect
            self.canvas.create_line(
                x1, y1, x2, y2, 
                fill="#a0a0a0", 
                width=3, 
                arrow=tk.LAST, 
                arrowshape=(8, 10, 5),
                smooth=True
            )
            
            # Add direction indicator
            mid_x, mid_y = (x1 + x2)/2, (y1 + y2)/2
            self.canvas.create_oval(
                mid_x-3, mid_y-3, mid_x+3, mid_y+3, 
                fill="#4a6baf", 
                outline="#2c3e50"
            )
        
        # Draw vertices with improved styling
        for i, vertex in enumerate(vertices):
            x, y = vertex[0], -vertex[1]
            cx = x * self.scale + self.center_x
            cy = y * self.scale + self.center_y
            
            # Store vertex position for click detection
            self.vertex_positions.append((cx, cy, i))
            
            # Determine vertex style
            vertex_attrs = vertex[2] if len(vertex) > 2 else {}
            is_charger = vertex_attrs.get("is_charger", False)
            name = vertex_attrs.get("name", "")
            
            # Vertex colors and styles
            if is_charger:
                color = "#27ae60"  # Green for chargers
                radius = 12
            elif name:
                color = "#3498db"  # Blue for named vertices
                radius = 10
            else:
                color = "#e74c3c"  # Red for unnamed vertices
                radius = 8
            
            # Draw vertex with shadow effect
            self.canvas.create_oval(
                cx-radius+1, cy-radius+1, cx+radius+1, cy+radius+1,
                fill="#555555", outline="",
                tags=f"vertex_shadow_{i}"
            )
            
            self.canvas.create_oval(
                cx-radius, cy-radius, cx+radius, cy+radius,
                fill=color, outline="#2c3e50", width=1.5,
                tags=f"vertex_{i}"
            )
            
            # Add label if available
            if name:
                self.canvas.create_text(
                    cx, cy-radius-12,
                    text=name,
                    fill="#2c3e50",
                    font=("Segoe UI", 9, "bold"),
                    tags=f"label_{i}"
                )
        
        # Draw robots with improved styling
        for robot_id, robot in self.robots.items():
            self.draw_robot(robot)
        
        # Draw legend with improved styling
        self.draw_legend()
        
        # Update status
        self.update_status()
    
    def draw_grid(self):
        """Draw a subtle grid in the background"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Vertical lines
        for x in range(0, width, 50):
            self.canvas.create_line(x, 0, x, height, fill="#e0e0e0", tags="grid")
        
        # Horizontal lines
        for y in range(0, height, 50):
            self.canvas.create_line(0, y, width, y, fill="#e0e0e0", tags="grid")
    
    def draw_robot(self, robot: Robot):
        """Draw a robot on the canvas with improved visuals"""
        x, y = robot.position[0], -robot.position[1]
        cx = x * self.scale + self.center_x
        cy = y * self.scale + self.center_y
        
        # Robot color based on ID for better distinction
        colors = ["#e74c3c", "#3498db", "#9b59b6", "#1abc9c", "#f39c12", "#d35400"]
        robot_color = colors[robot.id % len(colors)]
        
        # Base robot appearance with shadow
        radius = 14
        self.canvas.create_oval(
            cx-radius+2, cy-radius+2, cx+radius+2, cy+radius+2,
            fill="#555555", outline="", tags=f"robot_shadow_{robot.id}"
        )
        
        self.canvas.create_oval(
            cx-radius, cy-radius, cx+radius, cy+radius,
            fill=robot_color, outline="#2c3e50", width=1.5,
            tags=f"robot_{robot.id}"
        )
        
        # Robot ID with improved styling
        self.canvas.create_text(
            cx, cy,
            text=str(robot.id),
            fill="white",
            font=("Segoe UI", 9, "bold"),
            tags=f"robot_label_{robot.id}"
        )
        
        # Status indicator with improved styling
        status_radius = 5
        status_colors = {
            "idle": "#95a5a6",
            "moving": "#2ecc71",
            "waiting": "#f1c40f",
            "charging": "#3498db",
            "error": "#e74c3c"
        }
        status_color = status_colors.get(robot.status, "#e74c3c")
        
        self.canvas.create_oval(
            cx+radius-8, cy+radius-8,
            cx+radius-8+status_radius*2, cy+radius-8+status_radius*2,
            fill=status_color, outline="#2c3e50", width=1,
            tags=f"robot_status_{robot.id}"
        )
        
        # Selection highlight with improved styling
        if robot.id == self.selected_robot:
            self.canvas.create_oval(
                cx-radius-4, cy-radius-4,
                cx+radius+4, cy+radius+4,
                outline="#f1c40f", width=3,
                tags=f"robot_highlight_{robot.id}"
            )
            
            # Draw path to destination if selected
            if robot.path:
                self.draw_robot_path(robot)
    
    def draw_robot_path(self, robot: Robot):
        """Draw the path for a selected robot"""
        vertices = self.nav_graph.get_vertices(self.current_level)
        path_points = []
        
        for vertex_idx in robot.path:
            vertex = vertices[vertex_idx]
            x = vertex[0] * self.scale + self.center_x
            y = -vertex[1] * self.scale + self.center_y
            path_points.extend([x, y])
        
        if len(path_points) >= 4:
            # Draw path line
            self.canvas.create_line(
                *path_points,
                fill="#f1c40f",
                width=2,
                dash=(5, 3),
                tags=f"robot_path_{robot.id}"
            )
            
            # Draw path markers
            for i in range(0, len(path_points), 2):
                x, y = path_points[i], path_points[i+1]
                self.canvas.create_oval(
                    x-3, y-3, x+3, y+3,
                    fill="#f1c40f", outline="#d35400",
                    tags=f"path_marker_{robot.id}_{i//2}"
                )
    
    def draw_legend(self):
        """Draw a perfectly aligned legend with consistent spacing"""
        legend_x = 20
        legend_y = 20
        box_width = 200
        item_height = 24  # Increased for better spacing
        padding = 12
        
        # Draw legend box with subtle shadow and rounded corners
        self.canvas.create_rectangle(
            legend_x+2, legend_y+2, legend_x+box_width+2, legend_y+118,
            fill="#e0e0e0", outline="", tags="legend_shadow"
        )
        self.canvas.create_rectangle(
            legend_x, legend_y, legend_x+box_width, legend_y+116,
            fill="white", outline="#bdc3c7", width=1,
            tags="legend_box"
        )
        
        # Legend header (centered)
        self.canvas.create_text(
            legend_x + box_width//2, legend_y + padding,
            text="LEGEND", 
            fill="#2c3e50",
            font=("Segoe UI", 10, "bold"),
            tags="legend_header"
        )
        
        # Legend items data (color, text, radius, is_robot)
        items = [
            ("#27ae60", "Charging Station", 8, False),
            ("#3498db", "Named Vertex", 8, False),
            ("#e74c3c", "Unnamed Vertex", 8, False),
            ("", "Robot (with status)", 0, True),
            ("#2ecc71", "Moving", 6, False),
            ("#f1c40f", "Waiting", 6, False),
            ("#3498db", "Charging", 6, False),
            ("#95a5a6", "Idle", 6, False)
        ]
        
        for i, (color, text, radius, is_robot) in enumerate(items):
            y_pos = legend_y + padding + 20 + (i * item_height)
            
            if is_robot:
                # Draw robot example with status indicator
                robot_x = legend_x + 12
                self.canvas.create_oval(
                    robot_x, y_pos-8,
                    robot_x+16, y_pos+8,
                    fill="#e74c3c", outline="#2c3e50", width=1,
                    tags="legend_robot"
                )
                self.canvas.create_text(
                    robot_x+8, y_pos,
                    text="1", fill="white", font=("Segoe UI", 8, "bold"),
                    tags="legend_robot_label"
                )
                # Status indicator
                self.canvas.create_oval(
                    robot_x+12, y_pos+4,
                    robot_x+16, y_pos+8,
                    fill="#2ecc71", outline="#27ae60", width=1,
                    tags="legend_robot_status"
                )
            else:
                # Draw colored circle
                circle_x = legend_x + 12
                self.canvas.create_oval(
                    circle_x, y_pos-radius,
                    circle_x+radius*2, y_pos+radius,
                    fill=color, outline="#2c3e50", width=1,
                    tags=f"legend_item_{i}"
                )
            
            # Text label (perfectly aligned to same baseline)
            text_x = legend_x + 36  # Consistent left alignment
            self.canvas.create_text(
                text_x, y_pos,
                text=text, 
                anchor=tk.W,  # West anchor for left alignment
                fill="#2c3e50",
                font=("Segoe UI", 9),
                tags=f"legend_text_{i}"
            )

    def update_status(self):
        """Update the system status display"""
        status_text = (
            f"System: {'Running' if self.animation_running else 'Paused'}\n"
            f"Robots: {len(self.robots)}\n"
            f"Level: {self.current_level}\n"
            f"Zoom: {self.zoom_level:.1f}x"
        )
        self.status_label.config(text=status_text)
    
    def on_mousewheel(self, event):
        """Handle mouse wheel for zooming"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def on_canvas_click(self, event):
        """Handle canvas click events according to problem statement"""
        # Check if we clicked on a vertex
        clicked_vertex = None
        for x, y, idx in self.vertex_positions:
            distance = sqrt((event.x - x)**2 + (event.y - y)**2)
            if distance <= 10:  # Clicked near a vertex
                clicked_vertex = idx
                break
        
        # Check if we clicked on a robot
        clicked_robot = None
        for robot_id, robot in self.robots.items():
            x, y = robot.position[0], -robot.position[1]
            cx = x * self.scale + self.center_x
            cy = y * self.scale + self.center_y
            distance = sqrt((event.x - cx)**2 + (event.y - cy)**2)
            if distance <= 12:  # Clicked on a robot
                clicked_robot = robot_id
                break
        
        # Behavior according to problem statement
        if clicked_vertex is not None:
            vertex = self.nav_graph.get_vertex_by_index(self.current_level, clicked_vertex)
            position = (vertex[0], vertex[1])
            
            if clicked_robot is None:  # Clicked on vertex, not robot
                if self.selected_robot is None:
                    # First click - spawn new robot
                    self.spawn_robot(position)
                else:
                    # Second click - set destination for selected robot
                    self.assign_destination(self.selected_robot, position)
                    self.selected_robot = None  # Deselect after assignment
            else:
                # Clicked on both vertex and robot (edge case) - treat as robot selection
                self.select_robot(clicked_robot)
        
        elif clicked_robot is not None:
            # Clicked only on robot - select it
            self.select_robot(clicked_robot)
    
    def on_canvas_release(self, event):
        """Handle canvas release events"""
        self.pan_start_x = None
        self.pan_start_y = None
    
    def spawn_robot(self, position: Tuple[float, float]):
        """Spawn a new robot at the specified position"""
        new_robot = Robot(self.next_robot_id, position)
        self.robots[self.next_robot_id] = new_robot
        self.next_robot_id += 1
        log_system_event("Robot spawned", f"ID: {new_robot.id} at {position}")
        self.draw_graph()
    
    def select_robot(self, robot_id: int):
        """Select a robot by its ID"""
        self.selected_robot = robot_id
        log_system_event("Robot selected", f"ID: {robot_id}")
        self.update_robot_info()
        self.draw_graph()
    
    def clear_selection(self):
        """Clear the current robot selection"""
        self.selected_robot = None
        self.update_robot_info()
        self.draw_graph()
    
    def assign_destination(self, robot_id: int, destination: Tuple[float, float]):
        if robot_id not in self.robots:
            log_system_event("Warning", f"Invalid robot ID: {robot_id}")
            return
            
        robot = self.robots[robot_id]
        start_idx = self.find_closest_vertex(robot.position)
        end_idx = self.find_closest_vertex(destination)
        
        if start_idx == end_idx:
            log_system_event("Warning", "Robot already at destination")
            return
        
        path = self.nav_graph.find_path(self.current_level, start_idx, end_idx)
        
        if not path:
            log_system_event("Warning", "No valid path found")
            return
        
        robot.set_destination(destination, path)
        self.update_robot_info()
        self.draw_graph()
    
    def change_level(self, level_name: str):
        log_system_event("Level changed", f"to {level_name}")
        self.current_level = level_name
        self.reset_view()
        
    def update_robot_info(self):
        """Update the robot information display"""
        if self.selected_robot is None:
            self.robot_info_label.config(text="No robot selected")
        else:
            robot = self.robots[self.selected_robot]
            info = (
                f"Robot ID: {robot.id}\n"
                f"Status: {robot.status}\n"
                f"Position: {robot.position}\n"
                f"Destination: {robot.destination if robot.destination else 'None'}"
            )
            self.robot_info_label.config(text=info)
    
    
    def zoom_in(self):
        """Zoom in on the graph"""
        self.zoom_level *= 1.2
        self.draw_graph()
    
    def zoom_out(self):
        """Zoom out from the graph"""
        self.zoom_level /= 1.2
        self.draw_graph()
    
    def reset_view(self):
        """Reset zoom and pan to default"""
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.draw_graph()
    
    def pan(self, event):
        """Pan the view based on mouse movement"""
        if not hasattr(self, 'pan_start_x'):
            self.pan_start_x = event.x
            self.pan_start_y = event.y
        
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        
        self.offset_x += dx
        self.offset_y += dy
        
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        
        self.draw_graph()

    def start_animation(self):
        """Start the animation loop"""
        self.animation_running = True
        self.animate_robots()
    
    def stop_animation(self):
        """Stop the animation loop"""
        self.animation_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
    
    def animate_robots(self):
        """Update robot positions and redraw"""
        if not self.animation_running:
            return
            
        any_robot_moved = False
        
        # Update all robot positions
        for robot in self.robots.values():
            if robot.status == "moving":
                robot.update_position()
                any_robot_moved = True
        
        # Redraw if any robot moved
        if any_robot_moved:
            self.draw_graph()
        
        # Schedule next animation frame
        self.after_id = self.root.after(50, self.animate_robots)
    
    def assign_destination(self, robot_id: int, destination: Tuple[float, float]):
        """Assign a destination to a robot with pathfinding"""
        if robot_id not in self.robots:
            return
            
        robot = self.robots[robot_id]
        
        # Find closest vertex to robot's current position
        start_idx = self.find_closest_vertex(robot.position)
        end_idx = self.find_closest_vertex(destination)
        
        if start_idx == end_idx:
            return  # Already at destination
        
        # Find path
        path = self.nav_graph.find_path(self.current_level, start_idx, end_idx)
        
        if path:
            robot.set_destination(destination, path)
            self.update_robot_info()
    
    def find_closest_vertex(self, position: Tuple[float, float]) -> int:
        """Find the index of the vertex closest to given position"""
        vertices = self.nav_graph.get_vertices(self.current_level)
        min_dist = float('inf')
        closest_idx = 0
        
        for i, vertex in enumerate(vertices):
            dist = sqrt((position[0] - vertex[0])**2 + (position[1] - vertex[1])**2)
            if dist < min_dist:
                min_dist = dist
                closest_idx = i
                
        return closest_idx
    