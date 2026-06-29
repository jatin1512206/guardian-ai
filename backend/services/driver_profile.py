import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from backend.database import AsyncSessionLocal, DriverProfile
from sqlalchemy import select

class DriverProfileService:
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    async def get_profile(self, driver_id: str = "default_driver") -> Dict[str, Any]:
        if driver_id in self._cache:
            return self._cache[driver_id]
            
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(DriverProfile).where(DriverProfile.id == driver_id))
            profile = result.scalars().first()
            if not profile:
                profile = DriverProfile(id=driver_id)
                session.add(profile)
                await session.commit()
                
            data = {
                "id": profile.id,
                "avg_blink_rate": profile.avg_blink_rate,
                "avg_fatigue": profile.avg_fatigue,
                "driving_hours": profile.driving_hours,
                "risk_events_count": profile.risk_events_count,
                "preferred_speed": profile.preferred_speed
            }
            self._cache[driver_id] = data
            return data

    async def update_profile(self, driver_id: str, updates: Dict[str, Any]):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(DriverProfile).where(DriverProfile.id == driver_id))
            profile = result.scalars().first()
            if profile:
                for k, v in updates.items():
                    if hasattr(profile, k):
                        setattr(profile, k, v)
                profile.updated_at = datetime.utcnow()
                await session.commit()
                if driver_id in self._cache:
                    del self._cache[driver_id]

driver_profile_service = DriverProfileService()
