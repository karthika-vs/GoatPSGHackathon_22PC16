import json
import tkinter as tk
from tkinter import ttk
from math import floor

class NavigationGraphVisualizer:
    def __init__(self, root, nav_graph_file):
        self.root = root
        self.root.title("Fleet Management System - Navigation Graph Visualizer")
        
        # Load the navigation graph
        with open(nav_graph_file) as f:
            self.nav_graph = json.load(f)
        
        # Get the first level (assuming there's at least one level)
        self.level_name, self.level_data = next(iter(self.nav_graph["levels"].items()))
        
        # Create canvas for visualization
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add zoom controls
        self.zoom_frame = ttk.Frame(root)
        self.zoom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(self.zoom_frame, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT)
        ttk.Button(self.zoom_frame, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT)
        ttk.Button(self.zoom_frame, text="Reset View", command=self.reset_view).pack(side=tk.LEFT)
        
        # Add level selector if multiple levels exist
        if len(self.nav_graph["levels"]) > 1:
            self.level_var = tk.StringVar(value=self.level_name)
            level_menu = ttk.OptionMenu(
                self.zoom_frame, 
                self.level_var, 
                self.level_name, 
                *self.nav_graph["levels"].keys(),
                command=self.change_level
            )
            level_menu.pack(side=tk.RIGHT, padx=5)
        
        # Initialize zoom parameters
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Draw the initial graph
        self.draw_graph()
        
        # Bind mouse events for panning
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)
    
    def change_level(self, level_name):
        """Change the displayed level"""
        self.level_name = level_name
        self.level_data = self.nav_graph["levels"][level_name]
        self.reset_view()
    
    def draw_graph(self):
        """Draw the navigation graph on the canvas"""
        self.canvas.delete("all")
        
        vertices = self.level_data["vertices"]
        lanes = self.level_data["lanes"]
        
        # Calculate bounds to center the view
        if not vertices:
            return
            
        x_coords = [v[0] for v in vertices]
        y_coords = [-v[1] for v in vertices]  # Invert y-axis for display
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        # Calculate scaling factors to fit the graph in the canvas
        graph_width = max_x - min_x
        graph_height = max_y - min_y
        
        if graph_width == 0:
            graph_width = 1
        if graph_height == 0:
            graph_height = 1
            
        self.scale_x = (self.canvas.winfo_width() * 0.8) / graph_width
        self.scale_y = (self.canvas.winfo_height() * 0.8) / graph_height
        self.scale = min(self.scale_x, self.scale_y) * self.zoom_level
        
        # Calculate center offset
        center_x = (self.canvas.winfo_width() / 2) - ((min_x + max_x) / 2) * self.scale + self.offset_x
        center_y = (self.canvas.winfo_height() / 2) - ((min_y + max_y) / 2) * self.scale + self.offset_y
        
        # Draw lanes first (so vertices appear on top)
        for lane in lanes:
            start_idx, end_idx = lane[0], lane[1]
            start_x, start_y = vertices[start_idx][0], -vertices[start_idx][1]
            end_x, end_y = vertices[end_idx][0], -vertices[end_idx][1]
            
            # Scale and position coordinates
            x1 = start_x * self.scale + center_x
            y1 = start_y * self.scale + center_y
            x2 = end_x * self.scale + center_x
            y2 = end_y * self.scale + center_y
            
            # Draw the lane
            self.canvas.create_line(x1, y1, x2, y2, fill="gray", width=2, arrow=tk.LAST)
            
            # Add lane direction indicator (small circle at midpoint)
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            self.canvas.create_oval(mid_x-2, mid_y-2, mid_x+2, mid_y+2, fill="blue")
        
        # Draw vertices
        self.vertex_objects = []
        for i, vertex in enumerate(vertices):
            x, y = vertex[0], -vertex[1]  # Invert y-axis
            cx = x * self.scale + center_x
            cy = y * self.scale + center_y
            
            # Determine vertex color and size
            vertex_attrs = vertex[2] if len(vertex) > 2 else {}
            is_charger = vertex_attrs.get("is_charger", False)
            name = vertex_attrs.get("name", "")
            
            if is_charger:
                color = "green"
                radius = 10
            elif name:
                color = "blue"
                radius = 8
            else:
                color = "red"
                radius = 6
                
            # Draw the vertex
            vertex_id = self.canvas.create_oval(
                cx-radius, cy-radius, cx+radius, cy+radius,
                fill=color, outline="black", width=2
            )
            
            # Store vertex information for interaction
            self.vertex_objects.append({
                "id": vertex_id,
                "index": i,
                "x": cx,
                "y": cy,
                "name": name,
                "is_charger": is_charger
            })
            
            # Add vertex name if available
            if name:
                self.canvas.create_text(
                    cx, cy-radius-10,
                    text=name,
                    fill="black",
                    font=("Arial", 10, "bold")
                )
        
        # Add legend
        legend_x = 20
        legend_y = 20
        
        self.canvas.create_rectangle(legend_x-10, legend_y-10, legend_x+150, legend_y+90, fill="white", outline="black")
        self.canvas.create_text(legend_x+70, legend_y, text="Legend", font=("Arial", 10, "bold"))
        
        # Charger
        self.canvas.create_oval(legend_x, legend_y+20, legend_x+10, legend_y+30, fill="green", outline="black")
        self.canvas.create_text(legend_x+60, legend_y+25, text="Charging Station", anchor=tk.W)
        
        # Named location
        self.canvas.create_oval(legend_x, legend_y+40, legend_x+8, legend_y+48, fill="blue", outline="black")
        self.canvas.create_text(legend_x+60, legend_y+44, text="Named Location", anchor=tk.W)
        
        # Unnamed location
        self.canvas.create_oval(legend_x, legend_y+60, legend_x+6, legend_y+66, fill="red", outline="black")
        self.canvas.create_text(legend_x+60, legend_y+63, text="Unnamed Location", anchor=tk.W)
        
        # Lane direction
        self.canvas.create_oval(legend_x, legend_y+80, legend_x+4, legend_y+84, fill="blue")
        self.canvas.create_text(legend_x+60, legend_y+82, text="Lane Direction", anchor=tk.W)
    
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
    from tkinter import filedialog
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