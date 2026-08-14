"use client";

import { useCallback, useEffect, useId, useState, type ReactNode } from "react";
import { CelestialMoon } from "@/components/celestial/CelestialMoon";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import type { TodayDayBriefModel } from "@/lib/todayDayBrief";
import styles from "@/components/today/composition/TodayDayBrief.module.css";

/**
 * Block 1 — dashboard (mockup-led) + orientation pane.
 * Tap opens detail sheet overlay. Canon: TODAY_SCREEN_SCENARIO_V3 v3.4.2
 */

export type TodayDayBriefPane = "atmosphere" | "orientation";

export type TodayDayBriefProps = {
  model: TodayDayBriefModel;
  pane?: TodayDayBriefPane;
  loading?: boolean;
  timeline?: ReactNode;
  /** Advance ScreenFlow after personal CTA (optional). */
  onContinue?: () => void;
};

type SheetState = {
  title: string;
  body: string;
  kicker?: string;
} | null;

export function TodayDayBrief({
  model,
  pane = "atmosphere",
  loading = false,
  timeline = null,
  onContinue,
}: TodayDayBriefProps) {
  if (pane === "orientation") {
    return <TodayDayOrientation model={model} loading={loading} timeline={timeline} />;
  }
  return (
    <TodayDayDashboard model={model} loading={loading} onContinue={onContinue} />
  );
}

function TodayDayDetailSheet({
  sheet,
  onClose,
}: {
  sheet: SheetState;
  onClose: () => void;
}) {
  const titleId = useId();
  useEffect(() => {
    if (!sheet) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [sheet, onClose]);

  if (!sheet) return null;

  return (
    <div
      className={styles.sheetRoot}
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      data-testid="today-day-detail-sheet"
    >
      <button
        type="button"
        className={styles.sheetBackdrop}
        aria-label={copy.sheetClose}
        onClick={onClose}
      />
      <div className={styles.sheetPanel}>
        {sheet.kicker ? <p className={styles.sheetKicker}>{sheet.kicker}</p> : null}
        <h3 id={titleId} className={styles.sheetTitle}>
          {sheet.title}
        </h3>
        <p className={styles.sheetBody}>{sheet.body}</p>
        <button type="button" className={styles.sheetClose} onClick={onClose}>
          {copy.sheetClose}
        </button>
      </div>
    </div>
  );
}

function TodayDayDashboard({
  model,
  loading,
  onContinue,
}: {
  model: TodayDayBriefModel;
  loading: boolean;
  onContinue?: () => void;
}) {
  const [sheet, setSheet] = useState<SheetState>(null);
  const openSheet = useCallback((next: SheetState) => setSheet(next), []);
  const closeSheet = useCallback(() => setSheet(null), []);

  const {
    dateLabel,
    salutation,
    atmosphereLine,
    vibe,
    moodPills,
    atmosphereNote,
    expect,
    modeLabel,
    lunarCaption,
    moonPhase,
    betterCards,
    supportLine,
    supportDetail,
    trap,
    personalLine,
  } = model;

  const line = atmosphereLine ?? vibe;
  const heroBody = line || expect || atmosphereNote;
  const heroCue = moodPills[0] || null;
  const betterIcon: Record<string, string> = {
    work: "◆",
    people: "◎",
    self: "✧",
  };
  const showMoon = typeof moonPhase === "number" && Number.isFinite(moonPhase);
  const heroMeta = lunarCaption || salutation;

  return (
    <div
      className={[styles.dash, showMoon ? styles.dashWithMoon : null].filter(Boolean).join(" ")}
      data-testid="today-day-brief"
      data-pane="atmosphere"
      data-has-moon={showMoon ? "true" : "false"}
    >
      {showMoon ? (
        <div className={styles.moonBackdrop} aria-hidden data-testid="today-day-brief-moon">
          <CelestialMoon
            phase={moonPhase}
            size={608}
            spin={0.014}
            glow={1.35}
            animated
            textureSrc="/images/celestial/moon_lro_2k.jpg"
            className={styles.moonDisk}
          />
        </div>
      ) : null}

      <div className={styles.dashForeground}>
      <button
        type="button"
        className={styles.heroCard}
        data-testid="today-day-brief-vibe"
        data-mode={model.visualMode || undefined}
        onClick={() =>
          openSheet({
            title: modeLabel || copy.atmosphereLabel,
            kicker: copy.atmosphereLabel,
            body:
              [heroMeta, line, expect, atmosphereNote, heroCue].filter(Boolean).join("\n\n") ||
              copy.loadingDay,
          })
        }
      >
        <div className={styles.heroMeta}>
          <p className={styles.date} data-testid="today-day-brief-date">
            {dateLabel}
          </p>
          {heroMeta ? (
            <p
              className={styles.lunarCaption}
              data-testid={lunarCaption ? "today-day-brief-lunar" : undefined}
            >
              {heroMeta}
            </p>
          ) : null}
        </div>
        <h2 className={styles.heroMode}>
          {loading ? copy.loadingDay : modeLabel || "Сегодня"}
        </h2>
        {heroBody ? <p className={styles.heroBody}>{heroBody}</p> : null}
        {heroCue ? (
          <p className={styles.heroCue} data-testid="today-day-brief-mood">
            {heroCue}
          </p>
        ) : null}
      </button>

      {betterCards.length > 0 ? (
        <section className={styles.section} data-testid="today-day-brief-better">
          <p className={styles.blockLabel}>{copy.betterTodayLabel}</p>
          <div
            className={styles.betterGrid}
            data-count={Math.min(3, betterCards.length)}
          >
            {betterCards.map((card) => (
              <button
                key={card.id}
                type="button"
                className={styles.betterCard}
                data-bucket={card.id}
                data-testid={`today-day-better-${card.id}`}
                onClick={() =>
                  openSheet({
                    title: card.title,
                    kicker: copy.betterTodayLabel,
                    body: card.detail || card.body,
                  })
                }
              >
                <span className={styles.betterIcon} aria-hidden>
                  {betterIcon[card.id] || "•"}
                </span>
                <span className={styles.betterTitle}>{card.title}</span>
                <span className={styles.betterBody}>{card.body}</span>
              </button>
            ))}
          </div>
        </section>
      ) : null}

      {(supportLine || trap) && (
        <section className={styles.pairGrid} data-testid="today-day-brief-pair">
          {supportLine ? (
            <button
              type="button"
              className={styles.supportCard}
              data-testid="today-day-brief-do"
              onClick={() =>
                openSheet({
                  title: copy.supportLabel,
                  body: supportDetail || supportLine,
                })
              }
            >
              <span className={styles.pairLabel}>{copy.supportLabel}</span>
              <span className={styles.pairBody}>{supportLine}</span>
            </button>
          ) : null}
          {trap ? (
            <button
              type="button"
              className={styles.trapCard}
              data-testid="today-day-brief-trap"
              onClick={() =>
                openSheet({
                  title: copy.trapDayLabel,
                  body: trap,
                })
              }
            >
              <span className={styles.pairLabel}>{copy.trapDayLabel}</span>
              <span className={styles.pairBody}>{trap}</span>
            </button>
          ) : null}
        </section>
      )}

      {personalLine || onContinue ? (
        <section className={styles.personalCard} data-testid="today-day-brief-personal">
          <p className={styles.blockLabel}>{copy.personalTodayLabel}</p>
          {personalLine ? (
            <button
              type="button"
              className={styles.personalBodyBtn}
              onClick={() =>
                openSheet({
                  title: copy.personalTodayLabel,
                  body: personalLine,
                })
              }
            >
              <p className={styles.blockBody}>{personalLine}</p>
            </button>
          ) : null}
          {onContinue ? (
            <button
              type="button"
              className={styles.personalCta}
              data-testid="today-day-personal-cta"
              onClick={onContinue}
            >
              {copy.personalTodayCta}
            </button>
          ) : null}
        </section>
      ) : null}

      </div>

      <TodayDayDetailSheet sheet={sheet} onClose={closeSheet} />
    </div>
  );
}

function TodayDayOrientation({
  model,
  loading,
  timeline,
}: {
  model: TodayDayBriefModel;
  loading: boolean;
  timeline: ReactNode;
}) {
  const { trap, doItems, avoidItems, energy, energyCause, expect } = model;
  const hasCues = doItems.length > 0 || avoidItems.length > 0;
  const empty = !trap && !hasCues && !energy && !expect && !timeline && !loading;

  return (
    <div
      className={styles.root}
      data-testid="today-day-brief"
      data-pane="orientation"
    >
      {expect ? (
        <section className={styles.expectCard} data-testid="today-day-brief-expect">
          <p className={styles.blockLabel}>{copy.expectLabel}</p>
          <p className={styles.blockBody}>{expect}</p>
        </section>
      ) : null}

      {trap ? (
        <section className={styles.trapBlock} data-testid="today-day-brief-trap">
          <p className={styles.compassLabel}>{copy.trapLabel}</p>
          <p className={styles.compassBody}>{trap}</p>
        </section>
      ) : null}

      {hasCues ? (
        <section className={styles.cuesStack} data-testid="today-day-brief-instruction">
          {doItems.length > 0 ? (
            <div className={styles.cueDo} data-testid="today-day-brief-do" data-polarity="support">
              <ul className={styles.list}>
                {doItems.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {avoidItems.length > 0 ? (
            <div className={styles.cueAvoid} data-testid="today-day-brief-avoid" data-polarity="caution">
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
        <section className={styles.energyCard} data-testid="today-day-brief-energy">
          <p className={styles.blockLabel}>{copy.pulseLabel}</p>
          <p className={styles.blockBody}>{energy}</p>
          {energyCause ? (
            <p className={styles.blockBodyMuted} data-testid="today-day-brief-energy-cause">
              {energyCause}
            </p>
          ) : null}
        </section>
      ) : null}

      {timeline ? (
        <section className={styles.timeline} data-testid="today-day-brief-timeline">
          <p className={styles.blockLabel}>{copy.timelineLabel}</p>
          <div className={styles.timelineBody}>{timeline}</div>
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
