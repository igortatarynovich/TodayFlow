"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { RitualNumberPickExperience } from "@/components/today/ritual/RitualNumberPickExperience";
import { RitualTarotPickExperience } from "@/components/today/ritual/RitualTarotPickExperience";
import type { PracticeResponse } from "@/components/today/todayPageUtils";
import { TodayDayContinuityClosed } from "@/components/today/experience/TodayDayContinuityClosed";
import { TodayDayContinuityEveningClose } from "@/components/today/experience/TodayDayContinuityEveningClose";
import { TodayEveningProductClose } from "@/components/today/composition/TodayEveningProductClose";
import { TodayPersonalizedProductSection } from "@/components/today/composition/TodayPersonalizedProductSection";
import { LoadingSpinner } from "@/components/orbit";
import { HeroMedium } from "@/components/foundation/HeroMedium";
import { profileMotionStyles } from "@/components/foundation/ProfileMotion";
import { SacredGeometryBackdrop } from "@/components/visualIdentity/SacredGeometryBackdrop";
import { buildTodayHeroPillars, buildTodayHeroSymbol, resolveTodaySunSignLabel } from "@/lib/todayHeroMedium";
import type { MorningRitualData, TodayCycleData } from "@/components/today/todayPageUtils";
import { anchorTarotTagsFromLead, RITUAL_COPY } from "@/components/today/todayRitualCopy";
import { getTodayTarotCardRu } from "@/components/today/todayTarotCardsRu";
import type { TodayContractV1 } from "@/lib/todayContract";
import type { CoreProfile } from "@/lib/types";
import { resolveDailyTarotDeckIndex } from "@/lib/tarotCardAssets";
import {
  buildContinuityOpeningLine,
  isDayContinuityClosed,
  loadDayContinuity,
  loadPreviousDayContinuity,
  saveDayContinuity,
  type DayContinuityRecord,
  type DayFocusOutcome,
} from "@/lib/todayDayContinuity";
import {
  applyEngagementToViewModel,
  applyGuideNarrativeToCompositionViewModel,
  applyRecommendedPracticeToStrengthen,
  buildTodayCompositionViewModel,
} from "@/lib/todayCompositionModel";
import { buildTodayDayStoryViewModel, applySupplementaryNarrativesToDayStory } from "@/lib/todayDayStoryModel";
import { usesDayStorySingleVoice } from "@/lib/todayContractMapper";
import { loadDayEngagement, mergeEngagementWithCompactUserModel, saveDayEngagement, createEmptyDayEngagement, engagementProfileScope } from "@/lib/todayDayEngagement";
import { fetchCompactUserModelCached, clearCompactUserModelCache } from "@/lib/compactUserModelCache";
import {
  loadRitualPersisted,
  saveRitualPersisted,
  type RitualPersistedState,
} from "@/lib/todayRitualPersisted";
import {
  resolveTodayCompositionZones,
  type TodayCompositionVariant,
} from "@/lib/todayCompositionZones";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { useAuth } from "@/lib/useAuth";
import { revealDayCard, revealDayNumber, type DaySymbolPublicView } from "@/lib/daySymbolReveal";
import { TodayDayDialogueMorning } from "@/components/today/composition/TodayDayDialogueMorning";
import { ConversationThread } from "@/components/conversation/ConversationThread";
import { ConversationTurn } from "@/components/conversation/ConversationTurn";
import { TodayInterpretationConfirm } from "@/components/today/composition/TodayInterpretationConfirm";
import { TodaySkyStoryCards } from "@/components/today/composition/TodaySkyStoryCards";
import { TodayDayColorGuideSection } from "@/components/today/composition/TodayDayColorGuideSection";
import { buildTodayPromiseSuggestions, isLowEnergyMood } from "@/lib/todayDayDialogue";
import {
  buildInterpretationConfirmPayload,
  type InterpretationResonance,
  type ProximityChoiceId,
} from "@/lib/todayInterpretationConfirm";
import { TODAY_COMPOSITION_COPY as copy } from "@/components/today/composition/todayCompositionCopy";
import { buildTarotDeepenHref } from "@/lib/buildTarotDeepenHref";
import {
  buildTarotDeepenEventPayload,
  tarotDeepenIdempotencyKey,
  TAROT_DEEPEN_EVENT_SOURCE,
} from "@/lib/tarotDeepenEvents";
import styles from "@/components/today/composition/TodayCompositionSurface.module.css";
import { DsRitualGate, DsRitualGateSection } from "@/design-system";
import { getJson, postJson } from "@/lib/api";
import { PersonalizationDegradedBadge } from "@/components/product-ui/PersonalizationDegradedBadge";
import { buildDayEventsForNarrative } from "@/components/today/todayPageUtils";
import type { TodayRitualNarrativePayload } from "@/lib/todayNarrativeApi";

type Props = {
  variant?: TodayCompositionVariant;
  dateISO: string;
  displayDate: string;
  todayData: TodayCycleData;
  morningRitualData: MorningRitualData | null;
  contract: TodayContractV1;
  cardName: string;
  cardMeaning: string | null;
  numerologyValue: string;
  numerologyMeaning: string | null;
  guideNarrativeLoading: boolean;
  guideNarrativePayload: Record<string, unknown> | null;
  guideNarrativeRequestFailed?: boolean;
  dayLayerNarrativePayload?: Record<string, unknown> | null;
  dayLayerNarrativeLoading?: boolean;
  spheresNarrativePayload?: Record<string, unknown> | null;
  eveningNarrativePayload?: Record<string, unknown> | null;
  onRitualSpineComplete?: (ctx: TodayRitualNarrativePayload) => void;
  colorLine?: string | null;
  stoneLine?: string | null;
  coreProfile?: CoreProfile | null;
  onVisible?: () => void;
  onDayClosed?: () => void;
  /** When true, chrome is provided by TodayWebDashboard; only ritual/personalized blocks render. */
  embeddedInWebDashboard?: boolean;
  /** Day story is being rebuilt after symbol reveal — do not treat old text as updated. */
  dayStoryUpdating?: boolean;
  onSymbolRevealResult?: (view: DaySymbolPublicView) => void;
};

function useReduceMotion(): boolean {
  const [reduce, setReduce] = useState(false);
  useEffect(() => {
    if (typeof window.matchMedia !== "function") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduce(mq.matches);
    const onChange = () => setReduce(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduce;
}

function stripRitualCtaFromPulse(pulse: string): string {
  return pulse.replace(/\s*Открой карту и число — и день станет личным\.?\s*$/u, ".").replace(/\.\.$/, ".");
}

function splitSalutation(salutation: string): { lead: string; name: string | null } {
  const commaIdx = salutation.indexOf(", ");
  if (commaIdx > 0) {
    return { lead: salutation.slice(0, commaIdx + 1), name: salutation.slice(commaIdx + 2) };
  }
  return { lead: salutation, name: null };
}

function userInitial(profile?: CoreProfile | null): string {
  const name = resolveUserName(profile);
  return name ? name.charAt(0).toUpperCase() : "T";
}

function resolveUserName(profile?: CoreProfile | null): string | null {
  return profile?.person?.display_name?.trim() || profile?.person?.first_name?.trim() || null;
}

export function TodayCompositionSurface(props: Props) {
  const { onVisible, onDayClosed, dateISO, embeddedInWebDashboard = false } = props;
  const variant = props.variant ?? "default";
  const isFirstToday = variant === "firstToday";
  const { trackMeaningEvent } = useMeaningRuntime();
  const { isAuthenticated } = useAuth();
  const reduceMotion = useReduceMotion();

  const [eveningMode, setEveningMode] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [continuityRecord, setContinuityRecord] = useState<DayContinuityRecord | null>(null);
  const [continuitySaving, setContinuitySaving] = useState(false);
  const [engagement, setEngagement] = useState(createEmptyDayEngagement);
  const [tarotPendingId, setTarotPendingId] = useState<number | null>(null);
  const [goalDraftOpen, setGoalDraftOpen] = useState(false);
  const [goalDraft, setGoalDraft] = useState("");
  const [recommendedPractice, setRecommendedPractice] = useState<PracticeResponse | null>(null);
  const [practiceCompleting, setPracticeCompleting] = useState(false);
  const [ritualPickOpen, setRitualPickOpen] = useState<"tarot" | "number" | null>(null);

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

  const ritualNarrativePostKeyRef = useRef<string | null>(null);
  const singleVoice = usesDayStorySingleVoice(props.contract);

  const baseModel = useMemo(
    () => {
      const vm = buildTodayCompositionViewModel({
        contract: props.contract,
        cardName: props.cardName,
        cardMeaning: props.cardMeaning,
        numerologyValue: props.numerologyValue,
        numerologyMeaning: props.numerologyMeaning,
        morningRitualData: props.morningRitualData,
        colorLine: props.colorLine,
        stoneLine: props.stoneLine,
        isFirstToday,
      });
      if (singleVoice) return vm;
      return applyGuideNarrativeToCompositionViewModel(vm, props.guideNarrativePayload);
    },
    [
      props.contract,
      props.cardName,
      props.cardMeaning,
      props.numerologyValue,
      props.numerologyMeaning,
      props.morningRitualData,
      props.colorLine,
      props.stoneLine,
      props.guideNarrativePayload,
      isFirstToday,
      singleVoice,
    ],
  );

  const engagedModel = useMemo(() => applyEngagementToViewModel(baseModel, engagement), [baseModel, engagement]);

  const prevContinuityForStory = useMemo(() => {
    if (!hydrated) return null;
    return loadPreviousDayContinuity(dateISO);
  }, [hydrated, dateISO]);
  const yesterdayClosed = Boolean(prevContinuityForStory && isDayContinuityClosed(prevContinuityForStory));

  const story = useMemo(() => {
    const base = buildTodayDayStoryViewModel({
      base: engagedModel,
      contract: props.contract,
      userName: resolveUserName(props.coreProfile),
      yesterdayClosed,
      todayOpened: engagement.todayOpened,
      isFirstToday,
      dateISO,
      cardName: props.cardName,
      cardMeaning: props.cardMeaning,
      tarotMainId: engagement.tarotPickedId ?? anchorTarotId,
      numerologyValue: props.numerologyValue,
      numerologyMeaning: props.numerologyMeaning,
      morningRitualData: props.morningRitualData,
      colorLine: props.colorLine,
      stoneLine: props.stoneLine,
      sunSignLabel: resolveTodaySunSignLabel(props.coreProfile),
      engagement,
    });
    return applySupplementaryNarrativesToDayStory(base, props.contract, {
      dayLayerPayload: props.dayLayerNarrativePayload,
      spheresPayload: props.spheresNarrativePayload,
      eveningPayload: props.eveningNarrativePayload,
    });
  }, [
    engagedModel,
    props.contract,
    props.coreProfile,
    yesterdayClosed,
    engagement,
    isFirstToday,
    dateISO,
    anchorTarotId,
    props.cardName,
    props.cardMeaning,
    props.numerologyValue,
    props.numerologyMeaning,
    props.morningRitualData,
    props.colorLine,
    props.stoneLine,
    props.dayLayerNarrativePayload,
    props.spheresNarrativePayload,
    props.eveningNarrativePayload,
  ]);

  useEffect(() => {
    if (singleVoice || !props.onRitualSpineComplete || !story.personalizedReady) return;
    const tarotMainId = engagement.tarotPickedId ?? anchorTarotId;
    if (tarotMainId == null) return;
    const drawn = getTodayTarotCardRu(tarotMainId);
    if (!drawn) return;
    const key = `${dateISO}|${tarotMainId}|${props.numerologyValue}`;
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
    props.todayData,
    props.numerologyValue,
    story.personalizedReady,
    engagement.tarotPickedId,
    anchorTarotId,
    dateISO,
    singleVoice,
  ]);

  const zones = useMemo(
    () =>
      resolveTodayCompositionZones({
        variant,
        engagement,
        isEveningSurface: story.isEveningSurface,
        personalizedReady: story.personalizedReady,
      }),
    [story.isEveningSurface, story.personalizedReady, variant, engagement],
  );

  const showRitualSpine = useMemo(
    () =>
      !story.personalizedReady &&
      (Boolean(zones.ritualTarot && !engagement.tarotPickedName) ||
        Boolean(zones.ritualNumber && engagement.tarotPickedName && !engagement.numberConfirmed) ||
        Boolean(story.tarotImpact && !engagement.numberConfirmed)),
    [
      story.personalizedReady,
      story.tarotImpact,
      zones.ritualTarot,
      zones.ritualNumber,
      engagement.tarotPickedName,
      engagement.numberConfirmed,
    ],
  );

  const pulseDisplay = useMemo(() => {
    if (showRitualSpine) return stripRitualCtaFromPulse(story.pulse);
    return story.pulse;
  }, [showRitualSpine, story.pulse]);

  const showContextPanel = useMemo(
    () => zones.glance && story.sphereFocus.cards.length > 0,
    [zones.glance, story.sphereFocus.cards.length],
  );

  const showColorGuide = zones.glance && Boolean(story.colorGuide);

  const showSkyCards = zones.astroContext && story.skyCards.length > 0;

  const promiseSuggestions = useMemo(
    () =>
      buildTodayPromiseSuggestions({
        primaryAction: props.contract.primary_action,
        focusTopicId: engagement.focusTopicId,
        developmentPoint: props.contract.personal_growth.development_point,
      }),
    [props.contract.primary_action, props.contract.personal_growth.development_point, engagement.focusTopicId],
  );

  const strengthenTools = useMemo(
    () =>
      applyRecommendedPracticeToStrengthen(
        story.personalizedReady ? story.strengthenLinked : story.strengthenPreview,
        story.personalizedReady ? recommendedPractice : null,
        {
          lowEnergy: isLowEnergyMood(engagement.morningMoodId),
        },
      ),
    [
      story.personalizedReady,
      story.strengthenLinked,
      story.strengthenPreview,
      recommendedPractice,
      engagement.morningMoodId,
    ],
  );

  const practiceTool = useMemo(
    () => strengthenTools.find((tool) => tool.id === "practice") ?? null,
    [strengthenTools],
  );
  const supportTools = useMemo(
    () => strengthenTools.filter((tool) => tool.id !== "practice"),
    [strengthenTools],
  );

  const prevContinuity = useMemo(() => {
    if (!hydrated) return null;
    return loadPreviousDayContinuity(dateISO);
  }, [hydrated, dateISO]);
  const continuityLine = useMemo(
    () => (prevContinuity ? buildContinuityOpeningLine(prevContinuity) : null),
    [prevContinuity],
  );
  const showContinuity = zones.continuity && Boolean(continuityLine);

  const mainFocusText = story.focusTitle;

  const engagementProfileKey = useMemo(
    () => engagementProfileScope(props.coreProfile ?? null),
    [props.coreProfile],
  );

  const persistEngagement = useCallback(
    (patch: Parameters<typeof saveDayEngagement>[1]) => {
      const next = saveDayEngagement(dateISO, patch, engagementProfileKey);
      setEngagement(next);
    },
    [dateISO, engagementProfileKey],
  );

  useEffect(() => {
    setEngagement(loadDayEngagement(dateISO, engagementProfileKey));
    setContinuityRecord(loadDayContinuity(dateISO));
    setGoalDraft(loadDayEngagement(dateISO, engagementProfileKey).dayGoal ?? "");
    setHydrated(true);
  }, [dateISO, engagementProfileKey]);

  useEffect(() => {
    let cancelled = false;
    void fetchCompactUserModelCached({ localDate: dateISO }).then((cum) => {
      if (cancelled || !cum) return;
      setEngagement((prev) => {
        const merged = mergeEngagementWithCompactUserModel(dateISO, prev, cum, engagementProfileKey);
        if (merged !== prev) {
          saveDayEngagement(dateISO, merged, engagementProfileKey);
        }
        return merged;
      });
    });
    return () => {
      cancelled = true;
    };
  }, [dateISO, engagementProfileKey]);

  useEffect(() => {
    if (!hydrated || !engagement.tarotPickedName || !engagement.numberConfirmed) return;
    let cancelled = false;
    void getJson<PracticeResponse>("/practices/current")
      .catch(async () => {
        const fallback = await getJson<PracticeResponse[]>("/practices?limit=1").catch(() => []);
        return fallback.length ? fallback[0] : null;
      })
      .then((practice) => {
        if (cancelled || !practice?.id) return;
        setRecommendedPractice(practice);
      });
    return () => {
      cancelled = true;
    };
  }, [hydrated, engagement.tarotPickedName, engagement.numberConfirmed, dateISO]);

  useEffect(() => {
    onVisible?.();
    if (!engagement.todayOpened) {
      persistEngagement({ todayOpened: true });
    }
  }, [onVisible, engagement.todayOpened, persistEngagement]);

  const onOpenEvening = useCallback(() => {
    const focus =
      engagement.dayGoal?.trim() ||
      mainFocusText ||
      continuityRecord?.mainFocus ||
      story.hero.themeShort ||
      "Главная тема дня";
    const draft: DayContinuityRecord = {
      dateISO,
      mainFocus: focus,
      outcome: continuityRecord?.outcome,
      outcomeNote: continuityRecord?.outcomeNote,
      closedAt: continuityRecord?.closedAt,
    };
    saveDayContinuity(draft);
    setContinuityRecord(draft);
    setEveningMode(true);
  }, [engagement.dayGoal, mainFocusText, continuityRecord, dateISO, story.hero.themeShort]);

  const onSubmitEveningClose = useCallback(
    (outcome: DayFocusOutcome, highlightId: string | null, note: string) => {
      const focus = engagement.dayGoal?.trim() || continuityRecord?.mainFocus || mainFocusText;
      if (!focus) return;
      setContinuitySaving(true);
      const closed: DayContinuityRecord = {
        dateISO,
        mainFocus: focus,
        outcome,
        outcomeNote: note || undefined,
        closedAt: new Date().toISOString(),
      };
      saveDayContinuity(closed);
      setContinuityRecord(closed);
      if (highlightId) {
        persistEngagement({ eveningHighlightId: highlightId });
      }
      setEveningMode(false);
      setContinuitySaving(false);
      trackMeaningEvent({
        event_type: "day_focus_outcome",
        event_source: "today",
        local_date: dateISO,
        payload: {
          outcome,
          main_focus: focus.slice(0, 500),
          note: note ? note.slice(0, 400) : null,
          source: isFirstToday ? "today_composition_first_today" : "today_day_story_v3",
          day_continuity_v0: true,
          practice_started: engagement.practiceStarted,
          practice_completed: engagement.practiceCompleted,
          promise_set: Boolean(engagement.dayGoal),
        },
        refreshRings: false,
      });
      if (highlightId || note) {
        trackMeaningEvent({
          event_type: "evening_reflection_submitted",
          event_source: "today",
          local_date: dateISO,
          payload: {
            highlight_id: highlightId,
            note: note ? note.slice(0, 400) : null,
            surface: "today_day_story_v3",
          },
          refreshRings: false,
        });
      }
      onDayClosed?.();
    },
    [
      engagement.dayGoal,
      continuityRecord?.mainFocus,
      mainFocusText,
      dateISO,
      onDayClosed,
      trackMeaningEvent,
      isFirstToday,
      engagement.practiceStarted,
      engagement.practiceCompleted,
      persistEngagement,
    ],
  );

  const onTarotCommit = useCallback(
    (id: number) => {
      setTarotPendingId(id);
      persistEngagement({ tarotPickedId: id });
      void revealDayCard({
        cardId: id,
        isAuthenticated,
        source: "today_ritual",
        idempotencyKey: `tarot_reveal:${dateISO}:${id}:${isAuthenticated ? "u" : "g"}`,
      })
        .then((view) => props.onSymbolRevealResult?.(view))
        .catch(() => {
          /* local engagement still tracks pick; server SoT retries on continue */
        });
      trackMeaningEvent({
        event_type: "tarot_selected",
        event_source: "today",
        local_date: dateISO,
        payload: { tarot_main_id: id, surface: "today_day_story_v3", experience_inline: true },
        refreshRings: false,
      });
    },
    [dateISO, isAuthenticated, persistEngagement, props.onSymbolRevealResult, trackMeaningEvent],
  );

  const onTarotRevealed = useCallback(
    (id: number) => {
      trackMeaningEvent({
        event_type: "tarot_revealed",
        event_source: "today",
        local_date: dateISO,
        payload: { tarot_main_id: id, surface: "today_day_story_v3", experience_inline: true },
        refreshRings: false,
      });
    },
    [dateISO, trackMeaningEvent],
  );

  const onTarotContinue = useCallback(() => {
    const id = tarotPendingId ?? engagement.tarotPickedId ?? anchorTarotId;
    const drawn = getTodayTarotCardRu(id);
    const ritual: RitualPersistedState = {
      ...(loadRitualPersisted(dateISO) ?? {
        opened: false,
        numberRevealed: false,
        mood: null,
        headTopic: null,
        essentials: {},
        honestStep: null,
        numberRhythm: null,
        tarotClarifierId: null,
        tarotApplied: false,
        tarotContinueAck: false,
        checkInSubmitted: false,
      }),
      tarotMainId: id,
      tarotApplied: true,
      tarotContinueAck: true,
    };
    saveRitualPersisted(dateISO, ritual);
    persistEngagement({ tarotPickedId: id, tarotPickedName: drawn?.nameRu ?? props.cardName });
    setTarotPendingId(null);
    setRitualPickOpen(null);
    if (!engagement.numberConfirmed) {
      setRitualPickOpen("number");
    }
  }, [anchorTarotId, dateISO, engagement.numberConfirmed, engagement.tarotPickedId, persistEngagement, props.cardName, tarotPendingId]);

  const onNumberComplete = useCallback(() => {
    persistEngagement({ numberConfirmed: true });
    setRitualPickOpen(null);
    void revealDayNumber({
      isAuthenticated,
      source: "today_ritual",
      idempotencyKey: `number_reveal:${dateISO}:${isAuthenticated ? "u" : "g"}`,
    })
      .then((view) => props.onSymbolRevealResult?.(view))
      .catch(() => {
        /* local ack kept; server SoT can retry */
      });
    trackMeaningEvent({
      event_type: "number_selected",
      event_source: "today",
      local_date: dateISO,
      payload: { surface: "today_day_story_v3", experience_inline: true },
      refreshRings: false,
    });
  }, [dateISO, isAuthenticated, persistEngagement, props.onSymbolRevealResult, trackMeaningEvent]);

  const onInterpretationConfirm = useCallback(
    (
      target: "tarot_impact" | "number_impact",
      choiceId: ProximityChoiceId,
      resonance: InterpretationResonance,
      headline?: string | null,
    ) => {
      persistEngagement(
        target === "tarot_impact"
          ? { tarotResonance: choiceId }
          : { numberResonance: choiceId },
      );
      trackMeaningEvent({
        event_type: "sphere_feedback",
        event_source: "today",
        local_date: dateISO,
        payload: buildInterpretationConfirmPayload({ target, resonance, choiceId, headline }),
        refreshRings: false,
      });
    },
    [dateISO, persistEngagement, trackMeaningEvent],
  );

  const onSaveGoal = useCallback(() => {
    const trimmed = goalDraft.trim();
    if (!trimmed) return;
    persistEngagement({ dayGoal: trimmed });
    setGoalDraftOpen(false);
    trackMeaningEvent({
      event_type: "action_option_selected",
      event_source: "today",
      local_date: dateISO,
      payload: {
        action: "day_promise_set",
        promise_text: trimmed.slice(0, 200),
        surface: "today_day_story_v3",
      },
      refreshRings: false,
    });
  }, [goalDraft, dateISO, persistEngagement, trackMeaningEvent]);

  const onPracticeAction = useCallback(async () => {
    if (engagement.practiceCompleted) return;

    if (!engagement.practiceStarted) {
      persistEngagement({
        practiceStarted: true,
        recommendedPracticeId: recommendedPractice?.id ?? null,
      });
      trackMeaningEvent({
        event_type: "action_option_selected",
        event_source: "today",
        local_date: dateISO,
        payload: {
          action: "practice_started",
          practice_id: recommendedPractice?.id ?? null,
          surface: "today_day_story_v3",
        },
        refreshRings: false,
      });
      if (recommendedPractice?.id) {
        trackMeaningEvent({
          event_type: "support_selected",
          event_source: "today",
          local_date: dateISO,
          payload: {
            recommended: "practice",
            practice_id: recommendedPractice.id,
            surface: "today_day_story_v3",
          },
          refreshRings: false,
        });
      }
      return;
    }

    if (!recommendedPractice?.id) return;

    try {
      setPracticeCompleting(true);
      await postJson(`/practices/${recommendedPractice.id}/complete`, {});
      persistEngagement({ practiceCompleted: true });
      trackMeaningEvent({
        event_type: "practice_completed",
        event_source: "today",
        local_date: dateISO,
        payload: {
          practice_id: recommendedPractice.id,
          duration_minutes: recommendedPractice.duration_minutes ?? null,
          surface: "today_day_story_v3",
        },
        refreshRings: false,
      });
    } catch {
      /* network — user can retry */
    } finally {
      setPracticeCompleting(false);
    }
  }, [
    dateISO,
    engagement.practiceCompleted,
    engagement.practiceStarted,
    persistEngagement,
    recommendedPractice,
    trackMeaningEvent,
  ]);

  const dayClosed = isDayContinuityClosed(continuityRecord);
  const todayHeroSymbol = useMemo(() => buildTodayHeroSymbol(props.coreProfile), [props.coreProfile]);
  const todayHeroPillars = useMemo(() => buildTodayHeroPillars(props.coreProfile), [props.coreProfile]);
  const themeLoading = !singleVoice && props.guideNarrativeLoading && !props.guideNarrativePayload;
  const useProductFoundation = !isFirstToday;
  const useProductPersonalized = useProductFoundation && story.personalizedReady;

  if (eveningMode && continuityRecord && !dayClosed) {
    if (useProductFoundation) {
      return (
        <TodayEveningProductClose
          userName={resolveUserName(props.coreProfile)}
          userPromise={engagement.dayGoal}
          themeShort={story.hero.themeShort}
          practiceCompleted={engagement.practiceCompleted}
          practiceStarted={engagement.practiceStarted}
          affirmationRead={engagement.affirmationRead}
          strengthenToolCount={strengthenTools.length}
          promiseSuggestions={promiseSuggestions}
          onPickPromise={(text) => {
            persistEngagement({ dayGoal: text });
            trackMeaningEvent({
              event_type: "action_option_selected",
              event_source: "today",
              local_date: dateISO,
              payload: {
                action: "day_promise_set",
                promise_text: text.slice(0, 200),
                surface: "today_evening_close",
              },
              refreshRings: false,
            });
          }}
          saving={continuitySaving}
          onSubmit={onSubmitEveningClose}
          onBack={() => setEveningMode(false)}
        />
      );
    }

    return (
      <div className={styles.shellEvening} data-testid="today-composition-evening">
        <TodayDayContinuityEveningClose
          userPromise={engagement.dayGoal}
          themeShort={story.hero.themeShort}
          promiseSuggestions={promiseSuggestions}
          onPickPromise={(text) => {
            persistEngagement({ dayGoal: text });
            trackMeaningEvent({
              event_type: "action_option_selected",
              event_source: "today",
              local_date: dateISO,
              payload: {
                action: "day_promise_set",
                promise_text: text.slice(0, 200),
                surface: "today_evening_close",
              },
              refreshRings: false,
            });
          }}
          saving={continuitySaving}
          onSubmit={onSubmitEveningClose}
          onBack={() => setEveningMode(false)}
        />
      </div>
    );
  }

  if (dayClosed && continuityRecord) {
    return (
      <div className={styles.shellEvening} data-testid="today-composition-closed">
        <TodayDayContinuityClosed record={continuityRecord} />
      </div>
    );
  }

  const morningDialogue = (
    <TodayDayDialogueMorning
      dateISO={dateISO}
      morningMoodId={engagement.morningMoodId}
      morningMoodCapturedAtMs={engagement.morningMoodCapturedAtMs}
      focusTopicId={engagement.focusTopicId}
      focusTopicCapturedAtMs={engagement.focusTopicCapturedAtMs}
      onSelectMood={(id) => {
        persistEngagement({ morningMoodId: id, morningMoodCapturedAtMs: Date.now() });
        clearCompactUserModelCache(dateISO);
        trackMeaningEvent({
          event_type: "mood_selected",
          event_source: "today",
          local_date: dateISO,
          payload: { mood_id: id, surface: "today_day_dialogue_v1" },
          refreshRings: false,
        });
      }}
      onSelectFocus={(id) => {
        persistEngagement({ focusTopicId: id, focusTopicCapturedAtMs: Date.now() });
        clearCompactUserModelCache(dateISO);
        trackMeaningEvent({
          event_type: "head_topic_selected",
          event_source: "today",
          local_date: dateISO,
          payload: { topic_id: id, head_topic: id, surface: "today_day_dialogue_v1" },
          refreshRings: false,
        });
      }}
    />
  );

  const greetingParts = splitSalutation(story.greeting.salutation);
  const showGlance = zones.glance && (story.glance.supported.length > 0 || story.glance.helpful.length > 0);

  const greetingSection = zones.greeting ? (
    <section className={styles.greeting} data-testid="today-zone-greeting">
      {useProductFoundation ? (
        <>
          <p className={styles.greetingLead}>{greetingParts.lead}</p>
          {greetingParts.name ? (
            <h1 className={styles.greetingName}>{greetingParts.name}</h1>
          ) : (
            <h1 className={styles.greetingName}>{greetingParts.lead}</h1>
          )}
        </>
      ) : (
        <h1 className={styles.greetingSalutation}>{story.greeting.salutation}</h1>
      )}
      <p className={styles.greetingLine}>{story.greeting.line}</p>
      {!useProductFoundation ? <p className={styles.greetingDate}>{props.displayDate}</p> : null}
    </section>
  ) : null;

  const topRowSection = useProductFoundation && zones.greeting ? (
    <div className={styles.topRow} data-testid="today-zone-top-row">
      <p className={styles.topRowDate}>{props.displayDate}</p>
      <div className={styles.avatarChip} aria-hidden>
        {userInitial(props.coreProfile)}
      </div>
    </div>
  ) : null;

  const pulseSection = zones.pulse ? (
    <div
      className={useProductFoundation ? styles.pulseCard : styles.dayAnchorPulse}
      data-testid="today-zone-pulse"
    >
      <p className={styles.pulseLabel}>{story.pulseLabel}</p>
      {props.dayStoryUpdating ? (
        <p className={styles.pulseText} data-testid="today-day-story-updating" aria-live="polite">
          Обновляем описание дня…
        </p>
      ) : (
        <p className={styles.pulseText}>{pulseDisplay}</p>
      )}
      {story.ritualUnlockHint && !story.personalizedReady ? (
        <p className={styles.ritualUnlockHint}>{story.ritualUnlockHint}</p>
      ) : null}
    </div>
  ) : null;

  const glanceSection = showGlance ? (
    <section className={styles.glanceSection} data-testid="today-zone-glance">
      <div className={styles.glanceCardGrid}>
        {story.glance.supported.map((card) => (
          <article key={card.id} className={styles.glanceColCard} data-testid={`today-glance-${card.id}`}>
            <p className={styles.glanceColTitleStrong}>{copy.glanceStrongTitle}</p>
            <p className={styles.glanceSphereLabel}>
              <span className={styles.glanceDotStrong} aria-hidden />
              {card.sphere}
            </p>
            <p className={styles.glanceSphereComment}>{card.comment}</p>
          </article>
        ))}
        {story.glance.helpful.map((card) => (
          <article key={card.id} className={styles.glanceColCard} data-testid={`today-glance-${card.id}`}>
            <p className={styles.glanceColTitleHelpful}>{copy.glanceWeakTitle}</p>
            <p className={styles.glanceSphereLabel}>
              <span className={styles.glanceDotWeak} aria-hidden />
              {card.sphere}
            </p>
            <p className={styles.glanceSphereComment}>{card.comment}</p>
          </article>
        ))}
      </div>
    </section>
  ) : null;

  const heroSection = zones.hero ? (
    useProductFoundation ? (
      <section
        className={`${styles.themeDarkHero} ${story.personalizedReady ? styles.themeDarkHeroCompact : ""}`.trim()}
        data-testid="today-zone-hero"
        aria-labelledby="today-day-theme-title"
      >
        <div className={styles.themeDarkAtmosphere} aria-hidden>
          <SacredGeometryBackdrop emphasis="soft" preset="today" />
        </div>
        <div className={`${styles.themeDarkContent} ${profileMotionStyles.heroEnter}`}>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>1</span>
            <span>{copy.journey.dayTitle}</span>
          </p>
          {themeLoading ? (
            <p className={styles.themeDarkLoading}>{copy.loadingDay}</p>
          ) : (
            <>
              <PersonalizationDegradedBadge
                contract={props.contract}
                narrativeRequestFailed={props.guideNarrativeRequestFailed}
              />
              <p className={styles.themeDarkKicker}>{copy.themeLabel}</p>
              <h2
                id="today-day-theme-title"
                className={styles.themeDarkTitle}
                data-testid="today-entity-daily-theme"
              >
                {story.hero.centralThought}
              </h2>
              {story.hero.themeShort ? <p className={styles.themeDarkSubline}>{story.hero.themeShort}</p> : null}
              {!story.personalizedReady && copy.journey.dayLead ? (
                <p className={styles.themeDarkLead}>{copy.journey.dayLead}</p>
              ) : null}
            </>
          )}
        </div>
      </section>
    ) : (
      <div className={styles.dayAnchorHero} data-testid="today-zone-hero">
        {!themeLoading ? (
          <PersonalizationDegradedBadge
            contract={props.contract}
            narrativeRequestFailed={props.guideNarrativeRequestFailed}
          />
        ) : null}
        <HeroMedium
          embedded
          loading={themeLoading}
          loadingText={copy.loadingDay}
          kicker={isFirstToday ? undefined : copy.themeLabel}
          title={story.hero.centralThought}
          subline={story.hero.themeShort}
          symbol={todayHeroSymbol}
          pillars={todayHeroPillars}
          ariaLabel={copy.themeLabel}
          titleTestId="today-entity-daily-theme"
        />
      </div>
    )
  ) : null;

  const dayAnchorSection =
    !useProductFoundation && (zones.hero || zones.pulse) ? (
      <section className={styles.dayAnchor} data-testid="today-zone-day-anchor">
        {heroSection}
        {pulseSection}
      </section>
    ) : null;

  const tarotPickExperience = (
    <RitualTarotPickExperience
      anchorCardId={anchorTarotId}
      resumeCommittedId={tarotPendingId ?? engagement.tarotPickedId}
      cardTitleRu={anchorTarotRecord?.nameRu ?? props.cardName}
      tagLabels={anchorTarotTags}
      onCommitMain={onTarotCommit}
      onRevealed={onTarotRevealed}
      onContinue={onTarotContinue}
      reduceMotion={reduceMotion}
      startAtGrid
      allowSkipAnimation={false}
      gridSize={5}
      gridLead={RITUAL_COPY.experiencePickCardEyebrow}
      gridSub={RITUAL_COPY.experienceTarotGridSub}
    />
  );

  const numberPickExperience = (
    <RitualNumberPickExperience
      systemDisplay={props.numerologyValue}
      numberMeaning={props.numerologyMeaning ?? undefined}
      tileMode="symbol"
      reduceMotion={reduceMotion}
      onComplete={onNumberComplete}
    />
  );

  const ritualTarotImpactStage =
    story.tarotImpact && !story.personalizedReady ? (
      <div className={styles.ritualSpineStage} data-testid="today-zone-tarot-impact">
        <section className={styles.ritualReveal}>
          <p className={styles.ritualRevealKind}>Символ дня</p>
          <h2 className={styles.ritualRevealTitle}>{story.tarotImpact.title}</h2>
          <p className={styles.ritualRevealHeadline}>{story.tarotImpact.headline}</p>
          <p className={styles.ritualRevealBody}>{story.tarotImpact.body}</p>
          <TodayInterpretationConfirm
            target="tarot_impact"
            selectedChoiceId={(engagement.tarotResonance as ProximityChoiceId | null) ?? null}
            onSelect={(choiceId, resonance) =>
              onInterpretationConfirm("tarot_impact", choiceId, resonance, story.tarotImpact?.headline)
            }
          />
        </section>
      </div>
    ) : null;

  const ritualGateSection =
    useProductFoundation && showRitualSpine ? (
      <div className={styles.journeyScene} data-testid="today-zone-open-day">
        <header className={styles.journeySceneHeader}>
          <p className={styles.journeyStepIndex}>
            <span className={styles.journeyStepBadge}>2</span>
            <span>{copy.journey.openTitle}</span>
          </p>
          <p className={styles.journeySceneLead}>{copy.journey.openLead}</p>
        </header>
        <DsRitualGateSection testId="today-zone-ritual-gates">
          {zones.ritualTarot && !engagement.tarotPickedName ? (
            <DsRitualGate
              kind="tarot"
              step="Шаг 1"
              title={copy.ritualTarotPendingTitle}
              body={copy.ritualTarotPendingBody}
              cta={copy.ritualTarotOpenCta}
              testId="today-ritual-tarot-gate"
              onClick={() => setRitualPickOpen("tarot")}
            />
          ) : null}
          {zones.ritualNumber && engagement.tarotPickedName && !engagement.numberConfirmed ? (
            <DsRitualGate
              kind="number"
              step="Шаг 2"
              title={copy.ritualNumberPendingTitle}
              body={copy.ritualNumberPendingBody}
              cta={copy.ritualNumberOpenCta}
              testId="today-ritual-number-gate"
              onClick={() => setRitualPickOpen("number")}
            />
          ) : null}
        </DsRitualGateSection>
      </div>
    ) : null;

  const ritualSpineStages = showRitualSpine ? (
    <>
      {!useProductFoundation && zones.ritualTarot && !engagement.tarotPickedName ? (
        <div className={styles.ritualSpineStage} data-testid="today-zone-ritual-tarot">
          {!isFirstToday ? (
            <>
              <h3 className={styles.ritualGateTitle}>{copy.ritualTarotPendingTitle}</h3>
              <p className={styles.ritualGateBody}>{copy.ritualTarotPendingBody}</p>
            </>
          ) : null}
          <div className={`${styles.ritualPickEmbed} ${styles.ritualPickEmbedFlush}`} data-testid="today-ritual-tarot-pick">
            {tarotPickExperience}
          </div>
        </div>
      ) : null}

      {!useProductFoundation ? ritualTarotImpactStage : null}

      {!useProductFoundation && zones.ritualNumber && engagement.tarotPickedName && !engagement.numberConfirmed ? (
        <div className={styles.ritualSpineStage} data-testid="today-zone-ritual-number">
          {!isFirstToday ? (
            <>
              <h3 className={styles.ritualGateTitle}>{copy.ritualNumberPendingTitle}</h3>
              <p className={styles.ritualGateBody}>{copy.ritualNumberPendingBody}</p>
            </>
          ) : null}
          <div className={`${styles.ritualPickEmbed} ${styles.ritualPickEmbedFlush}`} data-testid="today-ritual-number-pick">
            {numberPickExperience}
          </div>
        </div>
      ) : null}
    </>
  ) : null;

  const ritualSpineSection =
    showRitualSpine && isFirstToday ? (
      <ConversationTurn
        turnId="today_ritual"
        message={
          <>
            <h2>{copy.ritualTarotPendingTitle}</h2>
            <p>{copy.ritualTarotPendingBody}</p>
          </>
        }
        response={ritualSpineStages}
      />
    ) : null;

  const dayStoryFoundation = isFirstToday ? (
    <ConversationThread testId="conversation-thread-first-today">
      {greetingSection ? (
        <ConversationTurn turnId="today_opening" message={greetingSection} response={morningDialogue} />
      ) : null}
      {dayAnchorSection ? <ConversationTurn turnId="today_focus" message={dayAnchorSection} /> : null}
      {ritualSpineSection}
    </ConversationThread>
  ) : (
    <div className={styles.foundationStack} data-testid="today-zone-foundation">
      {/* Dashboard owns greeting chrome when embedded; day hero still leads the story. */}
      {!embeddedInWebDashboard ? topRowSection : null}
      {!embeddedInWebDashboard ? greetingSection : null}

      {heroSection}

      {!story.personalizedReady ? (
        <>
          {pulseSection}
          {glanceSection}
          {ritualGateSection}
          {ritualTarotImpactStage}
          {morningDialogue}
        </>
      ) : (
        morningDialogue
      )}
    </div>
  );

  return (
    <>
      <div
        id={isFirstToday ? "today-first-day-surface" : "today-composition-surface"}
        data-testid={isFirstToday ? "today-composition-first-today" : "today-composition-surface"}
        className={`${styles.root} ${embeddedInWebDashboard ? styles.rootWebEmbed : ""}`}
      >
        {showContinuity ? (
          <div className={styles.continuityWrap} data-testid="today-zone-continuity">
            <section className={styles.continuityPill} data-testid="today-entity-continuity-recall">
              <div className={styles.continuityInner}>
                <span className={styles.continuityAccent} aria-hidden />
                <div>
                  <p className={styles.continuityEyebrow}>{copy.continuityEyebrow}</p>
                  <p className={styles.continuityBody}>{continuityLine}</p>
                </div>
              </div>
              <span className={styles.continuityChevron} aria-hidden>
                ›
              </span>
            </section>
          </div>
        ) : null}

        {dayStoryFoundation}

        {useProductPersonalized ? (
          <TodayPersonalizedProductSection
            embeddedInWebDashboard={embeddedInWebDashboard}
            story={story}
            contract={props.contract}
            strengthenTools={strengthenTools}
            promiseSuggestions={promiseSuggestions}
            dayGoal={engagement.dayGoal}
            practiceCompleted={engagement.practiceCompleted}
            practiceStarted={engagement.practiceStarted}
            affirmationRead={engagement.affirmationRead}
            practiceCompleting={practiceCompleting}
            goalDraftOpen={goalDraftOpen}
            goalDraft={goalDraft}
            coreProfile={props.coreProfile}
            tarotDeepenHref={
              engagement.tarotPickedId != null
                ? buildTarotDeepenHref({
                    cardId: engagement.tarotPickedId,
                    orientation: "upright",
                    source: "today",
                  })
                : null
            }
            onPickPromise={(text) => {
              persistEngagement({ dayGoal: text });
              trackMeaningEvent({
                event_type: "action_option_selected",
                event_source: "today",
                local_date: dateISO,
                payload: {
                  action: "day_promise_set",
                  promise_text: text.slice(0, 200),
                  surface: "today_day_story_v3",
                },
                refreshRings: false,
              });
            }}
            onOpenGoalDraft={() => setGoalDraftOpen(true)}
            onGoalDraftChange={setGoalDraft}
            onSaveGoal={onSaveGoal}
            onPracticeAction={() => void onPracticeAction()}
            onAffirmationRead={() => {
              persistEngagement({ affirmationRead: true });
              trackMeaningEvent({
                event_type: "action_option_selected",
                event_source: "today",
                local_date: dateISO,
                payload: { action: "affirmation_read", surface: "today_day_story_v3" },
                refreshRings: false,
              });
            }}
          />
        ) : null}

        {!useProductPersonalized && showSkyCards ? (
          <section className={styles.skySection} data-testid="today-zone-sky-influences">
            <span className={styles.sectionEyebrow}>Что формирует день</span>
            <h2 className={styles.sectionTitle}>{copy.astroContextTitle}</h2>
            <TodaySkyStoryCards cards={story.skyCards} />
          </section>
        ) : null}

        {story.ritualTransformBanner ? (
          <p className={styles.ritualTransformBanner} data-testid="today-ritual-transform">
            {story.ritualTransformBanner}
          </p>
        ) : null}

        {!useProductPersonalized && showColorGuide && story.colorGuide ? (
          <TodayDayColorGuideSection guide={story.colorGuide} />
        ) : null}

        {!useProductPersonalized && showContextPanel ? (
          <section className={styles.contextPanel} data-testid="today-zone-context">
            <span className={styles.sectionEyebrow}>Сферы дня</span>
            <h2 className={styles.contextPanelTitle}>{copy.contextPanelTitle}</h2>
            {story.sphereFocus.cards.length > 0 ? (
              <div className={styles.contextPanelBlock} data-testid="today-zone-sphere-focus">
                <div className={styles.sphereFocusGrid}>
                  {story.sphereFocus.cards.map((card) => (
                    <article
                      key={card.id}
                      className={card.role === "peak" ? styles.sphereFocusPeak : styles.sphereFocusCaution}
                      data-testid={`today-sphere-${card.role}`}
                    >
                      <p className={styles.sphereFocusRole}>
                        {card.role === "peak" ? copy.glanceStrongTitle : copy.glanceWeakTitle}
                      </p>
                      <h3 className={styles.sphereFocusHeadline}>{card.headline}</h3>
                      <p className={styles.sphereFocusBody}>{card.body}</p>
                      {card.releaseLine ? (
                        <p className={styles.sphereFocusRelease}>{card.releaseLine}</p>
                      ) : null}
                    </article>
                  ))}
                </div>
                <p className={styles.sphereNeutralNote}>{story.sphereFocus.neutralNote}</p>
              </div>
            ) : null}
          </section>
        ) : null}

        {!useProductPersonalized && zones.strengthen && strengthenTools.length > 0 ? (
          <section
            data-testid="today-zone-strengthen"
            className={story.personalizedReady ? undefined : styles.strengthenPreview}
          >
            <span className={styles.sectionEyebrow}>Для тебя сегодня</span>
            <h2 className={styles.sectionTitle}>{copy.strengthenTitle}</h2>
            {!story.personalizedReady && story.ritualUnlockHint ? (
              <p className={styles.strengthenPreviewHint}>{story.ritualUnlockHint}</p>
            ) : null}
            <div className={styles.toolGrid}>
              {practiceTool ? (
                <article className={styles.toolCardFeatured} data-testid="today-tool-practice">
                  <p className={styles.toolLabel}>{practiceTool.label}</p>
                  <p className={styles.toolTitle}>{practiceTool.title}</p>
                  <p className={styles.toolDetail}>{practiceTool.detail}</p>
                  {practiceTool.duration ? <p className={styles.toolMeta}>{practiceTool.duration}</p> : null}
                  <button
                    type="button"
                    className={`orbit-button orbit-button-primary ${styles.toolActionPrimary}`}
                    disabled={!story.personalizedReady || engagement.practiceCompleted || practiceCompleting}
                    onClick={() => void onPracticeAction()}
                  >
                    {engagement.practiceCompleted
                      ? copy.practiceCompleted
                      : engagement.practiceStarted
                        ? copy.practiceComplete
                        : story.personalizedReady
                          ? copy.practiceStart
                          : "Откроется после ритуала"}
                  </button>
                </article>
              ) : null}
              {supportTools.length > 0 ? (
                <div className={styles.toolGridSecondary}>
                  {supportTools.map((tool) => (
                    <article
                      key={tool.id}
                      className={styles.toolCardCompact}
                      data-testid={`today-tool-${tool.id}`}
                    >
                      <p className={styles.toolLabel}>{tool.label}</p>
                      <p className={styles.toolTitle}>{tool.title}</p>
                      <p className={styles.toolDetail}>{tool.detail}</p>
                      {tool.id === "affirmation" && story.personalizedReady ? (
                        <button
                          type="button"
                          className={`orbit-button orbit-button-secondary ${styles.toolAction}`}
                          disabled={engagement.affirmationRead}
                          onClick={() => {
                            persistEngagement({ affirmationRead: true });
                            trackMeaningEvent({
                              event_type: "action_option_selected",
                              event_source: "today",
                              local_date: dateISO,
                              payload: { action: "affirmation_read", surface: "today_day_story_v3" },
                              refreshRings: false,
                            });
                          }}
                        >
                          {engagement.affirmationRead ? copy.readAffirmation : copy.readAffirmation}
                        </button>
                      ) : null}
                    </article>
                  ))}
                </div>
              ) : null}
            </div>
          </section>
        ) : null}

        {!useProductPersonalized && story.personalizedReady ? (
        <div className={styles.personalSection} data-testid="today-zone-personal">

        {story.tarotImpact ? (
          <section className={styles.ritualReveal} data-testid="today-zone-tarot-impact">
            <p className={styles.ritualRevealKind}>Символ дня</p>
            <h2 className={styles.ritualRevealTitle}>{story.tarotImpact.title}</h2>
            <p className={styles.ritualRevealHeadline}>{story.tarotImpact.headline}</p>
            <p className={styles.ritualRevealBody}>{story.tarotImpact.body}</p>
            <TodayInterpretationConfirm
              target="tarot_impact"
              selectedChoiceId={(engagement.tarotResonance as ProximityChoiceId | null) ?? null}
              onSelect={(choiceId, resonance) =>
                onInterpretationConfirm("tarot_impact", choiceId, resonance, story.tarotImpact?.headline)
              }
            />
            {engagement.tarotPickedId != null ? (
              <Link
                href={buildTarotDeepenHref({
                  cardId: engagement.tarotPickedId,
                  orientation: "upright",
                  source: "today",
                })}
                className={`orbit-button orbit-button-secondary ${styles.ritualDeepenCta}`}
                data-testid="today-tarot-deepen"
                onClick={() => {
                  trackMeaningEvent({
                    event_type: "tarot_deepen_started",
                    event_source: TAROT_DEEPEN_EVENT_SOURCE,
                    local_date: dateISO,
                    payload: buildTarotDeepenEventPayload({
                      cardId: engagement.tarotPickedId!,
                      orientation: "upright",
                      source: "today",
                    }),
                    idempotency_key: tarotDeepenIdempotencyKey({
                      cardId: engagement.tarotPickedId!,
                      source: "today",
                      localDate: dateISO,
                    }),
                    refreshRings: false,
                  });
                }}
              >
                Исследовать глубже →
              </Link>
            ) : null}
          </section>
        ) : null}

        {story.numberImpact ? (
          <section className={styles.ritualReveal} data-testid="today-zone-number-impact">
            <p className={styles.ritualRevealKind}>Число дня</p>
            <h2 className={styles.ritualRevealTitle}>{story.numberImpact.title}</h2>
            <p className={styles.ritualRevealHeadline}>{story.numberImpact.headline}</p>
            <p className={styles.ritualRevealBody}>{story.numberImpact.body}</p>
            <TodayInterpretationConfirm
              target="number_impact"
              selectedChoiceId={(engagement.numberResonance as ProximityChoiceId | null) ?? null}
              onSelect={(choiceId, resonance) =>
                onInterpretationConfirm("number_impact", choiceId, resonance, story.numberImpact?.headline)
              }
            />
          </section>
        ) : null}

        {zones.whyStory && story.whyStory.length > 0 ? (
          <section className={styles.whyStory} data-testid="today-zone-why-story">
            <h2 className={styles.sectionTitle}>{copy.whyStoryTitle}</h2>
            <div className={styles.whyStoryBody} data-testid="today-entity-why-expand">
              {story.whyStory.map((line) => (
                <p key={line} className={styles.whyStoryParagraph}>
                  {line}
                </p>
              ))}
            </div>
          </section>
        ) : null}

        {zones.promise && story.personalizedReady ? (
          <section data-testid="today-zone-promise">
            <h2 className={styles.sectionTitle}>{copy.promiseTitle}</h2>
            <p className={styles.actionsLead}>{copy.promiseLead}</p>
            {!engagement.dayGoal ? (
              <p className={styles.promiseUnsetHint}>{copy.promiseUnsetHint}</p>
            ) : null}
            <div className={styles.promiseGrid}>
              {promiseSuggestions.map((s) => (
                <button
                  key={s.id}
                  type="button"
                  className={
                    engagement.dayGoal === s.text ? `${styles.promiseChip} ${styles.promiseChipActive}` : styles.promiseChip
                  }
                  data-testid={`today-promise-${s.id}`}
                  onClick={() => {
                    persistEngagement({ dayGoal: s.text });
                    trackMeaningEvent({
                      event_type: "action_option_selected",
                      event_source: "today",
                      local_date: dateISO,
                      payload: {
                        action: "day_promise_set",
                        promise_text: s.text.slice(0, 200),
                        surface: "today_day_story_v3",
                      },
                      refreshRings: false,
                    });
                  }}
                >
                  {s.text}
                </button>
              ))}
            </div>
            {goalDraftOpen ? (
              <div className={styles.goalForm} data-testid="today-entity-daily-goal">
                <label className={styles.toolLabel} htmlFor="day-goal-input">
                  {copy.goalPrompt}
                </label>
                <input
                  id="day-goal-input"
                  className={styles.goalInput}
                  value={goalDraft}
                  onChange={(e) => setGoalDraft(e.target.value)}
                  maxLength={200}
                />
                <button type="button" className="orbit-button orbit-button-primary" onClick={onSaveGoal}>
                  {copy.goalSave}
                </button>
              </div>
            ) : (
              <button type="button" className={`orbit-button orbit-button-secondary ${styles.promiseCustom}`} onClick={() => setGoalDraftOpen(true)}>
                Написать своё
              </button>
            )}
            {engagement.dayGoal ? (
              <p className={styles.promiseChosen} data-testid="today-promise-chosen">
                Твоё обещание: {engagement.dayGoal}
              </p>
            ) : null}
          </section>
        ) : null}

        {zones.actions ? (
          <section data-testid="today-zone-actions">
            <h2 className={styles.sectionTitle}>{copy.actionsTitle}</h2>
            <p className={styles.actionsLead}>{copy.actionsLead}</p>
            <div className={styles.actionGrid}>
              {story.actions
                .filter((action) => action.id !== "goal")
                .map((action) => {
                  if (action.id === "practice") {
                    return (
                      <button
                        key={action.id}
                        type="button"
                        className={styles.actionCard}
                        data-testid={`today-action-${action.id}`}
                        onClick={() => {
                          void onPracticeAction();
                          document.querySelector('[data-testid="today-zone-strengthen"]')?.scrollIntoView({ behavior: "smooth" });
                        }}
                      >
                        <p className={styles.actionLabel}>{action.label}</p>
                        <p className={styles.actionDesc}>{action.description}</p>
                      </button>
                    );
                  }
                  if (action.href) {
                    return (
                      <Link
                        key={action.id}
                        href={action.href}
                        className={styles.actionCard}
                        data-testid={`today-action-${action.id}`}
                      >
                        <p className={styles.actionLabel}>{action.label}</p>
                        <p className={styles.actionDesc}>{action.description}</p>
                      </Link>
                    );
                  }
                  return null;
                })}
            </div>
          </section>
        ) : null}

        {zones.growthPromise && story.dayContinuityNote ? (
          <section className={styles.growthPromise} data-testid="today-zone-growth">
            <h2 className={styles.sectionTitle}>{copy.continuityNoteTitle}</h2>
            <p className={styles.growthPromiseLine}>{story.dayContinuityNote}</p>
          </section>
        ) : null}
        </div>
        ) : null}

        {useProductPersonalized && zones.evening ? (
          <div className={styles.eveningZone} data-testid="today-zone-evening-entry">
            <p className={styles.eveningHint}>{copy.eveningHint}</p>
            <button
              type="button"
              className={`orbit-button orbit-button-primary ${styles.eveningButton}`}
              data-testid="today-evening-open"
              onClick={onOpenEvening}
            >
              {copy.eveningCta}
            </button>
          </div>
        ) : null}

        {!useProductPersonalized && story.isEveningSurface && zones.evening ? (
          <section className={styles.eveningRecap} data-testid="today-zone-evening-recap">
            <h2 className={styles.sectionTitle}>{copy.eveningRecapTitle}</h2>
            {story.eveningReflectionPrompt ? (
              <p className={styles.eveningRecapLine} data-testid="today-evening-reflection-prompt">
                {story.eveningReflectionPrompt}
              </p>
            ) : null}
            {story.eveningQuestion ? (
              <p className={styles.eveningRecapQuestion} data-testid="today-evening-question">
                {story.eveningQuestion}
              </p>
            ) : null}
            {engagement.dayGoal ? (
              <p className={styles.eveningRecapLine}>
                Обещание дня: {engagement.dayGoal}
              </p>
            ) : zones.promise ? (
              <p className={styles.eveningRecapLine}>
                Обещание на сегодня ещё можно выбрать ниже — если хочется завершить день с маленьким шагом.
              </p>
            ) : (
              <p className={styles.eveningRecapLine}>Главная тема: {story.hero.themeShort}</p>
            )}
          </section>
        ) : null}

        {!useProductPersonalized && zones.evening ? (
          <div className={styles.eveningZone} data-testid="today-zone-evening-entry">
            <p className={styles.eveningHint}>{story.isEveningSurface ? copy.eveningRecapTitle : copy.eveningHint}</p>
            <button
              type="button"
              className={`orbit-button orbit-button-primary ${styles.eveningButton}`}
              data-testid="today-evening-open"
              onClick={onOpenEvening}
            >
              {copy.eveningCta}
            </button>
          </div>
        ) : null}

        {props.guideNarrativeLoading ? (
          <div className={styles.loadingInline} role="status" aria-live="polite">
            <LoadingSpinner size="sm" />
            <span className={styles.loadingText}>{copy.loadingDay}</span>
          </div>
        ) : null}
      </div>

      {ritualPickOpen === "tarot" ? (
        <div
          className={styles.pickOverlay}
          role="dialog"
          aria-modal="true"
          aria-label={copy.ritualTarotPendingTitle}
          data-testid="today-ritual-tarot-overlay"
        >
          <div className={styles.pickSheet}>
            <div data-testid="today-ritual-tarot-pick">{tarotPickExperience}</div>
            <button type="button" className={`orbit-button orbit-button-secondary ${styles.pickClose}`} onClick={() => setRitualPickOpen(null)}>
              Закрыть
            </button>
          </div>
        </div>
      ) : null}

      {ritualPickOpen === "number" ? (
        <div
          className={styles.pickOverlay}
          role="dialog"
          aria-modal="true"
          aria-label={copy.ritualNumberPendingTitle}
          data-testid="today-ritual-number-overlay"
        >
          <div className={styles.pickSheet}>
            <div data-testid="today-ritual-number-pick">{numberPickExperience}</div>
            <button type="button" className={`orbit-button orbit-button-secondary ${styles.pickClose}`} onClick={() => setRitualPickOpen(null)}>
              Закрыть
            </button>
          </div>
        </div>
      ) : null}

    </>
  );
}
