"use client";

import { useEffect, useState } from "react";
import { TodayVerdictStripSlot } from "@/components/today/composition/TodayWave2Slots";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import styles from "@/components/today/composition/TodayGlanceAct.module.css";
import {
  fetchGlanceTimeline,
  formatGlanceClock,
  isGlanceLiveNow,
  type GlanceTimelineItem,
} from "@/lib/todayGlanceTimeline";
import { pickNearestGlanceItem } from "@/lib/todayGlanceNearest";
import { todaySlotFailureCopy, type TodaySlotLoadFailure } from "@/lib/todaySlotAvailability";

export type TodayGlanceTeaser = {
  id: string;
  label: string;
  onSelect?: () => void;
};

type Props = {
  dateISO: string;
  title: string;
  thesis?: string | null;
  teasers: TodayGlanceTeaser[];
  themeLoading?: boolean;
};

export function TodayGlanceAct({
  dateISO,
  title,
  thesis = null,
  teasers,
  themeLoading = false,
}: Props) {
  const [nearest, setNearest] = useState<GlanceTimelineItem | null>(null);
  const [failure, setFailure] = useState<TodaySlotLoadFailure | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [nowTick, setNowTick] = useState(() => new Date());

  useEffect(() => {
    let cancelled = false;
    setLoaded(false);
    setFailure(null);
    void fetchGlanceTimeline(dateISO)
      .then((data) => {
        if (cancelled) return;
        if (data.is_fallback ?? data.degraded) {
          setFailure("unavailable");
          setNearest(null);
        } else {
          setFailure(null);
          setNearest(pickNearestGlanceItem(data.glance_timeline ?? [], new Date()));
        }
        setLoaded(true);
      })
      .catch(() => {
        if (cancelled) return;
        setFailure("no_connection");
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

  return (
    <div className={styles.root} data-testid="today-zone-glance-act">
      <div className={styles.themeBlock}>
        {themeLoading ? (
          <p className={styles.loading}>{copy.loadingDay}</p>
        ) : (
          <>
            <h3 className={styles.title} data-testid="today-entity-daily-theme-glance">
              {title}
            </h3>
            {thesis ? (
              <p className={styles.thesis} data-testid="today-glance-thesis">
                {thesis}
              </p>
            ) : null}
          </>
        )}
      </div>

      <TodayVerdictStripSlot dateISO={dateISO} />

      <div className={styles.nearest} data-testid="today-slot-glance-nearest" data-wave2-slot="glance-nearest">
        {!loaded ? <div className={styles.nearestSkeleton} aria-busy="true" data-loading="true" /> : null}
        {loaded && failure ? (
          <p className={styles.nearestFail} role="status" data-testid="today-glance-nearest-fallback">
            {todaySlotFailureCopy(failure)}
          </p>
        ) : null}
        {loaded && !failure && nearest ? (
          <div
            className={styles.nearestRow}
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
          </div>
        ) : null}
        {loaded && !failure && !nearest ? <div className={styles.nearestEmpty} data-empty="true" aria-hidden /> : null}
      </div>

      {teasers.length > 0 ? (
        <ul className={styles.teasers} aria-label={copy.journey.glanceTeasersLabel} data-testid="today-glance-teasers">
          {teasers.map((t) => (
            <li key={t.id}>
              <button type="button" className={styles.teaser} data-testid={`today-glance-teaser-${t.id}`} onClick={t.onSelect}>
                <span className={styles.teaserMark} aria-hidden>·</span>
                <span className={styles.teaserLabel}>{t.label}</span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
