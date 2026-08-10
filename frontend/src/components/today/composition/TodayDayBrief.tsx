"use client";

import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { HandoffWelcomeGlass } from "@/lib/todayHandoffWelcome";
import styles from "@/components/today/composition/TodayDayBrief.module.css";

/**
 * Block 1 — day trend ambassador (SCENARIO v3.4).
 * Assembles existing contract fields; does not invent copy.
 */

export type TodayDayBriefProps = {
  dateLabel: string;
  salutation: string;
  headline: string | null;
  loading?: boolean;
  welcomeGlass?: HandoffWelcomeGlass | null;
  energyLine?: string | null;
  energyCause?: string | null;
  expect?: string | null;
  trap?: string | null;
  doItems?: string[] | null;
  avoidItems?: string[] | null;
  whyLine?: string | null;
};

export function TodayDayBrief({
  dateLabel,
  salutation,
  headline,
  loading = false,
  welcomeGlass = null,
  energyLine = null,
  energyCause = null,
  expect = null,
  trap = null,
  doItems = null,
  avoidItems = null,
  whyLine = null,
}: TodayDayBriefProps) {
  const vibe = (headline || "").trim() || null;
  const reason = welcomeGlass?.reasonLine?.trim() || whyLine?.trim() || null;
  const doList = (doItems || []).map((s) => s.trim()).filter(Boolean).slice(0, 3);
  const avoidList = (avoidItems || []).map((s) => s.trim()).filter(Boolean).slice(0, 3);
  const expectText = (expect || "").trim() || null;
  const trapText = (trap || "").trim() || null;
  const energy = (energyLine || "").trim() || null;
  const cause = (energyCause || "").trim() || null;

  return (
    <div className={styles.root} data-testid="today-day-brief">
      <p className={styles.date} data-testid="today-day-brief-date">
        {dateLabel}
      </p>
      <p className={styles.salutation}>{salutation}</p>
      <h2 className={styles.vibe} data-testid="today-day-brief-vibe">
        {loading ? copy.loadingDay : vibe || "Сегодняшний день"}
      </h2>

      {welcomeGlass?.moodPills && welcomeGlass.moodPills.length > 0 ? (
        <ul className={styles.moodRow} data-testid="today-day-brief-mood">
          {welcomeGlass.moodPills.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
      ) : null}

      {reason ? (
        <section className={styles.block} data-testid="today-day-brief-why">
          <p className={styles.blockLabel}>{copy.whyStoryTitle}</p>
          <p className={styles.blockBody}>{reason}</p>
        </section>
      ) : null}

      {energy ? (
        <section className={styles.block} data-testid="today-day-brief-energy">
          <p className={styles.blockLabel}>{copy.pulseLabel}</p>
          <p className={styles.blockBody}>{energy}</p>
          {cause ? <p className={styles.blockBodyMuted}>{cause}</p> : null}
        </section>
      ) : null}

      {welcomeGlass?.activityTags && welcomeGlass.activityTags.length > 0 ? (
        <ul className={styles.tagRow} data-testid="today-day-brief-tags">
          {welcomeGlass.activityTags.map((t) => (
            <li key={t}>{t}</li>
          ))}
        </ul>
      ) : null}

      {expectText ? (
        <section className={styles.block} data-testid="today-day-brief-expect">
          <p className={styles.blockLabel}>{copy.expectLabel}</p>
          <p className={styles.blockBody}>{expectText}</p>
        </section>
      ) : null}

      {trapText ? (
        <section className={styles.block} data-testid="today-day-brief-trap">
          <p className={styles.blockLabel}>{copy.trapLabel}</p>
          <p className={styles.blockBody}>{trapText}</p>
        </section>
      ) : null}

      {doList.length > 0 ? (
        <section className={styles.block} data-testid="today-day-brief-do">
          <p className={styles.blockLabel}>{copy.doLabel}</p>
          <ul className={styles.list}>
            {doList.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      ) : null}

      {avoidList.length > 0 ? (
        <section className={styles.block} data-testid="today-day-brief-avoid">
          <p className={styles.blockLabel}>{copy.avoidLabel}</p>
          <ul className={styles.list}>
            {avoidList.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
