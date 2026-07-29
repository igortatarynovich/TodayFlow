"use client";

/**
 * Wave 2 slots — VerdictStrip Phase B + TapWidget Phase A; Glance stub.
 */
import { useEffect, useState } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import styles from "@/components/today/composition/TodayWave2Slots.module.css";
import type { TodayContractV1 } from "@/lib/todayContract";
import {
  DOMAIN_LABEL_RU,
  fetchDomainVerdicts,
  orderDomainVerdicts,
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

type VerdictStripProps = {
  dateISO: string;
};

export function TodayVerdictStripSlot({ dateISO }: VerdictStripProps) {
  const [rows, setRows] = useState<DomainVerdict[]>(() => orderDomainVerdicts([]));
  const [isFallback, setIsFallback] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void fetchDomainVerdicts(dateISO)
      .then((data) => {
        if (cancelled) return;
        const fallback = Boolean(data.is_fallback ?? data.degraded);
        setIsFallback(fallback);
        setRows(fallback ? orderDomainVerdicts([]) : orderDomainVerdicts(data.domain_verdicts ?? []));
      })
      .catch(() => {
        if (cancelled) return;
        setIsFallback(true);
        setRows(orderDomainVerdicts([]));
      });
    return () => {
      cancelled = true;
    };
  }, [dateISO]);

  if (isFallback) {
    return (
      <div
        className={styles.verdictStrip}
        data-testid="today-slot-verdict-strip"
        data-wave2-slot="verdict"
        data-fallback="true"
        role="status"
        aria-label={copy.journey.verdictStripLabel}
      >
        <p className={styles.verdictFallback} data-testid="today-verdict-fallback">
          {copy.journey.verdictFallback}
        </p>
      </div>
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
        return (
          <div
            key={row.domain}
            className={styles.verdictRow}
            role="listitem"
            data-domain={row.domain}
            data-verdict={row.verdict}
            data-testid={`today-verdict-${row.domain}`}
          >
            <div className={styles.verdictHead}>
              <span className={styles.verdictDomain}>{domainLabel}</span>
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
        );
      })}
    </div>
  );
}

export function TodayGlanceTimelineSlot() {
  return (
    <div
      className={styles.slot}
      data-testid="today-slot-glance-timeline"
      data-wave2-slot="glance"
      aria-hidden={true}
    />
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
      <div className={styles.tap} data-testid="today-slot-tap-widget" data-wave2-slot="tap" data-empty="true">
        <p className={styles.tapHint}>{copy.journey.tapEmptyHint}</p>
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
