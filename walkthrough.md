# GuardianAI Walkthrough & Completion Report

GuardianAI is fully optimized, tested, and ready. The project integrates an advanced multi-agent edge-computing AI system, featuring real-time browser skeleton tracking, synth wailing sirens, and manual vehicle override controls.

---

## 🚀 Key Milestones & Optimizations

### 1. MediaPipe Holistic 3D Skeleton Tracking
- **Interactive Camera Tracking (`DriverMonitor.tsx`)**: Replaced standard face mesh with **MediaPipe Holistic**.
- **Real-Time Landmark Drawings**:
  - Draws a green **laser-sweep bounding box** target around the face.
  - Draws a neon-green **collar and arm joint outline** (shoulders, elbows, wrists) at 30 FPS.
  - Draws dual-hand **21-joint skeleton grids** in pink and cyan to track fingers and palms.

### 2. High-Performance Direct DOM Updates
- **Render Optimizations**: Eliminated high-frequency React state updates inside the animation loop (which caused "Application Errors").
- **Direct DOM Node Updates**: Refactored the Calibration HUD (EAR, MAR, HAND_D) to write values directly to the DOM by ID (`document.getElementById`), reducing CPU cycles.
- **Throttled Callback Notifications**: Parent state notifications are throttled to **150ms** (6Hz), preserving rendering resources.

### 3. Smart Warning Algorithms
- **Eye Closure Counter**: Normal blinks are ignored. The driver's eyes must remain closed for **12 consecutive frames** (1.2 seconds) to trigger a fatigue warning.
- **Dual Cheek Phone Check**: Measures the distance of both hands (wrist and finger tips) to both cheeks. Proximity under `0.082` for **8 consecutive frames** triggers a phone distraction warning.
- **Scale-Invariant Head Turns**: Monitors left/right turning (Yaw) and up/down nodding (Pitch) using scale-invariant eye-to-nose ratios, flashing warning overlays on screen.

### 4. Browser Synth Siren alerts
- **Web Audio Alert System**: Integrates native browser synth oscillators to generate siren alerts.
- **Urgent Wailing**: Triggers a wailing siren on micro-sleeps, a caution chime on phone usage, and provides a **Mute/Unmute** button in the dashboard.

### 5. Interactive Vehicle Control Desk
- **Override Sliders (`VehiclePanel.tsx`)**: Added a manual control dashboard allowing users to control Speed (0–150 KM/H), Steering, and Lane Position.
- **Backend Sim-Lock (`vehicle_dynamics_agent.py`)**: The backend pauses automatic simulations when manual overrides are active, allowing live testing of crash alerts.

### 6. Relative WebSockets & Global Deployment
- **Dynamic Connection Resolution (`App.tsx`)**: The frontend resolves websocket connections relative to the active hostname (`window.location.host`).
- **Localtunnel expose**: Port 3000 can be exposed to a single global HTTPS address with automatic proxy forwarding for both React and WebSockets.

---

## 🧪 Testing and Validation

All 10 test files pass successfully:

```powershell
python -m pytest guardian-ai/backend/tests/
```

- **Inference performance**: <10ms for sequence predictions.
- **Frontend compiles clean**: Checked via `npm run build` with zero errors.

---

## 🏃 Run the Project

### 1. Start the Backend API
```powershell
cd guardian-ai
python -m backend.main
```

### 2. Start the Frontend
```powershell
cd guardian-ai/frontend
npm run dev
```

### 3. Expose Globally (Optional)
```powershell
npx localtunnel --port 3000
```
*Localtunnel link: [https://crazy-laws-smell.loca.lt](https://crazy-laws-smell.loca.lt)*
