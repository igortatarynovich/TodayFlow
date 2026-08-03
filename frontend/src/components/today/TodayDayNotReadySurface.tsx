"use client";

import type { DayLifecycleC5 } from "@/lib/todayContract";

function formatReadyAt(lifecycle: DayLifecycleC5 | null): string {
  const clock = (lifecycle?.ready_time || "05:00").trim();
  const iso = lifecycle?.ready_at;
  if (!iso) return clock;
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return clock;
    return d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
  } catch {
    return clock;
  }
}

type Props = {
  lifecycle: DayLifecycleC5 | null;
  primaryAction?: string;
};

/** C5: before ready_at — day plot is closed; calm wait, no scenario leak. */
export function TodayDayNotReadySurface({ lifecycle, primaryAction }: Props) {
  const readyLabel = formatReadyAt(lifecycle);
  return (
    <main
      data-testid="today-day-not-ready"
      style={{
        maxWidth: 560,
        margin: "0 auto",
        padding: "48px 20px 64px",
        minHeight: "70vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        gap: 20,
      }}
    >
      <p
        style={{
          margin: 0,
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          fontSize: 12,
          color: "rgba(63, 52, 40, 0.55)",
        }}
      >
        Сегодня
      </p>
      <h1
        style={{
          margin: 0,
          fontFamily: "var(--font-display, Georgia, serif)",
          fontSize: "clamp(28px, 5vw, 40px)",
          fontWeight: 500,
          lineHeight: 1.15,
          color: "#3f3428",
        }}
      >
        День ещё собирается
      </h1>
      <p
        style={{
          margin: 0,
          fontFamily: "var(--font-body, Georgia, serif)",
          fontSize: 17,
          lineHeight: 1.55,
          color: "rgba(63, 52, 40, 0.78)",
        }}
      >
        {primaryAction?.trim() ||
          `Сценарий будет готов около ${readyLabel}. До этого часа тишина — ничего решать не нужно.`}
      </p>
      <p
        style={{
          margin: 0,
          fontFamily: "var(--font-body, Georgia, serif)",
          fontSize: 15,
          lineHeight: 1.5,
          color: "rgba(63, 52, 40, 0.62)",
        }}
      >
        Мы соберём день один раз к утру. Открой Today после {readyLabel} — или дождись пуша «Твой день
        готов».
      </p>
    </main>
  );
}
