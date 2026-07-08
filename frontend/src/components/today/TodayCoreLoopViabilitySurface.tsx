"use client";

import type { CSSProperties, ReactNode } from "react";
import {
  guideCanonicalPrimaryStepLine,
  parseCoreMessageForUi,
} from "@/components/today/todayGuideActionable";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

function narrativeString(payload: Record<string, unknown> | null | undefined, key: string): string | null {
  if (!payload || typeof payload !== "object") return null;
  const v = payload[key];
  return typeof v === "string" && v.trim() ? v.trim() : null;
}

type Props = {
  displayDate: string;
  guideNarrativeLoading: boolean;
  guideNarrativePayload: Record<string, unknown> | null;
  onOpenOptionalRitual?: () => void;
  ritualTextWrap?: CSSProperties;
};

function blockShell(
  eyebrow: string,
  body: ReactNode,
  ritualTextWrap: CSSProperties | undefined,
  loading: boolean,
) {
  return (
    <div
      className="todayflow-surface-primary todayflow-inset"
      style={{
        padding: "0.85rem 1rem",
        borderRadius: 14,
        minWidth: 0,
      }}
    >
      <p className="todayflow-eyebrow" style={{ margin: "0 0 0.4rem", ...ritualTextWrap }}>
        {eyebrow}
      </p>
      {loading ? (
        <div
          aria-hidden
          style={{
            height: "1.35rem",
            borderRadius: 6,
            background: "linear-gradient(90deg, rgba(214,142,122,0.12) 0%, rgba(214,142,122,0.22) 50%, rgba(214,142,122,0.12) 100%)",
            backgroundSize: "200% 100%",
            animation: "todayCoreLoopShimmer 1.2s ease-in-out infinite",
          }}
        />
      ) : (
        body
      )}
    </div>
  );
}

export function TodayCoreLoopViabilitySurface({
  displayDate,
  guideNarrativeLoading,
  guideNarrativePayload,
  onOpenOptionalRitual,
  ritualTextWrap,
}: Props) {
  const core = parseCoreMessageForUi(guideNarrativePayload);
  const headline =
    narrativeString(guideNarrativePayload, "headline") ||
    (core?.kind === "structured" ? core.headline : undefined) ||
    null;
  const subline =
    narrativeString(guideNarrativePayload, "subline") ||
    (core?.kind === "structured" ? core.body : core?.kind === "paragraphs" ? core.paragraphs[0] : null);
  const themeLine = headline || subline || RITUAL_COPY.coreLoopViabilityThemeFallback;
  const themeDetail = headline && subline && subline !== headline ? subline : null;

  const actionLine = guideCanonicalPrimaryStepLine(
    guideNarrativePayload,
    [],
    RITUAL_COPY.guidePrimaryDoFallback,
  );

  return (
    <div id="today-core-loop-viability" style={{ minWidth: 0, maxWidth: "100%" }}>
      <style jsx global>{`
        @keyframes todayCoreLoopShimmer {
          0% {
            background-position: 200% 0;
          }
          100% {
            background-position: -200% 0;
          }
        }
      `}</style>
      <p className="todayflow-eyebrow" style={{ margin: "0 0 0.65rem", ...ritualTextWrap }}>
        {displayDate} · {RITUAL_COPY.coreLoopViabilityExperimentEyebrow}
      </p>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.65rem" }}>
        {blockShell(
          RITUAL_COPY.coreLoopViabilityThemeEyebrow,
          (
            <>
              <p
                className="orbit-body-sm"
                style={{ margin: 0, color: "#3f3428", fontWeight: 700, lineHeight: 1.5, ...ritualTextWrap }}
              >
                {themeLine}
              </p>
              {themeDetail ? (
                <p
                  className="orbit-body-sm"
                  style={{ margin: "0.45rem 0 0", color: "#5f4930", lineHeight: 1.55, ...ritualTextWrap }}
                >
                  {themeDetail}
                </p>
              ) : null}
            </>
          ),
          ritualTextWrap,
          guideNarrativeLoading,
        )}
        {blockShell(
          RITUAL_COPY.coreLoopViabilityActionEyebrow,
          (
            <p
              className="orbit-body-sm"
              style={{ margin: 0, color: "#3f3428", fontWeight: 600, lineHeight: 1.55, ...ritualTextWrap }}
            >
              {actionLine}
            </p>
          ),
          ritualTextWrap,
          guideNarrativeLoading,
        )}
        {blockShell(
          RITUAL_COPY.coreLoopViabilityProgressEyebrow,
          (
            <>
              <p
                className="orbit-body-sm"
                style={{ margin: 0, color: "#3f3428", fontWeight: 600, lineHeight: 1.5, ...ritualTextWrap }}
              >
                {RITUAL_COPY.coreLoopViabilityProgressDayOne}
              </p>
              <p
                className="orbit-body-xs"
                style={{ margin: "0.4rem 0 0", color: "#5f4930", lineHeight: 1.5, ...ritualTextWrap }}
              >
                {RITUAL_COPY.coreLoopViabilityProgressAfterHint}
              </p>
            </>
          ),
          ritualTextWrap,
          false,
        )}
      </div>
      {onOpenOptionalRitual ? (
        <button
          type="button"
          onClick={onOpenOptionalRitual}
          className="orbit-button orbit-button-secondary orbit-button-sm"
          style={{ width: "100%", marginTop: "0.75rem", ...ritualTextWrap }}
        >
          {RITUAL_COPY.coreLoopViabilityOptionalRitualCta}
        </button>
      ) : null}
    </div>
  );
}
