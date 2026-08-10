"use client";

import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { TodayDayBriefModel } from "@/lib/todayDayBrief";
import styles from "@/components/today/composition/TodayDayBrief.module.css";

/**
 * Block 1 — day trend ambassador (SCENARIO v3.4+ useful compass).
 * Scan hierarchy: vibe → short why → Trap ‖ Instruction → secondary expect/energy.
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
    why,
    energy,
    energyCause,
    expect,
    trap,
    doItems,
    avoidItems,
    vibeClosing,
  } = model;

  const hasCompass = Boolean(trap) || doItems.length > 0 || avoidItems.length > 0;

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
        <section className={styles.why} data-testid="today-day-brief-why">
          <p className={styles.blockBody}>{why}</p>
        </section>
      ) : null}

      {hasCompass ? (
        <section className={styles.compass} data-testid="today-day-brief-compass">
          {trap ? (
            <div className={styles.compassTrap} data-testid="today-day-brief-trap">
              <p className={styles.compassLabel}>{copy.trapLabel}</p>
              <p className={styles.compassBody}>{trap}</p>
            </div>
          ) : null}
          {doItems.length > 0 || avoidItems.length > 0 ? (
            <div className={styles.compassDo} data-testid="today-day-brief-instruction">
              {doItems.length > 0 ? (
                <div data-testid="today-day-brief-do">
                  <p className={styles.compassLabel}>{copy.doLabel}</p>
                  <ul className={styles.list}>
                    {doItems.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              {avoidItems.length > 0 ? (
                <div data-testid="today-day-brief-avoid">
                  <p className={styles.compassLabel}>{copy.avoidLabel}</p>
                  <ul className={styles.list}>
                    {avoidItems.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          ) : null}
        </section>
      ) : null}

      {expect ? (
        <section className={styles.secondary} data-testid="today-day-brief-expect">
          <p className={styles.blockLabel}>{copy.expectLabel}</p>
          <p className={styles.blockBodyMuted}>{expect}</p>
        </section>
      ) : null}

      {energy ? (
        <section className={styles.secondary} data-testid="today-day-brief-energy">
          <p className={styles.blockLabel}>{copy.pulseLabel}</p>
          <p className={styles.blockBodyMuted}>{energy}</p>
          {energyCause ? <p className={styles.blockBodyMuted}>{energyCause}</p> : null}
        </section>
      ) : null}

      {vibeClosing ? (
        <section className={styles.secondary} data-testid="today-day-brief-vibe-closing">
          <p className={styles.blockLabel}>{copy.vibeLabel}</p>
          <p className={styles.blockBodyMuted}>{vibeClosing}</p>
        </section>
      ) : null}
    </div>
  );
}
