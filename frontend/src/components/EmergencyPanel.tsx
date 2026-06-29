import React from "react";
import { Radio } from "lucide-react";

export const EmergencyPanel: React.FC = () => {
  return (
    <div className="glass-card flex flex-col p-6 justify-between">
      <div>
        <h3 className="mb-4 text-xs font-bold uppercase tracking-wider text-slate-500">Emergency Dispatch Services</h3>
        <p className="text-xs text-slate-400">
          In severe anomalies or pre-impact scenarios, high-priority cellular notifications are dispatched to emergency hubs.
        </p>
      </div>
      <button className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-red-600 hover:bg-red-700 py-3.5 text-sm font-black text-white transition-all shadow-lg shadow-red-900/40">
        <Radio className="h-4.5 w-4.5" />
        TRIGGER PANIC PROTOCOL
      </button>
    </div>
  );
};
