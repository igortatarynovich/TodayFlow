"use client";

import type { CSSProperties } from "react";
import { useEffect, useRef } from "react";
import { RITUAL_COPY } from "@/components/today/todayRitualCopy";

export type TodayDayHistoryStripProps = {
  line: string;
  /** O7: `null` — не показывать нижнюю подсказку; `undefined` — `RITUAL_COPY.dayHistoryHint`. */
  footerHint?: string | null;
  /** DE-9 v1.2: сводка `trailing_7d_summary`, если есть в ответе fusion. */
  weekSummaryLine?: string | null;
  /** DE-9 v1.4: смысловые шаги вчера (`meaning_day_signals`). */
  meaningLine?: string | null;
  /** DE-9 v1.5: вечерняя заметка / дневник вчера. */
  reflectionLine?: string | null;
  /** DE-9 §5.2: один раз, когда блок впервые попадает во viewport (learning). */
  onFirstVisible?: (() => void) | null;
  ritualTextWrap: CSSProperties;
  ritualSectionContain: CSSProperties;
  /** Обёртка: в ритуале — отступ сверху после callout; в «Твой день» — снизу под заголовком секции. */
  style?: CSSProperties;
};

/** DE-9: один визуальный блок для `fusion.day_history` (паритет iOS `dayReadyBlock` / `spheresTriadBlock`). */
export function TodayDayHistoryStrip(props: TodayDayHistoryStripProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const firedRef = useRef(false);
  const footerHint = props.footerHint === undefined ? RITUAL_COPY.dayHistoryHint : props.footerHint;

  useEffect(() => {
    const cb = props.onFirstVisible;
    if (!cb || firedRef.current) return;
    if (typeof IntersectionObserver === "undefined") return;
    const el = rootRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting && e.intersectionRatio >= 0.2) {
            firedRef.current = true;
            cb();
            obs.disconnect();
            return;
          }
        }
      },
      { threshold: [0, 0.2, 0.35, 0.5] },
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [props.onFirstVisible]);

  return (
    <div
      ref={rootRef}
      className="todayflow-surface-soft todayflow-inset"
      data-testid="today-day-history-strip"
      style={{
        padding: "0.65rem 0.85rem",
        borderRadius: 14,
        ...props.ritualSectionContain,
        ...props.style,
      }}
    >
      <p className="todayflow-eyebrow" style={{ margin: "0 0 0.35rem", fontSize: "0.68rem", ...props.ritualTextWrap }}>
        {RITUAL_COPY.dayHistoryEyebrow}
      </p>
      <p className="orbit-body-xs" style={{ margin: 0, color: "#4a3828", lineHeight: 1.5, fontWeight: 600, ...props.ritualTextWrap }}>
        {props.line}
      </p>
      {props.meaningLine ? (
        <p
          className="orbit-body-xs"
          data-testid="today-day-history-meaning-line"
          style={{ margin: "0.35rem 0 0", color: "#5c4d3a", lineHeight: 1.45, fontWeight: 600, ...props.ritualTextWrap }}
        >
          {props.meaningLine}
        </p>
      ) : null}
      {props.reflectionLine ? (
        <p
          className="orbit-body-xs"
          data-testid="today-day-history-reflection-line"
          style={{ margin: "0.35rem 0 0", color: "#5c4d3a", lineHeight: 1.45, fontWeight: 500, fontStyle: "italic", ...props.ritualTextWrap }}
        >
          {props.reflectionLine}
        </p>
      ) : null}
      {props.weekSummaryLine ? (
        <p
          className="orbit-body-xs"
          data-testid="today-day-history-week-summary"
          style={{ margin: "0.35rem 0 0", color: "#5c4d3a", lineHeight: 1.45, fontWeight: 600, ...props.ritualTextWrap }}
        >
          {props.weekSummaryLine}
        </p>
      ) : null}
      {footerHint ? (
        <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7a6a52", lineHeight: 1.45, ...props.ritualTextWrap }}>
          {footerHint}
        </p>
      ) : null}
    </div>
  );
}
