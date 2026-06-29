import React from "react";
import { LiveData } from "../types";
import { RiskGauge } from "./RiskGauge";
import { DriverMonitor } from "./DriverMonitor";
import { VehiclePanel } from "./VehiclePanel";
import { PredictionTimeline } from "./PredictionTimeline";
import { AgentStatus } from "./AgentStatus";
import { InterventionLog } from "./InterventionLog";
import { AnalyticsChart } from "./AnalyticsChart";
import { EmergencyPanel } from "./EmergencyPanel";
import { LaneDetection } from "./LaneDetection";
import { GPSMap } from "./GPSMap";
import { AITipsPanel } from "./AITipsPanel";

interface DashboardProps {
  data: LiveData | null;
  history: any[];
  onDriverStateDetected?: (detectedState: any) => void;
  onVehicleTelemetryOverride?: (telemetryState: any) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ 
  data, 
  history, 
  onDriverStateDetected, 
  onVehicleTelemetryOverride 
}) => {
  return (
    <main className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-8 bg-mesh bg-grid min-h-[calc(100vh-70px)]">
      <AITipsPanel driverState={data?.driver_state} telemetry={data?.vehicle_telemetry} risk={data?.risk_assessment} />
      
      <RiskGauge assessment={data?.risk_assessment} />
      <DriverMonitor state={data?.driver_state} onDriverStateDetected={onDriverStateDetected} />
      <VehiclePanel telemetry={data?.vehicle_telemetry} onVehicleTelemetryOverride={onVehicleTelemetryOverride} />
      
      <PredictionTimeline assessment={data?.risk_assessment} />
      <AgentStatus agents={data?.agents} />
      <InterventionLog interventions={data?.interventions} />
      
      <AnalyticsChart history={history} />
      <EmergencyPanel />
      
      <LaneDetection lanePosition={data?.vehicle_telemetry?.lane_position} />
      <GPSMap lat={data?.vehicle_telemetry?.gps_lat} lon={data?.vehicle_telemetry?.gps_lon} />
    </main>
  );
};
