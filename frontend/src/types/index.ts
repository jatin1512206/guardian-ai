export interface DriverState {
  attention_score: number;
  fatigue_level: number;
  distraction_probability: number;
  emotion: string;
  is_phone: boolean;
  is_drowsy: boolean;
  blink_rate: number;
  head_yaw: number;
  head_pitch: number;
}

export interface VehicleTelemetry {
  speed: number;
  rpm: number;
  steering_angle: number;
  acceleration: number;
  brake_pressure: number;
  lane_position: number;
  stability_score: number;
  road_risk: number;
  gps_lat: number;
  gps_lon: number;
}

export interface RiskAssessment {
  risk_score: number;
  risk_level: string;
  accident_probability: number;
  time_to_collision: number | null;
  confidence: number;
  contributing_factors: string[];
  recommended_intervention: string;
}

export interface Intervention {
  timestamp: string;
  risk_score: number;
  severity: string;
  action_taken: string;
}

export interface AgentStatus {
  name: string;
  status: string;
  health: string;
  stats: {
    events_processed: number;
    errors: number;
  };
}

export interface LiveData {
  driver_state: DriverState;
  vehicle_telemetry: VehicleTelemetry;
  risk_assessment: RiskAssessment;
  interventions: Intervention[];
  agents: Record<string, AgentStatus>;
  timestamp: number;
}
