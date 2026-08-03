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
import type { GlanceSphereChip } from "@/lib/todayGlanceSphereChips";
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
  /** ≤2 Reading domain chips (SCENARIO_V3 Экран 0). */
  sphereChips?: GlanceSphereChip[];
  /** Pulse facet — shown as «Энергия дня» when non-empty (honest omit). */
  energyLine?: string | null;
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
  sphereChips = [],
  energyLine = null,
  onSphereSelect,
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
        </DsCard>
      ) : null}

      <DsCard variant="glass" size="compact" className={styles.block} testId="today-glance-spheres">
        <p className={styles.eyebrow}>{copy.journey.glanceSpheresLabel}</p>
        {sphereChips.length > 0 ? (
          <ul className={styles.sphereChips} data-testid="today-glance-sphere-chips">
            {sphereChips.map((chip) => (
              <li key={chip.domain}>
                {onSphereSelect ? (
                  <button
                    type="button"
                    className={styles.sphereChip}
                    data-testid={`today-glance-sphere-${chip.domain}`}
                    onClick={() => onSphereSelect(chip.domain)}
                  >
                    {chip.label}
                  </button>
                ) : (
                  <span
                    className={styles.sphereChip}
                    data-testid={`today-glance-sphere-${chip.domain}`}
                  >
                    {chip.label}
                  </span>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className={styles.detail} data-testid="today-glance-spheres-empty">
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
