"use client";

import type { ReactNode } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { TodayDayBriefModel } from "@/lib/todayDayBrief";
import styles from "@/components/today/composition/TodayDayBrief.module.css";

/**
 * Block 1 frames — atmosphere (page 1) · orientation (page 2).
 * Canon: TODAY_SCREEN_SCENARIO_V3 v3.4.1
 */

export type TodayDayBriefPane = "atmosphere" | "orientation";

export type TodayDayBriefProps = {
  model: TodayDayBriefModel;
  pane?: TodayDayBriefPane;
  loading?: boolean;
  /** Timeline / поток — only on atmosphere pane. */
  timeline?: ReactNode;
};

export function TodayDayBrief({
  model,
  pane = "atmosphere",
  loading = false,
  timeline = null,
}: TodayDayBriefProps) {
  if (pane === "orientation") {
    return <TodayDayOrientation model={model} loading={loading} />;
  }
  return <TodayDayAtmosphere model={model} loading={loading} timeline={timeline} />;
}

function TodayDayAtmosphere({
  model,
  loading,
  timeline,
}: {
  model: TodayDayBriefModel;
  loading: boolean;
  timeline: ReactNode;
}) {
  const {
    dateLabel,
    salutation,
    atmosphereLine,
    vibe,
    moodPills,
    atmosphereNote,
    expect,
  } = model;
  const line = atmosphereLine ?? vibe;

  return (
    <div
      className={styles.root}
      data-testid="today-day-brief"
      data-pane="atmosphere"
    >
      <header className={styles.hero}>
        <p className={styles.date} data-testid="today-day-brief-date">
          {dateLabel}
        </p>
        <p className={styles.salutation}>{salutation}</p>
        <h2 className={styles.atmosphereLine} data-testid="today-day-brief-vibe">
          {loading ? copy.loadingDay : line || "Сегодняшний день"}
        </h2>
      </header>

      {(moodPills.length > 0 || atmosphereNote) && (
        <section className={styles.section} data-testid="today-day-brief-atmosphere">
          <p className={styles.blockLabel}>{copy.atmosphereLabel}</p>
          {moodPills.length > 0 ? (
            <ul className={styles.moodRow} data-testid="today-day-brief-mood">
              {moodPills.map((m) => (
                <li key={m}>{m}</li>
              ))}
            </ul>
          ) : null}
          {atmosphereNote ? (
            <p className={styles.blockBody} data-testid="today-day-brief-why">
              {atmosphereNote}
            </p>
          ) : null}
        </section>
      )}

      {expect ? (
        <section className={styles.section} data-testid="today-day-brief-expect">
          <p className={styles.blockLabel}>{copy.expectLabel}</p>
          <p className={styles.blockBody}>{expect}</p>
        </section>
      ) : null}

      {timeline ? (
        <section className={styles.timeline} data-testid="today-day-brief-timeline">
          <p className={styles.blockLabel}>{copy.timelineLabel}</p>
          <div className={styles.timelineBody}>{timeline}</div>
        </section>
      ) : null}
    </div>
  );
}

function TodayDayOrientation({
  model,
  loading,
}: {
  model: TodayDayBriefModel;
  loading: boolean;
}) {
  const { trap, doItems, avoidItems, energy, energyCause } = model;
  const hasCues = doItems.length > 0 || avoidItems.length > 0;
  const empty = !trap && !hasCues && !energy && !loading;

  return (
    <div
      className={styles.root}
      data-testid="today-day-brief"
      data-pane="orientation"
    >
      {trap ? (
        <section className={styles.trapBlock} data-testid="today-day-brief-trap">
          <p className={styles.compassLabel}>{copy.trapLabel}</p>
          <p className={styles.compassBody}>{trap}</p>
        </section>
      ) : null}

      {hasCues ? (
        <section className={styles.cuesStack} data-testid="today-day-brief-instruction">
          {doItems.length > 0 ? (
            <div
              className={styles.cueDo}
              data-testid="today-day-brief-do"
              data-polarity="support"
              aria-label="Ориентир"
            >
              <ul className={styles.list}>
                {doItems.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {avoidItems.length > 0 ? (
            <div
              className={styles.cueAvoid}
              data-testid="today-day-brief-avoid"
              data-polarity="caution"
              aria-label="Осторожность"
            >
              <ul className={styles.list}>
                {avoidItems.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>
      ) : null}

      {energy ? (
        <section className={styles.section} data-testid="today-day-brief-energy">
          <p className={styles.blockLabel}>{copy.pulseLabel}</p>
          <p className={styles.blockBody}>{energy}</p>
          {energyCause ? (
            <p className={styles.blockBodyMuted} data-testid="today-day-brief-energy-cause">
              {energyCause}
            </p>
          ) : null}
        </section>
      ) : null}

      {empty ? (
        <p className={styles.blockBodyMuted} data-testid="today-day-brief-orientation-empty">
          {copy.orientationEmpty}
        </p>
      ) : null}
    </div>
  );
}
