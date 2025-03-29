import json
import tkinter as tk
from tkinter import ttk, filedialog
from math import sqrt

class NavigationGraphVisualizer:
    def __init__(self, root, nav_graph_file):
        self.root = root
        self.root.title("Navigation Graph Visualizer")
        
        # Load the navigation graph
        with open(nav_graph_file) as f:
            self.nav_graph = json.load(f)
        
        # Get the first level
        self.level_name, self.level_data = next(iter(self.nav_graph["levels"].items()))
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add controls
        self.setup_controls()
        
        # Initialize view parameters
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Draw the graph
        self.draw_graph()
        
        # Bind mouse events for navigation only
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)
    
    def setup_controls(self):
        """Set up zoom and level controls"""
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Reset View", command=self.reset_view).pack(side=tk.LEFT)
        
        if len(self.nav_graph["levels"]) > 1:
            self.level_var = tk.StringVar(value=self.level_name)
            level_menu = ttk.OptionMenu(
                control_frame, 
                self.level_var, 
                self.level_name, 
                *self.nav_graph["levels"].keys(),
                command=self.change_level
            )
            level_menu.pack(side=tk.RIGHT, padx=5)
    
    def draw_graph(self):
        """Draw the navigation graph"""
        self.canvas.delete("all")
        vertices = self.level_data["vertices"]
        lanes = self.level_data["lanes"]
        
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
            
            # Determine vertex style
            vertex_attrs = vertex[2] if len(vertex) > 2 else {}
            is_charger = vertex_attrs.get("is_charger", False)
            name = vertex_attrs.get("name", "")
            
            color = "green" if is_charger else "blue" if name else "red"
            radius = 10 if is_charger else 8 if name else 6
            
            # Draw vertex
            self.canvas.create_oval(
                cx-radius, cy-radius, cx+radius, cy+radius,
                fill=color, outline="black", width=2
            )
            
            # Add label if available
            if name:
                self.canvas.create_text(
                    cx, cy-radius-10,
                    text=name,
                    fill="black",
                    font=("Arial", 10, "bold")
                )
        
        # Draw legend
        self.draw_legend()
    
    def draw_legend(self):
        """Draw the legend on the canvas"""
        legend_x = 20
        legend_y = 20
        
        self.canvas.create_rectangle(legend_x-10, legend_y-10, legend_x+150, legend_y+90, fill="white", outline="black")
        self.canvas.create_text(legend_x+70, legend_y, text="Legend", font=("Arial", 10, "bold"))
        
        # Legend items
        items = [
            ("green", 10, "Charging Station"),
            ("blue", 8, "Named Location"), 
            ("red", 6, "Unnamed Location"),
            ("blue", 4, "Lane Direction")
        ]
        
        for i, (color, radius, text) in enumerate(items):
            y_offset = 20 + i*20
            if color == "blue" and radius == 4:  # Lane direction indicator
                self.canvas.create_oval(
                    legend_x, legend_y+y_offset-2,
                    legend_x+4, legend_y+y_offset+2,
                    fill=color
                )
            else:  # Vertex examples
                self.canvas.create_oval(
                    legend_x, legend_y+y_offset-radius,
                    legend_x+radius*2, legend_y+y_offset+radius,
                    fill=color, outline="black"
                )
            self.canvas.create_text(legend_x+60, legend_y+y_offset, text=text, anchor=tk.W)
    
    def change_level(self, level_name):
        """Change the displayed level"""
        self.level_name = level_name
        self.level_data = self.nav_graph["levels"][level_name]
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
    
    def start_pan(self, event):
        """Start panning the view"""
        self.pan_start_x = event.x
        self.pan_start_y = event.y
    
    def pan(self, event):
        """Pan the view based on mouse movement"""
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        
        self.offset_x += dx
        self.offset_y += dy
        
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        
        self.draw_graph()

def main():
    root = tk.Tk()
    root.geometry("900x700")
    
    # Ask user to select a nav_graph file
    nav_graph_file = filedialog.askopenfilename(
        title="Select Navigation Graph JSON File",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    
    if not nav_graph_file:
        return
    
    app = NavigationGraphVisualizer(root, nav_graph_file)
    root.mainloop()

if __name__ == "__main__":
    main()