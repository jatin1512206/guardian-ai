import React from "react";
import { Shield, Radio, Activity } from "lucide-react";

interface HeaderProps {
  connected: boolean;
}

export const Header: React.FC<HeaderProps> = ({ connected }) => {
  return (
    <header className="glass-nav sticky top-0 z-50 flex items-center justify-between px-8 py-4">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-400 text-white shadow-lg">
          <Shield className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-lg font-black tracking-tight text-white">
            Guardian<span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">AI</span>
          </h1>
          <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Behavioral Guard Ecosystem</p>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/60 px-4 py-1.5 text-xs text-slate-400">
          <Activity className="h-3.5 w-3.5 text-cyan-400 spin-slow" />
          <span>Multi-Agent Engine Active</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`status-dot ${connected ? "active" : "error"}`}></span>
          <span className="text-xs font-semibold text-slate-300">
            {connected ? "LIVE CLOUD CONNECT" : "LOCAL SIMULATOR ACTIVE"}
          </span>
        </div>
      </div>
    </header>
  );
};
