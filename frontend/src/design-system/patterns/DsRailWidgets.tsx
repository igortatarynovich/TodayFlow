import type { ReactNode } from "react";
import { DsSurface } from "@/design-system/primitives/DsTypography";
import p from "@/design-system/patterns/dsPatterns.module.css";

export type DsTimelineEvent = {
  time: string;
  title: string;
  active?: boolean;
};

export function DsRailPanel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <DsSurface className={p.railPanel}>
      <h2 className={p.railTitle}>{title}</h2>
      {children}
    </DsSurface>
  );
}

export function DsTimeline({ events }: { events: DsTimelineEvent[] }) {
  return (
    <>
      {events.map((event, index) => (
        <div key={`${event.time}-${event.title}`} className={p.timelineItem}>
          <div className={p.timelineMarker}>
            <span className={`${p.timelineDot} ${event.active ? p.timelineDotActive : ""}`} />
            {index < events.length - 1 ? <span className={p.timelineLine} /> : null}
          </div>
          <div>
            <p className={p.timelineTime}>{event.time}</p>
            <p className={p.timelineLabel}>{event.title}</p>
          </div>
        </div>
      ))}
    </>
  );
}

const WEEKDAY_LABELS = ["П", "В", "С", "Ч", "П", "С", "В"];

export function DsWeeklyBars({ values }: { values: number[] }) {
  return (
    <div className={p.weeklyBars}>
      {values.map((value, index) => (
        <div key={WEEKDAY_LABELS[index]} className={p.weeklyBarWrap}>
          <div
            className={`${p.weeklyBar} ${index >= 5 ? p.weeklyBarActive : ""}`}
            style={{ height: `${Math.max(12, value * 100)}%` }}
          />
          <span className={p.weeklyDay}>{WEEKDAY_LABELS[index]}</span>
        </div>
      ))}
    </div>
  );
}

export function DsStreakRing({ days, label = "дней подряд" }: { days: number; label?: string }) {
  const progress = Math.min(1, days / 100);
  return (
    <div className={p.streakRing}>
      <div className={p.streakCircle}>
        <svg viewBox="0 0 100 100" aria-hidden>
          <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(201, 169, 110, 0.2)" strokeWidth="8" />
          <circle
            cx="50"
            cy="50"
            r="42"
            fill="none"
            stroke="#c9a96e"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${progress * 264} 264`}
          />
        </svg>
        <div className={p.streakValue}>{days}</div>
      </div>
      <p className={p.streakLabel}>{label}</p>
    </div>
  );
}
