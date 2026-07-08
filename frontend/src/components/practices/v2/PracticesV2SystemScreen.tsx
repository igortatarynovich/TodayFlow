"use client";

import Link from "next/link";
import type { CSSProperties } from "react";
import { IconSparkles } from "@/design-system/icons/DsIcons";
import p from "@/design-system/primitives/dsPrimitives.module.css";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import {
  practicesV2Copy,
  type PracticesV2Locale,
} from "@/components/practices/v2/practicesV2SystemCopy";
import type { PracticesProgressSummary } from "@/lib/practicesPage/practicesCatalogModel";
import type { PracticesV2LiveContext } from "@/lib/practicesPage/buildPracticesV2LiveContext";
import styles from "@/components/practices/v2/practicesV2System.module.css";

export type PracticesV2ProgramCard = {
  id: string;
  href: string;
  title: string;
  description: string;
  durationLabel: string;
  tagLabel?: string;
  iconGlyph: string;
  featured?: boolean;
};

export type PracticesV2QuickItem = {
  id: string;
  href: string;
  title: string;
  subtitle: string;
  durationLabel: string;
  iconGlyph: string;
};

export type PracticesV2Tab = {
  id: string;
  label: string;
  tone?: "dark" | "gold" | "default";
};

export type PracticesV2SystemScreenProps = {
  locale: PracticesV2Locale;
  displayName: string;
  userInitial: string;
  statusLabel?: string | null;
  searchQuery: string;
  onSearchChange: (value: string) => void;
  tabs: PracticesV2Tab[];
  activeTabId: string;
  onTabChange: (tabId: string) => void;
  heroBody: string;
  heroEyebrowSuffix?: string | null;
  heroPrimaryHref: string;
  heroSecondaryHref: string;
  historyHref?: string;
  progressSummary?: PracticesProgressSummary | null;
  limitsRemaining?: number | null;
  showGuestProgressHint?: boolean;
  practiceOfDay: {
    title: string;
    description: string;
    minutes: number | null;
    steps: number | null;
    href: string;
  } | null;
  programCards: PracticesV2ProgramCard[];
  quickItems: PracticesV2QuickItem[];
  live: PracticesV2LiveContext;
  monthLabel: string;
  emptyLibraryMessage?: string | null;
};

export function PracticesV2SystemScreen({
  locale,
  displayName,
  userInitial,
  statusLabel,
  searchQuery,
  onSearchChange,
  tabs,
  activeTabId,
  onTabChange,
  heroBody,
  heroEyebrowSuffix,
  heroPrimaryHref,
  heroSecondaryHref,
  historyHref = "/practices/history",
  progressSummary,
  limitsRemaining,
  showGuestProgressHint = false,
  practiceOfDay,
  programCards,
  quickItems,
  live,
  monthLabel,
  emptyLibraryMessage,
}: PracticesV2SystemScreenProps) {
  const copy = practicesV2Copy(locale);
  const ringStyle = {
    "--ring-deg": `${Math.round((live.weeklyPercent / 100) * 360)}deg`,
  } as CSSProperties;

  return (
    <div className={`${v2.pageRoot} ${styles.pageRoot}`} data-testid="practices-v2-system">
      <header className={styles.topBar}>
        <div className={styles.topBarLead}>
          <p className={v2.eyebrow}>{copy.pageEyebrow}</p>
          <h1 className={v2.sectionTitle}>{copy.pageTitle}</h1>
        </div>
        <div className={`${styles.searchField} ${p.search}`.trim()}>
          <IconSparkles aria-hidden />
          <input
            className={p.searchInput}
            value={searchQuery}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder={copy.searchPlaceholder}
            aria-label={copy.searchPlaceholder}
          />
        </div>
      </header>

      <section className={styles.heroGrid} aria-label={copy.heroTitle}>
        <article className={`${v2.surfaceHero} ${styles.heroPanel}`}>
          <div className={styles.heroOrbLarge} aria-hidden />
          <div className={styles.heroOrbMid} aria-hidden />
          <div className={styles.heroOrbSmall} aria-hidden />
          <div className={styles.heroContent}>
            <p className={v2.eyebrow}>
              {copy.heroEyebrow}
              {heroEyebrowSuffix ? ` · ${heroEyebrowSuffix}` : ""}
            </p>
            <h2 className={v2.displayTitle}>{copy.heroTitle}</h2>
            <p className={v2.bodyLead}>{heroBody}</p>
            <div className={styles.heroActions}>
              <Link href={heroPrimaryHref} className={styles.heroPrimaryBtn}>
                {copy.heroPrimaryCta}
              </Link>
              <Link href={heroSecondaryHref} className={styles.heroSecondaryBtn}>
                {copy.heroSecondaryCta}
              </Link>
            </div>
          </div>
        </article>

        {practiceOfDay ? (
          <Link href={practiceOfDay.href} className={styles.practiceOfDayCard}>
            <div className={styles.practiceOfDayGlow} aria-hidden />
            <p className={styles.practiceOfDayEyebrow}>{copy.practiceOfDayEyebrow}</p>
            <h2 className={styles.practiceOfDayTitle}>{practiceOfDay.title}</h2>
            <p className={styles.practiceOfDayBody}>{practiceOfDay.description}</p>
            <div className={styles.practiceOfDayStats}>
              <div className={styles.practiceOfDayStat}>
                <p className={styles.practiceOfDayStatValue}>{practiceOfDay.minutes ?? "—"}</p>
                <p className={styles.practiceOfDayStatLabel}>{copy.practiceOfDayMinutes}</p>
              </div>
              <div className={styles.practiceOfDayStat}>
                <p className={styles.practiceOfDayStatValue}>{practiceOfDay.steps ?? "—"}</p>
                <p className={styles.practiceOfDayStatLabel}>{copy.practiceOfDaySteps}</p>
              </div>
            </div>
          </Link>
        ) : null}
      </section>

      <div className={styles.bottomGrid}>
        <section className={`${v2.surfacePanel} ${styles.libraryPanel}`} aria-labelledby="practices-v2-library">
          <div className={styles.libraryHead}>
            <h2 id="practices-v2-library" className={styles.libraryTitle}>
              {copy.libraryTitle}
            </h2>
            <Link href={historyHref} className={styles.manageFiltersBtn}>
              {copy.viewHistory}
            </Link>
          </div>

          <nav className={styles.tabRow} aria-label={copy.libraryTitle}>
            {tabs.map((tab) => {
              const isActive = tab.id === activeTabId;
              const chipClass = isActive
                ? tab.tone === "gold"
                  ? styles.tabChipActiveGold
                  : styles.tabChipActiveDark
                : "";
              return (
                <button
                  key={tab.id}
                  type="button"
                  className={`${styles.tabChip} ${chipClass}`.trim()}
                  onClick={() => onTabChange(tab.id)}
                >
                  {tab.label}
                </button>
              );
            })}
          </nav>

          {programCards.length > 0 ? (
            <div className={styles.programGrid}>
              {programCards.map((card) => (
                <Link
                  key={card.id}
                  href={card.href}
                  className={`${styles.programCard} ${card.featured ? styles.programCardFeatured : ""}`.trim()}
                >
                  <div className={styles.programCardOrb} aria-hidden />
                  <div className={styles.programCardIcon} aria-hidden>
                    {card.iconGlyph}
                  </div>
                  <h3 className={styles.programCardTitle}>{card.title}</h3>
                  <p className={styles.programCardBody}>{card.description}</p>
                  <div className={styles.programCardMeta}>
                    {card.tagLabel ? <span className={styles.programTag}>{card.tagLabel}</span> : <span />}
                    <span className={styles.programDuration}>{card.durationLabel}</span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <p className={styles.emptyState}>{emptyLibraryMessage ?? "—"}</p>
          )}

          <div className={styles.sectionHead}>
            <h3 className={styles.sectionTitle}>{copy.quickEntryTitle}</h3>
            <Link href={heroSecondaryHref} className={styles.sectionLink}>
              {copy.allPrograms}
            </Link>
          </div>

          <div className={styles.quickList}>
            {quickItems.map((item) => (
              <div key={item.id} className={styles.quickRow}>
                <div className={styles.quickIcon} aria-hidden>
                  {item.iconGlyph}
                </div>
                <div className={styles.quickText}>
                  <p className={styles.quickTitle}>{item.title}</p>
                  <p className={styles.quickSubtitle}>{item.subtitle}</p>
                </div>
                <span className={styles.quickDuration}>{item.durationLabel}</span>
                <Link href={item.href} className={styles.quickOpenBtn}>
                  {copy.openCta}
                </Link>
              </div>
            ))}
          </div>
        </section>

        <aside className={`${v2.surfacePanel} ${styles.progressPanel}`} aria-labelledby="practices-v2-progress">
          <div className={styles.progressHead}>
            <h2 id="practices-v2-progress" className={styles.progressTitle}>
              {copy.progressTitle}
            </h2>
            <span className={styles.progressMonth}>{monthLabel}</span>
          </div>

          <div className={styles.rhythmCard}>
            <div className={styles.rhythmHead}>
              <h3 className={styles.rhythmTitle}>{copy.weeklyRhythm}</h3>
              <span className={styles.rhythmPercent}>{live.weeklyPercent}%</span>
            </div>
            <div className={styles.rhythmRingWrap}>
              <div className={styles.rhythmRing} style={ringStyle}>
                <div className={styles.rhythmRingInner}>
                  <p className={styles.rhythmStreakValue}>{live.streakDays}</p>
                  <p className={styles.rhythmStreakLabel}>{copy.streakDaysLabel}</p>
                </div>
              </div>
            </div>
            <div className={styles.weekdayRow}>
              {live.weekCells.map((cell) => (
                <span
                  key={cell.dateISO}
                  className={`${styles.weekdayPill} ${cell.closed ? styles.weekdayPillActive : ""}`.trim()}
                >
                  {cell.weekdayLabel}
                </span>
              ))}
            </div>
          </div>

          {showGuestProgressHint ? (
            <p className={styles.guestProgressHint}>{copy.guestProgressHint}</p>
          ) : null}

          {progressSummary ? (
            <>
              <dl className={styles.progressStats}>
                <div className={styles.progressStat}>
                  <dt>{copy.totalCompletedLabel}</dt>
                  <dd>{progressSummary.totalCompleted}</dd>
                </div>
                <div className={styles.progressStat}>
                  <dt>{copy.personalizedCompletedLabel}</dt>
                  <dd>{progressSummary.personalizedCompleted}</dd>
                </div>
                <div className={styles.progressStat}>
                  <dt>{copy.longestStreakLabel}</dt>
                  <dd>{progressSummary.longestStreakDays}</dd>
                </div>
                <div className={styles.progressStat}>
                  <dt>{copy.weeksActiveLabel}</dt>
                  <dd>{progressSummary.weeksActive}</dd>
                </div>
                {limitsRemaining != null ? (
                  <div className={styles.progressStat}>
                    <dt>{copy.limitsRemainingLabel}</dt>
                    <dd>{limitsRemaining}</dd>
                  </div>
                ) : null}
              </dl>

              {progressSummary.byCategory.length > 0 ? (
                <div className={styles.categoryBreakdown}>
                  <h3 className={styles.categoryBreakdownTitle}>{copy.byCategoryTitle}</h3>
                  <ul className={styles.categoryBreakdownList}>
                    {progressSummary.byCategory.map((row) => (
                      <li key={row.categoryId} className={styles.categoryBreakdownRow}>
                        <div className={styles.categoryBreakdownMeta}>
                          <span className={styles.categoryBreakdownLabel}>{row.label}</span>
                          <span className={styles.categoryBreakdownCount}>{row.totalCompleted}</span>
                        </div>
                        <div className={styles.categoryBreakdownTrack}>
                          <div
                            className={styles.categoryBreakdownFill}
                            style={{ width: `${row.sharePercent}%` }}
                          />
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </>
          ) : null}
        </aside>
      </div>
    </div>
  );
}
