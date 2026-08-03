"use client";

import { useEffect, useMemo, useState } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import styles from "@/components/today/composition/TodayGlanceAct.module.css";
import {
  formatGlanceClock,
  isGlanceLiveNow,
  type GlanceTimelineItem,
} from "@/lib/todayGlanceTimeline";
import { fetchDayFacts } from "@/lib/todayDayFacts";
import { pickNearestGlanceItem } from "@/lib/todayGlanceNearest";
import { todaySlotFailureCopy, type TodaySlotLoadFailure } from "@/lib/todaySlotAvailability";

export type TodayGlanceTeaser = {
  id: string;
  label: string;
  hook?: string;
  onSelect?: () => void;
};

type Props = {
  dateISO: string;
  /** short_name eyebrow — optional */
  title?: string | null;
  /** Texture: short day overview (dominates). Falls back to thesis/title. */
  dayTexture?: string | null;
  thesis?: string | null;
  teasers: TodayGlanceTeaser[];
  themeLoading?: boolean;
  /** ScreenFlow progress — act index 0-based; display = currentStep / stepCount */
  screenFlowStep?: number;
  screenFlowStepCount?: number;
  /** @deprecated spheres are not Glance hero — kept for call-site compat */
  onSphereSelect?: (domain: string) => void;
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
 * Glance / Сводка — Day Atmosphere surface (FOUNDATION_UI §11.9 + TODAY_SCREEN_SCENARIO_V3).
 * Glass hero + ScreenFlow gauge + sparse chrome — jobs of meaning unchanged.
 */
export function TodayGlanceAct({
  dateISO,
  title = null,
  dayTexture = null,
  thesis = null,
  teasers,
  themeLoading = false,
  screenFlowStep = 0,
  screenFlowStepCount = 6,
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

  const texture =
    (dayTexture || "").trim() || (thesis || "").trim() || (title || "").trim() || null;
  const modeLabel =
    title && texture && title.trim().toLowerCase() !== texture.trim().toLowerCase()
      ? title.trim()
      : null;

  const dateLabel = useMemo(() => formatGlanceDateRu(dateISO), [dateISO]);
  const stepCount = Math.max(1, screenFlowStepCount);
  const currentStep = Math.min(stepCount, Math.max(1, screenFlowStep + 1));
  const gaugePct = currentStep / stepCount;

  // Sparse: prefer symbols ritual teaser only on Glance hero chrome
  const primaryTeaser =
    teasers.find((t) => t.id === "symbols") ?? teasers.find((t) => t.id === "plot") ?? teasers[0] ?? null;

  const gaugeStyle = {
    background: `conic-gradient(var(--day-accent-soft, rgba(120,130,145,0.55)) ${gaugePct * 360}deg, rgba(255,255,255,0.22) 0)`,
  };

  return (
    <div className={styles.root} data-testid="today-zone-glance-act">
      <header className={styles.chrome}>
        <p className={styles.dateLine} data-testid="today-glance-date">
          Сегодня · {dateLabel}
        </p>
      </header>

      <div className={styles.glass} data-testid="today-glance-glass">
        {themeLoading ? (
          <p className={styles.loading}>{copy.loadingDay}</p>
        ) : (
          <>
            {modeLabel ? (
              <p className={styles.eyebrow} data-testid="today-entity-daily-theme-glance">
                {modeLabel}
              </p>
            ) : null}
            {texture ? (
              <h3 className={styles.thesis} data-testid="today-glance-thesis">
                {texture}
              </h3>
            ) : (
              <h3 className={styles.thesis} data-testid="today-entity-daily-theme-glance">
                {copy.journey.glanceTitle}
              </h3>
            )}

            <div
              className={styles.gauge}
              style={gaugeStyle}
              role="img"
              aria-label={`Шаг ${currentStep} из ${stepCount}`}
              data-testid="today-glance-screenflow-gauge"
              data-step={currentStep}
              data-step-count={stepCount}
            >
              <div className={styles.gaugeInner}>
                <span className={styles.gaugeLabel}>Шаг</span>
                <span className={styles.gaugeValue}>
                  {currentStep}/{stepCount}
                </span>
              </div>
            </div>
          </>
        )}
      </div>

      <div className={styles.metaRow} data-testid="today-glance-meta">
        {loaded && loadFailure ? (
          <p
            className={styles.metaFail}
            role="status"
            data-testid="today-glance-meta-fallback"
            data-fallback="true"
            data-failure={loadFailure}
          >
            {todaySlotFailureCopy(loadFailure)}
          </p>
        ) : null}

        <div
          className={styles.nearestInline}
          data-testid="today-slot-glance-nearest"
          data-wave2-slot="glance-nearest"
          data-inline="true"
          data-fallback={loadFailure ? "true" : "false"}
          data-failure={loadFailure || undefined}
        >
          {!loaded ? <div className={styles.nearestSkeleton} data-loading="true" aria-busy="true" /> : null}
          {loaded && !loadFailure && nearest ? (
            <p
              className={styles.nearestInlineText}
              data-valence={nearest.valence}
              data-live={live ? "true" : "false"}
              data-testid={`today-glance-nearest-${nearest.driver_id}`}
            >
              <span className={styles.nearestTime}>{formatGlanceClock(nearest.time_local)}</span>
              <span className={styles.nearestDot} aria-hidden>
                ·
              </span>
              <span className={styles.nearestLabel}>{nearest.label_short}</span>
              {live ? (
                <span className={styles.nearestNow} data-testid="today-glance-now">
                  {copy.journey.glanceNow}
                </span>
              ) : null}
            </p>
          ) : null}
          {loaded && !loadFailure && !nearest ? (
            <p className={styles.nearestEmptyCopy} data-empty="true" data-testid="today-glance-nearest-empty">
              {copy.journey.glanceNearestEmpty}
            </p>
          ) : null}
        </div>
      </div>

      {primaryTeaser ? (
        <ul className={styles.teasers} aria-label={copy.journey.glanceTeasersLabel} data-testid="today-glance-teasers">
          <li>
            <button
              type="button"
              className={styles.teaser}
              data-testid={`today-glance-teaser-${primaryTeaser.id}`}
              data-primary="true"
              onClick={primaryTeaser.onSelect}
            >
              <span className={styles.teaserMark} aria-hidden>
                ·
              </span>
              <span className={styles.teaserText}>
                <span className={styles.teaserLabel}>{primaryTeaser.label}</span>
                {primaryTeaser.hook ? (
                  <span className={styles.teaserHook}>{primaryTeaser.hook}</span>
                ) : null}
              </span>
            </button>
          </li>
        </ul>
      ) : null}
    </div>
  );
}
