"use client";

import type { CSSProperties, ReactNode } from "react";
import type { DayEngineBriefForUi, DayModelBriefForUi } from "@/components/today/todayGuideActionable";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";
import { DsBody, DsCallout, DsEmph } from "@/design-system";

type Props = {
  variant: "ritual" | "guide";
  dayEngineBrief: DayEngineBriefForUi | null;
  dayModelBrief: DayModelBriefForUi | null;
  /** Доп. стили переноса (ритуал — `ritualTextWrap`). */
  wrap?: CSSProperties;
};

function HintList({
  hints,
  style,
}: {
  hints: string[];
  style?: CSSProperties;
}) {
  if (!hints.length) return null;
  return (
    <>
      {hints.map((h, i) => (
        <DsBody key={`hint-${i}-${h.slice(0, 24)}`} size="sm" tone="secondary" style={style}>
          {h}
        </DsBody>
      ))}
    </>
  );
}

function FocusLine({ focus, style }: { focus: string; style?: CSSProperties }) {
  return (
    <DsBody size="sm" tone="secondary" style={style}>
      <DsEmph>{RITUAL_COPY.dayModelOneFocusLabel}:</DsEmph> {focus}
    </DsBody>
  );
}

function CalloutShell({
  title,
  children,
  style,
}: {
  title: ReactNode;
  children?: ReactNode;
  style?: CSSProperties;
}) {
  return (
    <DsCallout
      tone="insight"
      label="main"
      icon="spark"
      title={title}
      style={{ marginTop: "0.65rem", ...style }}
      testId="today-day-logic-callout"
    >
      {children}
    </DsCallout>
  );
}

/** Блок «Опора дня» + опционально day_model; иначе только «Логика дня». Паритет ритуал / вкладка Guide. */
export function TodayDayLogicCallout({ variant, dayEngineBrief, dayModelBrief, wrap = {} }: Props) {
  void variant;

  if (dayEngineBrief) {
    return (
      <CalloutShell title={dayEngineBrief.anchor} style={wrap}>
        <HintList hints={dayEngineBrief.hints} style={wrap} />
        {dayModelBrief ? (
          <>
            {dayModelBrief.vectorSummary ? (
              <DsBody size="sm" tone="secondary" style={wrap}>
                {dayModelBrief.vectorSummary}
              </DsBody>
            ) : null}
            <FocusLine focus={dayModelBrief.oneFocus} style={wrap} />
          </>
        ) : null}
      </CalloutShell>
    );
  }

  if (dayModelBrief) {
    const takeaway = dayModelBrief.vectorSummary || dayModelBrief.oneFocus;
    return (
      <CalloutShell title={takeaway} style={wrap}>
        {dayModelBrief.vectorSummary ? <FocusLine focus={dayModelBrief.oneFocus} style={wrap} /> : null}
      </CalloutShell>
    );
  }

  return null;
}
