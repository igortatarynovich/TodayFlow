"use client";

type OnboardingHeroSectionProps = {
  buildSteps: Array<{ title: string; done: boolean; active: boolean }>;
};

export function OnboardingHeroSection({ buildSteps }: OnboardingHeroSectionProps) {
  return (
    <div
      className="orbit-card todayflow-panel"
      style={{
        padding: "1.1rem",
        borderRadius: "28px",
        background: "linear-gradient(135deg, rgba(255,253,249,0.96) 0%, rgba(252,246,236,0.94) 100%)",
      }}
    >
      <p className="orbit-body-xs" style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.08em", color: "#ab8750" }}>
        Шаг 1 из 3 · Данные рождения
      </p>
      <h1 className="orbit-display-sm" style={{ margin: "0.45rem 0 0", color: "#37281a" }}>
        Собери основу своего дня
      </h1>
      <p className="orbit-body" style={{ margin: "0.6rem 0 0", color: "#5b4630", maxWidth: "720px" }}>
        Имя, дата и место рождения нужны, чтобы Today стал персональным. Это займёт около минуты — дальше два коротких выбора и ты на своём Today.
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
    </div>
  );
}
