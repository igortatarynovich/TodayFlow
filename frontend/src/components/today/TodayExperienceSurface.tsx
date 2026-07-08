"use client";

import { useCallback, useEffect, useMemo, useState, type CSSProperties } from "react";
import {
  buildTodayExperienceActionLine,
  buildTodayExperienceProgress,
  buildTodayExperienceTheme,
} from "@/components/today/todayExperienceModel";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

type Props = {
  displayDate: string;
  guideNarrativeLoading: boolean;
  guideNarrativePayload: Record<string, unknown> | null;
  themeHeadlineFallback: string;
  actionFallback: readonly string[];
  initialActionDone?: boolean;
  streakDays?: number;
  onActionComplete?: () => void;
  onVisible?: () => void;
  textWrap?: CSSProperties;
};

export function TodayExperienceSurface({
  displayDate,
  guideNarrativeLoading,
  guideNarrativePayload,
  themeHeadlineFallback,
  actionFallback,
  initialActionDone = false,
  streakDays = 0,
  onActionComplete,
  onVisible,
  textWrap,
}: Props) {
  const [actionDone, setActionDone] = useState(initialActionDone);

  useEffect(() => {
    setActionDone(initialActionDone);
  }, [initialActionDone]);

  useEffect(() => {
    onVisible?.();
  }, [onVisible]);

  const theme = useMemo(
    () => buildTodayExperienceTheme(guideNarrativePayload, themeHeadlineFallback),
    [guideNarrativePayload, themeHeadlineFallback],
  );
  const actionLine = useMemo(
    () => buildTodayExperienceActionLine(guideNarrativePayload, actionFallback),
    [guideNarrativePayload, actionFallback],
  );
  const progress = useMemo(
    () => buildTodayExperienceProgress({ actionDone, streakDays }),
    [actionDone, streakDays],
  );
  const whyText = useMemo(() => {
    const core = guideNarrativePayload?.core_message;
    if (core && typeof core === "object" && !Array.isArray(core)) {
      const o = core as Record<string, unknown>;
      const body = typeof o.body === "string" ? o.body.trim() : "";
      const risk = typeof o.risk === "string" ? o.risk.trim() : "";
      if (body && risk) return `${body} Риск дня: ${risk}.`;
      if (body) return body;
    }
    const subline = typeof guideNarrativePayload?.subline === "string" ? guideNarrativePayload.subline.trim() : "";
    return subline || RITUAL_COPY.todayExperienceWhyFallback;
  }, [guideNarrativePayload]);

  const onMarkDone = useCallback(() => {
    if (actionDone) return;
    setActionDone(true);
    onActionComplete?.();
  }, [actionDone, onActionComplete]);

  return (
    <div
      id="today-experience-surface"
      className="today-experience-surface"
      style={{
        minHeight: "min(100dvh - 5rem, 720px)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        gap: "1.35rem",
        padding: "0.25rem 0 1.5rem",
        minWidth: 0,
        maxWidth: "100%",
        boxSizing: "border-box",
      }}
    >
      <style jsx global>{`
        @keyframes todayExperienceShimmer {
          0% {
            background-position: 200% 0;
          }
          100% {
            background-position: -200% 0;
          }
        }
        .today-experience-shimmer {
          height: 1.5rem;
          border-radius: 8px;
          background: linear-gradient(
            90deg,
            rgba(214, 142, 122, 0.1) 0%,
            rgba(214, 142, 122, 0.22) 50%,
            rgba(214, 142, 122, 0.1) 100%
          );
          background-size: 200% 100%;
          animation: todayExperienceShimmer 1.2s ease-in-out infinite;
        }
      `}</style>

      <header style={{ minWidth: 0 }}>
        <p className="todayflow-eyebrow" style={{ margin: 0, ...textWrap }}>
          {RITUAL_COPY.todayExperienceDayEyebrow}
        </p>
        <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7a623d", ...textWrap }}>
          {displayDate}
        </p>
      </header>

      <section aria-labelledby="today-experience-theme" style={{ minWidth: 0 }}>
        <h1
          id="today-experience-theme"
          className="todayflow-title-hero"
          style={{
            margin: 0,
            fontSize: "clamp(1.85rem, 5vw, 2.35rem)",
            lineHeight: 1.15,
            color: "#2d241c",
            ...textWrap,
          }}
        >
          {guideNarrativeLoading ? (
            <span className="today-experience-shimmer" style={{ display: "block", width: "min(18rem, 88%)" }} aria-hidden />
          ) : (
            theme.headline
          )}
        </h1>
        {!guideNarrativeLoading && theme.meta ? (
          <p
            className="orbit-body-sm"
            style={{ margin: "0.55rem 0 0", color: "#6a5132", lineHeight: 1.5, ...textWrap }}
          >
            {theme.meta}
          </p>
        ) : null}
      </section>

      <section
        aria-labelledby="today-experience-action-label"
        className="todayflow-surface-primary todayflow-inset"
        style={{
          padding: "1.1rem 1.15rem 1.15rem",
          borderRadius: 8,
          minWidth: 0,
          border: "1px solid rgba(201, 168, 115, 0.28)",
          background: "linear-gradient(165deg, rgba(255,252,248,0.98), rgba(255,244,232,0.92))",
        }}
      >
        <p
          id="today-experience-action-label"
          className="todayflow-eyebrow"
          style={{ margin: "0 0 0.5rem", ...textWrap }}
        >
          {RITUAL_COPY.todayExperienceActionLabel}
        </p>
        {guideNarrativeLoading ? (
          <div className="today-experience-shimmer" style={{ width: "100%", marginBottom: "0.85rem" }} aria-hidden />
        ) : (
          <p
            className="orbit-body-sm"
            style={{ margin: "0 0 1rem", color: "#3f3428", fontWeight: 600, lineHeight: 1.55, ...textWrap }}
          >
            {actionLine}
          </p>
        )}
        <button
          type="button"
          onClick={onMarkDone}
          disabled={guideNarrativeLoading || actionDone}
          className="orbit-button orbit-button-primary"
          style={{
            width: "100%",
            justifyContent: "center",
            padding: "0.9rem 1.1rem",
            fontSize: "1.02rem",
            fontWeight: 700,
            opacity: actionDone ? 0.72 : 1,
            ...textWrap,
          }}
        >
          {actionDone ? RITUAL_COPY.todayExperienceActionDoneCta : RITUAL_COPY.todayExperienceActionCta}
        </button>
      </section>

      <section
        aria-label={RITUAL_COPY.todayExperienceProgressLabel}
        style={{ minWidth: 0 }}
      >
        <p className="todayflow-eyebrow" style={{ margin: "0 0 0.5rem", ...textWrap }}>
          {RITUAL_COPY.todayExperienceProgressLabel}
        </p>
        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            gap: "0.65rem",
            padding: "0.15rem 0.1rem",
          }}
        >
          <span
            aria-hidden
            style={{
              width: 10,
              height: 10,
              marginTop: "0.35rem",
              borderRadius: "50%",
              flexShrink: 0,
              background: progress.active ? "#7a9a6e" : "transparent",
              border: progress.active ? "none" : "2px solid rgba(122, 98, 61, 0.45)",
              boxShadow: progress.active ? "0 0 0 3px rgba(122, 154, 110, 0.22)" : "none",
            }}
          />
          <div style={{ minWidth: 0, flex: 1 }}>
            <p
              className="orbit-body-sm"
              style={{
                margin: 0,
                color: progress.active ? "#3f3428" : "#5f4930",
                fontWeight: progress.active ? 700 : 600,
                lineHeight: 1.45,
                ...textWrap,
              }}
            >
              {progress.primary}
            </p>
            {progress.secondary ? (
              <p
                className="orbit-body-xs"
                style={{ margin: "0.35rem 0 0", color: "#7a623d", lineHeight: 1.5, ...textWrap }}
              >
                {progress.secondary}
              </p>
            ) : null}
          </div>
        </div>
      </section>

      <details
        style={{
          borderTop: "1px solid rgba(122, 98, 61, 0.18)",
          paddingTop: "0.85rem",
          minWidth: 0,
        }}
      >
        <summary
          className="orbit-body-sm"
          style={{
            cursor: "pointer",
            color: "#5f4930",
            fontWeight: 700,
            listStyle: "none",
            ...textWrap,
          }}
        >
          {RITUAL_COPY.todayExperienceWhySummary}
        </summary>
        <p className="orbit-body-xs" style={{ margin: "0.55rem 0 0", color: "#7a623d", lineHeight: 1.55, ...textWrap }}>
          {whyText}
        </p>
      </details>
    </div>
  );
}
