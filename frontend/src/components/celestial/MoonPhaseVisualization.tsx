"use client";

import React from "react";
import type { MoonPhaseSnapshot, UpcomingPhase } from "@/lib/types";

interface MoonPhaseVisualizationProps {
  current: MoonPhaseSnapshot;
  nextPhase?: UpcomingPhase | null;
  size?: "sm" | "md" | "lg";
}

// Маппинг фаз на углы освещения (0-360 градусов)
const PHASE_ANGLES: Record<string, number> = {
  "new_moon": 0,           // Новолуние - 0°
  "waxing_crescent": 45,   // Молодая луна - 45°
  "first_quarter": 90,     // Первая четверть - 90°
  "waxing_gibbous": 135,   // Растущая луна - 135°
  "full_moon": 180,        // Полнолуние - 180°
  "waning_gibbous": 225,   // Убывающая луна - 225°
  "last_quarter": 270,     // Последняя четверть - 270°
  "waning_crescent": 315,  // Старая луна - 315°
};

// Альтернативные названия фаз
const PHASE_ALIASES: Record<string, string> = {
  "новолуние": "new_moon",
  "молодая луна": "waxing_crescent",
  "первая четверть": "first_quarter",
  "растущая луна": "waxing_gibbous",
  "полнолуние": "full_moon",
  "убывающая луна": "waning_gibbous",
  "последняя четверть": "last_quarter",
  "старая луна": "waning_crescent",
};

function getPhaseAngle(phaseId: string): number {
  const normalizedId = phaseId.toLowerCase().replace(/\s+/g, "_");
  const alias = PHASE_ALIASES[phaseId.toLowerCase()];
  const key = alias || normalizedId;
  return PHASE_ANGLES[key] ?? 0;
}

function calculateMoonIllumination(cycleDay: number): number {
  // Лунный цикл ~29.5 дней, день 0 = новолуние, день 14-15 = полнолуние
  const normalizedDay = cycleDay % 29.5;
  // Освещение от 0 (новолуние) до 1 (полнолуние) и обратно
  if (normalizedDay <= 14.75) {
    return normalizedDay / 14.75;
  } else {
    return (29.5 - normalizedDay) / 14.75;
  }
}

function MoonCircle({ 
  illumination, 
  phaseAngle, 
  size = 200 
}: { 
  illumination: number; 
  phaseAngle: number; 
  size?: number;
}) {
  const radius = size / 2 - 4;
  const center = size / 2;
  
  // Определяем, растущая или убывающая луна
  const isWaxing = phaseAngle < 180;
  
  // Создаем маску для освещенной части
  const getMoonClipPath = () => {
    if (illumination === 0) {
      return "none";
    }
    if (illumination === 1) {
      return "none";
    }
    
    // Смещение для создания фазы
    const offset = radius * (1 - illumination * 2);
    const clipX = isWaxing ? center - offset : center + offset;
    
    return `circle(${radius}px at ${clipX}px ${center}px)`;
  };

  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ display: "block" }}>
        <defs>
          <radialGradient id={`moonGradient-${size}`}>
            <stop offset="0%" stopColor="rgba(255, 255, 220, 1)" />
            <stop offset="70%" stopColor="rgba(255, 255, 200, 0.9)" />
            <stop offset="100%" stopColor="rgba(240, 240, 180, 0.7)" />
          </radialGradient>
          <filter id={`moonGlow-${size}`}>
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        {/* Фон - темная часть луны */}
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="rgba(40, 40, 60, 0.3)"
          stroke="rgba(100, 100, 120, 0.5)"
          strokeWidth="2"
        />
        
        {/* Освещенная часть */}
        {illumination > 0 && illumination < 1 && (
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="url(#moonGradient)"
            clipPath={getMoonClipPath()}
            filter={`url(#moonGlow-${size})`}
          />
        )}
        
        {/* Полнолуние */}
        {illumination >= 1 && (
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="url(#moonGradient)"
            filter={`url(#moonGlow-${size})`}
          />
        )}
      </svg>
    </div>
  );
}

export function MoonPhaseVisualization({ current, nextPhase, size = "md" }: MoonPhaseVisualizationProps) {
  const sizeMap = {
    sm: 120,
    md: 200,
    lg: 300,
  };
  
  const circleSize = sizeMap[size];
  const phaseAngle = getPhaseAngle(current.id);
  const illumination = calculateMoonIllumination(current.cycle_day || 0);

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "var(--orbit-space-md)" }}>
      {/* Текущая фаза */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "var(--orbit-space-sm)" }}>
        <MoonCircle illumination={illumination} phaseAngle={phaseAngle} size={circleSize} />
        <div style={{ textAlign: "center" }}>
          <h3 className="orbit-display-xs" style={{ marginBottom: "var(--orbit-space-xs)" }}>
            {current.name}
          </h3>
          <p className="orbit-body-sm orbit-text-muted">
            День {current.cycle_day || 0} из 29.5
          </p>
          <p className="orbit-body-xs orbit-text-muted" style={{ marginTop: "var(--orbit-space-xs)" }}>
            Освещение: {Math.round(illumination * 100)}%
          </p>
        </div>
      </div>

      {/* Следующая фаза */}
      {nextPhase && (
        <div style={{ 
          padding: "var(--orbit-space-md)",
          border: "1px solid var(--orbit-color-border)",
          borderRadius: "var(--orbit-radius-sm)",
          width: "100%",
          textAlign: "center"
        }}>
          <p className="orbit-body-sm orbit-text-muted" style={{ marginBottom: "var(--orbit-space-xs)" }}>
            Следующая фаза
          </p>
          <p className="orbit-body" style={{ fontWeight: 600, marginBottom: "var(--orbit-space-xs)" }}>
            {nextPhase.name}
          </p>
          <p className="orbit-body-xs orbit-text-muted">
            Через {nextPhase.in_days} {nextPhase.in_days === 1 ? "день" : nextPhase.in_days < 5 ? "дня" : "дней"}
          </p>
        </div>
      )}
    </div>
  );
}

