"use client";

import type { CSSProperties } from "react";
import type { DayEngineBriefForUi, DayModelBriefForUi } from "@/components/today/todayGuideActionable";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

const shellRitual: CSSProperties = {
  marginTop: "0.65rem",
  padding: "0.65rem 0.75rem",
  borderRadius: 14,
  border: "1px solid rgba(214,142,122,0.28)",
  background: "rgba(255, 248, 242, 0.72)",
  maxWidth: "40rem",
};

const shellGuide: CSSProperties = {
  marginTop: "0.65rem",
  padding: "0.55rem 0.7rem",
  borderRadius: 12,
  border: "1px solid rgba(214,142,122,0.26)",
  background: "rgba(255, 248, 242, 0.65)",
  maxWidth: "42rem",
};

type Props = {
  variant: "ritual" | "guide";
  dayEngineBrief: DayEngineBriefForUi | null;
  dayModelBrief: DayModelBriefForUi | null;
  /** Доп. стили переноса (ритуал — `ritualTextWrap`). */
  wrap?: CSSProperties;
};

/** Блок «Опора дня» + опционально day_model; иначе только «Логика дня». Паритет ритуал / вкладка Guide. */
export function TodayDayLogicCallout({ variant, dayEngineBrief, dayModelBrief, wrap = {} }: Props) {
  const shell = variant === "ritual" ? shellRitual : shellGuide;
  const isRitual = variant === "ritual";

  if (dayEngineBrief) {
    return (
      <div style={shell}>
        {isRitual ? (
          <p className="todayflow-eyebrow" style={{ margin: "0 0 0.35rem", ...wrap }}>
            {RITUAL_COPY.dayEngineBriefEyebrow}
          </p>
        ) : (
          <p className="orbit-body-xs" style={{ margin: "0 0 0.3rem", color: "#8a6c45", fontWeight: 700 }}>
            {RITUAL_COPY.dayEngineBriefEyebrow}
          </p>
        )}
        <p className="orbit-body-sm" style={{ margin: 0, color: "#3f3428", lineHeight: 1.55, ...(isRitual ? wrap : {}) }}>
          {dayEngineBrief.anchor}
        </p>
        {dayEngineBrief.hints.map((h, i) => (
          <p
            key={`${variant}-de-hint-${i}-${h.slice(0, 24)}`}
            className="orbit-body-xs"
            style={{ margin: isRitual ? "0.35rem 0 0" : "0.3rem 0 0", color: "#5f4930", lineHeight: 1.45, ...(isRitual ? wrap : {}) }}
          >
            {h}
          </p>
        ))}
        {dayModelBrief ? (
          <>
            {dayModelBrief.vectorSummary ? (
              <p
                className="orbit-body-xs"
                style={{
                  margin: isRitual ? "0.4rem 0 0" : "0.35rem 0 0",
                  color: "#5f4930",
                  lineHeight: 1.45,
                  ...(isRitual ? wrap : {}),
                }}
              >
                {dayModelBrief.vectorSummary}
              </p>
            ) : null}
            <p
              className="orbit-body-xs"
              style={{ margin: "0.35rem 0 0", color: "#5f4930", lineHeight: 1.45, ...(isRitual ? wrap : {}) }}
            >
              <strong style={{ color: "#a89880" }}>{RITUAL_COPY.dayModelOneFocusLabel}:</strong> {dayModelBrief.oneFocus}
            </p>
          </>
        ) : null}
      </div>
    );
  }

  if (dayModelBrief) {
    return (
      <div style={shell}>
        {isRitual ? (
          <p className="todayflow-eyebrow" style={{ margin: "0 0 0.35rem", ...wrap }}>
            {RITUAL_COPY.dayModelBriefEyebrow}
          </p>
        ) : (
          <p className="orbit-body-xs" style={{ margin: "0 0 0.3rem", color: "#8a6c45", fontWeight: 700 }}>
            {RITUAL_COPY.dayModelBriefEyebrow}
          </p>
        )}
        {dayModelBrief.vectorSummary ? (
          <p className="orbit-body-sm" style={{ margin: "0 0 0.35rem", color: "#3f3428", lineHeight: 1.55, ...(isRitual ? wrap : {}) }}>
            {dayModelBrief.vectorSummary}
          </p>
        ) : null}
        <p className="orbit-body-sm" style={{ margin: 0, color: "#3f3428", lineHeight: 1.55, ...(isRitual ? wrap : {}) }}>
          <strong style={{ color: "#a89880" }}>{RITUAL_COPY.dayModelOneFocusLabel}:</strong> {dayModelBrief.oneFocus}
        </p>
      </div>
    );
  }

  return null;
}
