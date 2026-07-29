"use client";

/**
 * Wave 2 reserved slots — layout only in Wave 1 (stubs OK).
 * Do not remove testids; Wave 2 fills meaning (verdict / ephemeris / accuracy).
 */
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import styles from "@/components/today/composition/TodayWave2Slots.module.css";

export function TodayVerdictStripSlot() {
  return (
    <div
      className={styles.slot}
      data-testid="today-slot-verdict-strip"
      data-wave2-slot="verdict"
      aria-hidden={true}
    />
  );
}

export function TodayGlanceTimelineSlot() {
  return (
    <div
      className={styles.slot}
      data-testid="today-slot-glance-timeline"
      data-wave2-slot="glance"
      aria-hidden={true}
    />
  );
}

type TapProps = {
  onTap?: () => void;
  answered?: boolean | null;
};

export function TodayTapWidgetStub({ onTap, answered = null }: TapProps) {
  return (
    <div className={styles.tap} data-testid="today-slot-tap-widget" data-wave2-slot="tap">
      <p className={styles.tapLabel}>{copy.journey.tapStubLabel}</p>
      <div className={styles.tapRow}>
        <button
          type="button"
          className={styles.tapBtn}
          data-testid="today-tap-yes"
          data-selected={answered === true ? "true" : undefined}
          onClick={() => onTap?.()}
        >
          Да
        </button>
        <button
          type="button"
          className={styles.tapBtn}
          data-testid="today-tap-no"
          data-selected={answered === false ? "true" : undefined}
          onClick={() => onTap?.()}
        >
          Нет
        </button>
      </div>
      <p className={styles.tapHint}>{copy.journey.tapStubHint}</p>
    </div>
  );
}
