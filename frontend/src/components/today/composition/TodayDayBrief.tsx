"use client";

import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { TodayDayBriefModel } from "@/lib/todayDayBrief";
import styles from "@/components/today/composition/TodayDayBrief.module.css";

/**
 * Block 1 — day trend ambassador (SCENARIO v3.4).
 * Renders assembled model only — no invent.
 */

export type TodayDayBriefProps = {
  model: TodayDayBriefModel;
  loading?: boolean;
};

export function TodayDayBrief({ model, loading = false }: TodayDayBriefProps) {
  const {
    dateLabel,
    salutation,
    vibe,
    moodPills,
    accents,
    activityTags,
    why,
    energy,
    energyCause,
    expect,
    trap,
    doItems,
    avoidItems,
    vibeClosing,
  } = model;

  const hasInstruction = doItems.length > 0 || avoidItems.length > 0;

  return (
    <div className={styles.root} data-testid="today-day-brief">
      <header className={styles.hero}>
        <p className={styles.date} data-testid="today-day-brief-date">
          {dateLabel}
        </p>
        <p className={styles.salutation}>{salutation}</p>
        <h2 className={styles.vibe} data-testid="today-day-brief-vibe">
          {loading ? copy.loadingDay : vibe || "Сегодняшний день"}
        </h2>
        {moodPills.length > 0 ? (
          <ul className={styles.moodRow} data-testid="today-day-brief-mood">
            {moodPills.map((m) => (
              <li key={m}>{m}</li>
            ))}
          </ul>
        ) : null}
        {accents.length > 0 ? (
          <ul className={styles.accentRow} data-testid="today-day-brief-accents">
            {accents.map((a) => (
              <li key={a}>{a}</li>
            ))}
          </ul>
        ) : null}
      </header>

      {why ? (
        <section className={styles.block} data-testid="today-day-brief-why">
          <p className={styles.blockLabel}>{copy.whyStoryTitle}</p>
          <p className={styles.blockBody}>{why}</p>
        </section>
      ) : null}

      {energy ? (
        <section className={styles.block} data-testid="today-day-brief-energy">
          <p className={styles.blockLabel}>{copy.pulseLabel}</p>
          <p className={styles.blockBody}>{energy}</p>
          {energyCause ? <p className={styles.blockBodyMuted}>{energyCause}</p> : null}
        </section>
      ) : null}

      {activityTags.length > 0 ? (
        <ul className={styles.tagRow} data-testid="today-day-brief-tags">
          {activityTags.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
      ) : null}

      {expect ? (
        <section className={styles.block} data-testid="today-day-brief-expect">
          <p className={styles.blockLabel}>{copy.expectLabel}</p>
          <p className={styles.blockBody}>{expect}</p>
        </section>
      ) : null}

      {trap ? (
        <section className={styles.block} data-testid="today-day-brief-trap">
          <p className={styles.blockLabel}>{copy.trapLabel}</p>
          <p className={styles.blockBody}>{trap}</p>
        </section>
      ) : null}

      {hasInstruction ? (
        <section className={styles.instruction} data-testid="today-day-brief-instruction">
          <p className={styles.blockLabel}>{copy.instructionTitle}</p>
          {doItems.length > 0 ? (
            <div className={styles.block} data-testid="today-day-brief-do">
              <p className={styles.subLabel}>{copy.doLabel}</p>
              <ul className={styles.list}>
                {doItems.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {avoidItems.length > 0 ? (
            <div className={styles.block} data-testid="today-day-brief-avoid">
              <p className={styles.subLabel}>{copy.avoidLabel}</p>
              <ul className={styles.list}>
                {avoidItems.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>
      ) : null}

      {vibeClosing ? (
        <section className={styles.block} data-testid="today-day-brief-vibe-closing">
          <p className={styles.blockLabel}>{copy.vibeLabel}</p>
          <p className={styles.blockBody}>{vibeClosing}</p>
        </section>
      ) : null}
    </div>
  );
}
