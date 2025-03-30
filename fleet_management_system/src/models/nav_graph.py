import json
from typing import Dict, List, Tuple, Any
import heapq

class NavGraph:
    def __init__(self, file_path: str):
        with open(file_path) as f:
            self.graph_data = json.load(f)
        
        self.levels = self.graph_data.get("levels", {})
        self.building_name = self.graph_data.get("building_name", "Unknown")
    
    def get_level_names(self) -> List[str]:
        return list(self.levels.keys())
    
    def get_vertices(self, level_name: str) -> List[Tuple[float, float, Dict[str, Any]]]:
        level = self.levels.get(level_name, {})
        return level.get("vertices", [])
    
    def get_lanes(self, level_name: str) -> List[List[int]]:
        level = self.levels.get(level_name, {})
        return level.get("lanes", [])
    
    def get_vertex_by_index(self, level_name: str, index: int) -> Tuple[float, float, Dict[str, Any]]:
        vertices = self.get_vertices(level_name)
        if 0 <= index < len(vertices):
            return vertices[index]
        return None
    

    #So here i have used the A* algorithm to find the shortest path as it will be the optimal algorithm in this case
    def find_path(self, level_name: str, start_idx: int, end_idx: int) -> Tuple[List[Tuple[float, float]], List[int]]:
        vertices = self.get_vertices(level_name)
        lanes = self.get_lanes(level_name)
        
        graph = {i: [] for i in range(len(vertices))}
        for lane in lanes:
            a, b = lane[0], lane[1]
            graph[a].append(b)
            graph[b].append(a)
        
        open_set = []
        heapq.heappush(open_set, (0, start_idx))
        came_from = {}
        g_score = {i: float('inf') for i in range(len(vertices))}
        g_score[start_idx] = 0
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == end_idx:
                path_indices = []
                while current in came_from:
                    path_indices.append(current)
                    current = came_from[current]
                path_indices.reverse()
                path_indices.append(end_idx)  

                path_coords = []
                for idx in path_indices:
                    if 0 <= idx < len(vertices):
                        path_coords.append(vertices[idx][:2])
                
                return path_coords, path_indices
            
            for neighbor in graph[current]:
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    heapq.heappush(open_set, (tentative_g_score, neighbor))
        
        return [], [] 