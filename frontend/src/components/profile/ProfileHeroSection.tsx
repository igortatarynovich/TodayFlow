"use client";

import {
  SurfaceInsight,
  surfaceInsightStyles,
} from "@/components/foundation/SurfaceInsight";

type ProfileHeroSectionProps = {
  buildSteps: Array<{ title: string; done: boolean; active: boolean }>;
};

/** Показывается только во время сборки ядра профиля. */
export function ProfileHeroSection({ buildSteps }: ProfileHeroSectionProps) {
  return (
    <SurfaceInsight eyebrow="Сборка ядра" data-testid="profile-setup-hero">
      <h1 className={surfaceInsightStyles.sectionTitle}>Собери свою карту жизни</h1>
      <p className={surfaceInsightStyles.sectionLead}>
        Имя, дата, время и место рождения нужны не ради анкеты. Из них строится твоя карта жизни, через которую потом
        читаются Today, таро, прогнозы и совместимость.
      </p>
      <div style={{ marginTop: "0.9rem", display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
        {buildSteps.map((step) => (
          <span
            key={step.title}
            className={`todayflow-step-chip ${step.done ? "todayflow-step-chip--done" : step.active ? "todayflow-step-chip--active" : ""}`}
            style={{ padding: "0.4rem 0.7rem", borderRadius: "999px" }}
          >
            {step.done ? "✓ " : ""}
            {step.title}
          </span>
        ))}
      </div>
    </SurfaceInsight>
  );
}
