"use client";

import { useEffect, useMemo, useState } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import {
  DsBody,
  DsCallout,
  DsCaption,
  DsCard,
  DsContentCard,
  DsDisplayTitle,
  DsEyebrow,
  DsHeadline,
  DsPill,
  DsTitle,
} from "@/design-system";
import layout from "@/design-system/compositions/dsCompositions.module.css";
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
 * Glance / Сводка — story frame (FOUNDATION_UI §16 story-frame grammar).
 * Form Kit compositions only (FOUNDATION_UI §15.8).
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

  const primaryTeaser =
    teasers.find((t) => t.id === "symbols") ?? teasers.find((t) => t.id === "plot") ?? teasers[0] ?? null;

  return (
    <div className={layout.glanceRoot} data-testid="today-zone-glance-act">
      <header className={layout.glanceChrome}>
        <div data-testid="today-glance-today">
          <DsDisplayTitle as="p" size="lg">
            Сегодня
          </DsDisplayTitle>
        </div>
        <div data-testid="today-glance-date">
          <DsCaption muted>{dateLabel}</DsCaption>
        </div>
      </header>

      <div className={layout.glanceStage}>
        {themeLoading ? (
          <DsBody muted>{copy.loadingDay}</DsBody>
        ) : (
          <div className={layout.centerStack} data-testid="today-glance-glass">
            <div data-testid="today-glance-theme-label">
              <DsEyebrow>{copy.journey.glanceThemeLabel}</DsEyebrow>
            </div>
            {texture ? (
              <div data-testid="today-glance-thesis">
                <DsHeadline as="h3">{texture}</DsHeadline>
              </div>
            ) : (
              <div data-testid="today-entity-daily-theme-glance">
                <DsHeadline as="h3">{copy.journey.glanceTitle}</DsHeadline>
              </div>
            )}
            {detailLine ? (
              <div data-testid="today-glance-theme-detail">
                <DsBody size="sm" muted>
                  {detailLine}
                </DsBody>
              </div>
            ) : null}
          </div>
        )}

        {energyText ? (
          <div className={layout.centerStack} data-testid="today-glance-energy">
            <DsEyebrow>{copy.pulseLabel}</DsEyebrow>
            <div data-testid="today-glance-energy-text">
              <DsTitle as="p">{energyText}</DsTitle>
            </div>
            {energyCauseText ? (
              <div data-testid="today-glance-energy-cause">
                <DsBody size="sm" muted>
                  {energyCauseText}
                </DsBody>
              </div>
            ) : null}
          </div>
        ) : null}
      </div>

      <div className={layout.glanceFooter}>
        <div className={layout.stackTight} data-testid="today-glance-daily-focus">
          <DsEyebrow>{copy.journey.glanceFocusLabel}</DsEyebrow>
          {hasFocus ? (
            <>
              {focusTitle ? (
                <div
                  data-testid="today-glance-focus-title"
                  data-daily-focus-id={dailyFocus?.dailyFocusId}
                >
                  <DsBody>{focusTitle}</DsBody>
                </div>
              ) : null}
              {(prioritize || avoid) && (
                <div className={layout.stack}>
                  {prioritize ? (
                    <div
                      data-testid="today-glance-focus-prioritize"
                      data-polarity="support"
                      aria-label="Ориентир"
                    >
                      <DsCallout tone="help">{prioritize}</DsCallout>
                    </div>
                  ) : null}
                  {avoid ? (
                    <div
                      data-testid="today-glance-focus-avoid"
                      data-polarity="caution"
                      aria-label="Осторожность"
                    >
                      <DsCallout tone="avoid">{avoid}</DsCallout>
                    </div>
                  ) : null}
                </div>
              )}
            </>
          ) : (
            <div data-testid="today-glance-focus-empty">
              <DsBody size="sm" muted>
                {TODAY_NO_SHARP_FOCUS_COPY}
              </DsBody>
            </div>
          )}
        </div>

        <div className={layout.stackTight} data-testid="today-glance-meta">
          <DsEyebrow>{copy.journey.glanceNearestLabel}</DsEyebrow>

          {loaded && loadFailure ? (
            <div
              role="status"
              data-testid="today-glance-meta-fallback"
              data-fallback="true"
              data-failure={loadFailure}
            >
              <DsBody size="sm" muted>
                {todaySlotFailureCopy(loadFailure)}
              </DsBody>
            </div>
          ) : null}

          <div
            data-testid="today-slot-glance-nearest"
            data-wave2-slot="glance-nearest"
            data-fallback={loadFailure ? "true" : "false"}
            data-failure={loadFailure || undefined}
          >
            {!loaded ? (
              <div data-loading="true" aria-busy="true">
                <span className={layout.skeletonPulse} />
              </div>
            ) : null}
            {loaded && !loadFailure && nearest ? (
              onNearestSelect ? (
                <div data-valence={nearest.valence} data-live={live ? "true" : "false"}>
                  <DsCard
                    tone="subtle"
                    size="compact"
                    as="button"
                    className={layout.glanceNearest}
                    testId={`today-glance-nearest-${nearest.driver_id}`}
                    onClick={() => onNearestSelect(nearest)}
                  >
                    <span className={layout.glanceNearestRow}>
                      <DsHeadline as="span">{formatGlanceClock(nearest.time_local)}</DsHeadline>
                      <span>{nearest.label_short}</span>
                      {live ? (
                        <span data-testid="today-glance-now">
                          <DsPill>{copy.journey.glanceNow}</DsPill>
                        </span>
                      ) : null}
                      <DsCaption muted className={layout.glanceNearestHint}>
                        {copy.journey.glanceNearestPracticeHint}
                      </DsCaption>
                    </span>
                  </DsCard>
                </div>
              ) : (
                <div
                  className={layout.glanceNearestRow}
                  data-valence={nearest.valence}
                  data-live={live ? "true" : "false"}
                  data-testid={`today-glance-nearest-${nearest.driver_id}`}
                >
                  <DsHeadline as="span">{formatGlanceClock(nearest.time_local)}</DsHeadline>
                  <span>{nearest.label_short}</span>
                  {live ? (
                    <span data-testid="today-glance-now">
                      <DsPill>{copy.journey.glanceNow}</DsPill>
                    </span>
                  ) : null}
                </div>
              )
            ) : null}
            {loaded && !loadFailure && !nearest ? (
              <div data-empty="true" data-testid="today-glance-nearest-empty">
                <DsBody size="sm" muted>
                  {copy.journey.glanceNearestEmpty}
                </DsBody>
              </div>
            ) : null}
          </div>
        </div>

        {primaryTeaser ? (
          <div data-testid="today-glance-teasers">
            <DsContentCard
              tone="glass"
              as="button"
              title={primaryTeaser.label}
              body={primaryTeaser.hook}
              testId={`today-glance-teaser-${primaryTeaser.id}`}
              onClick={primaryTeaser.onSelect}
              className={layout.actionCenter}
            />
          </div>
        ) : null}
      </div>
    </div>
  );
}
