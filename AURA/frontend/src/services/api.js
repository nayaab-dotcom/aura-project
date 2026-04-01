const BASE_URL = 'http://localhost:5000';

export async function fetchAllData() {
    const urls = ['/grid', '/drones', '/survivors', '/logs'];
    const responses = await Promise.all(urls.map(url => fetch(`${BASE_URL}${url}`)));
    const data = await Promise.all(responses.map(res => res.json()));
    
    return {
        grid: data[0].grid,
        drones: data[1].drones,
        survivors: data[2].survivors,
        logs: data[3].logs
    };
}

export async function resetMission() {
    const res = await fetch(`${BASE_URL}/mission/reset`, { method: 'POST' });
    return res.json();
}

export async function recallDrone(id) {
    const res = await fetch(`${BASE_URL}/action/recall`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    });
    return res.json();
}

export async function scanDrone(id) {
    const res = await fetch(`${BASE_URL}/action/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
    });
    return res.json();
}

export async function controlDrone(type, id, payload = {}) {
    const res = await fetch(`${BASE_URL}/control/${type}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, ...payload })
    });
    return res.json();
}

export async function fetchDroneFrame(id) {
    const res = await fetch(`${BASE_URL}/drone/${id}/frame`);
    return res.json();
}

export async function exportReport() {
    const res = await fetch(`${BASE_URL}/report`);
    return res.json();
}

