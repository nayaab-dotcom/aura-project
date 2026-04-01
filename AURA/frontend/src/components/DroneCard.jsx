import React from 'react';
import { useNavigate } from 'react-router-dom';
import { recallDrone, scanDrone } from '../services/api';

function DroneCard({ drone, onManualClick }) {
    const navigate = useNavigate();
    
    return (
        <div className="bg-[#171f33]/60 p-4 rounded border border-white/5 flex flex-col gap-3">
            <div className="flex justify-between items-center">
                <span className="text-[10px] font-bold uppercase tracking-wider text-[#869585]">
                    AURA-0{drone.id} <span className="ml-2 text-white/40">// {drone.mode}</span>
                </span>
                <span className={`text-[9px] font-black px-2 py-0.5 rounded ${
                    drone.state === 'RETURNING' ? 'bg-blue-500/20 text-blue-400' : 
                    drone.state === 'SCANNING' ? 'bg-[#4be277]/20 text-[#4be277]' : 
                    'bg-white/10 text-white/40'
                }`}>
                    {drone.state}
                </span>
            </div>

            <div className="flex items-center gap-3">
                <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
                    <div 
                        className={`h-full transition-all duration-500 ${
                            drone.battery < 25 ? 'bg-red-500 animate-pulse' : 'bg-[#4be277]'
                        }`} 
                        style={{ width: `${drone.battery}%` }}
                    ></div>
                </div>
                <span className="text-[9px] font-mono text-white/60">{Math.round(drone.battery)}%</span>
            </div>

            <div className="grid grid-cols-3 gap-2">
                <button 
                  onClick={() => scanDrone(drone.id)} 
                  className="py-1.5 text-[8px] font-black border border-white/10 rounded uppercase hover:bg-white/5 transition-all">
                  Scan
                </button>
                <button 
                  onClick={() => recallDrone(drone.id)} 
                  className="py-1.5 text-[8px] font-black border border-blue-500/30 text-blue-400 rounded uppercase hover:bg-blue-500/10 transition-all">
                  Recall
                </button>
                <button 
                  onClick={() => navigate(`/drone/${drone.id}`)} 
                  className="py-1.5 text-[8px] font-black border border-[#4be277]/30 text-[#4be277] rounded uppercase hover:bg-[#4be277]/10 transition-all">
                  Feed
                </button>
            </div>
            
            <button 
              onClick={() => onManualClick(drone.id)} 
              className="w-full py-1.5 text-[8px] font-black bg-white/5 border border-white/5 rounded uppercase hover:bg-white/10 transition-all tracking-widest text-white/50">
              Manual Override
            </button>
        </div>
    );
}

export default DroneCard;
