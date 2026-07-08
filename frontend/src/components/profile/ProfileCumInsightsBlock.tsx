"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { fetchCompactUserModelConfidenceHistoryCached } from "@/lib/compactUserModelCache";
import {
  buildConfidenceSparklineCells,
  cumDomainRows,
  formatConfidencePercent,
  formatDelta30dLabel,
  formatDeltaWindowLabel,
  shouldShowCumInsights,
  uncertaintyFlagMessage,
} from "@/lib/profileCumInsights";
import type { CompactUserModel, CompactUserModelConfidenceHistory } from "@/lib/types";
import styles from "./quickMap/profileQuickMap.module.css";

type Props = {
  cum: CompactUserModel | null | undefined;
  variant?: "quickMap";
};

export function ProfileCumInsightsBlock({ cum }: Props) {
  const [history, setHistory] = useState<CompactUserModelConfidenceHistory | null>(null);

  useEffect(() => {
    if (!shouldShowCumInsights(cum)) {
      setHistory(null);
      return;
    }
    let cancelled = false;
    void fetchCompactUserModelConfidenceHistoryCached({ windowDays: 90 })
      .then((payload) => {
        if (!cancelled) setHistory(payload);
      })
      .catch(() => {
        if (!cancelled) setHistory(null);
      });
    return () => {
      cancelled = true;
    };
  }, [cum?.as_of, cum?.generated_at]);

  if (!shouldShowCumInsights(cum) || !cum) return null;

  const delta30 = formatDelta30dLabel(cum.confidence?.delta_30d);
  const deltaWindow = formatDeltaWindowLabel(history?.summary?.delta_window, history?.window_days ?? 90);
  const sparkline = buildConfidenceSparklineCells(history?.points ?? []);
  const domains = cumDomainRows(cum);
  const primary = cum.recommendations?.primary;
  const alternates = cum.recommendations?.alternates ?? [];
  const flags = cum.confidence?.uncertainty_flags ?? [];

  return (
    <section className={styles.cumInsightsSection} data-testid="profile-cum-insights" aria-labelledby="profile-cum-insights-title">
      <p id="profile-cum-insights-title" className={styles.quickMapSectionLabel}>
        Уверенность и следующий шаг
      </p>

      <div className={styles.cumInsightsConfidenceRow}>
        <div className={styles.cumInsightsScoreWrap}>
          <p className={styles.cumInsightsScore}>{formatConfidencePercent(cum.confidence?.overall)}</p>
          <p className={styles.cumInsightsScoreCaption}>уверенность модели</p>
        </div>
        <div className={styles.cumInsightsBadges}>
          {delta30 ? <span className={styles.cumInsightsBadge}>{delta30}</span> : null}
          {deltaWindow && deltaWindow !== delta30 ? (
            <span className={styles.cumInsightsBadgeMuted}>{deltaWindow}</span>
          ) : null}
        </div>
      </div>

      {sparkline.length >= 2 ? (
        <div className={styles.cumInsightsSparklineWrap}>
          <div className={styles.cumInsightsSparkline} aria-hidden="true">
            {sparkline.map((cell) => (
              <span
                key={cell.dateISO}
                className={styles.cumInsightsSparkBar}
                style={{ height: `${cell.heightPct}%` }}
                title={`${cell.dateISO}: ${formatConfidencePercent(cell.overall)}`}
              />
            ))}
          </div>
          <p className={styles.cumInsightsSparkCaption}>
            {history?.summary.point_count ?? sparkline.length} точек за {history?.window_days ?? 90} дн
          </p>
        </div>
      ) : null}

      {domains.length ? (
        <div className={styles.cumInsightsDomains}>
          {domains.slice(0, 4).map((row) => (
            <div key={row.id} className={styles.cumInsightsDomainRow}>
              <span className={styles.cumInsightsDomainLabel}>{row.label}</span>
              <span className={styles.cumInsightsDomainBarTrack}>
                <span className={styles.cumInsightsDomainBarFill} style={{ width: `${Math.round(row.value * 100)}%` }} />
              </span>
              <span className={styles.cumInsightsDomainValue}>{formatConfidencePercent(row.value)}</span>
            </div>
          ))}
        </div>
      ) : null}

      {primary?.text ? (
        <article className={styles.cumInsightsRecPrimary}>
          <p className={styles.cumInsightsRecLabel}>Главный шаг</p>
          <p className={styles.cumInsightsRecText}>{primary.text}</p>
          {primary.timing_hint ? <p className={styles.cumInsightsRecMeta}>{primary.timing_hint}</p> : null}
        </article>
      ) : null}

      {alternates.length ? (
        <div className={styles.cumInsightsAlternates}>
          <p className={styles.cumInsightsRecLabel}>Альтернативы</p>
          <ul className={styles.cumInsightsAltList}>
            {alternates.map((alt) => (
              <li key={alt.id} className={styles.cumInsightsAltItem}>
                <span>{alt.text}</span>
                {alt.timing_hint ? <span className={styles.cumInsightsRecMeta}>{alt.timing_hint}</span> : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {flags.length ? (
        <ul className={styles.cumInsightsFlags}>
          {flags.map((flag) => (
            <li key={flag}>{uncertaintyFlagMessage(flag)}</li>
          ))}
        </ul>
      ) : null}

      <Link href="/today" className={styles.cumInsightsTodayLink}>
        Открыть Today для уточнения
      </Link>
    </section>
  );
}
