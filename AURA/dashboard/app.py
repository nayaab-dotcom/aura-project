"""
AURA Dashboard Server

A Flask-based web dashboard for AURA visualization that serves the Vanilla HTML/CSS frontend.
Run with: python dashboard/app.py
"""

import sys
import os

# Add root to path so we can import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, send_from_directory, jsonify
from main import AURASystem
import threading
import time

# Create Flask app. Point static and template files to ../frontend
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')

aura_system = AURASystem()

def run_simulation():
    while True:
        aura_system._simulation_tick()
        time.sleep(1.0)

sim_thread = threading.Thread(target=run_simulation, daemon=True)
sim_thread.start()

@app.route('/api/state')
def api_state():
    return jsonify(aura_system.get_state())

@app.route('/api/reset', methods=['POST'])
def api_reset():
    aura_system.reset()
    return jsonify({'status': 'reset'})

@app.route('/api/scan/<int:drone_id>', methods=['POST'])
def api_scan(drone_id):
    result = aura_system.scan_drone(drone_id)
    return jsonify({'status': 'success' if result else 'error'})

@app.route('/api/recall/<int:drone_id>', methods=['POST'])
def api_recall(drone_id):
    result = aura_system.recall_drone(drone_id)
    return jsonify({'status': 'success' if result else 'error'})

@app.route('/api/swarm', methods=['POST'])
def api_swarm():
    # Placeholder for future swarm logic
    aura_system._log("COMMAND: Swarm pattern requested (Not yet fully implemented)")
    # For now, just send all drones to scan
    for drone in aura_system.drones:
        aura_system.scan_drone(drone.drone_id)
    return jsonify({'status': 'success'})


# --- SPA Fallback (serve React build for client-side routes) ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def spa(path):
    """
    Serve the Vite-built frontend for any non-API route so deep links like
    /drone/1 work when refreshed.
    """
    static_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(static_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    print("=" * 50)
    print("AURA Dashboard - Starting...")
    print("Open http://localhost:8501 in your browser")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8501, debug=False)
