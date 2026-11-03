import os
from flask import Flask, render_template, request, jsonify
from algorithm import RescueGraph
from database import save_route, get_recent_routes, DatabaseUnavailable

app = Flask(__name__)
graph = RescueGraph()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate_route", methods=["POST"])
def calculate_route():
    data = request.get_json(silent=True) or {}
    source = data.get("source")
    destination = data.get("destination")
    algorithm = data.get("algorithm", "dijkstra").lower()

    if not source or not destination:
        return jsonify({"error": "Missing source or destination."}), 400
    if source not in graph.graph or destination not in graph.graph:
        return jsonify({"error": "Invalid source or destination node."}), 404
    if algorithm not in ("dijkstra", "astar"):
        return jsonify({"error": "Algorithm must be dijkstra or astar."}), 400

    if algorithm == "astar":
        path, total_cost, nodes_explored = graph.a_star_search(source, destination)
    else:
        path, total_cost, nodes_explored = graph.dijkstra(source, destination)

    if not path:
        return jsonify({"error": "No valid route found."}), 404

    # Oracle PL/SQL function calculates ETA; Python fallback keeps routing usable
    # when Oracle is not configured or temporarily unavailable.
    fallback_eta = round((total_cost / 40.0) * 60, 2)
    db_result = save_route(
        source=source,
        destination=destination,
        algorithm=algorithm.upper(),
        path=" -> ".join(path),
        distance_km=round(total_cost, 2),
        fallback_eta=fallback_eta,
        nodes_explored=nodes_explored
    )

    return jsonify({
        "success": True,
        "algorithm_used": algorithm.upper(),
        "distance": round(total_cost, 2),
        "eta": db_result.get("eta", fallback_eta),
        "nodes_explored": nodes_explored,
        "path": path,
        "coordinates": [graph.coordinates.get(node, [0, 0]) for node in path],
        "database": db_result
    })


@app.route("/route_history", methods=["GET"])
def route_history():
    try:
        return jsonify({"success": True, "routes": get_recent_routes()})
    except DatabaseUnavailable as exc:
        return jsonify({"success": False, "error": str(exc), "routes": []}), 503


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "true").lower() == "true", port=5000)
