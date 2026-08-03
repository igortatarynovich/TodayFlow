"use client";

/**
 * Wave 2 slots — VerdictStrip Phase B + GlanceTimeline Phase C + TapWidget Phase A.
 * Prefer parent day_facts payload (D.1); standalone fetchDayFacts as fallback.
 */
import { useEffect, useState } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import styles from "@/components/today/composition/TodayWave2Slots.module.css";
import { TODAY_DOMAIN_ICON_MAP } from "@/design-system/icons/DsIcons";
import type { TodayContractV1 } from "@/lib/todayContract";
import {
  DOMAIN_LABEL_RU,
  isSilentCalmBank,
  orderDomainVerdicts,
  scrubDomainVerdictJargon,
  VERDICT_LABEL_RU,
  type DomainKey,
  type DomainVerdict,
  type VerdictKey,
} from "@/lib/todayDomainVerdicts";
import {
  fetchAccuracySummary,
  formatAccuracyLine,
  postTapWidgetResponse,
  resolveTapPromptFromContract,
  type AccuracySummaryV1,
  type TapResponseCode,
} from "@/lib/todayTapWidget";
import {
  formatGlanceClock,
  isGlanceLiveNow,
  type GlanceTimelineItem,
} from "@/lib/todayGlanceTimeline";
import { fetchDayFacts, type DayFactsResponse } from "@/lib/todayDayFacts";
import {
  todaySlotFailureCopy,
  type TodaySlotLoadFailure,
} from "@/lib/todaySlotAvailability";

export type DayFactsSlotSlice = {
  domain_verdicts?: DomainVerdict[];
  glance_timeline?: GlanceTimelineItem[];
  day_facts_id?: string | null;
  is_fallback?: boolean;
  degraded?: boolean;
  loadFailure?: TodaySlotLoadFailure | null;
};

type VerdictStripProps = {
  dateISO: string;
  dayFacts?: DayFactsSlotSlice | null;
};

function failureFromDayFacts(data: DayFactsSlotSlice): TodaySlotLoadFailure | null {
  if (data.loadFailure) return data.loadFailure;
  if (data.is_fallback ?? data.degraded) return "unavailable";
  return null;
}

export function TodayVerdictStripSlot({ dateISO, dayFacts = null }: VerdictStripProps) {
  const fromParent = dayFacts != null;
  const [rows, setRows] = useState<DomainVerdict[] | null>(() =>
    fromParent ? scrubDomainVerdictJargon(orderDomainVerdicts(dayFacts?.domain_verdicts ?? [])) : null,
  );
  const [failure, setFailure] = useState<TodaySlotLoadFailure | null>(() =>
    fromParent ? failureFromDayFacts(dayFacts ?? {}) : null,
  );
  const [loaded, setLoaded] = useState(fromParent);

  useEffect(() => {
    if (dayFacts != null) {
      const parentFail = failureFromDayFacts(dayFacts);
      if (parentFail) {
        setFailure(parentFail);
        setRows([]);
      } else {
        const ordered = scrubDomainVerdictJargon(orderDomainVerdicts(dayFacts.domain_verdicts ?? []));
        if (isSilentCalmBank(ordered)) {
          setFailure("unavailable");
          setRows([]);
        } else {
          setFailure(null);
          setRows(ordered);
        }
      }
      setLoaded(true);
      return;
    }

    let cancelled = false;
    setLoaded(false);
    setFailure(null);
    void fetchDayFacts(dateISO)
      .then((data: DayFactsResponse) => {
        if (cancelled) return;
        if (data.is_fallback ?? data.degraded) {
          setFailure("unavailable");
          setRows([]);
        } else {
          const ordered = scrubDomainVerdictJargon(orderDomainVerdicts(data.domain_verdicts ?? []));
          if (isSilentCalmBank(ordered)) {
            setFailure("unavailable");
            setRows([]);
          } else {
            setFailure(null);
            setRows(ordered);
          }
        }
        setLoaded(true);
      })
      .catch(() => {
        if (cancelled) return;
        setFailure("no_connection");
        setRows([]);
        setLoaded(true);
      });
    return () => {
      cancelled = true;
    };
  }, [dateISO, dayFacts]);

  if (!loaded) {
    return (
      <div
        className={styles.verdictStrip}
        data-testid="today-slot-verdict-strip"
        data-wave2-slot="verdict"
        data-loading="true"
        aria-busy="true"
        aria-label={copy.journey.verdictStripLabel}
      />
    );
  }

  if (failure) {
    return (
      <div
        className={styles.verdictStrip}
        data-testid="today-slot-verdict-strip"
        data-wave2-slot="verdict"
        data-fallback="true"
        data-failure={failure}
        role="status"
        aria-label={copy.journey.verdictStripLabel}
      >
        <p className={styles.verdictFallback} data-testid="today-verdict-fallback">
          {todaySlotFailureCopy(failure)}
        </p>
      </div>
    );
  }

  if (!rows || rows.length === 0) {
    return (
      <div
        className={styles.verdictStrip}
        data-testid="today-slot-verdict-strip"
        data-wave2-slot="verdict"
        data-empty="true"
        aria-hidden={true}
      />
    );
  }

  return (
    <div
      className={styles.verdictStrip}
      data-testid="today-slot-verdict-strip"
      data-wave2-slot="verdict"
      data-fallback="false"
      role="list"
      aria-label={copy.journey.verdictStripLabel}
    >
      {rows.map((row) => {
        const domain = row.domain as DomainKey;
        const verdict = row.verdict as VerdictKey;
        const domainLabel = DOMAIN_LABEL_RU[domain] ?? row.domain;
        const verdictLabel = VERDICT_LABEL_RU[verdict] ?? row.verdict;
        // Unknown/legacy domain string (not in the closed DomainKey map) → no icon, label still renders.
        const DomainIcon = (TODAY_DOMAIN_ICON_MAP as Partial<Record<string, typeof TODAY_DOMAIN_ICON_MAP.work>>)[
          domain
        ];
        return (
          <div
            key={row.domain}
            className={styles.verdictRow}
            role="listitem"
            data-domain={row.domain}
            data-verdict={row.verdict}
            data-testid={`today-verdict-${row.domain}`}
          >
            <span className={styles.verdictSign} data-verdict={row.verdict} aria-hidden>
              {verdict === "open" ? "◇" : verdict === "charged" ? "▲" : verdict === "friction" ? "×" : "·"}
            </span>
            <div className={styles.verdictCopy}>
              <div className={styles.verdictHead}>
                <span className={styles.verdictDomainGroup}>
                  {DomainIcon ? <DomainIcon className={styles.verdictDomainIcon} /> : null}
                  <span className={styles.verdictDomain}>{domainLabel}</span>
                </span>
                <span className={styles.verdictKey} data-verdict={row.verdict}>
                  {verdictLabel}
                </span>
              </div>
              {row.why_short ? (
                <p className={styles.verdictWhy} data-testid={`today-verdict-why-${row.domain}`}>
                  {row.why_short}
                </p>
              ) : null}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function TodayGlanceTimelineSlot({
  dateISO,
  dayFacts = null,
}: {
  dateISO: string;
  dayFacts?: DayFactsSlotSlice | null;
}) {
  const fromParent = dayFacts != null;
  const [rows, setRows] = useState<GlanceTimelineItem[]>(() =>
    fromParent ? (dayFacts?.glance_timeline ?? []) : [],
  );
  const [failure, setFailure] = useState<TodaySlotLoadFailure | null>(() =>
    fromParent ? failureFromDayFacts(dayFacts ?? {}) : null,
  );
  const [loaded, setLoaded] = useState(fromParent);
  const [nowTick, setNowTick] = useState(() => new Date());

  useEffect(() => {
    if (dayFacts != null) {
      const parentFail = failureFromDayFacts(dayFacts);
      if (parentFail) {
        setFailure(parentFail);
        setRows([]);
      } else {
        setFailure(null);
        setRows(dayFacts.glance_timeline ?? []);
      }
      setLoaded(true);
      return;
    }

    let cancelled = false;
    setLoaded(false);
    setFailure(null);
    void fetchDayFacts(dateISO)
      .then((data: DayFactsResponse) => {
        if (cancelled) return;
        if (data.is_fallback ?? data.degraded) {
          setFailure("unavailable");
          setRows([]);
        } else {
          setFailure(null);
          setRows(data.glance_timeline ?? []);
        }
        setLoaded(true);
      })
      .catch(() => {
        if (cancelled) return;
        setFailure("no_connection");
        setRows([]);
        setLoaded(true);
      });
    return () => {
      cancelled = true;
    };
  }, [dateISO, dayFacts]);

  useEffect(() => {
    if (rows.length === 0) return;
    const id = window.setInterval(() => setNowTick(new Date()), 60_000);
    return () => window.clearInterval(id);
  }, [rows.length]);

  if (!loaded) {
    return (
      <div
        className={styles.glance}
        data-testid="today-slot-glance-timeline"
        data-wave2-slot="glance"
        data-loading="true"
        aria-busy="true"
      />
    );
  }

  if (failure) {
    return (
      <div
        className={styles.glance}
        data-testid="today-slot-glance-timeline"
        data-wave2-slot="glance"
        data-fallback="true"
        data-failure={failure}
        role="status"
      >
        <p className={styles.glanceFallback} data-testid="today-glance-fallback">
          {todaySlotFailureCopy(failure)}
        </p>
      </div>
    );
  }

  if (rows.length === 0) {
    return (
      <div
        className={styles.slot}
        data-testid="today-slot-glance-timeline"
        data-wave2-slot="glance"
        data-empty="true"
        aria-hidden={true}
      />
    );
  }

  return (
    <div
      className={styles.glance}
      data-testid="today-slot-glance-timeline"
      data-wave2-slot="glance"
      data-fallback="false"
      role="list"
      aria-label={copy.journey.glanceStripLabel}
    >
      {rows.map((row) => {
        const live = isGlanceLiveNow(row.time_local, nowTick);
        return (
          <div
            key={`${row.driver_id}-${row.time_local}`}
            className={styles.glanceRow}
            role="listitem"
            data-valence={row.valence}
            data-live={live ? "true" : "false"}
            data-testid={`today-glance-${row.driver_id}`}
          >
            <span className={styles.glanceTime}>{formatGlanceClock(row.time_local)}</span>
            <span className={styles.glanceLabel}>{row.label_short}</span>
            {live ? (
              <span className={styles.glanceNow} data-testid="today-glance-now">
                {copy.journey.glanceNow}
              </span>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}

type TapWidgetProps = {
  contract: TodayContractV1;
  dateISO: string;
  dayFactsId?: string | null;
  initialResponse?: TapResponseCode | null;
  onRecorded?: (response: TapResponseCode) => void;
};

export function TodayTapWidget({
  contract,
  dateISO,
  dayFactsId = null,
  initialResponse = null,
  onRecorded,
}: TapWidgetProps) {
  const prompt = resolveTapPromptFromContract(contract);
  const [response, setResponse] = useState<TapResponseCode | null>(initialResponse);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<AccuracySummaryV1 | null>(null);
  const [completedPulse, setCompletedPulse] = useState(false);

  useEffect(() => {
    setResponse(initialResponse);
  }, [initialResponse]);

  useEffect(() => {
    let cancelled = false;
    void fetchAccuracySummary("14d")
      .then((data) => {
        if (!cancelled) setSummary(data);
      })
      .catch(() => {
        if (!cancelled) setSummary(null);
      });
    return () => {
      cancelled = true;
    };
  }, [response, dateISO]);

  if (!prompt) {
    return (
      <div
        className={styles.tap}
        data-testid="today-slot-tap-widget"
        data-wave2-slot="tap"
        data-empty="true"
        data-no-trap="true"
      >
        <p className={styles.tapHint} role="status">
          {copy.journey.tapEmptyHint}
        </p>
      </div>
    );
  }

  const answered = response != null && response !== "skipped";
  const attention = !answered;

  const submit = async (code: TapResponseCode) => {
    if (pending) return;
    setPending(true);
    setError(null);
    try {
      await postTapWidgetResponse({
        localDate: dateISO,
        sceneId: prompt.sceneId,
        promptedText: prompt.promptedText,
        response: code,
        domain: prompt.domain,
        dayFactsId,
      });
      setResponse(code);
      setCompletedPulse(true);
      window.setTimeout(() => setCompletedPulse(false), 900);
      onRecorded?.(code);
    } catch {
      setError(copy.journey.tapError);
    } finally {
      setPending(false);
    }
  };

  const accuracyLine = formatAccuracyLine(summary);

  return (
    <div
      className={[
        styles.tap,
        attention ? styles.tapAttention : "",
        completedPulse ? styles.tapCompleted : "",
      ]
        .filter(Boolean)
        .join(" ")}
      data-testid="today-slot-tap-widget"
      data-wave2-slot="tap"
      data-tap-attention={attention ? "true" : "false"}
      data-tap-answered={answered ? "true" : "false"}
    >
      <p className={styles.tapLabel}>{copy.journey.tapQuestion}</p>
      <p className={styles.tapPrompt} data-testid="today-tap-prompt">
        {prompt.promptedText}
      </p>
      <div className={styles.tapRow} role="group" aria-label={copy.journey.tapQuestion}>
        <button
          type="button"
          className={styles.tapBtn}
          data-testid="today-tap-avoided"
          data-selected={response === "avoided_trap" ? "true" : undefined}
          disabled={pending}
          onClick={() => void submit("avoided_trap")}
        >
          {copy.journey.tapAvoided}
        </button>
        <button
          type="button"
          className={styles.tapBtn}
          data-testid="today-tap-fell"
          data-selected={response === "fell_into_trap" ? "true" : undefined}
          disabled={pending}
          onClick={() => void submit("fell_into_trap")}
        >
          {copy.journey.tapFell}
        </button>
        <button
          type="button"
          className={styles.tapBtnSecondary}
          data-testid="today-tap-na"
          data-selected={response === "not_applicable" ? "true" : undefined}
          disabled={pending}
          onClick={() => void submit("not_applicable")}
        >
          {copy.journey.tapNotApplicable}
        </button>
      </div>
      {answered ? (
        <p className={styles.tapDone} data-testid="today-tap-recorded">
          {copy.journey.tapRecorded}
        </p>
      ) : null}
      {error ? (
        <p className={styles.tapError} data-testid="today-tap-error">
          {error}
        </p>
      ) : null}
      {accuracyLine ? (
        <p className={styles.tapAccuracy} data-testid="today-tap-accuracy">
          {accuracyLine}
        </p>
      ) : null}
    </div>
  );
}

/** @deprecated Wave 1 stub — use TodayTapWidget */
export function TodayTapWidgetStub(props: { onTap?: () => void; answered?: boolean | null }) {
  return (
    <div className={styles.tap} data-testid="today-slot-tap-widget" data-wave2-slot="tap">
      <p className={styles.tapLabel}>{copy.journey.tapStubLabel}</p>
      <div className={styles.tapRow}>
        <button type="button" className={styles.tapBtn} data-testid="today-tap-yes" onClick={() => props.onTap?.()}>
          Да
        </button>
        <button type="button" className={styles.tapBtn} data-testid="today-tap-no" onClick={() => props.onTap?.()}>
          Нет
        </button>
      </div>
      <p className={styles.tapHint}>{copy.journey.tapStubHint}</p>
    </div>
  );
}
