import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default Leaflet marker icons not loading in React
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerIcon2x,
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
});

// Linear Mapping: Grid (0,0) -> Bangalore [12.9716, 77.5946]
const BASE_LAT = 12.9716;
const BASE_LNG = 77.5946;
const SCALE = 0.0001; // ~11m precision

const project = (x, y) => [BASE_LAT + (y * SCALE), BASE_LNG + (x * SCALE)];
const survivorIcon = new L.DivIcon({
  className: 'survivor-icon',
  html: '<div class="survivor-dot"></div>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
});

function MapView({ drones, grid, survivors, onSurvivorClick }) {
  // Optimization: Filter grid to only render non-zero risk cells
  const riskCells = useMemo(() => {
    const cells = [];
    if (!grid) return cells;
    grid.forEach((row, y) => {
      row.forEach((cell, x) => {
        if (cell > 0) {
          cells.push({ x, y, risk: cell });
        }
      });
    });
    return cells;
  }, [grid]);

  return (
    <MapContainer 
      center={[BASE_LAT + (25 * SCALE), BASE_LNG + (25 * SCALE)]} 
      zoom={18} 
      className="w-full h-full"
      zoomControl={false}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />

      {/* Optimized Grid Layer (Non-Zero Only) - circular heat pulses */}
      {riskCells.map((cell, i) => (
        <CircleMarker
          key={`cell-${i}`}
          center={project(cell.x + 0.5, cell.y + 0.5)}
          radius={6}
          pathOptions={{
            color: 'transparent',
            fillColor: cell.risk === 2 ? '#ff3131' : '#ffbf00',
            fillOpacity: cell.risk === 2 ? 0.45 : 0.25
          }}
        />
      ))}

      {/* Survivor Markers */}
      {survivors.map(s => (
        <Marker 
          key={`surv-${s.id}`} 
          position={project(s.x, s.y)} 
          icon={survivorIcon}
          eventHandlers={{
            click: () => onSurvivorClick && onSurvivorClick(s)
          }}
        >
          <Popup>
            <div className="text-xs font-mono">
                <b>LIFE SIGN DETECTED</b><br/>
                ID: {s.id}<br/>
                Coord: {s.x}, {s.y}
            </div>
          </Popup>
        </Marker>
      ))}

      {/* Drone Markers & Paths */}
      {drones.map(drone => {
        const pos = project(drone.x, drone.y);
        const pathCoords = drone.path ? drone.path.map(p => project(p[0], p[1])) : [];

        return (
          <React.Fragment key={`drone-${drone.id}`}>
            {pathCoords.length > 0 && (
                <Polyline 
                    positions={pathCoords} 
                    pathOptions={{ color: '#4be277', weight: 2, dashArray: '5, 5', opacity: 0.5 }} 
                />
            )}
            <Marker 
                position={pos}
                icon={new L.DivIcon({
                    className: 'custom-drone-icon',
                    html: `
                        <div style="
                            width: 12px; height: 12px; 
                            background: ${drone.mode === 'MANUAL' ? '#ff3131' : '#4be277'}; 
                            border-radius: 50%; border: 2px solid white;
                            box-shadow: 0 0 10px ${drone.mode === 'MANUAL' ? '#ff3131' : '#4be277'};
                        "></div>
                        <span style="
                            position: absolute; top: -15px; left: 15px; 
                            color: white; font-family: Inter; font-weight: bold; font-size: 9px;
                            white-space: nowrap; text-shadow: 1px 1px 2px black;
                        ">AURA-0${drone.id}</span>
                    `
                })}
            />
          </React.Fragment>
        );
      })}
    </MapContainer>
  );
}

export default MapView;
