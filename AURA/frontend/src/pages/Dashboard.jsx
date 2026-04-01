import React, { useState, useEffect } from 'react';
import { 
  Shield, Globe, Activity, Download 
} from 'lucide-react';
import MapView from '../components/MapView';
import DroneCard from '../components/DroneCard';
import { fetchAllData, resetMission, exportReport, scanDrone } from '../services/api';

function Dashboard() {
  const [gridState, setGridState] = useState([]);
  const [drones, setDrones] = useState([]);
  const [survivors, setSurvivors] = useState([]);
  const [logs, setLogs] = useState([]);
  const [missionId, setMissionId] = useState('N/A');
  
  const [connected, setConnected] = useState(false);
  const [missionUptime, setMissionUptime] = useState(0);
  const [activeManualDrone, setActiveManualDrone] = useState(null);

  // --- MISSION LIFECYCLE ---
  useEffect(() => {
    const initMission = async () => {
        try {
            const data = await resetMission();
            setMissionId(data.mission_id);
            setMissionUptime(0);
        } catch (e) {
            console.error("Mission Initialization Failed");
        }
    };
    initMission();
  }, []);

  // --- POLLING LOGIC ---
  useEffect(() => {
    const updateAll = async () => {
        try {
            const data = await fetchAllData();
            setGridState(data.grid);
            setDrones(data.drones);
            setSurvivors(data.survivors);
            setLogs(data.logs);
            setConnected(true);
            setMissionUptime(prev => prev + 1);
        } catch (err) {
            setConnected(false);
        }
    };

    updateAll();
    const interval = setInterval(updateAll, 1000); // 1s Heartbeat
    return () => clearInterval(interval);
  }, []);

  const handleExport = async () => {
      const data = await exportReport();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AURA_REPORT_${missionId}.json`;
      a.click();
  };

  return (
    <div className="flex h-screen w-full bg-[#0b1326] text-[#dbe2fd] font-['Inter'] overflow-hidden">
      
      {/* Sidebar Navigation */}
      <nav className="w-16 bg-[#131b2e] border-r border-[#4be277]/10 flex flex-col items-center py-8 gap-8">
          <div className="bg-[#4be277] p-2.5 rounded-lg shadow-lg shadow-[#4be277]/20"><Shield className="w-6 h-6 text-[#0b1326]" /></div>
          <div className="flex flex-col gap-6 mt-8">
              <NavIcon icon={<Globe className="w-5 h-5"/>} active />
              <NavIcon icon={<Activity className="w-5 h-5"/>} />
              <button onClick={handleExport} className="p-2 text-[#869585] hover:text-[#4be277] transition-all"><Download className="w-5 h-5" /></button>
          </div>
      </nav>

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 bg-[#131b2e] border-b border-[#4be277]/10 flex items-center justify-between px-8 shadow-md relative z-10">
            <div className="flex items-center gap-6">
                <div className="flex flex-col">
                    <span className="text-[10px] font-black tracking-[0.4em] text-[#869585]">AURA COMMAND</span>
                    <span className="text-[8px] font-bold text-[#4be277]/60">MISSION_ID: {missionId}</span>
                </div>
                <div className="flex items-center gap-2 text-xs font-mono">
                    <span className={`w-2 h-2 rounded-full ${connected ? 'bg-[#4be277]' : 'bg-[#ff3131]'}`}></span>
                    {connected ? 'LINK_ACTIVE' : 'LINK_OFFLINE'}
                </div>
            </div>
            
            <div className="flex flex-col items-end">
                <span className="text-[8px] font-black text-[#869585] tracking-widest uppercase italic">Uptime</span>
                <span className="text-sm font-bold font-mono">{new Date(missionUptime * 1000).toISOString().substr(11, 8)}</span>
            </div>
        </header>

        <main className="flex-1 flex overflow-hidden">
            <section className="flex-1 h-full relative overflow-hidden bg-black">
                {activeManualDrone && <div className="absolute top-6 left-6 z-[2000] bg-red-600 px-4 py-2 rounded text-xs font-bold animate-pulse shadow-xl border border-red-400/50">REDIRECTING AURA-0{activeManualDrone}: CLICK MAP</div>}
                <MapView drones={drones} grid={gridState} survivors={survivors} />
            </section>

            {/* Side Panel */}
            <section className="w-[350px] bg-[#0b1326] p-6 overflow-y-auto flex flex-col gap-6 border-l border-white/5">
                <div className="flex justify-between items-center bg-[#131b2e] p-3 rounded border border-white/5 shadow-inner">
                    <h3 className="text-[10px] font-black uppercase text-[#869585] tracking-widest">Drone Fleet HUD</h3>
                    <div className="flex items-center gap-2 px-2 py-1 bg-[#4be277]/10 border border-[#4be277]/20 rounded">
                        <span className="w-1.5 h-1.5 bg-[#4be277] rounded-full animate-pulse"></span>
                        <span className="text-[9px] font-bold text-[#4be277] uppercase">Active</span>
                    </div>
                </div>

                <div className="grid gap-4">
                    {drones.map(drone => (
                        <DroneCard 
                            key={drone.id} 
                            drone={drone} 
                            onManualClick={setActiveManualDrone}
                        />
                    ))}
                </div>

                <div className="flex-1 bg-[#0d162b] p-5 rounded border border-white/5 font-mono text-[10px] overflow-hidden flex flex-col shadow-inner">
                    <span className="text-[#869585] mb-4 uppercase tracking-[0.2em] text-[9px] font-black border-b border-white/5 pb-2">Tactical Event Log</span>
                    <div className="flex-1 overflow-y-auto space-y-2 scrollbar-thin scrollbar-thumb-white/10">
                        {logs.slice().reverse().map((l, i) => (
                            <div key={i} className="flex gap-3 leading-relaxed group">
                                <span className="text-[#4be277]/40 font-bold shrink-0">{new Date(l.timestamp*1000).toLocaleTimeString([], { hour12: false })}</span>
                                <span className="text-white/70 group-hover:text-white transition-colors">{l.message}</span>
                            </div>
                        ))}
                        {logs.length === 0 && <span className="text-white/20 italic uppercase text-[8px] tracking-widest">Waiting for uplink...</span>}
                    </div>
                </div>
            </section>
        </main>
      </div>
    </div>
  );
}

function NavIcon({ icon, active }) {
    return <div className={`p-3 rounded-xl transition-all cursor-pointer ${active ? 'bg-[#4be277]/10 text-[#4be277] shadow-[0_0_15px_rgba(75,226,119,0.1)]' : 'text-[#869585] hover:bg-white/5 hover:text-white'}`}>{icon}</div>
}

export default Dashboard;
