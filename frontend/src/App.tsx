import React from "react";
import { useWebSocket } from "./hooks/useWebSocket";
import { useAgentData } from "./hooks/useAgentData";
import { Header } from "./components/Header";
import { Dashboard } from "./components/Dashboard";

export default function App() {
  const envWsUrl = import.meta.env.VITE_WS_URL;
  const wsUrl = envWsUrl || `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws/live`;
  const { data, connected, sendDriverState, sendVehicleTelemetry } = useWebSocket(wsUrl);
  const { history, riskHistory } = useAgentData(data);

  return (
    <div className="min-h-screen bg-[#0a0f1a] text-slate-100 flex flex-col">
      <Header connected={connected} />
      <Dashboard 
        data={data} 
        history={riskHistory} 
        onDriverStateDetected={sendDriverState} 
        onVehicleTelemetryOverride={sendVehicleTelemetry}
      />
    </div>
  );
}
