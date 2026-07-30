"use client";

import { useEffect, useMemo, useState } from "react";
import { TodayVerdictStripSlot } from "@/components/today/composition/TodayWave2Slots";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import styles from "@/components/today/composition/TodayGlanceAct.module.css";
import {
  formatGlanceClock,
  isGlanceLiveNow,
  type GlanceTimelineItem,
} from "@/lib/todayGlanceTimeline";
import { fetchDayFacts } from "@/lib/todayDayFacts";
import type { DomainVerdict } from "@/lib/todayDomainVerdicts";
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
  const [dayFactsSlice, setDayFactsSlice] = useState<{
    domain_verdicts: DomainVerdict[];
    glance_timeline: GlanceTimelineItem[];
    day_facts_id: string | null;
    is_fallback?: boolean;
    degraded?: boolean;
  } | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoaded(false);
    setFailure(null);
    setDayFactsSlice(null);
    void fetchDayFacts(dateISO)
      .then((data) => {
        if (cancelled) return;
        const slice = {
          domain_verdicts: data.domain_verdicts ?? [],
          glance_timeline: data.glance_timeline ?? [],
          day_facts_id: data.id ?? null,
          is_fallback: data.is_fallback,
          degraded: data.degraded,
        };
        setDayFactsSlice(slice);
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
        setDayFactsSlice(null);
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

  const stripFacts = useMemo(() => {
    if (!loaded) return undefined;
    if (failure) {
      return {
        domain_verdicts: [] as DomainVerdict[],
        glance_timeline: [] as GlanceTimelineItem[],
        day_facts_id: null as string | null,
        loadFailure: failure,
      };
    }
    if (dayFactsSlice) return dayFactsSlice;
    return undefined;
  }, [loaded, failure, dayFactsSlice]);

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

      {stripFacts !== undefined ? (
        <TodayVerdictStripSlot dateISO={dateISO} dayFacts={stripFacts} />
      ) : (
        <div
          className={styles.nearestSkeleton}
          data-testid="today-slot-verdict-strip"
          data-wave2-slot="verdict"
          data-loading="true"
          aria-busy="true"
        />
      )}

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
        {loaded && !failure && !nearest ? (
          <p className={styles.nearestEmptyCopy} data-empty="true" data-testid="today-glance-nearest-empty">
            {copy.journey.glanceNearestEmpty}
          </p>
        ) : null}
      </div>

      {teasers.length > 0 ? (
        <ul className={styles.teasers} aria-label={copy.journey.glanceTeasersLabel} data-testid="today-glance-teasers">
          {teasers.map((t) => (
            <li key={t.id}>
              <button type="button" className={styles.teaser} data-testid={`today-glance-teaser-${t.id}`} onClick={t.onSelect}>
                <span className={styles.teaserMark} aria-hidden>·</span>
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
