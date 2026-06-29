import { useState, useEffect } from "react";
import { LiveData } from "../types";

export function useAgentData(liveData: LiveData | null) {
  const [history, setHistory] = useState<LiveData[]>([]);

  useEffect(() => {
    if (!liveData) return;
    setHistory((prev) => {
      const next = [...prev, liveData];
      if (next.length > 100) next.shift();
      return next;
    });
  }, [liveData]);

  return {
    history,
    current: liveData,
    riskHistory: history.map(h => ({
      time: new Date(h.timestamp).toLocaleTimeString(),
      risk: h.risk_assessment.risk_score,
      attention: h.driver_state.attention_score,
      fatigue: h.driver_state.fatigue_level
    }))
  };
}
