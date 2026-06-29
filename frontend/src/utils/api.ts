const API_BASE = "/api";

export async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, options);
  if (!res.ok) {
    throw new Error(`API Error: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  getAgents: () => fetchJson<Record<string, any>>("/agents"),
  startAgent: (name: string) => fetchJson<any>(`/agents/${name}/start`, { method: "POST" }),
  stopAgent: (name: string) => fetchJson<any>(`/agents/${name}/stop`, { method: "POST" }),
  getCurrentPrediction: () => fetchJson<any>("/predictions/current"),
  getDriverState: () => fetchJson<any>("/driver/state"),
  getDriverProfile: () => fetchJson<any>("/driver/profile"),
  getVehicleTelemetry: () => fetchJson<any>("/vehicle/telemetry"),
  getEmergencyStatus: () => fetchJson<any>("/emergency/status"),
  triggerEmergency: (payload: any) => fetchJson<any>("/emergency/trigger", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
};
