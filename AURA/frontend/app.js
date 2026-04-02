const API_BASE = 'http://localhost:5000';

// Canvas Setup
const canvas = document.getElementById('grid-canvas');
const ctx = canvas.getContext('2d');
const GRID_SIZE = 50;
let CELL_SIZE = 10;

// Resize canvas dynamically
function resizeCanvas() {
    const container = canvas.parentElement;
    const size = Math.min(container.clientWidth, container.clientHeight) - 40;
    canvas.width = size;
    canvas.height = size;
    CELL_SIZE = size / GRID_SIZE;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// State
let gridData = [];
let dronesData = [];
let survivorsData = [];
let logsData = [];

// API Polling
async function fetchState() {
    try {
        const [gridRes, dronesRes, survivorsRes, logsRes] = await Promise.all([
            fetch(`${API_BASE}/grid`).then(res => res.json()),
            fetch(`${API_BASE}/drones`).then(res => res.json()),
            fetch(`${API_BASE}/survivors`).then(res => res.json()),
            fetch(`${API_BASE}/logs`).then(res => res.json())
        ]);

        gridData = gridRes.grid;
        dronesData = dronesRes.drones;
        survivorsData = survivorsRes.survivors;
        logsData = logsRes.logs;

        updateDashboard();
    } catch (err) {
        console.error("Error fetching state from backend:", err);
    }
}

// Draw Map
function drawGrid() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let x = 0; x < GRID_SIZE; x++) {
        for (let y = 0; x < gridData.length && y < gridData[x].length; y++) {
            const risk = gridData[x][y];
            if (risk === "SAFE") ctx.fillStyle = "rgba(31, 41, 55, 1)";
            else if (risk === "MEDIUM") ctx.fillStyle = "rgba(245, 158, 11, 0.4)";
            else if (risk === "HIGH") ctx.fillStyle = "rgba(239, 68, 68, 0.6)";
            
            ctx.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1);
        }
    }
}

// Update Map markers overlay
function updateMarkers() {
    const droneLayer = document.getElementById('drone-markers');
    const survivorLayer = document.getElementById('survivor-markers');
    
    // Update Drones
    droneLayer.innerHTML = '';
    dronesData.forEach(d => {
        const dEl = document.createElement('div');
        dEl.className = 'drone-marker';
        dEl.dataset.id = d.id;
        dEl.style.left = `${(d.x / GRID_SIZE) * 100}%`;
        dEl.style.top = `${(d.y / GRID_SIZE) * 100}%`;
        droneLayer.appendChild(dEl);
    });

    // Update Survivors
    survivorLayer.innerHTML = '';
    survivorsData.forEach(s => {
        const sEl = document.createElement('div');
        sEl.className = 'survivor-marker';
        sEl.style.left = `${(s.x / GRID_SIZE) * 100}%`;
        sEl.style.top = `${(s.y / GRID_SIZE) * 100}%`;
        survivorLayer.appendChild(sEl);
    });
}

// Update Drone Cards
function updateDronesList() {
    const list = document.getElementById('drones-list');
    list.innerHTML = '';
    const template = document.getElementById('drone-card-template');

    dronesData.forEach(d => {
        const clone = template.content.cloneNode(true);
        clone.querySelector('.d-id').textContent = d.id;
        clone.querySelector('.d-state').textContent = d.state;
        
        // Color state
        if(d.state === 'SCANNING') clone.querySelector('.d-state').className = 'val d-state text-blue';
        if(d.state === 'IDLE') clone.querySelector('.d-state').className = 'val d-state text-orange';
        if(d.state === 'RETURNING') clone.querySelector('.d-state').className = 'val d-state text-green';

        clone.querySelector('.d-battery').style.width = `${d.battery}%`;
        clone.querySelector('.d-batt-txt').textContent = `${Math.round(d.battery)}%`;
        
        // Battery color
        if(d.battery < 20) clone.querySelector('.d-battery').style.backgroundColor = 'var(--accent-red)';
        else if(d.battery < 50) clone.querySelector('.d-battery').style.backgroundColor = 'var(--accent-orange)';

        clone.querySelector('.d-loc').textContent = `[${d.x}, ${d.y}]`;

        // Buttons
        clone.querySelector('.scan-btn').addEventListener('click', () => sendAction('/action/scan', {id: d.id}));
        clone.querySelector('.recall-btn').addEventListener('click', () => sendAction('/action/recall', {id: d.id}));

        list.appendChild(clone);
    });
}

// Update Logs
function updateLogs() {
    const container = document.getElementById('logs-container');
    container.innerHTML = '';
    
    [...logsData].reverse().forEach(log => {
        const lEl = document.createElement('div');
        lEl.className = 'log-entry';
        
        const time = new Date(log.timestamp * 1000).toLocaleTimeString();
        lEl.innerHTML = `<span class="log-timestamp">[${time}]</span> ${log.message}`;
        container.appendChild(lEl);
    });
}

// Update Header Stats
function updateStats() {
    document.getElementById('stat-drones').textContent = `${dronesData.length}/4`;
    document.getElementById('stat-survivors').textContent = survivorsData.length;
    
    let highRiskCount = 0;
    for (let x = 0; x < gridData.length; x++) {
        for (let y = 0; y < gridData[x].length; y++) {
            if (gridData[x][y] === 'HIGH') highRiskCount++;
        }
    }
    document.getElementById('stat-risk').textContent = highRiskCount;
}

// Global update function
function updateDashboard() {
    drawGrid();
    updateMarkers();
    updateDronesList();
    updateLogs();
    updateStats();
}

// Action Dispatcher
async function sendAction(endpoint, payload) {
    try {
        await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        fetchState(); // Force immediate update
    } catch (err) {
        console.error(`Failed to execute ${endpoint}:`, err);
    }
}

// Global Buttons
document.getElementById('btn-swarm').addEventListener('click', () => sendAction('/action/swarm', {}));
document.getElementById('btn-reset').addEventListener('click', () => sendAction('/mission/reset', {}));

// Init
setInterval(fetchState, 1000);
fetchState();
