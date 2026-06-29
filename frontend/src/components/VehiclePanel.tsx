import React, { useState, useEffect } from "react";
import { VehicleTelemetry } from "../types";
import { Compass, Gauge, Sliders, PlayCircle } from "lucide-react";

interface VehiclePanelProps {
  telemetry?: VehicleTelemetry;
  onVehicleTelemetryOverride?: (telemetryState: any) => void;
}

export const VehiclePanel: React.FC<VehiclePanelProps> = ({ telemetry, onVehicleTelemetryOverride }) => {
  const [manualMode, setManualMode] = useState(false);
  const [manualSpeed, setManualSpeed] = useState(60);
  const [manualSteering, setManualSteering] = useState(0);
  const [manualLane, setManualLane] = useState(0);

  // If manual mode is active, override server speed and stability with local slider feedback
  const speed = manualMode ? manualSpeed : (telemetry?.speed ?? 0);
  const stability = manualMode 
    ? Math.max(0, 100 - Math.abs(manualSteering) * 5 - (manualSpeed - 60) * 0.2)
    : (telemetry?.stability_score ?? 100);
  
  const steeringAngle = manualMode ? manualSteering : (telemetry?.steering_angle ?? 0);

  // Send updates to the server when sliders change
  useEffect(() => {
    if (!manualMode || !onVehicleTelemetryOverride) return;

    // Send initial values on switch
    onVehicleTelemetryOverride({
      speed: manualSpeed,
      steering_angle: manualSteering,
      lane_position: manualLane
    });
  }, [manualMode]);

  const handleSpeedChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = Number(e.target.value);
    setManualSpeed(val);
    if (onVehicleTelemetryOverride) {
      onVehicleTelemetryOverride({
        speed: val,
        steering_angle: manualSteering,
        lane_position: manualLane
      });
    }
  };

  const handleSteeringChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = Number(e.target.value);
    setManualSteering(val);
    if (onVehicleTelemetryOverride) {
      onVehicleTelemetryOverride({
        speed: manualSpeed,
        steering_angle: val,
        lane_position: manualLane
      });
    }
  };

  const handleLaneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = Number(e.target.value);
    setManualLane(val);
    if (onVehicleTelemetryOverride) {
      onVehicleTelemetryOverride({
        speed: manualSpeed,
        steering_angle: manualSteering,
        lane_position: val
      });
    }
  };

  return (
    <div className="glass-card flex flex-col p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Vehicle Telemetry Diagnostics</h3>
        
        {/* Toggle simulation override */}
        <button
          onClick={() => setManualMode(!manualMode)}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase transition-all duration-300 ${
            manualMode
              ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
              : "bg-slate-900 text-slate-400 border border-slate-800 hover:border-slate-700"
          }`}
        >
          {manualMode ? (
            <>
              <Sliders className="h-3.5 w-3.5 animate-pulse" />
              <span>Manual Control</span>
            </>
          ) : (
            <>
              <PlayCircle className="h-3.5 w-3.5" />
              <span>Auto Sim Active</span>
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col items-center justify-center rounded-xl bg-slate-950/60 p-5 border border-slate-900 text-center">
          <Gauge className="h-6 w-6 text-cyan-400 mb-2" />
          <span className="text-3xl font-black text-white">{speed.toFixed(0)}</span>
          <span className="text-[10px] text-slate-500 uppercase font-bold mt-1">KM/H SPEED</span>
        </div>
        <div className="flex flex-col items-center justify-center rounded-xl bg-slate-950/60 p-5 border border-slate-900 text-center">
          <Compass className="h-6 w-6 text-emerald-400 mb-2" />
          <span className="text-3xl font-black text-white">{stability.toFixed(0)}%</span>
          <span className="text-[10px] text-slate-500 uppercase font-bold mt-1">STABILITY</span>
        </div>
      </div>

      {/* Manual Sliders UI panel */}
      {manualMode ? (
        <div className="mt-5 space-y-4 rounded-xl bg-slate-950/60 p-4 border border-slate-900">
          <div>
            <div className="flex justify-between text-xs font-bold mb-1.5">
              <span className="text-slate-400">Control Speed (KM/H)</span>
              <span className="text-cyan-400">{manualSpeed} KM/H</span>
            </div>
            <input
              type="range"
              min="0"
              max="150"
              value={manualSpeed}
              onChange={handleSpeedChange}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-bold mb-1.5">
              <span className="text-slate-400">Control Steering Angle</span>
              <span className="text-cyan-400">{manualSteering}°</span>
            </div>
            <input
              type="range"
              min="-45"
              max="45"
              value={manualSteering}
              onChange={handleSteeringChange}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
          </div>

          <div>
            <div className="flex justify-between text-xs font-bold mb-1.5">
              <span className="text-slate-400">Control Lane Alignment</span>
              <span className="text-cyan-400">{manualLane.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="-0.5"
              max="0.5"
              step="0.05"
              value={manualLane}
              onChange={handleLaneChange}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
          </div>
        </div>
      ) : (
        <div className="mt-4 space-y-3">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-slate-400">Steering Input</span>
            <span className="text-white">{steeringAngle.toFixed(1)}°</span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-slate-950">
            <div
              className="h-full rounded-full bg-cyan-400 transition-all duration-300"
              style={{ width: `${Math.min(100, Math.max(0, 50 + steeringAngle * 1.1))}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};
