import asyncio
from backend.agents.base_agent import BaseAgent
from backend.services.event_bus import event_bus, EventType
from backend.services.emergency import emergency_service
from backend.services.cloud_sync import cloud_sync

class InterventionAgent(BaseAgent):
    def __init__(self):
        super().__init__("intervention")
        self.risk_q = None
        self.last_intervention_time = 0
        self.cooldown_seconds = 3
        self.latest_interventions = []

    async def start(self):
        await super().start()
        self.risk_q = await event_bus.subscribe(EventType.RISK_UPDATE)

    async def process(self):
        while not self.risk_q.empty():
            evt = await self.risk_q.get()
            risk_payload = evt.data
            
            score = risk_payload["risk_score"]
            level = risk_payload["risk_level"]
            
            # Prevent rapid alerts cooldown
            import time
            curr_time = time.time()
            if curr_time - self.last_intervention_time < self.cooldown_seconds:
                continue
                
            action = None
            if score >= 90: # CRITICAL
                action = "Critical intervention: Active lane alignment + automatic braking applied."
                # Call emergency notify
                location = {"lat": 28.6139, "lon": 77.2090}
                asyncio.create_task(emergency_service.trigger_alert(level, location, action))
                asyncio.create_task(cloud_sync.sync_incident(risk_payload))
                self.last_intervention_time = curr_time
            elif score >= 75: # HIGH
                action = "High Risk Alert: Steering wheel vibration + warning chime."
                self.last_intervention_time = curr_time
            elif score >= 50: # MEDIUM
                action = "Moderate Risk: Loud audio notification triggered."
                self.last_intervention_time = curr_time
                
            if action:
                self.logger.warning(f"Intervention Command: {action}")
                intervention_evt = {
                    "timestamp": evt.timestamp,
                    "risk_score": score,
                    "severity": level,
                    "action_taken": action
                }
                self.latest_interventions.append(intervention_evt)
                if len(self.latest_interventions) > 20:
                    self.latest_interventions.pop(0)
                    
                await self.publish_event(EventType.INTERVENTION_COMMAND, intervention_evt)
