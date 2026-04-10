// Use same-origin by default; override with Vite env when needed.
const BASE_URL = import.meta.env.VITE_API_BASE || window.location.origin;

const jsonOrThrow = async (res) => {
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Request failed ${res.status}: ${text || res.statusText}`);
    }
    return res.json();
};

export async function fetchAllData() {
    // Unified state endpoint works for both dashboard/app.py and backend/app.py
    const res = await fetch(`${BASE_URL}/api/state`);
    const data = await jsonOrThrow(res);
    return {
        grid: data.grid || [],
        drones: data.drones || [],
        survivors: data.survivors || [],
        logs: data.logs || [],
        stats: data.stats || {}
    };
}

export async function resetMission() {
    const res = await fetch(`${BASE_URL}/api/reset`, { method: 'POST' });
    return jsonOrThrow(res);
}

export async function recallDrone(id) {
    const res = await fetch(`${BASE_URL}/api/recall/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    });
    return jsonOrThrow(res);
}

export async function scanDrone(id) {
    const res = await fetch(`${BASE_URL}/api/scan/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    });
    return jsonOrThrow(res);
}

export async function controlDrone(type, id, payload = {}) {
    // Backend exposes /control/mode|move|pause (no /api prefix)
    const res = await fetch(`${BASE_URL}/control/${type}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, ...payload })
    });
    return jsonOrThrow(res);
}

export async function fetchDroneFrame(id) {
    // Frame feed lives at /drone/<id>/frame
    const res = await fetch(`${BASE_URL}/drone/${id}/frame`);
    return jsonOrThrow(res);
}

export async function exportReport() {
    const res = await fetch(`${BASE_URL}/report`);
    return jsonOrThrow(res);
}
