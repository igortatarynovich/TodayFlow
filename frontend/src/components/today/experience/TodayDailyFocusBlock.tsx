"use client";

import { LoadingSpinner } from "@/components/orbit";
import type { DailyFocusModel } from "@/lib/todayDailyFocus";

type Props = {
  model: DailyFocusModel;
  loading?: boolean;
  loadingLabel?: string;
  surfaceClassName?: string;
};

export function TodayDailyFocusBlock({
  model,
  loading = false,
  loadingLabel = "Уточняем фокус дня…",
  surfaceClassName,
}: Props) {
  return (
    <section
      className={`todayflow-surface-primary todayflow-inset ${surfaceClassName ?? ""}`.trim()}
      data-testid="today-daily-focus-block"
      data-daily-focus-id={model.dailyFocusId}
      style={
        surfaceClassName
          ? undefined
          : {
              padding: "1.1rem 1rem",
              borderRadius: 18,
              border: "1px solid rgba(201,168,115,0.28)",
              background: "rgba(255,255,255,0.94)",
            }
      }
    >
      <p className="todayflow-eyebrow" style={{ margin: 0 }}>
        Фокус дня
      </p>
      {loading ? (
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.65rem" }}>
          <LoadingSpinner size="sm" />
          <span className="orbit-body-sm" style={{ color: "#6a5132" }}>
            {loadingLabel}
          </span>
        </div>
      ) : (
        <>
          <h2 className="orbit-heading-2" style={{ margin: "0.35rem 0 0", lineHeight: 1.35, color: "#1f1a16" }}>
            {model.title}
          </h2>
          {model.lines.map((line) => (
            <p
              key={line}
              className="orbit-body-sm"
              style={{ margin: "0.55rem 0 0", lineHeight: 1.58, color: "#3d3228" }}
            >
              {line}
            </p>
          ))}
        </>
      )}
    </section>
  );
}
