"use client";

import type { ColdState } from "@/lib/coldStart";

interface OnboardingScreen2Props {
  state: ColdState;
  onNext: () => void;
}

export function OnboardingScreen2({ state, onNext }: OnboardingScreen2Props) {
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
        <p className="orbit-body" style={{
          fontSize: "clamp(1.1rem, 2vw, 1.25rem)",
          lineHeight: 1.6,
          marginBottom: "var(--orbit-space-xl)",
          color: "var(--orbit-color-slate)",
          fontWeight: 400
        }}>
          {state.explanation}
        </p>
        <button
          onClick={onNext}
          className="orbit-button orbit-button-primary"
          style={{
            fontSize: "1rem",
            padding: "var(--orbit-space-md) var(--orbit-space-xl)"
          }}
        >
          Продолжить →
        </button>
      </div>
    </div>
  );
}

