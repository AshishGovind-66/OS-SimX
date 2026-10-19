from flask import Flask, render_template, request, jsonify
from src.scheduler import simulate_cpu
from src.memory import simulate_page_replacement
from src.deadlock import detect_deadlock, bankers_safe_sequence

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/schedule")
def schedule_api():
    payload = request.get_json(silent=True) or {}
    try:
        algorithm = payload.get("algorithm", "RR")
        quantum = int(payload.get("quantum", 2))
        processes = payload.get("processes", [])
        result = simulate_cpu(processes, algorithm, quantum)
        return jsonify(result)
    except (ValueError, TypeError, KeyError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/memory")
def memory_api():
    payload = request.get_json(silent=True) or {}
    try:
        refs = payload.get("references", [])
        frames = int(payload.get("frames", 3))
        algorithm = payload.get("algorithm", "LRU")
        return jsonify(simulate_page_replacement(refs, frames, algorithm))
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/deadlock")
def deadlock_api():
    payload = request.get_json(silent=True) or {}
    try:
        allocation = payload.get("allocation", [])
        request_matrix = payload.get("request", [])
        available = payload.get("available", [])
        result = detect_deadlock(allocation, request_matrix, available)
        max_claim = payload.get("max_claim")
        if max_claim is not None:
            result["bankers"] = bankers_safe_sequence(allocation, max_claim, available)
        return jsonify(result)
    except (ValueError, TypeError, IndexError) as exc:
        return jsonify({"error": str(exc)}), 400

if __name__ == "__main__":
    app.run(debug=True)
