"use client";

import { useMemo } from "react";
import { guidanceResultChromeBundle } from "@/components/guidance/guidanceResultChrome";
import type { FlowPracticesChromeLocale } from "@/components/today/flowPracticesMainTabChrome";
import { getLocale } from "@/lib/i18n";

type GuidanceResultCardProps = {
  modeLabel: string;
  title: string;
  currentFocus: string;
  manifestation: string;
  caution: string;
  nextStepText: string;
  nextStepLabel: string;
  onNextStep?: () => void;
  profileHint?: string | null;
};

export function GuidanceResultCard({
  modeLabel,
  title,
  currentFocus,
  manifestation,
  caution,
  nextStepText,
  nextStepLabel,
  onNextStep,
  profileHint,
}: GuidanceResultCardProps) {
  const locale: FlowPracticesChromeLocale = getLocale() === "ru" ? "ru" : "en";
  const gr = useMemo(() => guidanceResultChromeBundle(locale), [locale]);

  return (
    <section
      className="orbit-card guidance-lux-result"
      style={{ padding: "1rem", background: "rgba(255,255,255,0.8)", boxShadow: "0 12px 36px rgba(95, 72, 38, 0.07)" }}
    >
      <style jsx>{`
        .guidance-lux-result-block {
          transition: box-shadow 200ms ease, border-color 200ms ease, transform 200ms ease;
        }
        @media (hover: hover) and (pointer: fine) {
          .guidance-lux-result-block:hover {
            box-shadow: 0 8px 22px rgba(100, 75, 40, 0.07);
            transform: translateY(-0.5px);
          }
        }
      `}</style>
      <div style={{ display: "flex", gap: "0.55rem", flexWrap: "wrap", alignItems: "center", marginBottom: "0.75rem" }}>
        <span
          className="orbit-body-xs"
          style={{
            padding: "0.24rem 0.55rem",
            borderRadius: "999px",
            background: "#fff8ee",
            border: "1px solid #eadfcf",
            color: "#7c6241",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
          }}
        >
          {modeLabel}
        </span>
        {profileHint ? (
          <span className="orbit-body-xs" style={{ color: "#8a6f49" }}>
            {profileHint}
          </span>
        ) : null}
      </div>

      <h3 className="orbit-display-sm" style={{ marginBottom: "0.45rem", color: "#352515" }}>
        {title}
      </h3>

      <div style={{ display: "grid", gap: "0.65rem", marginTop: "0.95rem" }}>
        {[
          [gr.guidanceResultCardBlockCurrent, currentFocus],
          [gr.guidanceResultCardBlockManifestation, manifestation],
          [gr.guidanceResultCardBlockCaution, caution],
          [gr.guidanceResultCardBlockNextStep, nextStepText],
        ].map(([blockTitle, text]) => (
          <div
            key={blockTitle}
            className="guidance-lux-result-block"
            style={{ padding: "0.9rem 0.95rem", borderRadius: "16px", background: "#fffdf9", border: "1px solid #ece4d8" }}
          >
            <p className="orbit-body-xs" style={{ margin: 0, color: "#8a6f49", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              {blockTitle}
            </p>
            <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", color: "#334155", lineHeight: 1.75 }}>
              {text}
            </p>
          </div>
        ))}
      </div>

      {onNextStep ? (
        <button
          type="button"
          onClick={onNextStep}
          className="orbit-button orbit-button-primary"
          style={{ marginTop: "0.95rem", justifyContent: "center" }}
        >
          {nextStepLabel}
        </button>
      ) : null}
    </section>
  );
}
