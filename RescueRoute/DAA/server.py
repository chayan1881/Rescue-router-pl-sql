from flask import Flask, render_template, request, jsonify
from algorithm import RescueGraph

app = Flask(__name__)
graph = RescueGraph()

@app.route('/')
def index():
    """Renders the frontend emergency control panel interface."""
    return render_template('index.html')

@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    """REST API endpoint to process pathfinding requests from the client."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Invalid JSON payload."}), 400

    source = data.get('source')
    destination = data.get('destination')
    algorithm = data.get('algorithm', 'dijkstra')
    
    if not source or not destination:
        return jsonify({"error": "Missing required source or destination parameters."}), 400

    if source not in graph.graph or destination not in graph.graph:
        return jsonify({"error": "Invalid source or destination node specified."}), 404

    # Execute selected pathfinding algorithm
    if algorithm == 'astar':
        path, total_cost, nodes_explored = graph.a_star_search(source, destination)
    else:
        path, total_cost, nodes_explored = graph.dijkstra(source, destination)
        
    if not path:
        return jsonify({"error": "No valid route found between selected nodes."}), 404

    # Calculate estimated time of arrival (ETA) assuming 40 km/h average emergency vehicle speed
    eta = round((total_cost / 40.0) * 60, 2)

    return jsonify({
        "success": True,
        "algorithm_used": algorithm.upper(),
        "distance": round(total_cost, 2),
        "eta": eta,
        "nodes_explored": nodes_explored,
        "path": path,
        "coordinates": [graph.coordinates.get(n, [0, 0]) for n in path]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)