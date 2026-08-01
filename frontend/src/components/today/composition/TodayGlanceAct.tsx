"use client";

import { useEffect, useState } from "react";
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
  /** @deprecated spheres are not Glance hero — kept for call-site compat */
  onSphereSelect?: (domain: string) => void;
};

/**
 * Glance / Сводка — 2-second day overview.
 * Not four spheres. Hooks live in Symbols ritual act.
 */
export function TodayGlanceAct({
  dateISO,
  title = null,
  dayTexture = null,
  thesis = null,
  teasers,
  themeLoading = false,
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
  const eyebrow =
    title && texture && title.trim().toLowerCase() !== texture.trim().toLowerCase()
      ? title.trim()
      : null;

  // Prefer symbols teaser first — hooks are the next center after overview.
  const orderedTeasers = (() => {
    const symbols = teasers.filter((t) => t.id === "symbols");
    const rest = teasers.filter((t) => t.id !== "symbols");
    return [...symbols, ...rest];
  })();

  return (
    <div className={styles.root} data-testid="today-zone-glance-act">
      <div className={styles.themeBlock}>
        {themeLoading ? (
          <p className={styles.loading}>{copy.loadingDay}</p>
        ) : (
          <>
            {eyebrow ? (
              <p className={styles.eyebrow} data-testid="today-entity-daily-theme-glance">
                {eyebrow}
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
            <p className={styles.glanceLead} data-testid="today-glance-lead">
              {copy.journey.glanceLead}
            </p>
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

      {orderedTeasers.length > 0 ? (
        <ul className={styles.teasers} aria-label={copy.journey.glanceTeasersLabel} data-testid="today-glance-teasers">
          {orderedTeasers.map((t) => (
            <li key={t.id}>
              <button
                type="button"
                className={styles.teaser}
                data-testid={`today-glance-teaser-${t.id}`}
                data-primary={t.id === "symbols" ? "true" : undefined}
                onClick={t.onSelect}
              >
                <span className={styles.teaserMark} aria-hidden>
                  ·
                </span>
                <span className={styles.teaserText}>
                  <span className={styles.teaserLabel}>{t.label}</span>
                  {t.hook ? <span className={styles.teaserHook}>{t.hook}</span> : null}
                </span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
