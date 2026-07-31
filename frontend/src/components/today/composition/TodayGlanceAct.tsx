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
import {
  DOMAIN_LABEL_RU,
  DOMAIN_ORDER,
  isSilentCalmBank,
  orderDomainVerdicts,
  scrubDomainVerdictJargon,
  VERDICT_LABEL_RU,
  type DomainKey,
  type DomainVerdict,
  type VerdictKey,
} from "@/lib/todayDomainVerdicts";
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
  /** Texture: why_arose (dominates). Falls back to thesis/title. */
  dayTexture?: string | null;
  thesis?: string | null;
  teasers: TodayGlanceTeaser[];
  themeLoading?: boolean;
  onSphereSelect?: (domain: DomainKey) => void;
};

function verdictMark(verdict: VerdictKey): string {
  if (verdict === "open") return "◇";
  if (verdict === "charged") return "▲";
  if (verdict === "friction") return "×";
  return "·";
}

export function TodayGlanceAct({
  dateISO,
  title = null,
  dayTexture = null,
  thesis = null,
  teasers,
  themeLoading = false,
  onSphereSelect,
}: Props) {
  const [nearest, setNearest] = useState<GlanceTimelineItem | null>(null);
  const [loadFailure, setLoadFailure] = useState<TodaySlotLoadFailure | null>(null);
  const [sphereFailure, setSphereFailure] = useState<TodaySlotLoadFailure | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [nowTick, setNowTick] = useState(() => new Date());
  const [domainRows, setDomainRows] = useState<DomainVerdict[]>([]);

  useEffect(() => {
    let cancelled = false;
    setLoaded(false);
    setLoadFailure(null);
    setSphereFailure(null);
    setDomainRows([]);
    void fetchDayFacts(dateISO)
      .then((data) => {
        if (cancelled) return;
        if (data.is_fallback ?? data.degraded) {
          setLoadFailure("unavailable");
          setSphereFailure("unavailable");
          setNearest(null);
          setDomainRows([]);
        } else {
          setLoadFailure(null);
          setNearest(pickNearestGlanceItem(data.glance_timeline ?? [], new Date()));
          const ordered = scrubDomainVerdictJargon(orderDomainVerdicts(data.domain_verdicts ?? []));
          if (isSilentCalmBank(ordered)) {
            setSphereFailure("unavailable");
            setDomainRows([]);
          } else {
            setSphereFailure(null);
            setDomainRows(ordered);
          }
        }
        setLoaded(true);
      })
      .catch(() => {
        if (cancelled) return;
        setLoadFailure("no_connection");
        setSphereFailure("no_connection");
        setNearest(null);
        setDomainRows([]);
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

  const tokenRows = useMemo(() => {
    if (!loaded || sphereFailure) return [];
    const byDomain = new Map(domainRows.map((r) => [r.domain, r]));
    return DOMAIN_ORDER.map((domain) => byDomain.get(domain)).filter(Boolean) as DomainVerdict[];
  }, [loaded, sphereFailure, domainRows]);

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
          </>
        )}
      </div>

      <div className={styles.metaRow} data-testid="today-glance-meta">
        {loaded && (sphereFailure || loadFailure) ? (
          <p
            className={styles.metaFail}
            role="status"
            data-testid="today-glance-meta-fallback"
            data-fallback="true"
            data-failure={sphereFailure || loadFailure || undefined}
          >
            {todaySlotFailureCopy((sphereFailure || loadFailure)!)}
          </p>
        ) : null}
        <div
          className={styles.sphereTokens}
          data-testid="today-slot-verdict-strip"
          data-wave2-slot="verdict"
          data-variant="tokens"
          data-fallback={sphereFailure ? "true" : "false"}
          data-failure={sphereFailure || undefined}
          aria-label={copy.journey.verdictStripLabel}
        >
          {!loaded ? <div className={styles.nearestSkeleton} data-loading="true" aria-busy="true" /> : null}
          {loaded && !sphereFailure
            ? tokenRows.map((row) => {
                const domain = row.domain as DomainKey;
                const verdict = row.verdict as VerdictKey;
                const label = DOMAIN_LABEL_RU[domain] ?? row.domain;
                const verdictLabel = VERDICT_LABEL_RU[verdict] ?? row.verdict;
                const interactive = Boolean(onSphereSelect);
                if (interactive) {
                  return (
                    <button
                      key={row.domain}
                      type="button"
                      className={styles.sphereToken}
                      data-domain={row.domain}
                      data-verdict={row.verdict}
                      data-testid={`today-verdict-token-${row.domain}`}
                      aria-label={`${label}: ${verdictLabel}`}
                      onClick={() => onSphereSelect?.(domain)}
                    >
                      <span className={styles.sphereTokenMark} aria-hidden>
                        {verdictMark(verdict)}
                      </span>
                      <span className={styles.sphereTokenLabel}>{label}</span>
                    </button>
                  );
                }
                return (
                  <span
                    key={row.domain}
                    className={styles.sphereToken}
                    data-domain={row.domain}
                    data-verdict={row.verdict}
                    data-testid={`today-verdict-token-${row.domain}`}
                    aria-label={`${label}: ${verdictLabel}`}
                  >
                    <span className={styles.sphereTokenMark} aria-hidden>
                      {verdictMark(verdict)}
                    </span>
                    <span className={styles.sphereTokenLabel}>{label}</span>
                  </span>
                );
              })
            : null}
        </div>

        <div
          className={styles.nearestInline}
          data-testid="today-slot-glance-nearest"
          data-wave2-slot="glance-nearest"
          data-inline="true"
          data-fallback={loadFailure ? "true" : "false"}
          data-failure={loadFailure || undefined}
        >
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

      {teasers.length > 0 ? (
        <ul className={styles.teasers} aria-label={copy.journey.glanceTeasersLabel} data-testid="today-glance-teasers">
          {teasers.map((t) => (
            <li key={t.id}>
              <button type="button" className={styles.teaser} data-testid={`today-glance-teaser-${t.id}`} onClick={t.onSelect}>
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
