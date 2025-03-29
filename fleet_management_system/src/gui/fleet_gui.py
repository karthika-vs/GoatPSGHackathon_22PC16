import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Tuple, Any
from math import sqrt
from ..models.nav_graph import NavGraph
from ..models.robot import Robot

class FleetManagementGUI:
    def __init__(self, root: tk.Tk, nav_graph_file: str):
        self.root = root
        self.root.title("Fleet Management System")
        
        # Load navigation graph
        self.nav_graph = NavGraph(nav_graph_file)
        
        # Set current level (initialize this first)
        self.current_level = self.nav_graph.get_level_names()[0]
        
        # Robot management
        self.robots = {}  # robot_id: Robot object
        self.next_robot_id = 1
        self.selected_robot = None
        
        # Create main frames
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for visualization
        self.canvas = tk.Canvas(self.main_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create control panel
        self.control_frame = ttk.Frame(self.main_frame, width=200)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        # Setup controls
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
        
        # Draw the initial graph
        self.draw_graph()
        # Add animation control
        self.animation_running = False
        self.after_id = None
        
        # Start animation loop
        self.start_animation()
    
    def setup_controls(self):
        """Set up the control panel"""
        # Level selection
        ttk.Label(self.control_frame, text="Level:").pack(pady=(10, 0))
        self.level_var = tk.StringVar(value=self.current_level)
        level_menu = ttk.OptionMenu(
            self.control_frame,
            self.level_var,
            self.current_level,
            *self.nav_graph.get_level_names(),
            command=self.change_level
        )
        level_menu.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # Zoom controls
        ttk.Label(self.control_frame, text="View Controls:").pack()
        zoom_frame = ttk.Frame(self.control_frame)
        zoom_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(zoom_frame, text="+", command=self.zoom_in, width=3).pack(side=tk.LEFT)
        ttk.Button(zoom_frame, text="-", command=self.zoom_out, width=3).pack(side=tk.LEFT)
        ttk.Button(zoom_frame, text="Reset", command=self.reset_view).pack(side=tk.RIGHT)
        
        # Robot controls
        ttk.Label(self.control_frame, text="Robot Controls:").pack(pady=(10, 0))
        ttk.Button(self.control_frame, text="Clear Selection", command=self.clear_selection).pack(fill=tk.X, padx=5, pady=5)
        
        # Robot info display
        self.robot_info_frame = ttk.LabelFrame(self.control_frame, text="Robot Info")
        self.robot_info_frame.pack(fill=tk.X, padx=5, pady=5)
        self.robot_info_label = ttk.Label(self.robot_info_frame, text="No robot selected")
        self.robot_info_label.pack(padx=5, pady=5)
    
    # [Rest of the methods remain the same as in the previous implementation]
    # ...
    
    def draw_graph(self):
        """Draw the navigation graph with robots"""
        self.canvas.delete("all")
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
        
        # Draw lanes
        for lane in lanes:
            start_idx, end_idx = lane[0], lane[1]
            start = vertices[start_idx]
            end = vertices[end_idx]
            
            x1 = start[0] * self.scale + self.center_x
            y1 = -start[1] * self.scale + self.center_y
            x2 = end[0] * self.scale + self.center_x
            y2 = -end[1] * self.scale + self.center_y
            
            self.canvas.create_line(x1, y1, x2, y2, fill="gray", width=2, arrow=tk.LAST)
            
            # Add direction indicator
            mid_x, mid_y = (x1 + x2)/2, (y1 + y2)/2
            self.canvas.create_oval(mid_x-2, mid_y-2, mid_x+2, mid_y+2, fill="blue")
        
        # Draw vertices
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
            
            color = "green" if is_charger else "blue" if name else "red"
            radius = 10 if is_charger else 8 if name else 6
            
            # Draw vertex
            self.canvas.create_oval(
                cx-radius, cy-radius, cx+radius, cy+radius,
                fill=color, outline="black", width=2,
                tags=f"vertex_{i}"
            )
            
            # Add label if available
            if name:
                self.canvas.create_text(
                    cx, cy-radius-10,
                    text=name,
                    fill="black",
                    font=("Arial", 10, "bold"),
                    tags=f"label_{i}"
                )
        
        # Draw robots
        for robot_id, robot in self.robots.items():
            self.draw_robot(robot)
        
        # Draw legend
        self.draw_legend()
    
    def draw_robot(self, robot: Robot):
        """Draw a robot on the canvas"""
        x, y = robot.position[0], -robot.position[1]
        cx = x * self.scale + self.center_x
        cy = y * self.scale + self.center_y
        
        # Draw robot as a colored circle with ID
        radius = 12
        self.canvas.create_oval(
            cx-radius, cy-radius, cx+radius, cy+radius,
            fill=robot.color, outline="black", width=2,
            tags=f"robot_{robot.id}"
        )
        
        # Draw robot ID
        self.canvas.create_text(
            cx, cy,
            text=str(robot.id),
            fill="white",
            font=("Arial", 8, "bold"),
            tags=f"robot_label_{robot.id}"
        )
        
        # Highlight selected robot
        if robot.id == self.selected_robot:
            self.canvas.create_oval(
                cx-radius-3, cy-radius-3, cx+radius+3, cy+radius+3,
                outline="yellow", width=3,
                tags=f"robot_highlight_{robot.id}"
            )
    
    def draw_legend(self):
        """Draw the legend on the canvas"""
        legend_x = 20
        legend_y = 20
        
        self.canvas.create_rectangle(legend_x-10, legend_y-10, legend_x+180, legend_y+110, fill="white", outline="black")
        self.canvas.create_text(legend_x+85, legend_y, text="Legend", font=("Arial", 10, "bold"))
        
        # Legend items
        items = [
            ("green", 10, "Charging Station"),
            ("blue", 8, "Named Location"), 
            ("red", 6, "Unnamed Location"),
            ("blue", 4, "Lane Direction"),
            ("*", 12, "Robot (colored)")
        ]
        
        for i, (color, radius, text) in enumerate(items):
            y_offset = 20 + i*20
            if color == "blue" and radius == 4:  # Lane direction indicator
                self.canvas.create_oval(
                    legend_x, legend_y+y_offset-2,
                    legend_x+4, legend_y+y_offset+2,
                    fill=color
                )
            elif color == "*":  # Robot example
                self.canvas.create_oval(
                    legend_x, legend_y+y_offset-radius,
                    legend_x+radius*2, legend_y+y_offset+radius,
                    fill="red", outline="black"
                )
                self.canvas.create_text(
                    legend_x+radius, legend_y+y_offset,
                    text="1", fill="white", font=("Arial", 8, "bold")
                )
            else:  # Vertex examples
                self.canvas.create_oval(
                    legend_x, legend_y+y_offset-radius,
                    legend_x+radius*2, legend_y+y_offset+radius,
                    fill=color, outline="black"
                )
            self.canvas.create_text(legend_x+60, legend_y+y_offset, text=text, anchor=tk.W)
    
    def on_canvas_click(self, event):
        """Handle canvas click events for robot spawning and selection"""
        # Check if we clicked on a vertex
        clicked_vertex = None
        for x, y, idx in self.vertex_positions:
            distance = sqrt((event.x - x)**2 + (event.y - y)**2)
            if distance <= 10:  # Clicked near a vertex
                clicked_vertex = idx
                break
        
        if clicked_vertex is not None:
            vertex = self.nav_graph.get_vertex_by_index(self.current_level, clicked_vertex)
            position = (vertex[0], vertex[1])
            
            if self.selected_robot is None:
                # Spawn a new robot at this vertex
                self.spawn_robot(position)
            else:
                # Assign this vertex as destination for selected robot
                self.assign_destination(self.selected_robot, position)
        
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
        
        if clicked_robot is not None:
            self.select_robot(clicked_robot)
    
    def on_canvas_release(self, event):
        """Handle canvas release events"""
        self.pan_start_x = None
        self.pan_start_y = None
    
    def spawn_robot(self, position: Tuple[float, float]):
        """Spawn a new robot at the given position"""
        new_robot = Robot(self.next_robot_id, position)
        self.robots[self.next_robot_id] = new_robot
        self.next_robot_id += 1
        
        # Log the spawn event
        print(f"Spawned robot {new_robot.id} at position {position}")
        
        # Redraw to show the new robot
        self.draw_graph()
    
    def select_robot(self, robot_id: int):
        """Select a robot"""
        self.selected_robot = robot_id
        self.update_robot_info()
        self.draw_graph()  # Redraw to show selection highlight
    
    def clear_selection(self):
        """Clear the current robot selection"""
        self.selected_robot = None
        self.update_robot_info()
        self.draw_graph()
    
    def assign_destination(self, robot_id: int, destination: Tuple[float, float]):
        """Assign a destination to a robot"""
        if robot_id in self.robots:
            robot = self.robots[robot_id]
            robot.set_destination(destination)
            robot.set_status("moving")
            
            # Log the destination assignment
            print(f"Assigned destination {destination} to robot {robot_id}")
            
            self.update_robot_info()
            self.draw_graph()
    
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
    
    def change_level(self, level_name: str):
        """Change the displayed level"""
        self.current_level = level_name
        self.reset_view()
    
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
    