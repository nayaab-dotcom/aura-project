import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Zap, Shield, Target } from 'lucide-react';
import { fetchDroneFrame } from '../services/api';

function DroneView() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [frameUrl, setFrameUrl] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const updateFrame = async () => {
            try {
                const data = await fetchDroneFrame(id);
                setFrameUrl(data.frame);
                setLoading(false);
            } catch (err) {
                console.error("Frame acquisition failed:", err);
            }
        };

        updateFrame();
        const interval = setInterval(updateFrame, 1000); // 1s Heartbeat
        return () => clearInterval(interval);
    }, [id]);

    return (
        <div className="min-h-screen bg-[#0b1326] text-white p-8 font-['Inter'] flex flex-col overflow-hidden">
            <header className="flex items-center justify-between mb-8 px-4">
                <button 
                  onClick={() => navigate('/')} 
                  className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded uppercase text-[10px] font-black tracking-widest hover:bg-white/10 transition-all text-[#869585] hover:text-white">
                    <ChevronLeft className="w-4 h-4" /> Return to Dashboard
                </button>
                <div className="flex flex-col items-end">
                    <div className="flex items-center gap-3">
                        <span className="w-2 h-2 rounded-full bg-[#4be277] animate-pulse"></span>
                        <span className="text-[10px] font-black uppercase text-white tracking-[0.3em]">AURA-0{id} Live feed</span>
                    </div>
                    <span className="text-[8px] text-[#4be277]/60 font-black tracking-[0.3em] uppercase">Status: Optical Link Active</span>
                </div>
            </header>

            <main className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Simulated Camera Feed */}
                <section className="lg:col-span-3 rounded-lg border border-white/10 overflow-hidden relative shadow-2xl shadow-blue-500/5 bg-[#131b2e]">
                    {loading ? (
                        <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
                            <div className="w-12 h-0.5 bg-[#4be277] animate-scan-slow opacity-50"></div>
                            <span className="text-[10px] font-black tracking-widest uppercase animate-pulse text-[#4be277]">Establishing Signal...</span>
                        </div>
                    ) : (
                        <div className="w-full h-full relative">
                            <img 
                                src={frameUrl} 
                                alt={`AURA-0${id} Camera`} 
                                className="w-full h-full object-cover transition-opacity duration-1000" 
                            />
                            {/* Overlay UI */}
                            <div className="absolute inset-0 pointer-events-none">
                                <div className="absolute inset-0 border-[2px] border-[#4be277]/20 m-8 animate-pulse"></div>
                                <div className="absolute top-12 left-12 flex flex-col gap-1 text-[10px] font-mono text-[#4be277]">
                                    <span className="font-bold uppercase tracking-[0.2em] bg-black/40 px-2 py-1">REC // UNIT: AURA_0{id}</span>
                                    <span className="opacity-60 bg-black/40 px-2 py-1 mt-1">{new Date().toISOString()}</span>
                                </div>
                                <div className="absolute bottom-12 right-12 flex flex-col gap-1 text-[10px] font-mono text-white/50 text-right">
                                    <span className="bg-black/40 px-2 py-1">GPS: 12.97°N, 77.59°E</span>
                                    <span className="bg-black/40 px-2 py-1 mt-1 font-bold">ALT: 12.5M</span>
                                </div>
                                {/* CRT Effect Overlay (Subtle) */}
                                <div className="absolute inset-0 opacity-10 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,118,0.06))] bg-[length:100%_4px,3px_100%]"></div>
                            </div>
                        </div>
                    )}
                </section>

                <section className="flex flex-col gap-6">
                    {/* Unit HUD */}
                    <div className="bg-[#131b2e] p-6 rounded-lg border border-white/5 h-full flex flex-col shadow-inner">
                        <h3 className="text-[10px] font-black uppercase text-[#869585] mb-8 tracking-[0.2em] leading-loose">Mission Analytics</h3>
                        
                        <div className="space-y-8 flex-1">
                            <HUDItem icon={<Zap className="w-4 h-4 text-blue-400" />} label="Sat Uplink" value="98.4%" />
                            <HUDItem icon={<Shield className="w-4 h-4 text-[#4be277]" />} label="Integrity" value="NOMINAL" />
                            <HUDItem icon={<Target className="w-4 h-4 text-red-400" />} label="Target Lock" value="IDLE" />
                        </div>

                        <div className="mt-auto pt-8 border-t border-white/5">
                            <div className="flex flex-col gap-2">
                                <span className="text-[8px] font-black text-white/30 uppercase tracking-widest">Tactical Protocol</span>
                                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded text-[9px] text-red-400 font-mono italic">
                                    HARD_KILL_PROTOCOL_INACTIVE
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}

function HUDItem({ icon, label, value }) {
    return (
        <div className="flex items-center gap-5 group">
            <div className="bg-white/5 p-3 rounded group-hover:bg-white/10 transition-colors">{icon}</div>
            <div className="flex flex-col">
                <span className="text-[10px] font-black text-white/30 uppercase tracking-[0.1em] mb-1">{label}</span>
                <span className="text-xs font-bold font-mono tracking-[0.2em] text-white">{value}</span>
            </div>
        </div>
    );
}

export default DroneView;
