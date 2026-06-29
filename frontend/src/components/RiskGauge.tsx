import React from "react";
import { RiskAssessment } from "../types";
import { AlertOctagon, ShieldAlert } from "lucide-react";

interface RiskGaugeProps {
  assessment?: RiskAssessment;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ assessment }) => {
  const score = assessment?.risk_score ?? 0;
  const level = assessment?.risk_level ?? "low";
  const probability = assessment?.accident_probability ?? 0.0;
  const ttc = assessment?.time_to_collision ?? null;
  
  const radius = 80;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const getColor = (s: number) => {
    if (s < 25) return "stroke-emerald-500 text-emerald-400";
    if (s < 50) return "stroke-yellow-400 text-yellow-400";
    if (s < 75) return "stroke-orange-500 text-orange-400";
    return "stroke-red-500 text-red-400";
  };

  return (
    <div className="glass-card flex flex-col items-center justify-center p-6 text-center">
      <h3 className="mb-4 self-start text-xs font-bold uppercase tracking-wider text-slate-500">Live Crash Risk Rating</h3>
      <div className="relative mb-4 flex h-48 w-48 items-center justify-center">
        <svg className="h-full w-full -rotate-90">
          <circle
            className="stroke-slate-800"
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius + stroke}
            cy={radius + stroke}
          />
          <circle
            className={`transition-all duration-300 ${getColor(score)}`}
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={circumference + " " + circumference}
            style={{ strokeDashoffset }}
            r={normalizedRadius}
            cx={radius + stroke}
            cy={radius + stroke}
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-5xl font-black tracking-tight text-white">{score}</span>
          <span className={`text-[10px] uppercase font-black tracking-widest ${score > 50 ? "pulse-risk" : ""}`}>
            {level}
          </span>
        </div>
      </div>
      <div className="grid w-full grid-cols-2 gap-4 rounded-xl bg-slate-950/60 p-4 border border-slate-900">
        <div className="flex flex-col items-center border-r border-slate-900">
          <span className="text-[10px] font-bold text-slate-500 uppercase">Crash Prob</span>
          <span className="text-lg font-extrabold text-white">{(probability * 100).toFixed(0)}%</span>
        </div>
        <div className="flex flex-col items-center">
          <span className="text-[10px] font-bold text-slate-500 uppercase">Time to Collision</span>
          <span className="text-lg font-extrabold text-white">
            {ttc ? `${ttc.toFixed(1)}s` : "SAFE"}
          </span>
        </div>
      </div>
    </div>
  );
};
