"use client";

import Link from "next/link";
import { practicesV2HistoryCopy } from "@/components/practices/v2/practicesV2HistoryCopy";
import type { PracticesV2Locale } from "@/components/practices/v2/practicesV2SystemCopy";
import type { PracticesProgressSummary } from "@/lib/practicesPage/practicesCatalogModel";
import type { PracticeHistoryItem } from "@/lib/types";
import v2 from "@/design-system/layouts/productV2Surface.module.css";
import styles from "@/components/practices/v2/practicesV2History.module.css";

export type PracticesV2HistoryScreenProps = {
  locale: PracticesV2Locale;
  progressSummary: PracticesProgressSummary | null;
  currentStreakDays: number;
  history: PracticeHistoryItem[];
  historyTotal: number;
  categoryLabel: (categoryId: string | null | undefined) => string;
  dateLocaleTag: string;
};

export function PracticesV2HistoryScreen({
  locale,
  progressSummary,
  currentStreakDays,
  history,
  historyTotal,
  categoryLabel,
  dateLocaleTag,
}: PracticesV2HistoryScreenProps) {
  const copy = practicesV2HistoryCopy(locale);

  return (
    <div className={`${v2.pageRoot} ${styles.pageRoot}`} data-testid="practices-v2-history">
      <Link href="/practices" className={styles.backLink}>
        {copy.backLink}
      </Link>

      <header className={styles.header}>
        <h1 className={v2.displayTitle}>{copy.pageTitle}</h1>
        <p className={v2.bodyLead}>{copy.pageSubtitle}</p>
      </header>

      {progressSummary ? (
        <section className={`${v2.surfacePanel} ${styles.panel}`} aria-labelledby="practices-v2-history-stats">
          <h2 id="practices-v2-history-stats" className={v2.sectionTitle}>
            {copy.statsTitle}
          </h2>
          <div className={styles.statsGrid}>
            <StatCard label={copy.currentStreakLabel} value={`${currentStreakDays} ${copy.streakDaysSuffix}`} />
            <StatCard label={locale === "ru" ? "Завершено" : "Completed"} value={String(progressSummary.totalCompleted)} />
            <StatCard
              label={locale === "ru" ? "Персональных" : "Personalized"}
              value={String(progressSummary.personalizedCompleted)}
            />
            <StatCard
              label={locale === "ru" ? "Лучшая серия" : "Best streak"}
              value={String(progressSummary.longestStreakDays)}
            />
            <StatCard
              label={locale === "ru" ? "Недель с практикой" : "Active weeks"}
              value={String(progressSummary.weeksActive)}
            />
          </div>

          {progressSummary.byCategory.length > 0 ? (
            <ul className={styles.categoryList}>
              {progressSummary.byCategory.map((row) => (
                <li key={row.categoryId} className={styles.categoryRow}>
                  <div className={styles.categoryMeta}>
                    <span className={styles.categoryLabel}>{row.label}</span>
                    <span className={styles.categoryCount}>{row.totalCompleted}</span>
                  </div>
                  <div className={styles.categoryTrack}>
                    <div className={styles.categoryFill} style={{ width: `${row.sharePercent}%` }} />
                  </div>
                </li>
              ))}
            </ul>
          ) : null}
        </section>
      ) : null}

      <section className={`${v2.surfacePanel} ${styles.panel}`} aria-labelledby="practices-v2-history-list">
        <h2 id="practices-v2-history-list" className={v2.sectionTitle}>
          {copy.historyTitle} · {historyTotal} {copy.historyCountSuffix}
        </h2>

        {history.length > 0 ? (
          <ul className={styles.historyList}>
            {history.map((item) => (
              <li key={item.id} className={styles.historyItem}>
                <div className={styles.historyMain}>
                  <div className={styles.historyTitleRow}>
                    <h3 className={styles.historyTitle}>{item.practice_title || item.practice_id}</h3>
                    {item.is_personalized ? <span className={styles.badge}>{copy.personalizedBadge}</span> : null}
                    {item.sequence_id ? (
                      <span className={styles.badge}>
                        {copy.seriesStepLabel} {item.step_number}
                      </span>
                    ) : null}
                  </div>
                  <p className={styles.historyMeta}>{categoryLabel(item.category)}</p>
                  <p className={styles.historyMeta}>
                    {new Date(item.completed_at).toLocaleDateString(dateLocaleTag, {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
                <Link
                  href={`/practices/${item.practice_id.split("-step-")[0]}`}
                  className={styles.repeatBtn}
                >
                  {copy.repeatCta}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <div className={styles.emptyState}>
            <p className={styles.emptyTitle}>{copy.emptyTitle}</p>
            <p className={styles.emptyBody}>{copy.emptyBody}</p>
            <Link href="/practices" className={styles.emptyCta}>
              {copy.browseCta}
            </Link>
          </div>
        )}
      </section>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.statCard}>
      <p className={styles.statLabel}>{label}</p>
      <p className={styles.statValue}>{value}</p>
    </div>
  );
}
