import React from "react";

interface LaneDetectionProps {
  lanePosition?: number;
}

export const LaneDetection: React.FC<LaneDetectionProps> = ({ lanePosition = 0 }) => {
  // lanePosition is from -0.5 to 0.5 (where 0 is center)
  const offset = lanePosition * 100; // in percent

  return (
    <div className="glass-card flex flex-col p-6">
      <h3 className="mb-4 text-xs font-bold uppercase tracking-wider text-slate-500">Active Lane Alignment</h3>
      <div className="relative flex flex-1 items-center justify-center rounded-xl bg-slate-950/60 border border-slate-900 h-28 overflow-hidden">
        {/* Left Lane Line */}
        <div className="absolute left-6 top-0 bottom-0 w-1 bg-slate-800" />
        {/* Right Lane Line */}
        <div className="absolute right-6 top-0 bottom-0 w-1 bg-slate-800" />
        {/* Center Dotted Line */}
        <div className="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 border-l border-dashed border-slate-700 h-full" />
        
        {/* Car Indicator */}
        <div
          className="absolute h-10 w-6 rounded bg-gradient-to-t from-blue-600 to-cyan-400 border border-cyan-300 transition-all duration-100 flex items-center justify-center text-[8px] font-black text-white"
          style={{ left: `calc(50% + ${offset}% - 12px)` }}
        >
          🚘
        </div>
      </div>
    </div>
  );
};
