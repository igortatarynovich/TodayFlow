"use client";

import { useEffect, useMemo, useState } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import styles from "@/components/today/composition/TodayGlanceAct.module.css";
import { DsCard } from "@/design-system/primitives/DsCard";
import {
  formatGlanceClock,
  isGlanceLiveNow,
  type GlanceTimelineItem,
} from "@/lib/todayGlanceTimeline";
import { fetchDayFacts } from "@/lib/todayDayFacts";
import { pickNearestGlanceItem } from "@/lib/todayGlanceNearest";
import type { GlanceDailyFocusModel } from "@/lib/todayDailyFocus";
import { TODAY_NO_SHARP_FOCUS_COPY } from "@/lib/todayGlanceTexture";
import { todaySlotFailureCopy, type TodaySlotLoadFailure } from "@/lib/todaySlotAvailability";

export type TodayGlanceTeaser = {
  id: string;
  label: string;
  hook?: string;
  onSelect?: () => void;
};

type Props = {
  dateISO: string;
  /**
   * @deprecated Classification / short_name must not print on Glance.
   * Kept for call-site compat; ignored for visible chrome.
   */
  title?: string | null;
  /** Texture: short day overview (dominates). Falls back to thesis only — never title. */
  dayTexture?: string | null;
  thesis?: string | null;
  teasers: TodayGlanceTeaser[];
  themeLoading?: boolean;
  /**
   * One Daily Focus with prioritize / avoid (canon R15–R17).
   * Replaces legacy ≤2 domain sphere chips.
   */
  dailyFocus?: GlanceDailyFocusModel | null;
  /** Pulse facet — shown as «Энергия дня» when non-empty (honest omit). */
  energyLine?: string | null;
  /** Optional cause under energy effect (chorus). */
  energyCause?: string | null;
  /** Tap nearest timed window → micro-practice (keeps clock/label signal). */
  onNearestSelect?: (item: GlanceTimelineItem) => void;
};

const MONTHS_RU = [
  "января",
  "февраля",
  "марта",
  "апреля",
  "мая",
  "июня",
  "июля",
  "августа",
  "сентября",
  "октября",
  "ноября",
  "декабря",
];

function formatGlanceDateRu(dateISO: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(dateISO.trim());
  if (!m) return dateISO;
  const day = Number(m[3]);
  const month = Number(m[2]) - 1;
  if (month < 0 || month > 11 || !day) return dateISO;
  return `${day} ${MONTHS_RU[month]}`;
}

/**
 * Glance / Сводка — Day Atmosphere + Block Composition (FOUNDATION_UI §16).
 * Progress = ScreenFlow chrome (SCREEN_FLOW §1.5) — no in-hero gauge.
 * Jobs of meaning: TODAY_SCREEN_SCENARIO_V3.
 */
export function TodayGlanceAct({
  dateISO,
  dayTexture = null,
  thesis = null,
  teasers,
  themeLoading = false,
  dailyFocus = null,
  energyLine = null,
  energyCause = null,
  onNearestSelect,
}: Props) {
  const [nearest, setNearest] = useState<GlanceTimelineItem | null>(null);
  const [loadFailure, setLoadFailure] = useState<TodaySlotLoadFailure | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [nowTick, setNowTick] = useState(() => new Date());

  useEffect(() => {
    let cancelled = false;
    setLoaded(false);
    setLoadFailure(null);
    void fetchDayFacts(dateISO)
      .then((data) => {
        if (cancelled) return;
        if (data.is_fallback ?? data.degraded) {
          setLoadFailure("unavailable");
          setNearest(null);
        } else {
          setLoadFailure(null);
          setNearest(pickNearestGlanceItem(data.glance_timeline ?? [], new Date()));
        }
        setLoaded(true);
      })
      .catch(() => {
        if (cancelled) return;
        setLoadFailure("no_connection");
        setNearest(null);
        setLoaded(true);
      });
    return () => {
      cancelled = true;
    };
  }, [dateISO]);

  useEffect(() => {
    if (!nearest) return;
    const id = window.setInterval(() => setNowTick(new Date()), 60_000);
    return () => window.clearInterval(id);
  }, [nearest]);

  const live = nearest ? isGlanceLiveNow(nearest.time_local, nowTick) : false;

  // Never fall back to title/short_name — classification is internal only (SCENARIO_V3).
  const texture = (dayTexture || "").trim() || (thesis || "").trim() || null;
  const thesisLine = (thesis || "").trim() || null;
  const detailLine =
    thesisLine && texture && thesisLine.toLowerCase() !== texture.toLowerCase() ? thesisLine : null;

  const dateLabel = useMemo(() => formatGlanceDateRu(dateISO), [dateISO]);
  const energyText = (energyLine || "").trim() || null;
  const energyCauseText = (energyCause || "").trim() || null;
  const focusTitle = (dailyFocus?.title || "").trim() || null;
  const prioritize = (dailyFocus?.prioritize || "").trim() || null;
  const avoid = (dailyFocus?.avoid || "").trim() || null;
  const hasFocus = Boolean(focusTitle || prioritize || avoid);

  // Sparse: prefer symbols ritual teaser only on Glance hero chrome
  const primaryTeaser =
    teasers.find((t) => t.id === "symbols") ?? teasers.find((t) => t.id === "plot") ?? teasers[0] ?? null;

  return (
    <div className={styles.root} data-testid="today-zone-glance-act">
      <header className={styles.chrome}>
        <p className={styles.todayWord} data-testid="today-glance-today">
          Сегодня
        </p>
        <p className={styles.dateLine} data-testid="today-glance-date">
          {dateLabel}
        </p>
      </header>

      <DsCard variant="glass" size="compact" className={styles.block} testId="today-glance-glass">
        {themeLoading ? (
          <p className={styles.loading}>{copy.loadingDay}</p>
        ) : (
          <>
            <p className={styles.eyebrow} data-testid="today-glance-theme-label">
              {copy.journey.glanceThemeLabel}
            </p>
            {texture ? (
              <h3 className={styles.primary} data-testid="today-glance-thesis">
                {texture}
              </h3>
            ) : (
              <h3 className={styles.primary} data-testid="today-entity-daily-theme-glance">
                {copy.journey.glanceTitle}
              </h3>
            )}
            {detailLine ? (
              <p className={styles.detail} data-testid="today-glance-theme-detail">
                {detailLine}
              </p>
            ) : null}
          </>
        )}
      </DsCard>

      {energyText ? (
        <DsCard variant="glass" size="compact" className={styles.block} testId="today-glance-energy">
          <p className={styles.eyebrow}>{copy.pulseLabel}</p>
          <p className={styles.primaryCompact} data-testid="today-glance-energy-text">
            {energyText}
          </p>
          {energyCauseText ? (
            <p className={styles.detail} data-testid="today-glance-energy-cause">
              {energyCauseText}
            </p>
          ) : null}
        </DsCard>
      ) : null}

      <DsCard variant="glass" size="compact" className={styles.block} testId="today-glance-daily-focus">
        <p className={styles.eyebrow}>{copy.journey.glanceFocusLabel}</p>
        {hasFocus ? (
          <>
            {focusTitle ? (
              <p
                className={styles.primaryCompact}
                data-testid="today-glance-focus-title"
                data-daily-focus-id={dailyFocus?.dailyFocusId}
              >
                {focusTitle}
              </p>
            ) : null}
            {prioritize ? (
              <p className={styles.focusDirection} data-testid="today-glance-focus-prioritize">
                <span className={styles.focusDirectionLabel}>{copy.journey.glanceFocusPrioritize}</span>
                {prioritize}
              </p>
            ) : null}
            {avoid ? (
              <p className={styles.focusDirection} data-testid="today-glance-focus-avoid">
                <span className={styles.focusDirectionLabel}>{copy.journey.glanceFocusAvoid}</span>
                {avoid}
              </p>
            ) : null}
          </>
        ) : (
          <p className={styles.detail} data-testid="today-glance-focus-empty">
            {TODAY_NO_SHARP_FOCUS_COPY}
          </p>
        )}
      </DsCard>

      <DsCard variant="glass" size="compact" className={styles.block} testId="today-glance-meta">
        <p className={styles.eyebrow}>{copy.journey.glanceNearestLabel}</p>

        {loaded && loadFailure ? (
          <p
            className={styles.detail}
            role="status"
            data-testid="today-glance-meta-fallback"
            data-fallback="true"
            data-failure={loadFailure}
          >
            {todaySlotFailureCopy(loadFailure)}
          </p>
        ) : null}

        <div
          className={styles.nearestSlot}
          data-testid="today-slot-glance-nearest"
          data-wave2-slot="glance-nearest"
          data-fallback={loadFailure ? "true" : "false"}
          data-failure={loadFailure || undefined}
        >
          {!loaded ? <div className={styles.nearestSkeleton} data-loading="true" aria-busy="true" /> : null}
          {loaded && !loadFailure && nearest ? (
            onNearestSelect ? (
              <button
                type="button"
                className={styles.nearestPrimaryButton}
                data-valence={nearest.valence}
                data-live={live ? "true" : "false"}
                data-testid={`today-glance-nearest-${nearest.driver_id}`}
                onClick={() => onNearestSelect(nearest)}
              >
                <span className={styles.nearestTime}>{formatGlanceClock(nearest.time_local)}</span>
                <span className={styles.nearestLabel}>{nearest.label_short}</span>
                {live ? (
                  <span className={styles.nearestNow} data-testid="today-glance-now">
                    {copy.journey.glanceNow}
                  </span>
                ) : null}
                <span className={styles.nearestPracticeHint}>{copy.journey.glanceNearestPracticeHint}</span>
              </button>
            ) : (
              <p
                className={styles.nearestPrimary}
                data-valence={nearest.valence}
                data-live={live ? "true" : "false"}
                data-testid={`today-glance-nearest-${nearest.driver_id}`}
              >
                <span className={styles.nearestTime}>{formatGlanceClock(nearest.time_local)}</span>
                <span className={styles.nearestLabel}>{nearest.label_short}</span>
                {live ? (
                  <span className={styles.nearestNow} data-testid="today-glance-now">
                    {copy.journey.glanceNow}
                  </span>
                ) : null}
              </p>
            )
          ) : null}
          {loaded && !loadFailure && !nearest ? (
            <p className={styles.detail} data-empty="true" data-testid="today-glance-nearest-empty">
              {copy.journey.glanceNearestEmpty}
            </p>
          ) : null}
        </div>
      </DsCard>

      {primaryTeaser ? (
        <div data-testid="today-glance-teasers">
          <DsCard
            variant="glass"
            size="compact"
            as="button"
            className={styles.blockTeaser}
            testId={`today-glance-teaser-${primaryTeaser.id}`}
            onClick={primaryTeaser.onSelect}
          >
            <p className={styles.eyebrow}>{copy.journey.glanceTeasersLabel}</p>
            <span className={styles.primaryCompact}>{primaryTeaser.label}</span>
            {primaryTeaser.hook ? <span className={styles.detail}>{primaryTeaser.hook}</span> : null}
          </DsCard>
        </div>
      ) : null}
    </div>
  );
}
