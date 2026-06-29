import { useState, useEffect, useRef } from "react";
import { LiveData, DriverState } from "../types";

export function useWebSocket(url: string) {
  const [data, setData] = useState<LiveData | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const stepRef = useRef(0);
  const scenarioRef = useRef("normal");

  // Keep a reference to the active connection state
  const isConnectedRef = useRef(false);
  isConnectedRef.current = connected;

  const sendDriverState = (driverState: Partial<DriverState>) => {
    if (wsRef.current && isConnectedRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: "update_driver_state",
          data: driverState
        })
      );
    }
  };

  const sendVehicleTelemetry = (telemetry: any) => {
    if (wsRef.current && isConnectedRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: "update_vehicle_telemetry",
          data: telemetry
        })
      );
    }
  };

  useEffect(() => {
    function connect() {
      setError(null);
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setData(parsed);
        } catch (err) {
          console.error("Failed to parse socket payload", err);
        }
      };

      ws.onerror = () => {
        setError("WebSocket Connection Error");
      };

      ws.onclose = () => {
        setConnected(false);
        // Retry connection in 3 seconds
        reconnectTimeoutRef.current = window.setTimeout(connect, 3000);
      };
    }

    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [url]);

  // Dynamic simulation fallback when server is offline
  useEffect(() => {
    if (connected) return;

    const interval = setInterval(() => {
      stepRef.current += 1;
      const step = stepRef.current;
      
      // Rotate scenario every 100 steps (10 seconds)
      const scenarios = ["normal", "drowsy", "distracted", "aggressive", "recovery"];
      const scenario = scenarios[Math.floor(step / 100) % scenarios.length];
      scenarioRef.current = scenario;

      let speed = 60;
      let steering = 0;
      let lane = 0;
      let attn = 96;
      let fatigue = 8;
      let distract = 0.05;
      let is_phone = false;
      let is_drowsy = false;
      let collision = "none";
      let prob = 0.02;
      let ttc = null;
      let risk = 12;

      if (scenario === "normal") {
        speed = 60 + Math.sin(step * 0.1) * 3;
        steering = Math.random() * 2 - 1;
        lane = Math.random() * 0.1 - 0.05;
      } else if (scenario === "drowsy") {
        speed = 52 + Math.sin(step * 0.05) * 5;
        steering = Math.sin(step * 0.08) * 5;
        lane = Math.sin(step * 0.08) * 0.35;
        fatigue = Math.min(95, 30 + (step % 100) * 0.7);
        attn = Math.max(30, 85 - (step % 100) * 0.6);
        is_drowsy = fatigue > 55;
        risk = Math.round(fatigue * 0.7 + (is_drowsy ? 20 : 0));
        if (risk > 60) {
          collision = "loss_of_control";
          prob = 0.62;
          ttc = 3.6;
        }
      } else if (scenario === "distracted") {
        speed = 65 + Math.random() * 2;
        lane = Math.sin(step * 0.05) * 0.2;
        attn = Math.max(25, 45 - Math.sin(step * 0.1) * 15);
        distract = 0.88;
        is_phone = true;
        risk = Math.round((100 - attn) * 0.8 + 15);
        if (risk > 50) {
          collision = "rear_end";
          prob = 0.74;
          ttc = 2.3;
        }
      } else if (scenario === "aggressive") {
        speed = 95 + Math.sin(step * 0.2) * 8;
        steering = Math.sin(step * 0.2) * 9;
        lane = Math.sin(step * 0.2) * 0.28;
        risk = 82;
        collision = "loss_of_control";
        prob = 0.86;
        ttc = 1.9;
        attn = 82;
        fatigue = 15;
      } else { // recovery
        speed = 45;
        attn = 98;
        fatigue = 5;
        risk = 5;
      }

      const mockPayload: LiveData = {
        driver_state: {
          attention_score: attn,
          fatigue_level: fatigue,
          distraction_probability: distract,
          emotion: attn > 70 ? "neutral" : "stressed",
          is_phone,
          is_drowsy,
          blink_rate: 12 + fatigue * 0.18,
          head_yaw: steering * 0.2,
          head_pitch: is_phone ? -6.0 : 0
        },
        vehicle_telemetry: {
          speed,
          rpm: speed * 35,
          steering_angle: steering,
          acceleration: speed > 60 ? 0.3 : -0.1,
          brake_pressure: speed < 50 ? 0.4 : 0,
          lane_position: lane,
          stability_score: Math.max(0, 100 - Math.abs(steering) * 8 - (speed - 60) * 0.3),
          road_risk: speed > 80 ? 45 : 12,
          gps_lat: 28.6139 + step * 0.00005,
          gps_lon: 77.2090 + step * 0.00005
        },
        risk_assessment: {
          risk_score: risk,
          risk_level: risk < 25 ? "low" : risk < 50 ? "moderate" : risk < 75 ? "high" : "critical",
          accident_probability: prob,
          time_to_collision: ttc,
          confidence: 0.94,
          contributing_factors: risk > 50 ? ["High speed behavior", "Driver distraction triggered"] : [],
          recommended_intervention: risk < 25 ? "System Normal" : risk < 50 ? "Audio Chime" : risk < 75 ? "Throttling Active" : "Active Braking"
        },
        interventions: risk > 60 ? [{
          timestamp: new Date().toISOString(),
          risk_score: risk,
          severity: risk < 75 ? "high" : "critical",
          action_taken: risk < 75 ? "Braking Correction Applied" : "Collision Warning + Emergency Braking"
        }] : [],
        agents: {
          driver_behavior: { name: "driver_behavior", status: "running", health: "healthy", stats: { events_processed: step, errors: 0 } },
          vehicle_dynamics: { name: "vehicle_dynamics", status: "running", health: "healthy", stats: { events_processed: step, errors: 0 } },
          prediction: { name: "prediction", status: "running", health: "healthy", stats: { events_processed: step, errors: 0 } },
          intervention: { name: "intervention", status: "running", health: "healthy", stats: { events_processed: step, errors: 0 } }
        },
        timestamp: Date.now()
      };

      setData(mockPayload);
    }, 100);

    return () => clearInterval(interval);
  }, [connected]);

  return { data, connected, error, sendDriverState, sendVehicleTelemetry };
}
