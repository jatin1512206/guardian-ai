import React from "react";
import { Intervention } from "../types";
import { ShieldAlert, Info } from "lucide-react";

interface InterventionLogProps {
  interventions?: Intervention[];
}

export const InterventionLog: React.FC<InterventionLogProps> = ({ interventions }) => {
  return (
    <div className="glass-card flex flex-col p-6">
      <h3 className="mb-4 text-xs font-bold uppercase tracking-wider text-slate-500">Active Interventions</h3>
      <div className="flex-1 space-y-3 overflow-y-auto max-h-[160px] pr-2">
        {interventions?.map((item, idx) => (
          <div key={idx} className="flex items-start gap-3 rounded-xl border border-slate-900 bg-slate-950/40 p-3 text-xs">
            <ShieldAlert className="h-4.5 w-4.5 text-orange-400 mt-0.5" />
            <div className="flex-1">
              <div className="flex justify-between font-bold text-slate-300">
                <span>{item.action_taken}</span>
                <span className="text-[10px] text-slate-500">{new Date(item.timestamp).toLocaleTimeString()}</span>
              </div>
              <p className="mt-1 text-[10px] text-slate-400">Risk rating reached {item.risk_score}. Safety cascade triggered.</p>
            </div>
          </div>
        ))}
        {(!interventions || interventions.length === 0) && (
          <div className="flex flex-col items-center justify-center text-center py-8 text-xs text-slate-600">
            <Info className="h-6 w-6 text-slate-700 mb-2" />
            <span>Telemetry quiet. Safe operations active.</span>
          </div>
        )}
      </div>
    </div>
  );
};
