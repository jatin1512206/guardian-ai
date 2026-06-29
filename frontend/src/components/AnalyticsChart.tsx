import React from "react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from "recharts";

interface AnalyticsChartProps {
  history: any[];
}

export const AnalyticsChart: React.FC<AnalyticsChartProps> = ({ history }) => {
  return (
    <div className="glass-card flex flex-col p-6 col-span-1 lg:col-span-2">
      <h3 className="mb-4 text-xs font-bold uppercase tracking-wider text-slate-500">Temporal Session Analytics</h3>
      <div className="h-48 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={history}>
            <defs>
              <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorAttention" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <XAxis dataKey="time" tick={{ fill: "#64748b" }} />
            <YAxis tick={{ fill: "#64748b" }} />
            <Tooltip contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", color: "#f8fafc" }} />
            <Area type="monotone" dataKey="risk" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#colorRisk)" name="Risk Score" />
            <Area type="monotone" dataKey="attention" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorAttention)" name="Attention" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
