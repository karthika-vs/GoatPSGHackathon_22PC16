import tkinter as tk
from tkinter import filedialog
from src.gui.fleet_gui import NavigationGraphVisualizer

def main():
    root = tk.Tk()
    root.geometry("900x700")
    
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