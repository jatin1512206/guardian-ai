import React, { useState, useEffect, useRef } from "react";
import { DriverState } from "../types";
import { User, EyeOff, Smartphone, Camera, CameraOff, Loader2, Volume2, VolumeX } from "lucide-react";

interface DriverMonitorProps {
  state?: DriverState;
  onDriverStateDetected?: (detectedState: Partial<DriverState>) => void;
}

export const DriverMonitor: React.FC<DriverMonitorProps> = ({ state, onDriverStateDetected }) => {
  const attention = state?.attention_score ?? 100;
  const fatigue = state?.fatigue_level ?? 0;
  const phone = state?.is_phone ?? false;
  const drowsy = state?.is_drowsy ?? false;
  const distracted = state?.distraction_probability && state.distraction_probability > 0.5 ? true : false;

  const [cameraActive, setCameraActive] = useState(false);
  const [modelLoading, setModelLoading] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [audioMuted, setAudioMuted] = useState(false);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const requestRef = useRef<number | null>(null);
  
  const holisticRef = useRef<any>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  
  // Frame counters for smoothing (prevents false alarms on simple eye blinks)
  const eyesClosedCounterRef = useRef(0);
  const phoneCounterRef = useRef(0);
  const lookingAwayCounterRef = useRef(0);
  const lastParentNotificationTimeRef = useRef(0);

  // Web Audio Alert Synthesizer
  const playSirenAlert = (type: "critical" | "warning") => {
    if (audioMuted) return;
    try {
      if (!audioCtxRef.current || audioCtxRef.current.state === "closed") {
        audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }
      
      const ctx = audioCtxRef.current;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.connect(gain);
      gain.connect(ctx.destination);

      if (type === "critical") {
        osc.type = "sawtooth";
        const now = ctx.currentTime;
        osc.frequency.setValueAtTime(980, now);
        osc.frequency.linearRampToValueAtTime(660, now + 0.15);
        osc.frequency.linearRampToValueAtTime(980, now + 0.3);
        
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.3);
        
        osc.start(now);
        osc.stop(now + 0.3);
      } else {
        osc.type = "sine";
        const now = ctx.currentTime;
        osc.frequency.setValueAtTime(520, now);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.15);
        
        osc.start(now);
        osc.stop(now + 0.15);
      }
    } catch (e) {
      console.warn("Audio blocked by browser autoplay rules", e);
    }
  };

  // Sound sirens on warning states
  useEffect(() => {
    if (!cameraActive || audioMuted) return;
    
    let interval: number;
    if (drowsy) {
      interval = window.setInterval(() => {
        playSirenAlert("critical");
      }, 350);
    } else if (phone || distracted) {
      interval = window.setInterval(() => {
        playSirenAlert("warning");
      }, 800);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [drowsy, phone, distracted, cameraActive, audioMuted]);

  const loadHolisticScript = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      if ((window as any).Holistic) {
        resolve();
        return;
      }

      const script1 = document.createElement("script");
      script1.src = "https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js";
      script1.async = true;

      const script2 = document.createElement("script");
      script2.src = "https://cdn.jsdelivr.net/npm/@mediapipe/holistic/holistic.js";
      script2.async = true;

      script1.onload = () => {
        document.head.appendChild(script2);
      };

      script2.onload = () => {
        resolve();
      };

      script1.onerror = () => reject(new Error("Failed to load MediaPipe Camera Utils"));
      script2.onerror = () => reject(new Error("Failed to load MediaPipe Holistic"));

      document.head.appendChild(script1);
    });
  };

  const toggleCamera = async () => {
    if (cameraActive) {
      stopCamera();
    } else {
      await startCamera();
    }
  };

  const startCamera = async () => {
    setCameraError(null);
    setModelLoading(true);
    try {
      await loadHolisticScript();
      
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" }
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      if (!holisticRef.current) {
        const holistic = new (window as any).Holistic({
          locateFile: (file: string) => `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`
        });

        holistic.setOptions({
          modelComplexity: 1,
          smoothLandmarks: true,
          refineFaceLandmarks: false,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5
        });

        holistic.onResults(onResults);
        holisticRef.current = holistic;
      }

      setCameraActive(true);
      setModelLoading(false);
    } catch (err) {
      console.error("Holistic init failed", err);
      setCameraError("Webcam/MediaPipe Holistic load failed");
      setModelLoading(false);
      setCameraActive(false);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    if (requestRef.current) {
      cancelAnimationFrame(requestRef.current);
    }
    setCameraActive(false);
  };

  const drawLine = (ctx: CanvasRenderingContext2D, p1: any, p2: any, color: string, width: number = 2) => {
    if (!p1 || !p2) return;
    ctx.beginPath();
    ctx.moveTo(p1.x * ctx.canvas.width, p1.y * ctx.canvas.height);
    ctx.lineTo(p2.x * ctx.canvas.width, p2.y * ctx.canvas.height);
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
  };

  const drawHand = (ctx: CanvasRenderingContext2D, handLandmarks: any[], color: string) => {
    if (!handLandmarks) return;
    
    ctx.fillStyle = color;
    for (const pt of handLandmarks) {
      ctx.beginPath();
      ctx.arc(pt.x * ctx.canvas.width, pt.y * ctx.canvas.height, 3, 0, 2 * Math.PI);
      ctx.fill();
    }

    const connections = [
      [0, 1], [1, 2], [2, 3], [3, 4],
      [0, 5], [5, 6], [6, 7], [7, 8],
      [5, 9], [9, 10], [10, 11], [11, 12],
      [9, 13], [13, 14], [14, 15], [15, 16],
      [13, 17], [17, 18], [18, 19], [19, 20], [0, 17]
    ];

    for (const conn of connections) {
      drawLine(ctx, handLandmarks[conn[0]], handLandmarks[conn[1]], color, 1.5);
    }
  };

  const onResults = (results: any) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Track warning flags
    let isDangerSleeping = false;
    let isDangerPhone = false;
    let isDangerDistracted = false;

    // 1. Draw Face Mesh
    if (results.faceLandmarks) {
      const face = results.faceLandmarks;
      
      let minX = 1, maxX = 0, minY = 1, maxY = 0;
      for (const pt of face) {
        if (pt.x < minX) minX = pt.x;
        if (pt.x > maxX) maxX = pt.x;
        if (pt.y < minY) minY = pt.y;
        if (pt.y > maxY) maxY = pt.y;
      }

      isDangerSleeping = eyesClosedCounterRef.current > 12;
      isDangerDistracted = lookingAwayCounterRef.current > 10;
      isDangerPhone = phoneCounterRef.current > 8;

      const boxColor = isDangerSleeping 
        ? "rgba(239, 68, 68, 0.9)" 
        : (isDangerPhone || isDangerDistracted) 
          ? "rgba(249, 115, 22, 0.9)" 
          : "rgba(34, 197, 94, 0.7)";
          
      ctx.strokeStyle = boxColor;
      ctx.lineWidth = 1.5;
      
      const x = minX * canvas.width - 10;
      const y = minY * canvas.height - 15;
      const w = (maxX - minX) * canvas.width + 20;
      const h = (maxY - minY) * canvas.height + 25;
      
      ctx.strokeRect(x, y, w, h);

      ctx.fillStyle = boxColor;
      const cornerLength = 8;
      ctx.fillRect(x, y, cornerLength, 2); ctx.fillRect(x, y, 2, cornerLength);
      ctx.fillRect(x + w - cornerLength, y, cornerLength, 2); ctx.fillRect(x + w, y, 2, cornerLength);
      ctx.fillRect(x, y + h, cornerLength, 2); ctx.fillRect(x, y + h - cornerLength, 2, cornerLength);
      ctx.fillRect(x + w - cornerLength, y + h, cornerLength, 2); ctx.fillRect(x + w, y + h - cornerLength, 2, cornerLength);

      ctx.fillStyle = boxColor;
      ctx.font = "8px monospace";
      ctx.fillText(
        isDangerSleeping 
          ? "ALERT: DRIVER SLEEPING" 
          : isDangerPhone 
            ? "ALERT: PHONE DISTRACTION" 
            : isDangerDistracted 
              ? "ALERT: LOOKING AWAY" 
              : "AI_TRACKER_CALIBRATED", 
        x, y - 5
      );

      ctx.fillStyle = (isDangerSleeping || isDangerPhone || isDangerDistracted) 
        ? "rgba(239, 68, 68, 0.35)" 
        : "rgba(6, 182, 212, 0.35)";
        
      for (const landmark of face) {
        ctx.fillRect(landmark.x * canvas.width, landmark.y * canvas.height, 1, 1);
      }
    }

    // 2. Draw Pose
    if (results.poseLandmarks) {
      const landmarks = results.poseLandmarks;
      
      drawLine(ctx, landmarks[11], landmarks[13], "rgba(34, 197, 94, 0.85)", 3);
      drawLine(ctx, landmarks[13], landmarks[15], "rgba(34, 197, 94, 0.85)", 3);
      drawLine(ctx, landmarks[12], landmarks[14], "rgba(34, 197, 94, 0.85)", 3);
      drawLine(ctx, landmarks[14], landmarks[16], "rgba(34, 197, 94, 0.85)", 3);
      drawLine(ctx, landmarks[11], landmarks[12], "rgba(34, 197, 94, 0.85)", 3);

      ctx.fillStyle = "#ffffff";
      const joints = [11, 12, 13, 14, 15, 16];
      for (const j of joints) {
        if (landmarks[j]) {
          ctx.beginPath();
          ctx.arc(landmarks[j].x * canvas.width, landmarks[j].y * canvas.height, 4, 0, 2 * Math.PI);
          ctx.fill();
        }
      }
    }

    // 3. Draw Hands
    if (results.leftHandLandmarks) {
      drawHand(ctx, results.leftHandLandmarks, "#00e5ff");
    }
    if (results.rightHandLandmarks) {
      drawHand(ctx, results.rightHandLandmarks, "#ff007f");
    }

    // 4. Calculate Precision metrics
    if (results.faceLandmarks) {
      const landmarks = results.faceLandmarks;

      const distance = (p1: any, p2: any) => {
        return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));
      };

      // Precise EAR
      const getEyeEAR = (indices: number[]) => {
        const p1 = landmarks[indices[0]];
        const p2 = landmarks[indices[1]];
        const p3 = landmarks[indices[2]];
        const p4 = landmarks[indices[3]];
        const p5 = landmarks[indices[4]];
        const p6 = landmarks[indices[5]];
        return (distance(p2, p6) + distance(p3, p5)) / (2.0 * distance(p1, p4));
      };

      const leftEAR = getEyeEAR([33, 160, 158, 133, 153, 144]);
      const rightEAR = getEyeEAR([362, 385, 387, 263, 373, 380]);
      const ear = (leftEAR + rightEAR) / 2.0;

      const earEl = document.getElementById("calib-ear");
      if (earEl) earEl.innerText = ear.toFixed(3);

      const mar = distance(landmarks[13], landmarks[14]) / distance(landmarks[78], landmarks[308]);
      const marEl = document.getElementById("calib-mar");
      if (marEl) marEl.innerText = mar.toFixed(3);

      // --- Precise scale-invariant Head Pose (Yaw and Pitch) ---
      // Yaw: left eye-nose vs right eye-nose ratio
      const leftEyeOuter = landmarks[33];
      const rightEyeOuter = landmarks[263];
      const noseTip = landmarks[1];
      
      const distL = distance(leftEyeOuter, noseTip);
      const distR = distance(rightEyeOuter, noseTip);
      const ratioYaw = distL / distR;

      // Pitch: forehead to nose vs total forehead to chin ratio
      const forehead = landmarks[10];
      const chin = landmarks[152];
      const ratioPitch = (noseTip.y - forehead.y) / (chin.y - forehead.y);

      // Alert flags for Left, Right, Up, Down turn
      const turnedLeft = ratioYaw > 1.45;
      const turnedRight = ratioYaw < 0.68;
      const lookingUp = ratioPitch < 0.40;
      const lookingDown = ratioPitch > 0.60;
      
      const headDistracted = turnedLeft || turnedRight || lookingUp || lookingDown;

      // Smoothing filter for Looking Away (requires 10 consecutive frames)
      if (headDistracted) {
        lookingAwayCounterRef.current += 1;
      } else {
        lookingAwayCounterRef.current = 0;
      }
      const isLookingAway = lookingAwayCounterRef.current > 10;

      // Closed Eyes Smoothing filter
      if (ear < 0.205) {
        eyesClosedCounterRef.current += 1;
      } else {
        eyesClosedCounterRef.current = 0;
      }
      const isEyesClosed = eyesClosedCounterRef.current > 12;

      // Phone proximity checks
      let isPhoneDetected = false;
      let handsOffWheel = false;

      const leftCheek = landmarks[234];
      const rightCheek = landmarks[454];

      const checkHandNearEitherCheek = (handLandmarks: any[]) => {
        if (!handLandmarks) return 99.0;
        const indexTip = handLandmarks[8];
        const wrist = handLandmarks[0];
        
        const distToLCheek = distance(indexTip, leftCheek);
        const distToRCheek = distance(indexTip, rightCheek);
        
        const wristToLCheek = distance(wrist, leftCheek);
        const wristToRCheek = distance(wrist, rightCheek);
        
        return Math.min(distToLCheek, distToRCheek, wristToLCheek, wristToRCheek);
      };

      const leftHandDist = checkHandNearEitherCheek(results.leftHandLandmarks);
      const rightHandDist = checkHandNearEitherCheek(results.rightHandLandmarks);
      const minD = Math.min(leftHandDist, rightHandDist);

      const handEl = document.getElementById("calib-hand");
      if (handEl) {
        handEl.innerText = minD > 10.0 ? "N/A" : minD.toFixed(3);
      }

      if (minD < 0.082) {
        phoneCounterRef.current += 1;
      } else {
        phoneCounterRef.current = 0;
      }
      isPhoneDetected = phoneCounterRef.current > 8;

      // Hands off wheel check
      if (results.poseLandmarks) {
        const pose = results.poseLandmarks;
        const leftWrist = pose[15];
        const rightWrist = pose[16];
        const leftShoulder = pose[11];
        
        if (leftWrist && rightWrist && leftShoulder) {
          if (leftWrist.y < leftShoulder.y + 0.12 && rightWrist.y < leftShoulder.y + 0.12) {
            handsOffWheel = true;
          }
        }
      }

      const rawDistraction = isLookingAway || isPhoneDetected || handsOffWheel;

      // Notify parent hook, throttled to 150ms to prevent React re-render cascade
      const now = Date.now();
      if (now - lastParentNotificationTimeRef.current > 150) {
        if (onDriverStateDetected) {
          onDriverStateDetected({
            attention_score: isPhoneDetected ? 20 : handsOffWheel ? 40 : isLookingAway ? 35 : isEyesClosed ? 15 : 96,
            fatigue_level: isEyesClosed ? 95 : mar > 0.55 ? 70 : 8,
            distraction_probability: rawDistraction ? 0.90 : 0.05,
            is_phone: isPhoneDetected,
            is_drowsy: isEyesClosed,
            blink_rate: isEyesClosed ? 0 : 15,
            head_yaw: ratioYaw > 1.0 ? (ratioYaw - 1) * 35 : -(1 - ratioYaw) * 35,
            head_pitch: ratioPitch > 0.5 ? (ratioPitch - 0.5) * 50 : -(0.5 - ratioPitch) * 50
          });
        }
        lastParentNotificationTimeRef.current = now;
      }
    }
  };

  useEffect(() => {
    let active = true;

    const processFrame = async () => {
      if (!active || !cameraActive || !videoRef.current || !holisticRef.current) return;
      
      if (videoRef.current.readyState === 4) {
        await holisticRef.current.send({ image: videoRef.current });
      }
      
      requestRef.current = requestAnimationFrame(processFrame);
    };

    if (cameraActive) {
      requestRef.current = requestAnimationFrame(processFrame);
    }

    return () => {
      active = false;
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, [cameraActive]);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <div className="glass-card flex flex-col p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Cabin Driver Analysis</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setAudioMuted(!audioMuted)}
            className="flex items-center justify-center p-1.5 rounded-full bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
          >
            {audioMuted ? <VolumeX className="h-3.5 w-3.5" /> : <Volume2 className="h-3.5 w-3.5 text-cyan-400" />}
          </button>
          
          <button
            onClick={toggleCamera}
            disabled={modelLoading}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-bold uppercase transition-all duration-300 ${
              cameraActive
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.2)]"
                : "bg-slate-900 text-slate-400 border border-slate-800 hover:border-slate-700 disabled:opacity-55"
            }`}
          >
            {modelLoading ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                <span>Loading AI...</span>
              </>
            ) : cameraActive ? (
              <>
                <Camera className="h-3.5 w-3.5" />
                <span>Camera Active</span>
              </>
            ) : (
              <>
                <CameraOff className="h-3.5 w-3.5" />
                <span>Activate AI Cam</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Live Video Feed Container */}
      <div className="relative mb-4 h-40 w-full rounded-xl bg-slate-950/60 border border-slate-900 overflow-hidden flex items-center justify-center">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`w-full h-full object-cover scale-x-[-1] ${cameraActive ? "block" : "hidden"}`}
        />
        <canvas
          ref={canvasRef}
          width={320}
          height={240}
          className={`absolute inset-0 w-full h-full object-cover scale-x-[-1] pointer-events-none ${
            cameraActive ? "block" : "hidden"
          }`}
        />

        {cameraActive && (
          <>
            <div className="absolute inset-0 border border-cyan-500/20 pointer-events-none" />
            
            {/* Real-time calibration metrics sidebar updated via Direct DOM nodes */}
            <div className="absolute right-2 top-2 flex flex-col gap-1 bg-slate-950/85 p-2 rounded text-[7px] font-mono border border-slate-800 text-slate-400 pointer-events-none">
              <span className="font-bold border-b border-slate-800 pb-0.5 text-cyan-400">CALIBRATION</span>
              <span>EAR: <span id="calib-ear" className="text-white">0.300</span></span>
              <span>MAR: <span id="calib-mar" className="text-white">0.150</span></span>
              <span>HAND_D: <span id="calib-hand" className="text-white">N/A</span></span>
            </div>

            {drowsy && (
              <div className="absolute inset-x-8 inset-y-6 border border-red-500 rounded-lg animate-pulse flex flex-col items-center justify-center bg-red-500/10 pointer-events-none">
                <span className="text-[10px] font-black text-red-500 uppercase tracking-widest px-2 py-0.5 bg-slate-950 rounded">
                  ALARM: SLEEP IN PROGRESS
                </span>
              </div>
            )}

            {phone && (
              <div className="absolute inset-x-8 inset-y-6 border border-orange-500 rounded-lg animate-pulse flex flex-col items-center justify-center bg-orange-500/10 pointer-events-none">
                <span className="text-[10px] font-black text-orange-500 uppercase tracking-widest px-2 py-0.5 bg-slate-950 rounded">
                  ALARM: PHONE DISTRACTION
                </span>
              </div>
            )}

            {distracted && !phone && !drowsy && (
              <div className="absolute inset-x-8 inset-y-6 border border-yellow-500 rounded-lg animate-pulse flex flex-col items-center justify-center bg-yellow-500/10 pointer-events-none">
                <span className="text-[10px] font-black text-yellow-500 uppercase tracking-widest px-2 py-0.5 bg-slate-950 rounded">
                  ALARM: LOOKING AWAY
                </span>
              </div>
            )}
            <div className="absolute inset-0 bg-grid opacity-10 pointer-events-none" />
          </>
        )}

        {!cameraActive && !modelLoading && (
          <div className="flex flex-col items-center text-center p-4">
            <div className="h-12 w-12 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mb-2">
              <User className="h-6 w-6 text-slate-500" />
            </div>
            <span className="text-xs text-slate-500">Camera Feed Inactive</span>
            {cameraError && <span className="text-[10px] text-red-400 mt-1">{cameraError}</span>}
          </div>
        )}

        {modelLoading && (
          <div className="flex flex-col items-center text-center p-4 animate-pulse">
            <Loader2 className="h-8 w-8 text-cyan-400 animate-spin mb-2" />
            <span className="text-xs text-slate-400">Initializing MediaPipe Holistic...</span>
          </div>
        )}
      </div>

      <div className="mb-4 flex items-center justify-center gap-6 rounded-xl bg-slate-950/50 p-4 border border-slate-900">
        <div className="flex-1 space-y-3">
          <div>
            <div className="mb-1 flex justify-between text-xs font-bold">
              <span className="text-slate-400">Attention Rating</span>
              <span className={attention < 50 ? "text-red-400 font-black" : "text-emerald-400"}>
                {attention.toFixed(0)}%
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-slate-900">
              <div
                className={`h-full rounded-full transition-all duration-300 ${
                  attention < 50 ? "bg-red-500" : "bg-emerald-500"
                }`}
                style={{ width: `${attention}%` }}
              />
            </div>
          </div>
          <div>
            <div className="mb-1 flex justify-between text-xs font-bold">
              <span className="text-slate-400">Fatigue Index</span>
              <span className={fatigue > 60 ? "text-red-400 font-black" : "text-yellow-400"}>
                {fatigue.toFixed(0)}%
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-slate-900">
              <div
                className={`h-full rounded-full transition-all duration-300 ${
                  fatigue > 60 ? "bg-red-500" : "bg-yellow-400"
                }`}
                style={{ width: `${fatigue}%` }}
              />
            </div>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div
          className={`rounded-lg border p-2.5 font-bold transition-all ${
            phone
              ? "border-red-900 bg-red-950/40 text-red-400 shadow-[0_0_10px_rgba(239,68,68,0.2)] animate-pulse"
              : "border-slate-900 bg-slate-950/20 text-slate-400"
          }`}
        >
          Cell Usage
        </div>
        <div
          className={`rounded-lg border p-2.5 font-bold transition-all ${
            drowsy
              ? "border-red-900 bg-red-950/40 text-red-400 shadow-[0_0_10px_rgba(239,68,68,0.2)] animate-pulse"
              : "border-slate-900 bg-slate-950/20 text-slate-400"
          }`}
        >
          Eyes Closed
        </div>
        <div
          className={`rounded-lg border p-2.5 font-bold transition-all ${
            distracted
              ? "border-red-900 bg-red-950/40 text-red-400 shadow-[0_0_10px_rgba(239,68,68,0.2)] animate-pulse"
              : "border-slate-900 bg-slate-950/20 text-slate-400"
          }`}
        >
          Distracted
        </div>
      </div>
    </div>
  );
};
