"""
AURA Simple Dashboard

A simple Flask-based web dashboard for AURA visualization.
Run with: python dashboard/app.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from flask import Flask, render_template_string, jsonify
from main import AURASystem
import threading
import time

app = Flask(__name__)

aura_system = AURASystem()

def run_simulation():
    while True:
        aura_system._simulation_tick()
        time.sleep(1.0)

sim_thread = threading.Thread(target=run_simulation, daemon=True)
sim_thread.start()

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AURA - Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #0b1326; 
            color: #dbe2fd;
            min-height: 100vh;
        }
        .header {
            background: #131b2e;
            padding: 15px 30px;
            border-bottom: 1px solid rgba(75, 226, 119, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #4be277;
            font-size: 24px;
            letter-spacing: 3px;
        }
        .status {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            background: #4be277;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 20px;
            padding: 20px;
            height: calc(100vh - 70px);
        }
        .main-content {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
        }
        .stat-card {
            background: #131b2e;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .stat-card h3 {
            color: #869585;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }
        .stat-card .value {
            font-size: 28px;
            font-weight: bold;
            color: #fff;
        }
        .stat-card .value.green { color: #4be277; }
        .stat-card .value.red { color: #ff3131; }
        .stat-card .value.yellow { color: #ffbf00; }
        .map-container {
            flex: 1;
            background: #131b2e;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            overflow: hidden;
        }
        .map-container h2 {
            color: #869585;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 15px;
        }
        #grid-canvas {
            width: 100%;
            height: calc(100% - 40px);
            image-rendering: pixelated;
        }
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .drone-list {
            background: #131b2e;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .drone-list h2 {
            color: #869585;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 15px;
        }
        .drone-card {
            background: rgba(255, 255, 255, 0.03);
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .drone-card .header {
            display: flex;
            justify-content: space-between;
            padding: 0;
            background: none;
            border: none;
            margin-bottom: 10px;
        }
        .drone-id { font-weight: bold; color: #4be277; }
        .drone-state { 
            font-size: 10px; 
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }
        .state-idle { background: rgba(255,255,255,0.1); color: #869585; }
        .state-scanning { background: rgba(75,226,119,0.2); color: #4be277; }
        .state-returning { background: rgba(59,130,246,0.2); color: #3b82f6; }
        .drone-info {
            font-size: 11px;
            color: #869585;
            margin-bottom: 8px;
        }
        .battery-bar {
            height: 4px;
            background: rgba(255,255,255,0.1);
            border-radius: 2px;
            overflow: hidden;
        }
        .battery-fill {
            height: 100%;
            background: #4be277;
            transition: width 0.3s;
        }
        .battery-low .battery-fill { background: #ff3131; }
        .log-panel {
            flex: 1;
            background: #131b2e;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            overflow-y: auto;
        }
        .log-panel h2 {
            color: #869585;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 15px;
        }
        .log-entry {
            font-family: monospace;
            font-size: 10px;
            padding: 5px 0;
            border-bottom: 1px solid rgba(255,255,255,0.03);
        }
        .log-time { color: #4be277; opacity: 0.6; margin-right: 10px; }
        .log-msg { color: #dbe2fd; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AURA</h1>
        <div class="status">
            <div class="status-dot"></div>
            <span>SYSTEM ONLINE</span>
        </div>
    </div>
    
    <div class="container">
        <div class="main-content">
            <div class="stats">
                <div class="stat-card">
                    <h3>Survivors Found</h3>
                    <div class="value green" id="survivors">0</div>
                </div>
                <div class="stat-card">
                    <h3>Coverage</h3>
                    <div class="value" id="coverage">0%</div>
                </div>
                <div class="stat-card">
                    <h3>High Risk</h3>
                    <div class="value red" id="high-risk">0</div>
                </div>
                <div class="stat-card">
                    <h3>Mission Time</h3>
                    <div class="value" id="duration">0s</div>
                </div>
            </div>
            
            <div class="map-container">
                <h2>Risk Heatmap</h2>
                <canvas id="grid-canvas"></canvas>
            </div>
        </div>
        
        <div class="sidebar">
            <div class="drone-list">
                <h2>Drone Fleet</h2>
                <div id="drones"></div>
            </div>
            
            <div class="log-panel">
                <h2>Event Log</h2>
                <div id="logs"></div>
            </div>
        </div>
    </div>
    
    <script>
        const GRID_SIZE = 50;
        const COLORS = {
            0: '#4be277',
            1: '#ffbf00',
            2: '#ff3131'
        };
        
        async function fetchData() {
            const res = await fetch('/api/state');
            return res.json();
        }
        
        function drawGrid(grid) {
            const canvas = document.getElementById('grid-canvas');
            const ctx = canvas.getContext('2d');
            
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * 2;
            canvas.height = rect.height * 2;
            
            const cellW = canvas.width / GRID_SIZE;
            const cellH = canvas.height / GRID_SIZE;
            
            ctx.fillStyle = '#0b1326';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            for (let y = 0; y < GRID_SIZE; y++) {
                for (let x = 0; x < GRID_SIZE; x++) {
                    const cell = grid[y] ? grid[y][x] : 0;
                    if (cell > 0) {
                        ctx.fillStyle = COLORS[cell] || COLORS[0];
                        ctx.globalAlpha = cell === 2 ? 0.6 : 0.3;
                        ctx.fillRect(x * cellW, y * cellH, cellW, cellH);
                    }
                }
            }
            ctx.globalAlpha = 1;
        }
        
        function updateDrones(drones) {
            const container = document.getElementById('drones');
            container.innerHTML = drones.map(d => {
                const stateClass = 'state-' + d.state.toLowerCase();
                const batteryLow = d.battery < 25 ? 'battery-low' : '';
                return `
                    <div class="drone-card">
                        <div class="header">
                            <span class="drone-id">AURA-0${d.id}</span>
                            <span class="drone-state ${stateClass}">${d.state}</span>
                        </div>
                        <div class="drone-info">Position: [${d.x}, ${d.y}]</div>
                        <div class="drone-info ${batteryLow}">Battery: ${d.battery}%</div>
                        <div class="battery-bar">
                            <div class="battery-fill" style="width: ${d.battery}%"></div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        function updateLogs(logs) {
            const container = document.getElementById('logs');
            container.innerHTML = logs.slice(-15).reverse().map(l => {
                const time = new Date(l.timestamp * 1000).toLocaleTimeString();
                return `<div class="log-entry"><span class="log-time">${time}</span><span class="log-msg">${l.message}</span></div>`;
            }).join('');
        }
        
        async function update() {
            const data = await fetchData();
            
            document.getElementById('survivors').textContent = data.stats.survivors_found;
            document.getElementById('coverage').textContent = data.stats.coverage_percent + '%';
            document.getElementById('high-risk').textContent = data.stats.high_risk_cells;
            document.getElementById('duration').textContent = Math.floor(data.duration) + 's';
            
            drawGrid(data.grid);
            updateDrones(data.drones);
            updateLogs(data.logs);
        }
        
        setInterval(update, 1000);
        update();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)

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

if __name__ == '__main__':
    print("=" * 50)
    print("AURA Dashboard - Starting...")
    print("Open http://localhost:8501 in your browser")
    print("=" * 50)
    app.run(host='0.0.0.0', port=8501, debug=False)
