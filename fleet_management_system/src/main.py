import tkinter as tk
from tkinter import filedialog
from src.gui.fleet_gui import FleetManagementGUI

def main():
    root = tk.Tk()
    root.geometry("1000x800")
    root.title("Fleet Management System")
    
    nav_graph_file = filedialog.askopenfilename(
        title="Select Navigation Graph JSON File",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    
    if not nav_graph_file:
        return
    
    app = FleetManagementGUI(root, nav_graph_file)
    
    # Clean up animation when window closes
    def on_closing():
        app.stop_animation()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()