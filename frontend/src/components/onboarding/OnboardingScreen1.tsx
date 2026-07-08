"use client";

import { useState } from "react";
import type { ColdState } from "@/lib/coldStart";

interface OnboardingScreen1Props {
  state: ColdState;
  onNext: () => void;
}

export function OnboardingScreen1({ state, onNext }: OnboardingScreen1Props) {
  const [clicked, setClicked] = useState(false);

  const handleClick = () => {
    setClicked(true);
    // Небольшая задержка для ощущения взаимодействия
    setTimeout(() => {
      onNext();
    }, 300);
  };

  return (
    <div 
      onClick={handleClick}
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        padding: "var(--orbit-space-xl)",
        background: "linear-gradient(135deg, rgba(250, 248, 245, 0.95), rgba(240, 237, 232, 0.95))",
        textAlign: "center",
        cursor: "pointer",
        transition: "opacity 0.3s ease",
        opacity: clicked ? 0.9 : 1
      }}
    >
      <div style={{ maxWidth: "600px", width: "100%" }}>
        <p className="orbit-body-sm orbit-text-muted" style={{ 
          marginBottom: "var(--orbit-space-md)",
          fontSize: "0.875rem",
          letterSpacing: "0.05em",
          textTransform: "uppercase"
        }}>
          Сегодня твой внутренний фокус —
        </p>
        <h1 className="orbit-display" style={{
          fontSize: "clamp(2rem, 5vw, 3rem)",
          lineHeight: 1.2,
          marginBottom: "var(--orbit-space-xl)",
          color: "var(--orbit-color-ink)",
          fontWeight: 500
        }}>
          {state.keyPhrase}
        </h1>
        <p className="orbit-body-xs orbit-text-muted" style={{
          marginTop: "var(--orbit-space-lg)",
          fontSize: "0.75rem",
          opacity: 0.6
        }}>
          Нажми, чтобы продолжить
        </p>
      </div>
    </div>
  );
}
