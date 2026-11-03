import heapq
import itertools

class RescueGraph:
    def __init__(self):
        # Weighted directed adjacency list representing Chandigarh road network distances (in km)
        self.graph = {
            "Sector_17": {"PGI_Hospital": 4.2, "Industrial_Area": 6.8},
            "PGI_Hospital": {"Sector_17": 4.2, "Industrial_Area": 5.1, "University_Gate": 3.5},
            "Industrial_Area": {"Sector_17": 6.8, "PGI_Hospital": 5.1, "University_Gate": 4.6},
            "University_Gate": {"PGI_Hospital": 3.5, "Industrial_Area": 4.6}
        }
        
        # Landmark Hub Coordinates (WGS84)
        self.coordinates = {
            "Sector_17": [30.7333, 76.7794],       # Sector 17 Plaza
            "PGI_Hospital": [30.7671, 76.7783],     # PGI Emergency
            "Industrial_Area": [30.7131, 76.7915],  # Industrial Area Phase 1
            "University_Gate": [30.7627, 76.7720]   # Panjab University Gate
        }

        # Detailed road-following segment paths (Waypoints for Leaflet Polyline)
        self.edge_paths = {
            ("Sector_17", "PGI_Hospital"): [
                [30.7333, 76.7794],
                [30.7380, 76.7750],
                [30.7450, 76.7700],
                [30.7550, 76.7760],
                [30.7620, 76.7760],
                [30.7671, 76.7783]
            ],
            ("PGI_Hospital", "Sector_17"): [
                [30.7671, 76.7783],
                [30.7620, 76.7760],
                [30.7550, 76.7760],
                [30.7450, 76.7700],
                [30.7380, 76.7750],
                [30.7333, 76.7794]
            ],
            ("Sector_17", "Industrial_Area"): [
                [30.7333, 76.7794],
                [30.7250, 76.7820],
                [30.7200, 76.7860],
                [30.7131, 76.7915]
            ],
            ("Industrial_Area", "Sector_17"): [
                [30.7131, 76.7915],
                [30.7200, 76.7860],
                [30.7250, 76.7820],
                [30.7333, 76.7794]
            ],
            ("PGI_Hospital", "Industrial_Area"): [
                [30.7671, 76.7783],
                [30.7500, 76.7850],
                [30.7300, 76.7880],
                [30.7131, 76.7915]
            ],
            ("Industrial_Area", "PGI_Hospital"): [
                [30.7131, 76.7915],
                [30.7300, 76.7880],
                [30.7500, 76.7850],
                [30.7671, 76.7783]
            ],
            ("PGI_Hospital", "University_Gate"): [
                [30.7671, 76.7783],
                [30.7650, 76.7750],
                [30.7627, 76.7720]
            ],
            ("University_Gate", "PGI_Hospital"): [
                [30.7627, 76.7720],
                [30.7650, 76.7750],
                [30.7671, 76.7783]
            ],
            ("Industrial_Area", "University_Gate"): [
                [30.7131, 76.7915],
                [30.7380, 76.7800],
                [30.7627, 76.7720]
            ],
            ("University_Gate", "Industrial_Area"): [
                [30.7627, 76.7720],
                [30.7380, 76.7800],
                [30.7131, 76.7915]
            ]
        }

    def get_path_cost(self, path):
        total_cost = 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            weight = self.graph.get(u, {}).get(v)
            if weight is None:
                return float('inf')
            total_cost += weight
        return total_cost

    def shortest_multi_sector_tour(self, start_node="Sector_17"):
        nodes = list(self.graph.keys())
        if start_node in nodes:
            nodes.remove(start_node)
        
        best_path = []
        min_cost = float('inf')
        
        for perm in itertools.permutations(nodes):
            candidate_path = [start_node] + list(perm)
            cost = self.get_path_cost(candidate_path)
            if cost < min_cost:
                min_cost = cost
                best_path = candidate_path
                
        return best_path, min_cost, len(best_path)

    def dijkstra(self, start, target):
        queue = [(0, start, [start])]
        visited = set()
        while queue:
            cost, current, path = heapq.heappop(queue)
            if current in visited:
                continue
            visited.add(current)
            if current == target:
                return path, cost, len(visited)
            for neighbor, weight in self.graph.get(current, {}).items():
                if neighbor not in visited:
                    heapq.heappush(queue, (cost + weight, neighbor, path + [neighbor]))
        return [], float("inf"), len(visited)

    def a_star_search(self, start, target):
        return self.dijkstra(start, target)