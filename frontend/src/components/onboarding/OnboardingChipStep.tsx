"use client";

type OnboardingChipStepProps<T extends string> = {
  stepLabel: string;
  title: string;
  body: string;
  options: Array<{ slug: T; label: string; hint?: string }>;
  selectedSlug: T | null;
  submitting: boolean;
  onSelect: (slug: T) => void;
  hideHeader?: boolean;
};

export function OnboardingChipStep<T extends string>({
  stepLabel,
  title,
  body,
  options,
  selectedSlug,
  submitting,
  onSelect,
  hideHeader = false,
}: OnboardingChipStepProps<T>) {
  return (
    <div
      className="orbit-card todayflow-panel"
      style={{
        padding: "1.15rem",
        borderRadius: "28px",
        background: "linear-gradient(135deg, rgba(255,253,249,0.96) 0%, rgba(252,246,236,0.94) 100%)",
      }}
    >
      <p
        className="orbit-body-xs"
        style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.08em", color: "#ab8750" }}
      >
        {stepLabel}
      </p>
      {hideHeader ? null : (
        <>
          <h1 className="orbit-display-sm" style={{ margin: "0.45rem 0 0", color: "#37281a" }}>
            {title}
          </h1>
          <p className="orbit-body" style={{ margin: "0.6rem 0 0", color: "#5b4630", maxWidth: "640px", lineHeight: 1.6 }}>
            {body}
          </p>
        </>
      )}
      <div
        style={{
          marginTop: "1.1rem",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 148px), 1fr))",
          gap: "0.55rem",
        }}
      >
        {options.map((option) => {
          const selected = selectedSlug === option.slug;
          return (
            <button
              key={option.slug}
              type="button"
              disabled={submitting}
              onClick={() => onSelect(option.slug)}
              className="orbit-button orbit-button-secondary"
              style={{
                minHeight: "3.25rem",
                borderRadius: "16px",
                padding: "0.65rem 0.75rem",
                textAlign: "left",
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
                justifyContent: "center",
                gap: "0.15rem",
                border: selected ? "2px solid rgba(166, 124, 58, 0.85)" : "1px solid rgba(201, 168, 115, 0.28)",
                background: selected ? "rgba(255, 248, 236, 0.98)" : "rgba(255,255,255,0.88)",
                boxShadow: selected ? "0 8px 20px rgba(166, 124, 58, 0.12)" : "none",
                opacity: submitting && !selected ? 0.65 : 1,
                cursor: submitting ? "wait" : "pointer",
              }}
            >
              <span className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#37281a" }}>
                {option.label}
              </span>
              {option.hint ? (
                <span className="orbit-body-xs" style={{ margin: 0, color: "#7a623d", lineHeight: 1.35 }}>
                  {option.hint}
                </span>
              ) : null}
            </button>
          );
        })}
      </div>
    </div>
  );
}
