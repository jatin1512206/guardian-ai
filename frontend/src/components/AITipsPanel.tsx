import React, { useState, useEffect, useRef } from "react";
import { DriverState, VehicleTelemetry, RiskAssessment } from "../types";
import { Sparkles, Volume2, VolumeX, AlertTriangle, CheckCircle, Info } from "lucide-react";

interface AITipsPanelProps {
  driverState?: DriverState | null;
  telemetry?: VehicleTelemetry | null;
  risk?: RiskAssessment | null;
}

export const AITipsPanel: React.FC<AITipsPanelProps> = ({ driverState, telemetry, risk }) => {
  const [tipsText, setTipsText] = useState("Optimal Driving State: Focus levels are excellent. Keep up the safe driving!");
  const [statusType, setStatusType] = useState<"info" | "warning" | "critical" | "success">("success");
  const [voiceMuted, setVoiceMuted] = useState(false);
  
  const lastSpokenTextRef = useRef<string>("");
  const speakCooldownRef = useRef<number>(0);

  // Text-To-Speech Synthesis helper
  const speakAdvice = (text: string) => {
    if (voiceMuted || !("speechSynthesis" in window)) return;
    
    const now = Date.now();
    // Prevent repeating the same speech alert within 8 seconds to avoid voice overlap fatigue
    if (lastSpokenTextRef.current === text && now - speakCooldownRef.current < 8000) {
      return;
    }

    try {
      // Cancel active voice playbacks to speak immediately
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.05; // Slightly faster for urgent alerts
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      // Select a clear English voice if available
      const voices = window.speechSynthesis.getVoices();
      const engVoice = voices.find(v => v.lang.startsWith("en-") && v.name.includes("Google"));
      if (engVoice) {
        utterance.voice = engVoice;
      }

      window.speechSynthesis.speak(utterance);
      
      lastSpokenTextRef.current = text;
      speakCooldownRef.current = now;
    } catch (e) {
      console.warn("Speech Synthesis failed or blocked:", e);
    }
  };

  // Evaluate driving metrics to produce coaching recommendations
  useEffect(() => {
    const isSleeping = driverState?.is_drowsy ?? false;
    const isUsingPhone = driverState?.is_phone ?? false;
    const attentionScore = driverState?.attention_score ?? 100;
    const speed = telemetry?.speed ?? 0;
    const isDistracted = driverState?.distraction_probability && driverState.distraction_probability > 0.5;

    let tip = "";
    let level: "info" | "warning" | "critical" | "success" = "success";
    let voicePrompt = "";

    if (isSleeping) {
      tip = "CRITICAL ALERT: Driver micro-sleep detected! Pull over safely at the nearest service zone immediately.";
      level = "critical";
      voicePrompt = "Critical alert! Wake up, please pull over safely immediately.";
    } else if (isUsingPhone) {
      tip = "WARNING: Hands-free violation! Put down your mobile device and keep your hands on the steering wheel.";
      level = "critical";
      voicePrompt = "Warning, put down your phone and focus on the road.";
    } else if (isDistracted || attentionScore < 50) {
      tip = "ATTENTION LOST: Visual distraction detected. Focus your eyes back on the road ahead.";
      level = "warning";
      voicePrompt = "Attention warning, please look ahead at the road.";
    } else if (speed > 120) {
      tip = "SPEED WARNING: Traveling at high speed. Reduce velocity below 100 KM/H to ensure optimal braking distance.";
      level = "warning";
      voicePrompt = "Speed warning, please reduce your vehicle speed.";
    } else if (speed > 0 && speed < 30 && telemetry?.steering_angle && Math.abs(telemetry.steering_angle) > 25) {
      tip = "COACHING TIP: High steering angle at low speed. Watch out for blind spots on tight corners.";
      level = "info";
      voicePrompt = "Watch your blind spots.";
    } else {
      tip = "Optimal Driving State: Focus levels are excellent. Lane alignment is steady. Safe trip!";
      level = "success";
      voicePrompt = ""; // Quiet on normal
    }

    setTipsText(tip);
    setStatusType(level);

    if (voicePrompt) {
      speakAdvice(voicePrompt);
    }
  }, [driverState, telemetry, risk]);

  // Clean up any speaking on unmount
  useEffect(() => {
    return () => {
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const getThemeClasses = () => {
    switch (statusType) {
      case "critical":
        return "border-red-500/30 bg-red-500/5 text-red-400";
      case "warning":
        return "border-orange-500/30 bg-orange-500/5 text-orange-400";
      case "info":
        return "border-cyan-500/30 bg-cyan-500/5 text-cyan-400";
      default:
        return "border-emerald-500/30 bg-emerald-500/5 text-emerald-400";
    }
  };

  const getIcon = () => {
    switch (statusType) {
      case "critical":
        return <AlertTriangle className="h-5 w-5 text-red-500 animate-bounce" />;
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case "info":
        return <Info className="h-5 w-5 text-cyan-400" />;
      default:
        return <CheckCircle className="h-5 w-5 text-emerald-500" />;
    }
  };

  return (
    <div className="glass-card flex flex-col p-6 col-span-1 md:col-span-2 lg:col-span-3">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-cyan-500/10 flex items-center justify-center border border-cyan-500/20">
            <Sparkles className="h-4 w-4 text-cyan-400" />
          </div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            AI Copilot - Live Driver Coaching Desk
          </h3>
        </div>

        {/* Voice control button */}
        <button
          onClick={() => {
            const nextMuted = !voiceMuted;
            setVoiceMuted(nextMuted);
            if (nextMuted && "speechSynthesis" in window) {
              window.speechSynthesis.cancel();
            }
          }}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase transition-all duration-300 ${
            !voiceMuted
              ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 shadow-[0_0_10px_rgba(6,182,212,0.15)]"
              : "bg-slate-900 text-slate-500 border border-slate-800 hover:border-slate-700"
          }`}
        >
          {voiceMuted ? (
            <>
              <VolumeX className="h-3.5 w-3.5" />
              <span>Voice Guidance Muted</span>
            </>
          ) : (
            <>
              <Volume2 className="h-3.5 w-3.5" />
              <span>Voice Guidance On</span>
            </>
          )}
        </button>
      </div>

      <div className={`flex items-start gap-4 p-4 rounded-xl border transition-all duration-300 ${getThemeClasses()}`}>
        <div className="mt-0.5">{getIcon()}</div>
        <div className="flex-1">
          <span className="text-xs font-bold uppercase tracking-wide block mb-1">
            {statusType === "critical" ? "CRITICAL ADVISORY" : statusType === "warning" ? "WARNING" : statusType === "info" ? "DRIVING TIP" : "SYSTEM OK"}
          </span>
          <p className="text-sm font-semibold leading-relaxed text-slate-100">{tipsText}</p>
        </div>
      </div>
    </div>
  );
};
