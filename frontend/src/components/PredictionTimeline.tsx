import React from "react";
import { RiskAssessment } from "../types";
import { AlertCircle, AlertTriangle } from "lucide-react";

interface PredictionTimelineProps {
  assessment?: RiskAssessment;
}

export const PredictionTimeline: React.FC<PredictionTimelineProps> = ({ assessment }) => {
  const probability = assessment?.accident_probability ?? 0;
  const level = assessment?.risk_level ?? "low";

  return (
    <div className="glass-card flex flex-col p-6">
      <h3 className="mb-4 text-xs font-bold uppercase tracking-wider text-slate-500">Accident Prediction Cascade</h3>
      {probability > 0.5 ? (
        <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-red-950 bg-red-950/20 p-6 text-center animate-pulse">
          <AlertCircle className="mb-3 h-12 w-12 text-red-500" />
          <h4 className="text-base font-black text-red-400">IMMINENT COLLISION DANGER</h4>
          <p className="mt-2 text-xs text-slate-400 max-w-[280px]">
            {assessment?.recommended_intervention ?? "Intervention Command Dispatched"}
          </p>
        </div>
      ) : (
        <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-slate-900 bg-slate-950/30 p-6 text-center">
          <AlertTriangle className="mb-3 h-12 w-12 text-slate-600" />
          <h4 className="text-sm font-bold text-slate-400">Normal Operations</h4>
          <p className="mt-2 text-xs text-slate-500">No upcoming collision trajectories projected.</p>
        </div>
      )}
    </div>
  );
};
