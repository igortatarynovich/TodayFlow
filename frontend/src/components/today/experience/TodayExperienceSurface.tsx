"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { RitualNumberPickExperience } from "@/components/today/ritual/RitualNumberPickExperience";
import { RitualTarotPickExperience } from "@/components/today/ritual/RitualTarotPickExperience";
import { TodayDailyFocusBlock } from "@/components/today/experience/TodayDailyFocusBlock";
import { TodayDayContinuityClosed } from "@/components/today/experience/TodayDayContinuityClosed";
import { TodayDayContinuityEveningClose } from "@/components/today/experience/TodayDayContinuityEveningClose";
import { TodayS0Greeting } from "@/components/today/experience/TodayS0Greeting";
import { LoadingSpinner } from "@/components/orbit";
import { resolveDailyTarotDeckIndex } from "@/lib/tarotCardAssets";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { TodayRitualNarrativePayload } from "@/lib/todayNarrativeApi";
import { usesDayStorySingleVoice } from "@/lib/todayContractMapper";
import {
  applyTodayRitualSpineReducer,
  executeRitualSpineAnalytics,
  type TodayRitualSpineSnapshot,
} from "@/lib/todayRitualSpineMachine";
import { loadRitualPersisted, saveRitualPersisted, type RitualPersistedState } from "@/lib/todayRitualPersisted";
import { todayExperiencePhase } from "@/lib/todayExperiencePhase";
import { isExperienceSpineComplete } from "@/lib/todayExperienceSpine";
import { buildDailyFocusModel } from "@/lib/todayDailyFocus";
import {
  buildContinuityOpeningLine,
  isDayContinuityClosed,
  loadDayContinuity,
  loadPreviousDayContinuity,
  saveDayContinuity,
  type DayContinuityRecord,
  type DayFocusOutcome,
} from "@/lib/todayDayContinuity";
import { pickDaySkyFact, timeOfDayGreetingRu } from "@/lib/todayDaySkyFact";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import type { FusionResponse, MorningRitualData, TodayCycleData } from "@/components/today/todayPageUtils";
import { buildDayEventsForNarrative } from "@/components/today/todayPageUtils";
import { canShowTarotCardName } from "@/lib/todayRevealGate";
import { getTodayTarotCardRu } from "@/components/today/todayTarotCardsRu";
import { anchorTarotTagsFromLead, RITUAL_COPY } from "@/components/today/todayRitualCopy";

function buildRitualSpineSnapshotWeb(input: {
  dayOpened: boolean;
  tarotContinueAck: boolean;
  numberRevealed: boolean;
  tarotMainId: number | null;
  guideNarrativeLoading: boolean;
}): TodayRitualSpineSnapshot {
  const tarotMainResolved =
    input.tarotMainId != null && getTodayTarotCardRu(input.tarotMainId) != null;
  return {
    dayOpened: input.dayOpened,
    tarotContinueAck: input.tarotContinueAck,
    numberRevealed: input.numberRevealed,
    tarotMainId: input.tarotMainId,
    tarotMainResolved,
    selectedMoodId: null,
    checkInSubmitted: false,
    guideNarrativeLoading: input.guideNarrativeLoading,
  };
}

type Props = {
  dateISO: string;
  displayDate: string;
  firstName: string | null;
  todayData: TodayCycleData;
  morningRitualData: MorningRitualData | null;
  contract: TodayContractV1;
  fusion: FusionResponse | null;
  cardName: string;
  numerologyValue: string;
  numerologyMeaning: string;
  guideNarrativeLoading: boolean;
  guideNarrativePayload: Record<string, unknown> | null;
  guideGenerationId?: number | null;
  onRitualSpineComplete?: (ctx: TodayRitualNarrativePayload) => void;
  onVisible?: () => void;
};

export function TodayExperienceSurface(props: Props) {
  const { trackMeaningEvent } = useMeaningRuntime();
  const singleVoice = usesDayStorySingleVoice(props.contract);
  const guideNarrativeLoading = singleVoice ? false : props.guideNarrativeLoading;
  const guideNarrativePayload = singleVoice ? null : props.guideNarrativePayload;
  const ritualNarrativePostKeyRef = useRef<string | null>(null);
  const synthesisViewedRef = useRef(false);
  const skyFactViewedRef = useRef(false);

  const [hydrated, setHydrated] = useState(false);
  const [dayOpened, setDayOpened] = useState(false);
  const [tarotMainId, setTarotMainId] = useState<number | null>(null);
  const [tarotContinueAck, setTarotContinueAck] = useState(false);
  const [numberRevealed, setNumberRevealed] = useState(false);
  const [reduceMotion, setReduceMotion] = useState(false);
  const [synthesisVisible, setSynthesisVisible] = useState(false);
  const [continuityRecord, setContinuityRecord] = useState<DayContinuityRecord | null>(null);
  const [continuityEvening, setContinuityEvening] = useState(false);
  const [continuitySaving, setContinuitySaving] = useState(false);

  const skyFact = useMemo(() => pickDaySkyFact(props.morningRitualData), [props.morningRitualData]);
  const greeting = useMemo(() => (hydrated ? timeOfDayGreetingRu() : "Доброе утро"), [hydrated]);

  const spineSnap = useMemo(
    () =>
      buildRitualSpineSnapshotWeb({
        dayOpened,
        tarotContinueAck,
        numberRevealed,
        tarotMainId,
        guideNarrativeLoading: guideNarrativeLoading,
      }),
    [dayOpened, tarotContinueAck, numberRevealed, tarotMainId, guideNarrativeLoading],
  );

  const phase = useMemo(() => todayExperiencePhase(spineSnap), [spineSnap]);

  const spineComplete = isExperienceSpineComplete({ tarotMainId, tarotContinueAck, numberRevealed });
  const synthesisReady = spineComplete && !guideNarrativeLoading;

  const dailyFocus = useMemo(
    () => buildDailyFocusModel(props.contract, guideNarrativePayload),
    [props.contract, guideNarrativePayload],
  );

  const dayClosed = isDayContinuityClosed(continuityRecord);
  const continuityOpeningLine = useMemo(() => {
    if (!hydrated) return null;
    const prev = loadPreviousDayContinuity(props.dateISO);
    if (!prev || !isDayContinuityClosed(prev)) return null;
    return buildContinuityOpeningLine(prev);
  }, [hydrated, props.dateISO]);

  const mainFocusText = dailyFocus.title.trim() || dailyFocus.lines[0]?.trim() || "";

  useEffect(() => {
    props.onVisible?.();
  }, [props.onVisible]);

  useEffect(() => {
    ritualNarrativePostKeyRef.current = null;
    synthesisViewedRef.current = false;
    skyFactViewedRef.current = false;
    setContinuityEvening(false);
  }, [props.dateISO]);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const apply = () => setReduceMotion(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, []);

  useEffect(() => {
    const p = loadRitualPersisted(props.dateISO);
    if (p) {
      setDayOpened(p.opened);
      setNumberRevealed(p.numberRevealed);
      setTarotMainId(p.tarotMainId);
      setTarotContinueAck(p.tarotContinueAck);
    } else {
      setDayOpened(false);
      setNumberRevealed(false);
      setTarotMainId(null);
      setTarotContinueAck(false);
    }
    setHydrated(true);
    const continuity = loadDayContinuity(props.dateISO);
    setContinuityRecord(continuity);
    setContinuityEvening(false);
  }, [props.dateISO]);

  useEffect(() => {
    if (!hydrated) return;
    const snapshot: RitualPersistedState = {
      opened: dayOpened,
      numberRevealed,
      mood: null,
      headTopic: null,
      essentials: {},
      honestStep: null,
      numberRhythm: null,
      tarotMainId,
      tarotClarifierId: null,
      tarotApplied: false,
      tarotContinueAck,
      checkInSubmitted: false,
    };
    saveRitualPersisted(props.dateISO, snapshot);
  }, [hydrated, props.dateISO, dayOpened, numberRevealed, tarotMainId, tarotContinueAck]);

  useEffect(() => {
    if (phase !== "entry" || skyFactViewedRef.current) return;
    skyFactViewedRef.current = true;
    trackMeaningEvent({
      event_type: "day_sky_fact_viewed",
      event_source: "today",
      local_date: props.dateISO,
      payload: { sky_fact_id: skyFact.factKey, source: "today_experience" },
    });
  }, [phase, props.dateISO, skyFact.factKey, trackMeaningEvent]);

  useEffect(() => {
    if (singleVoice || !props.onRitualSpineComplete || !spineComplete) return;
    if (tarotMainId == null) return;
    const drawn = getTodayTarotCardRu(tarotMainId);
    if (!drawn) return;
    const key = `${props.dateISO}|${tarotMainId}|${props.numerologyValue}`;
    if (ritualNarrativePostKeyRef.current === key) return;
    ritualNarrativePostKeyRef.current = key;
    props.onRitualSpineComplete({
      tarot_main_id: tarotMainId,
      tarot_name_ru: drawn.nameRu,
      numerology_value: props.numerologyValue,
      day_events: buildDayEventsForNarrative(props.todayData),
    });
  }, [
    props.onRitualSpineComplete,
    props.dateISO,
    props.todayData,
    props.numerologyValue,
    spineComplete,
    tarotMainId,
    singleVoice,
  ]);

  useEffect(() => {
    if (phase !== "day_synthesis") {
      setSynthesisVisible(false);
      return;
    }
    const t = window.setTimeout(() => setSynthesisVisible(true), reduceMotion ? 0 : 120);
    return () => window.clearTimeout(t);
  }, [phase, reduceMotion]);

  useEffect(() => {
    if (!synthesisReady || !synthesisVisible || synthesisViewedRef.current) return;
    synthesisViewedRef.current = true;
    trackMeaningEvent({
      event_type: "first_synthesis_viewed",
      event_source: "today",
      local_date: props.dateISO,
      payload: {
        daily_focus_id: dailyFocus.dailyFocusId,
        ...(props.guideGenerationId ? { generation_id: props.guideGenerationId } : {}),
        source: "today_experience",
      },
    });
  }, [
    synthesisReady,
    synthesisVisible,
    dailyFocus.dailyFocusId,
    props.dateISO,
    props.guideGenerationId,
    trackMeaningEvent,
  ]);

  useEffect(() => {
    if (!synthesisReady || !mainFocusText || dayClosed) return;
    const existing = loadDayContinuity(props.dateISO);
    if (existing?.mainFocus === mainFocusText && existing.mainFocus) return;
    const draft: DayContinuityRecord = {
      dateISO: props.dateISO,
      mainFocus: mainFocusText,
      outcome: existing?.outcome,
      outcomeNote: existing?.outcomeNote,
      closedAt: existing?.closedAt,
    };
    saveDayContinuity(draft);
    setContinuityRecord(draft);
  }, [synthesisReady, mainFocusText, props.dateISO, dayClosed]);

  const onOpenEveningClose = useCallback(() => {
    const focus = mainFocusText || continuityRecord?.mainFocus || "Главный фокус дня";
    const draft: DayContinuityRecord = {
      dateISO: props.dateISO,
      mainFocus: focus,
      outcome: continuityRecord?.outcome,
      outcomeNote: continuityRecord?.outcomeNote,
      closedAt: continuityRecord?.closedAt,
    };
    saveDayContinuity(draft);
    setContinuityRecord(draft);
    setContinuityEvening(true);
  }, [mainFocusText, continuityRecord, props.dateISO]);

  const onSubmitEveningClose = useCallback(
    (outcome: DayFocusOutcome, _highlightId: string | null, note: string) => {
      const focus = continuityRecord?.mainFocus || mainFocusText;
      if (!focus) return;
      setContinuitySaving(true);
      const closed: DayContinuityRecord = {
        dateISO: props.dateISO,
        mainFocus: focus,
        outcome,
        outcomeNote: note || undefined,
        closedAt: new Date().toISOString(),
      };
      saveDayContinuity(closed);
      setContinuityRecord(closed);
      setContinuityEvening(false);
      setContinuitySaving(false);
      trackMeaningEvent({
        event_type: "day_focus_outcome",
        event_source: "today",
        local_date: props.dateISO,
        payload: {
          outcome,
          main_focus: focus.slice(0, 500),
          note: note ? note.slice(0, 400) : null,
          source: "today_experience",
          day_continuity_v0: true,
        },
      });
    },
    [continuityRecord?.mainFocus, mainFocusText, props.dateISO, trackMeaningEvent],
  );

  const snapForReducer = useCallback(
    () =>
      buildRitualSpineSnapshotWeb({
        dayOpened,
        tarotContinueAck,
        numberRevealed,
        tarotMainId,
        guideNarrativeLoading: guideNarrativeLoading,
      }),
    [dayOpened, tarotContinueAck, numberRevealed, tarotMainId, guideNarrativeLoading],
  );

  const onStartDay = useCallback(() => {
    const out = applyTodayRitualSpineReducer({ type: "openedDay" }, snapForReducer());
    if (!out) return;
    setDayOpened(out.after.dayOpened);
    trackMeaningEvent({
      event_type: "day_opened",
      event_source: "today",
      local_date: props.dateISO,
      payload: { day_key: props.dateISO, source: "today_experience" },
    });
  }, [snapForReducer, props.dateISO, trackMeaningEvent]);

  const commitTarotMain = useCallback(
    (id: number) => {
      setTarotMainId(id);
      trackMeaningEvent({
        event_type: "tarot_selected",
        event_source: "today",
        local_date: props.dateISO,
        payload: { card_id: id, main_card_index: id, experience_pr1: true },
      });
    },
    [props.dateISO, trackMeaningEvent],
  );

  const onTarotRevealed = useCallback(
    (id: number) => {
      trackMeaningEvent({
        event_type: "tarot_revealed",
        event_source: "today",
        local_date: props.dateISO,
        payload: { card_id: id, revealed: true, experience_pr1: true },
      });
    },
    [props.dateISO, trackMeaningEvent],
  );

  const onContinueFromTarot = useCallback(() => {
    const out = applyTodayRitualSpineReducer({ type: "continuedPastTarot" }, snapForReducer());
    if (!out) return;
    setTarotContinueAck(out.after.tarotContinueAck);
  }, [snapForReducer]);

  const onNumberComplete = useCallback(() => {
    const out = applyTodayRitualSpineReducer({ type: "revealedNumber" }, snapForReducer());
    if (!out) return;
    setNumberRevealed(out.after.numberRevealed);
    executeRitualSpineAnalytics(out.effects.analyticsHint, {
      numerologyValue: props.numerologyValue,
      guideGenerationId: props.guideGenerationId ?? null,
      trackMeaningEvent,
    });
  }, [snapForReducer, props.numerologyValue, props.guideGenerationId, trackMeaningEvent]);

  const anchorTarotId = useMemo(
    () =>
      resolveDailyTarotDeckIndex({
        morningTarotCardId: props.morningRitualData?.tarot_card?.id ?? null,
        morningTarotName: props.morningRitualData?.tarot_card?.name ?? null,
        cardName: props.cardName,
        dateISO: props.dateISO,
      }),
    [props.dateISO, props.cardName, props.morningRitualData?.tarot_card?.id, props.morningRitualData?.tarot_card?.name],
  );

  const anchorTarotRecord = useMemo(() => getTodayTarotCardRu(anchorTarotId), [anchorTarotId]);
  const anchorTarotTags = useMemo(
    () => anchorTarotTagsFromLead(anchorTarotRecord?.leadRu ?? ""),
    [anchorTarotRecord],
  );
  const drawnTarot = tarotMainId != null ? getTodayTarotCardRu(tarotMainId) : undefined;
  const tarotNameVisible = canShowTarotCardName(tarotMainId);

  if (!hydrated) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: "2rem 0" }}>
        <LoadingSpinner size="md" />
      </div>
    );
  }

  return (
    <div
      id="today-experience-surface"
      data-testid="today-experience-surface"
      data-phase={dayClosed ? "day_closed" : continuityEvening ? "evening_close" : phase}
      className="today-experience-root"
      style={{
        minHeight: "min(100dvh - 5.5rem, 780px)",
        display: "flex",
        flexDirection: "column",
        gap: "0.75rem",
        maxWidth: "100%",
        minWidth: 0,
        overflow: "hidden",
      }}
    >
      <style jsx global>{`
        @keyframes todayExperienceFadeIn {
          from {
            opacity: 0;
            transform: translateY(8px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .today-experience-stage-enter {
          animation: todayExperienceFadeIn 0.45s ease-out forwards;
        }
      `}</style>

      <div
        className="today-experience-stage"
        style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.65rem", minHeight: 0 }}
      >
        {dayClosed && continuityRecord ? (
          <TodayDayContinuityClosed record={continuityRecord} />
        ) : continuityEvening ? (
          <TodayDayContinuityEveningClose
            userPromise={null}
            themeShort={continuityRecord?.mainFocus || mainFocusText || "Главный фокус дня"}
            saving={continuitySaving}
            onSubmit={onSubmitEveningClose}
            onBack={() => setContinuityEvening(false)}
          />
        ) : null}

        {!dayClosed && !continuityEvening && phase === "entry" ? (
          <TodayS0Greeting
            greeting={greeting}
            displayDate={props.displayDate}
            firstName={props.firstName}
            skyFact={skyFact}
            continuityLine={continuityOpeningLine}
            onStartDay={onStartDay}
          />
        ) : null}

        {!dayClosed && !continuityEvening && phase === "tarot_reveal" ? (
          <section
            className="today-experience-stage-enter"
            data-testid="today-experience-tarot"
            style={{ minWidth: 0, flex: 1 }}
          >
            <p className="todayflow-eyebrow" style={{ margin: "0 0 0.35rem" }}>
              {tarotNameVisible ? RITUAL_COPY.cardEyebrow : RITUAL_COPY.experiencePickCardEyebrow}
            </p>
            <RitualTarotPickExperience
              anchorCardId={anchorTarotId}
              resumeCommittedId={tarotMainId}
              cardTitleRu={tarotNameVisible && drawnTarot ? drawnTarot.nameRu : ""}
              tagLabels={tarotNameVisible ? anchorTarotTags : []}
              reduceMotion={reduceMotion}
              startAtGrid
              allowSkipAnimation={false}
              gridSize={5}
              gridLead={RITUAL_COPY.experiencePickCardEyebrow}
              gridSub={RITUAL_COPY.experienceTarotGridSub}
              onCommitMain={commitTarotMain}
              onRevealed={onTarotRevealed}
              onContinue={onContinueFromTarot}
            />
            {tarotNameVisible && !tarotContinueAck && drawnTarot?.leadRu ? (
              <p className="orbit-body-sm" style={{ margin: "0.65rem 0 0", lineHeight: 1.55, color: "#3d3228" }}>
                {drawnTarot.leadRu}
              </p>
            ) : null}
          </section>
        ) : null}

        {!dayClosed && !continuityEvening && phase === "number_reveal" ? (
          <section
            className="today-experience-stage-enter"
            data-testid="today-experience-number"
            style={{ minWidth: 0, flex: 1 }}
          >
            <p className="todayflow-eyebrow" style={{ margin: "0 0 0.35rem" }}>
              {numberRevealed ? RITUAL_COPY.numberDayLead : RITUAL_COPY.experiencePickNumberEyebrow}
            </p>
            <RitualNumberPickExperience
              systemDisplay={props.numerologyValue}
              numberMeaning={props.numerologyMeaning}
              tileMode="symbol"
              reduceMotion={reduceMotion}
              onComplete={onNumberComplete}
            />
          </section>
        ) : null}

        {!dayClosed && !continuityEvening && phase === "day_synthesis" ? (
          <div
            data-testid="today-experience-day-synthesis"
            className={synthesisVisible ? "today-experience-stage-enter" : undefined}
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              gap: "0.75rem",
              opacity: synthesisVisible ? 1 : 0,
            }}
          >
            <TodayDailyFocusBlock model={dailyFocus} loading={guideNarrativeLoading} />
            {synthesisReady ? (
              <button
                type="button"
                className="orbit-button orbit-button-secondary"
                data-testid="today-day-continuity-open-evening"
                style={{ width: "100%" }}
                onClick={onOpenEveningClose}
              >
                Закрыть день
              </button>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}
