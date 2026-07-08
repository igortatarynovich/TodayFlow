"use client";

import type { DayContinuityRecord } from "@/lib/todayDayContinuity";
import { buildTomorrowContinuityHook, outcomeLabelRu } from "@/lib/todayDayContinuity";

type Props = {
  record: DayContinuityRecord;
};

export function TodayDayContinuityClosed({ record }: Props) {
  const hook = buildTomorrowContinuityHook();

  return (
    <section
      className="today-experience-stage-enter"
      data-testid="today-day-continuity-closed"
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        gap: "0.85rem",
        padding: "0.25rem 0",
      }}
    >
      <div
        className="todayflow-surface-primary todayflow-inset"
        style={{
          padding: "1.1rem 1rem",
          borderRadius: 18,
          border: "1px solid rgba(201,168,115,0.28)",
          background: "rgba(255,255,255,0.94)",
        }}
      >
        <p className="todayflow-eyebrow" style={{ margin: 0 }}>
          День закрыт
        </p>
        <h2 className="orbit-heading-2" style={{ margin: "0.35rem 0 0", lineHeight: 1.35, color: "#1f1a16" }}>
          {record.mainFocus}
        </h2>
        {record.outcome ? (
          <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", lineHeight: 1.55, color: "#3d3228" }}>
            Итог: <strong>{outcomeLabelRu(record.outcome)}</strong>
            {record.outcomeNote ? ` — ${record.outcomeNote}` : null}
          </p>
        ) : null}
      </div>

      <p
        className="orbit-body-sm"
        data-testid="today-day-continuity-tomorrow-hook"
        style={{ margin: 0, lineHeight: 1.58, color: "#3d3228" }}
      >
        {hook}
      </p>
    </section>
  );
}
