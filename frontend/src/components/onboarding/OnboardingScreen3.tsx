"use client";

import { useState } from "react";
import type { ColdState } from "@/lib/coldStart";

interface OnboardingScreen3Props {
  state: ColdState;
  onComplete: () => void;
}

export function OnboardingScreen3({ state, onComplete }: OnboardingScreen3Props) {
  const [completed, setCompleted] = useState(false);

  const handleComplete = () => {
    setCompleted(true);
    // Сохраняем в localStorage для отслеживания
    const completionKey = `cold_start_completed_${state.id}_${new Date().toDateString()}`;
    localStorage.setItem(completionKey, "true");
    
    // Небольшая задержка перед переходом для ощущения завершения
    setTimeout(() => {
      onComplete();
    }, 1500);
  };

  if (completed) {
    return (
      <div style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "var(--orbit-space-xl)",
        background: "var(--orbit-color-page)",
        textAlign: "center"
      }}>
        <div style={{ maxWidth: "600px", width: "100%" }}>
          <div style={{
            fontSize: "3rem",
            marginBottom: "var(--orbit-space-md)",
            animation: "fadeIn 0.3s ease"
          }}>
            ✔
          </div>
          <p className="orbit-body" style={{
            fontSize: "clamp(1.1rem, 2vw, 1.25rem)",
            lineHeight: 1.6,
            marginBottom: "var(--orbit-space-md)",
            color: "var(--orbit-color-success)",
            fontWeight: 500
          }}>
            Зафиксировано
          </p>
          <p className="orbit-body-sm orbit-text-muted" style={{
            lineHeight: 1.6,
            color: "var(--orbit-color-slate)"
          }}>
            {state.microAction.completionMessage}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      padding: "var(--orbit-space-xl)",
      background: "var(--orbit-color-page)",
      textAlign: "center"
    }}>
      <div style={{ maxWidth: "600px", width: "100%" }}>
        <p className="orbit-body-sm orbit-text-muted" style={{
          marginBottom: "var(--orbit-space-md)",
          fontSize: "0.875rem",
          letterSpacing: "0.05em",
          textTransform: "uppercase"
        }}>
          Сделай это прямо сейчас (30 секунд):
        </p>
        <p className="orbit-body" style={{
          fontSize: "clamp(1.1rem, 2vw, 1.25rem)",
          lineHeight: 1.6,
          marginBottom: "var(--orbit-space-xl)",
          color: "var(--orbit-color-slate)",
          fontWeight: 400
        }}>
          {state.microAction.instruction}
        </p>
        <button
          onClick={handleComplete}
          className="orbit-button orbit-button-primary"
          style={{
            fontSize: "1rem",
            padding: "var(--orbit-space-md) var(--orbit-space-xl)"
          }}
        >
          Я заметил →
        </button>
      </div>
    </div>
  );
}

