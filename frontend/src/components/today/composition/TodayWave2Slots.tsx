"use client";

/**
 * Wave 2 slots — Form Kit surfaces (FOUNDATION_UI §15.8 / §5.1 / §16.6).
 * Verdict → DsCallout tones · Glance → list rows · Tap → action cluster.
 */
import { useEffect, useState } from "react";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import {
  DsBody,
  DsButton,
  DsCallout,
  DsCaption,
  DsChip,
  DsChipCluster,
  DsContentCard,
  DsEyebrow,
  DsHeadline,
  DsListRow,
  DsPill,
} from "@/design-system";
import type { DsCalloutTone } from "@/design-system/primitives/DsCallout";
import { TODAY_DOMAIN_ICON_MAP } from "@/design-system/icons/DsIcons";
import layout from "@/design-system/compositions/dsCompositions.module.css";
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

function verdictTone(verdict: VerdictKey): DsCalloutTone {
  if (verdict === "open") return "help";
  if (verdict === "friction") return "avoid";
  if (verdict === "charged") return "insight";
  return "practice";
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
        className={layout.stack}
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
        className={layout.stack}
        data-testid="today-slot-verdict-strip"
        data-wave2-slot="verdict"
        data-fallback="true"
        data-failure={failure}
        role="status"
        aria-label={copy.journey.verdictStripLabel}
      >
        <div data-testid="today-verdict-fallback">
          <DsBody size="sm" muted>
            {todaySlotFailureCopy(failure)}
          </DsBody>
        </div>
      </div>
    );
  }

  if (!rows || rows.length === 0) {
    return (
      <div
        className={layout.stack}
        data-testid="today-slot-verdict-strip"
        data-wave2-slot="verdict"
        data-empty="true"
        aria-hidden={true}
      />
    );
  }

  return (
    <div
      className={layout.stack}
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
        const DomainIcon = (TODAY_DOMAIN_ICON_MAP as Partial<Record<string, typeof TODAY_DOMAIN_ICON_MAP.work>>)[
          domain
        ];
        const title = DomainIcon ? (
          <span className={layout.glanceNearestRow}>
            <DomainIcon className={layout.domainIcon} />
            {domainLabel}
          </span>
        ) : (
          domainLabel
        );
        return (
          <div
            key={row.domain}
            role="listitem"
            data-domain={row.domain}
            data-verdict={row.verdict}
            data-testid={`today-verdict-${row.domain}`}
          >
            <DsCallout tone={verdictTone(verdict)} title={title}>
              <DsCaption muted>{verdictLabel}</DsCaption>
              {row.why_short ? (
                <div data-testid={`today-verdict-why-${row.domain}`}>
                  <DsBody size="sm" muted>
                    {row.why_short}
                  </DsBody>
                </div>
              ) : null}
            </DsCallout>
          </div>
        );
      })}
    </div>
  );
}

export function TodayGlanceTimelineSlot({
  dateISO,
  dayFacts = null,
  variant = "default",
}: {
  dateISO: string;
  dayFacts?: DayFactsSlotSlice | null;
  /** Story-deck pane: fuller hour cards with valence. */
  variant?: "default" | "story";
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
        className={layout.stack}
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
        className={layout.stack}
        data-testid="today-slot-glance-timeline"
        data-wave2-slot="glance"
        data-fallback="true"
        data-failure={failure}
        role="status"
      >
        <div data-testid="today-glance-fallback">
          <DsBody size="sm" muted>
            {todaySlotFailureCopy(failure)}
          </DsBody>
        </div>
      </div>
    );
  }

  if (rows.length === 0) {
    return (
      <div
        className={layout.stack}
        data-testid="today-slot-glance-timeline"
        data-wave2-slot="glance"
        data-empty="true"
        role={variant === "story" ? "status" : undefined}
        aria-hidden={variant === "story" ? undefined : true}
      >
        {variant === "story" ? (
          <div data-testid="today-glance-empty">
            <DsBody size="sm" muted>
              {copy.journey.glanceNearestEmpty}
            </DsBody>
          </div>
        ) : null}
      </div>
    );
  }

  if (variant === "story") {
    return (
      <div
        className={layout.stack}
        data-testid="today-slot-glance-timeline"
        data-wave2-slot="glance"
        data-fallback="false"
        data-variant={variant}
        role="list"
        aria-label={copy.journey.glanceStripLabel}
      >
        {rows.map((row) => {
          const live = isGlanceLiveNow(row.time_local, nowTick);
          const tone =
            row.valence === "caution" ? "accent" : row.valence === "favorable" ? "solid" : "subtle";
          return (
            <div
              key={`${row.driver_id}-${row.time_local}`}
              role="listitem"
              data-valence={row.valence}
              data-live={live ? "true" : "false"}
              data-testid={`today-glance-${row.driver_id}`}
            >
              <DsContentCard
                tone={tone}
                eyebrow={formatGlanceClock(row.time_local)}
                title={row.label_short}
                chips={live ? <DsPill>{copy.journey.glanceNow}</DsPill> : undefined}
              />
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div
      className={layout.stack}
      data-testid="today-slot-glance-timeline"
      data-wave2-slot="glance"
      data-fallback="false"
      data-variant={variant}
      role="list"
      aria-label={copy.journey.glanceStripLabel}
    >
      {rows.map((row) => {
        const live = isGlanceLiveNow(row.time_local, nowTick);
        return (
          <div
            key={`${row.driver_id}-${row.time_local}`}
            role="listitem"
            data-valence={row.valence}
            data-live={live ? "true" : "false"}
            data-testid={`today-glance-${row.driver_id}`}
          >
            <DsListRow
              title={formatGlanceClock(row.time_local)}
              subtitle={
                live ? `${row.label_short} · ${copy.journey.glanceNow}` : row.label_short
              }
            />
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
        className={layout.actionCenter}
        data-testid="today-slot-tap-widget"
        data-wave2-slot="tap"
        data-empty="true"
        data-no-trap="true"
      >
        <p role="status">
          <DsBody size="sm" muted>
            {copy.journey.tapEmptyHint}
          </DsBody>
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
      className={layout.actionCenter}
      data-testid="today-slot-tap-widget"
      data-wave2-slot="tap"
      data-tap-attention={attention ? "true" : "false"}
      data-tap-answered={answered ? "true" : "false"}
    >
      <div data-testid="today-tap-prompt">
        <DsHeadline as="p">{prompt.promptedText}</DsHeadline>
      </div>
      <DsChipCluster>
        <DsButton
          variant="secondary"
          size="sm"
          data-testid="today-tap-avoided"
          data-selected={response === "avoided_trap" ? "true" : undefined}
          aria-pressed={response === "avoided_trap"}
          disabled={pending}
          onClick={() => void submit("avoided_trap")}
        >
          {copy.journey.tapAvoided}
        </DsButton>
        <DsButton
          variant="secondary"
          size="sm"
          data-testid="today-tap-fell"
          data-selected={response === "fell_into_trap" ? "true" : undefined}
          aria-pressed={response === "fell_into_trap"}
          disabled={pending}
          onClick={() => void submit("fell_into_trap")}
        >
          {copy.journey.tapFell}
        </DsButton>
        <DsButton
          variant="ghost"
          size="sm"
          data-testid="today-tap-na"
          data-selected={response === "not_applicable" ? "true" : undefined}
          aria-pressed={response === "not_applicable"}
          disabled={pending}
          onClick={() => void submit("not_applicable")}
        >
          {copy.journey.tapNotApplicable}
        </DsButton>
      </DsChipCluster>
      {answered ? (
        <div data-testid="today-tap-recorded">
          <DsCaption>{copy.journey.tapRecorded}</DsCaption>
        </div>
      ) : null}
      {error ? (
        <div data-testid="today-tap-error">
          <DsBody size="sm" muted>
            {error}
          </DsBody>
        </div>
      ) : null}
      {accuracyLine ? (
        <div data-testid="today-tap-accuracy">
          <DsCaption muted>{accuracyLine}</DsCaption>
        </div>
      ) : null}
    </div>
  );
}

/** @deprecated Wave 1 stub — use TodayTapWidget */
export function TodayTapWidgetStub(props: { onTap?: () => void; answered?: boolean | null }) {
  return (
    <div className={layout.actionCenter} data-testid="today-slot-tap-widget" data-wave2-slot="tap">
      <DsEyebrow>{copy.journey.tapStubLabel}</DsEyebrow>
      <DsChipCluster>
        <DsChip onClick={() => props.onTap?.()} testId="today-tap-yes">
          Да
        </DsChip>
        <DsChip variant="ghost" onClick={() => props.onTap?.()} testId="today-tap-no">
          Нет
        </DsChip>
      </DsChipCluster>
      <DsCaption muted>{copy.journey.tapStubHint}</DsCaption>
    </div>
  );
}
