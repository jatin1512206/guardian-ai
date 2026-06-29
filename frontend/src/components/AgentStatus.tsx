import React from "react";
import { AgentStatus as AgentType } from "../types";
import { Cpu } from "lucide-react";

interface AgentStatusProps {
  agents?: Record<string, AgentType>;
}

export const AgentStatus: React.FC<AgentStatusProps> = ({ agents }) => {
  const agentList = Object.values(agents ?? {});
  
  return (
    <div className="glass-card flex flex-col p-6">
      <h3 className="mb-4 text-xs font-bold uppercase tracking-wider text-slate-500">AI Agents Status</h3>
      <div className="grid grid-cols-2 gap-3">
        {agentList.map((agent) => (
          <div key={agent.name} className="flex flex-col rounded-xl border border-slate-900 bg-slate-950/50 p-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-300 capitalize">{agent.name.replace("_", " ")}</span>
              <span className={`status-dot ${agent.status === "running" ? "active" : "error"}`}></span>
            </div>
            <div className="mt-3 flex items-center justify-between text-[10px] text-slate-500">
              <span className="flex items-center gap-1">
                <Cpu className="h-3 w-3" />
                {agent.stats.events_processed} steps
              </span>
              <span className="font-semibold text-emerald-500 uppercase">{agent.health}</span>
            </div>
          </div>
        ))}
        {agentList.length === 0 && (
          <div className="col-span-2 text-center text-xs text-slate-500 py-6">Initializing AI modules...</div>
        )}
      </div>
    </div>
  );
};
