import React from "react";
import { Navigation } from "lucide-react";

interface GPSMapProps {
  lat?: number;
  lon?: number;
}

export const GPSMap: React.FC<GPSMapProps> = ({ lat = 28.6139, lon = 77.2090 }) => {
  return (
    <div className="glass-card flex flex-col p-6">
      <h3 className="mb-4 text-xs font-bold uppercase tracking-wider text-slate-500">Live GPS Navigation</h3>
      <div className="flex flex-1 items-center justify-center gap-4 rounded-xl bg-slate-950/60 border border-slate-900 h-28 p-4">
        <Navigation className="h-10 w-10 text-cyan-400 animate-pulse flex-shrink-0" />
        <div className="flex-1 font-mono text-xs">
          <div className="flex justify-between border-b border-slate-900 py-1">
            <span className="text-slate-500 font-bold">LATITUDE</span>
            <span className="text-white font-extrabold">{lat.toFixed(5)}</span>
          </div>
          <div className="flex justify-between py-1">
            <span className="text-slate-500 font-bold">LONGITUDE</span>
            <span className="text-white font-extrabold">{lon.toFixed(5)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
