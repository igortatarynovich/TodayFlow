"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import {
  PRACTICE_FORMAT_IDS,
  PRACTICE_NEED_IDS,
  formatPracticeMetaLine,
  practiceFormatLabel,
  practiceNeedLabel,
  type PracticeFormatId,
  type PracticeNeedId,
} from "@/lib/practicesPage/practicesCanon";
import {
  practicesStateCycleCopy,
  type PracticesStateCycleCopy,
} from "@/components/practices/stateCycle/practicesStateCycleCopy";
import { HubMusicLayer } from "@/components/practices/stateCycle/HubMusicLayer";
import {
  PracticeFormatIcon,
  PracticeNeedIcon,
} from "@/components/practices/stateCycle/practiceNeedIcons";
import styles from "@/components/practices/stateCycle/practicesStateCycle.module.css";

export type StateCyclePracticeCard = {
  id: string;
  href: string;
  title: string;
  description: string;
  minutes: number | null;
  formatId: PracticeFormatId | null;
  /** Optional CSS url() for recommend hero */
  imageUrl?: string | null;
};

export type StateCycleContinue = {
  href: string;
  title: string;
  minutesDone: number;
  minutesTotal: number;
};

export type StateCycleMyItem = {
  id: string;
  href: string;
  title: string;
};

export type StateCycleTodayRail = {
  mood?: string | null;
  goal?: string | null;
  practiceDone?: string | null;
};

export type PracticesStateCycleScreenProps = {
  locale: "ru" | "en";
  activeNeed: PracticeNeedId;
  onNeedChange: (need: PracticeNeedId) => void;
  activeFormat: PracticeFormatId | null;
  onFormatChange: (format: PracticeFormatId | null) => void;
  recommended: StateCyclePracticeCard | null;
  continueSession?: StateCycleContinue | null;
  momentCards: StateCyclePracticeCard[];
  practiceOfDay: StateCyclePracticeCard | null;
  practiceOfDaySource?: "personalized" | "current" | "catalog_fallback" | null;
  myItems?: StateCycleMyItem[];
  todayRail?: StateCycleTodayRail | null;
  catalogFailed?: boolean;
  onRetryCatalog?: () => void;
  favoritesHref?: string;
};

export function PracticesStateCycleScreen({
  locale,
  activeNeed,
  onNeedChange,
  activeFormat,
  onFormatChange,
  recommended,
  continueSession = null,
  momentCards,
  practiceOfDay,
  practiceOfDaySource = null,
  myItems = [],
  todayRail = null,
  catalogFailed = false,
  onRetryCatalog,
  favoritesHref = "#practices-my",
}: PracticesStateCycleScreenProps) {
  const copy: PracticesStateCycleCopy = practicesStateCycleCopy(locale);
  const minutesShort = copy.minutesShort;

  const recommendStyle: CSSProperties | undefined =
    recommended?.imageUrl != null
      ? ({ ["--psc-recommend-image"]: `url(${recommended.imageUrl})` } as CSSProperties)
      : undefined;

  return (
    <div className={styles.root} data-testid="practices-state-cycle">
      <div className={styles.layout}>
        <div className={styles.main}>
          <header className={styles.header}>
            <div className={styles.headerText}>
              <h1 className={styles.title}>{copy.pageTitle}</h1>
              <p className={styles.subtitle}>{copy.pageSubtitle}</p>
            </div>
            <Link
              href={favoritesHref}
              className={styles.favBtn}
              aria-label={copy.favoritesAria}
              data-testid="practices-favorites"
            >
              ♡
            </Link>
          </header>

          <nav className={styles.chipRow} aria-label={copy.pageSubtitle} data-testid="practices-need-chips">
            {PRACTICE_NEED_IDS.map((id) => (
              <button
                key={id}
                type="button"
                className={`${styles.chip} ${activeNeed === id ? styles.chipActive : ""}`}
                aria-pressed={activeNeed === id}
                onClick={() => onNeedChange(id)}
              >
                <PracticeNeedIcon id={id} className={styles.chipIcon} />
                <span>{practiceNeedLabel(locale, id)}</span>
              </button>
            ))}
          </nav>

          {catalogFailed ? (
            <div className={styles.failBox} role="alert">
              <span>{copy.catalogFailed}</span>
              {onRetryCatalog ? (
                <button type="button" className={styles.retryBtn} onClick={onRetryCatalog}>
                  {copy.retry}
                </button>
              ) : null}
            </div>
          ) : null}

          {recommended ? (
            <section aria-labelledby="psc-recommend-title" data-testid="practices-recommended">
              <div className={styles.recommend} style={recommendStyle}>
                <div
                  className={styles.recommendBg}
                  data-image={recommended.imageUrl ? "1" : "0"}
                  aria-hidden
                />
                <span className={styles.recommendPlay} aria-hidden>
                  ▶
                </span>
                <div className={styles.recommendBody}>
                  <p className={styles.recommendEyebrow}>{copy.recommendedEyebrow}</p>
                  <h2 id="psc-recommend-title" className={styles.recommendTitle}>
                    {recommended.title}
                  </h2>
                  <p className={styles.recommendMeta}>
                    {formatPracticeMetaLine(
                      locale,
                      recommended.minutes,
                      recommended.formatId,
                      minutesShort,
                      copy.audioMusicMeta,
                    )}
                  </p>
                  {recommended.description ? (
                    <p className={styles.recommendDesc}>{recommended.description}</p>
                  ) : null}
                </div>
                <Link href={recommended.href} className={styles.startBtn}>
                  {copy.startCta}
                </Link>
              </div>
            </section>
          ) : null}

          {continueSession ? (
            <Link
              href={continueSession.href}
              className={styles.continue}
              data-testid="practices-continue"
            >
              <div className={styles.continueThumb} aria-hidden />
              <div className={styles.continueMeta}>
                <p className={styles.continueEyebrow}>{copy.continueEyebrow}</p>
                <p className={styles.continueTitle}>{continueSession.title}</p>
                <div className={styles.continueBarTrack} aria-hidden>
                  <div
                    className={styles.continueBarFill}
                    style={{
                      width: `${Math.min(
                        100,
                        Math.round(
                          (continueSession.minutesDone / Math.max(1, continueSession.minutesTotal)) *
                            100,
                        ),
                      )}%`,
                    }}
                  />
                </div>
                <p className={styles.continueProgress}>
                  {copy.continueProgress(continueSession.minutesDone, continueSession.minutesTotal)}
                </p>
              </div>
              <span className={styles.playDot} aria-hidden>
                ▶
              </span>
            </Link>
          ) : null}

          <section aria-labelledby="psc-moment-title" data-testid="practices-moment">
            <div className={styles.sectionHead}>
              <h2 id="psc-moment-title" className={styles.sectionTitle}>
                {copy.momentTitle}
              </h2>
              <a href="#practices-formats" className={styles.seeAll}>
                {copy.seeAll}
              </a>
            </div>
            {momentCards.length === 0 ? (
              <p className={styles.emptyHint}>{copy.emptyMoment}</p>
            ) : (
              <div className={styles.momentRail}>
                {momentCards.map((card, index) => (
                  <Link key={card.id} href={card.href} className={styles.momentCard}>
                    <div className={styles.momentMedia} data-tone={String(index % 4)} aria-hidden>
                      {card.minutes != null ? (
                        <span className={styles.momentBadge}>
                          {card.minutes} {minutesShort}
                        </span>
                      ) : null}
                    </div>
                    <div className={styles.momentBody}>
                      <p className={styles.momentTitle}>{card.title}</p>
                      <p className={styles.momentMeta}>
                        {card.formatId
                          ? practiceFormatLabel(locale, card.formatId)
                          : copy.resultLineFallback}
                      </p>
                      <span className={styles.momentPlay} aria-hidden>
                        ▶
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </section>

          <section
            id="practices-formats"
            className={styles.formatSection}
            aria-labelledby="psc-formats-title"
            data-testid="practices-formats"
          >
            <h2 id="psc-formats-title" className={styles.sectionTitle}>
              {copy.formatsTitle}
            </h2>
            <div className={styles.formatIconRow}>
              {PRACTICE_FORMAT_IDS.map((id) => {
                const active = activeFormat === id;
                return (
                  <button
                    key={id}
                    type="button"
                    className={`${styles.formatChip} ${active ? styles.formatChipActive : ""}`}
                    aria-pressed={active}
                    onClick={() => onFormatChange(active ? null : id)}
                  >
                    <span className={styles.formatGlyph} aria-hidden>
                      <PracticeFormatIcon id={id} />
                    </span>
                    {practiceFormatLabel(locale, id)}
                  </button>
                );
              })}
            </div>
          </section>

          <HubMusicLayer locale={locale} />

          {practiceOfDay ? (
            <Link
              href={practiceOfDay.href}
              className={styles.dayCard}
              data-testid="practices-of-day"
            >
              <div className={styles.dayIcon} aria-hidden>
                ✦
              </div>
              <div className={styles.dayBody}>
                <p className={styles.dayEyebrow}>
                  {practiceOfDaySource === "catalog_fallback"
                    ? copy.practiceOfDayFallbackEyebrow
                    : copy.practiceOfDayEyebrow}
                </p>
                <p className={styles.dayTitle}>{practiceOfDay.title}</p>
                {practiceOfDay.description ? (
                  <p className={styles.dayDesc}>{practiceOfDay.description}</p>
                ) : null}
              </div>
              <span className={styles.chevron} aria-hidden>
                ›
              </span>
            </Link>
          ) : null}

          {myItems.length > 0 ? (
            <section id="practices-my" aria-labelledby="psc-my-title" data-testid="practices-my">
              <h2 id="psc-my-title" className={styles.sectionTitle}>
                {copy.myPracticesTitle}
              </h2>
              <div className={styles.myList}>
                {myItems.map((item) => (
                  <Link key={item.id} href={item.href} className={styles.myRow}>
                    <span>{item.title}</span>
                    <span className={styles.chevron} aria-hidden>
                      ›
                    </span>
                  </Link>
                ))}
              </div>
            </section>
          ) : null}
        </div>

        <aside className={styles.rail} data-testid="practices-today-rail" aria-label={copy.todayRailTitle}>
          <p className={styles.railTitle}>{copy.todayRailTitle}</p>
          {todayRail?.mood ? (
            <p className={styles.railLine}>
              <span className={styles.railMuted}>{copy.todayRailMood}: </span>
              {todayRail.mood}
            </p>
          ) : null}
          {todayRail?.goal ? (
            <p className={styles.railLine}>
              <span className={styles.railMuted}>{copy.todayRailGoal}: </span>
              {todayRail.goal}
            </p>
          ) : null}
          {todayRail?.practiceDone ? (
            <p className={styles.railLine}>
              <span className={styles.railMuted}>{copy.todayRailDone}: </span>
              {todayRail.practiceDone}
            </p>
          ) : null}
          {!todayRail?.mood && !todayRail?.goal && !todayRail?.practiceDone ? (
            <p className={`${styles.railLine} ${styles.railMuted}`}>{copy.todayRailEmpty}</p>
          ) : null}
        </aside>
      </div>
    </div>
  );
}
