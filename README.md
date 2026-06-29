# GuardianAI 🛡️

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-brightgreen?style=for-the-badge&logo=vercel)](https://frontend-jade-mu-yuaglzd84o.vercel.app)

GuardianAI is a production-ready, end-to-end multi-agent AI system designed for the **Hack2Skill Data & AI Challenge**.
It predicts vehicular accidents **3–5 seconds before impact** through driver cognitive analysis, vehicle telemetry monitoring, and temporal sensor fusion.

```
       [Cabin Video]          [Vehicle OBD-II]
             │                       │
             ▼                       ▼
    ┌────────────────┐      ┌────────────────┐
    │  Driver Agent  │      │ Vehicle Agent  │
    └────────┬───────┘      └────────┬───────┘
             │                       │
             └───────────┬───────────┘
                         ▼
             ┌───────────────────────┐
             │   Prediction Agent    │  ◄── [Event Bus]
             └───────────┬───────────┘
                         ▼
             ┌───────────────────────┐
             │  Intervention Agent   │
             └───────────────────────┘
```

## Features
- **4 Autonomous AI Agents** communicating via an asynchronous event bus.
- **7 Machine Learning Models** performing real-time inference in <100ms.
- **Real-time WebSockets Dashboard** built using React, TypeScript, Tailwind, and Recharts.
- **Safety Interventions Escalation Ladder** preventing accidents before impact.
