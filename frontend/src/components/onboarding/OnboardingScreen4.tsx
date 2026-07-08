"use client";

import Link from "next/link";
import type { ColdState } from "@/lib/coldStart";

interface OnboardingScreen4Props {
  state: ColdState;
}

export function OnboardingScreen4({ state }: OnboardingScreen4Props) {
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
          {state.hookMessage}
        </p>
        <Link
          href="/auth"
          className="orbit-button orbit-button-primary"
          style={{
            fontSize: "1rem",
            padding: "var(--orbit-space-md) var(--orbit-space-xl)",
            textDecoration: "none",
            display: "inline-block"
          }}
        >
          Создать профиль →
        </Link>
        <Link
          href="/"
          className="orbit-button orbit-button-secondary"
          style={{
            fontSize: "0.875rem",
            padding: "var(--orbit-space-sm) var(--orbit-space-lg)",
            textDecoration: "none",
            display: "inline-block",
            marginTop: "var(--orbit-space-md)",
            background: "transparent"
          }}
          onClick={() => {
            // Сохраняем флаг завершения онбординга
            const today = new Date().toDateString();
            const onboardingKey = `onboarding_completed_${today}`;
            localStorage.setItem(onboardingKey, "true");
          }}
        >
          Пропустить →
        </Link>
      </div>
    </div>
  );
}

