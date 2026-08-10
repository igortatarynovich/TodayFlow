"use client";

import { LoadingSpinner } from "@/components/orbit";
import { TODAY_COMPOSITION_COPY } from "@/components/today/composition/todayCompositionCopy";
import type { GlanceDailyFocusModel } from "@/lib/todayDailyFocus";
import { TODAY_NO_SHARP_FOCUS_COPY } from "@/lib/todayGlanceTexture";

type Props = {
  model: GlanceDailyFocusModel;
  loading?: boolean;
  loadingLabel?: string;
  surfaceClassName?: string;
};

const copy = TODAY_COMPOSITION_COPY;

export function TodayDailyFocusBlock({
  model,
  loading = false,
  loadingLabel = "Уточняем фокус дня…",
  surfaceClassName,
}: Props) {
  const title = (model.title || "").trim() || null;
  const prioritize = (model.prioritize || "").trim() || null;
  const avoid = (model.avoid || "").trim() || null;
  const hasFocus = Boolean(title || prioritize || avoid);

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
        {copy.journey.glanceFocusLabel}
      </p>
      {loading ? (
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.65rem" }}>
          <LoadingSpinner size="sm" />
          <span className="orbit-body-sm" style={{ color: "#6a5132" }}>
            {loadingLabel}
          </span>
        </div>
      ) : hasFocus ? (
        <>
          {title ? (
            <h2
              className="orbit-heading-2"
              style={{ margin: "0.35rem 0 0", lineHeight: 1.35, color: "#1f1a16" }}
              data-testid="today-experience-focus-title"
            >
              {title}
            </h2>
          ) : null}
          {prioritize ? (
            <p
              className="orbit-body-sm"
              style={{
                margin: "0.55rem 0 0",
                padding: "0.55rem 0.75rem",
                lineHeight: 1.58,
                color: "#1f3d2a",
                background: "color-mix(in srgb, #3d6b4f 12%, transparent)",
                borderLeft: "3px solid #2f5a40",
                borderRadius: "0.55rem",
              }}
              data-testid="today-experience-focus-prioritize"
              data-polarity="support"
              aria-label="Ориентир"
            >
              {prioritize}
            </p>
          ) : null}
          {avoid ? (
            <p
              className="orbit-body-sm"
              style={{
                margin: "0.55rem 0 0",
                padding: "0.55rem 0.75rem",
                lineHeight: 1.58,
                color: "#5c241c",
                background: "color-mix(in srgb, #8a3f35 11%, transparent)",
                borderLeft: "3px solid #7a342c",
                borderRadius: "0.55rem",
              }}
              data-testid="today-experience-focus-avoid"
              data-polarity="caution"
              aria-label="Осторожность"
            >
              {avoid}
            </p>
          ) : null}
        </>
      ) : (
        <p
          className="orbit-body-sm"
          style={{ margin: "0.55rem 0 0", lineHeight: 1.58, color: "#3d3228" }}
          data-testid="today-experience-focus-empty"
        >
          {TODAY_NO_SHARP_FOCUS_COPY}
        </p>
      )}
    </section>
  );
}
