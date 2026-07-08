"use client";

import type { DaySkyFact } from "@/lib/todayDaySkyFact";

type Props = {
  greeting: string;
  displayDate: string;
  firstName: string | null;
  skyFact: DaySkyFact;
  continuityLine?: string | null;
  onStartDay: () => void;
};

export function TodayS0Greeting({
  greeting,
  displayDate,
  firstName,
  skyFact,
  continuityLine,
  onStartDay,
}: Props) {
  const nameLine = firstName?.trim() ? `, ${firstName.trim()}` : "";

  return (
    <section
      className="today-experience-stage-enter"
      data-testid="today-experience-s0"
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        gap: "0.85rem",
        minHeight: "min(52dvh, 420px)",
        padding: "0.25rem 0",
      }}
    >
      <div>
        <p className="todayflow-eyebrow" style={{ margin: 0 }}>
          {displayDate}
        </p>
        <h1 className="orbit-heading-1" style={{ margin: "0.35rem 0 0", lineHeight: 1.25, color: "#1f1a16" }}>
          {greeting}
          {nameLine}
        </h1>
      </div>
      {continuityLine ? (
        <p
          className="orbit-body-sm"
          data-testid="today-day-continuity-opening"
          style={{
            margin: 0,
            lineHeight: 1.55,
            color: "#3d3228",
            padding: "0.65rem 0.75rem",
            borderRadius: 12,
            border: "1px solid rgba(201,168,115,0.22)",
            background: "rgba(255,251,245,0.92)",
          }}
        >
          {continuityLine}
        </p>
      ) : null}
      <p
        className="orbit-body-sm"
        data-testid="today-day-sky-fact"
        data-sky-fact-key={skyFact.factKey}
        style={{ margin: 0, lineHeight: 1.55, color: "#3d3228" }}
      >
        {skyFact.factLine}
      </p>
      <button
        type="button"
        className="orbit-button orbit-button-primary"
        style={{ width: "100%", marginTop: "0.35rem" }}
        onClick={onStartDay}
      >
        Начать день
      </button>
    </section>
  );
}
