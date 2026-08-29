"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { RitualNumberPickExperience } from "@/components/today/ritual/RitualNumberPickExperience";
import { RitualTarotPickExperience } from "@/components/today/ritual/RitualTarotPickExperience";
import type { PracticeResponse } from "@/components/today/todayPageUtils";
import { TodayDayContinuityClosed } from "@/components/today/experience/TodayDayContinuityClosed";
import { TodayDayContinuityEveningClose } from "@/components/today/experience/TodayDayContinuityEveningClose";
import { TodayEveningProductClose } from "@/components/today/composition/TodayEveningProductClose";
import { TodayPersonalizedProductSection } from "@/components/today/composition/TodayPersonalizedProductSection";
import { TodayScreenBlock, TodayScreenBlockStack } from "@/components/today/composition/TodayScreenBlock";
import { TodayDayBrief } from "@/components/today/composition/TodayDayBrief";
import { buildTodayDayBriefModel } from "@/lib/todayDayBrief";
import { TodayMyDayRhythm } from "@/components/today/composition/TodayMyDayRhythm";
import { TodayRitualLensPair } from "@/components/today/composition/TodayRitualLensPair";
import { buildTodayInstructionBridgeModel, omitIfOverlapsHeadline } from "@/lib/todayInstructionBridge";
import { TodayDayTasksBlock } from "@/components/today/composition/TodayDayTasksBlock";
import { buildTodayDayTasks } from "@/lib/todayDayTasks";
import { TodayProgressTracker } from "@/components/today/composition/TodayProgressTracker";
import { TodayProductScreenFlow, todayHandoffIndices, todayScreenFlowPracticeIndex, todayScreenFlowReadingIndex, todayScreenFlowStepCount } from "@/components/today/composition/TodayProductScreenFlow";
import { TodayEveningGratitudeBlock } from "@/components/today/composition/TodayEveningGratitudeBlock";
import { TodayMyDayPane } from "@/components/today/composition/TodayMyDayPane";
import { pickMoveIfThenFromContract } from "@/lib/todayMoveIfThen";
import {
  resolveScreenFlowEntryIndex,
  type ScreenFlowChangeReason,
} from "@/design-system/primitives/ScreenFlow";
import { TarotPicture } from "@/components/tarot/TarotPicture";
import { LoadingSpinner } from "@/components/orbit";
import { HeroMedium } from "@/components/foundation/HeroMedium";
import { MotionReveal } from "@/design-system/motion/MotionReveal";
import { MOTION } from "@/design-system/motion/tokens";
import { buildTodayHeroPillars, buildTodayHeroSymbol, resolveTodaySunSignLabel } from "@/lib/todayHeroMedium";
import type { MorningRitualData, TodayCycleData } from "@/components/today/todayPageUtils";
import { anchorTarotTags, RITUAL_COPY } from "@/components/today/todayRitualCopy";
import { getTodayTarotCardRu } from "@/components/today/todayTarotCardsRu";
import { isDayNotReady, isTodayInterpretationUnavailable, type TodayContractV1, type TodayDepthTopicId } from "@/lib/todayContract";
import type { CoreProfile } from "@/lib/types";
import { tarotCardFacePicture, tarotCardFaceSrc, resolveDailyTarotDeckIndex } from "@/lib/tarotCardAssets";
import {
  buildMemorySlotCopy,
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
import {
  loadDayEngagement,
  mergeEngagementWithCompactUserModel,
  mergeEngagementWithDaySymbolState,
  saveDayEngagement,
  createEmptyDayEngagement,
  engagementProfileScope,
} from "@/lib/todayDayEngagement";
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
import { getTimeOfDayByHour } from "@/lib/time-of-day";
import {
  fetchDaySymbolState,
  revealDayCard,
  revealDayNumber,
  type DaySymbolPublicView,
} from "@/lib/daySymbolReveal";
import { TodayDayDialogueMorning } from "@/components/today/composition/TodayDayDialogueMorning";
import { ConversationThread } from "@/components/conversation/ConversationThread";
import { ConversationTurn } from "@/components/conversation/ConversationTurn";
import {
  FirstTodayReactionGate,
  firstTodayReactionComplete,
} from "@/components/today/composition/FirstTodayReactionGate";
import { TodayInterpretationConfirm } from "@/components/today/composition/TodayInterpretationConfirm";
import { TodaySkyStoryCards } from "@/components/today/composition/TodaySkyStoryCards";
import { TodayDayColorGuideSection } from "@/components/today/composition/TodayDayColorGuideSection";
import { TodayPracticeGiftBlock } from "@/components/today/composition/TodayPracticeGiftBlock";
import { TodayMakeYoursBlock } from "@/components/today/composition/TodayMakeYoursBlock";
import { TodayRecapAchievements } from "@/components/today/composition/TodayRecapAchievements";
import { TodayHookRevealShell } from "@/components/today/composition/TodayHookRevealShell";
import { StoryBlockCue, StoryNextAnchor } from "@/components/today/composition/TodayStoryDeckFrames";
import { isDayScenarioReadyForChapters } from "@/lib/todayScenarioChapters";
import { buildGlanceDayTexture, buildGlanceThemeEyebrow } from "@/lib/todayGlanceTexture";
import { buildGlanceDailyFocus } from "@/lib/todayDailyFocus";
import { pickPersonalFocusAxisLabel } from "@/lib/todayPersonalFocusAxis";
import { buildGlanceEnergyFromChorus } from "@/lib/todayGlanceEnergy";
import { buildPlotConflictNarrative, buildPlotStoryBeats } from "@/lib/todayPlotNarrative";
import { TODAY_NO_CONNECTION_COPY } from "@/lib/todaySlotAvailability";
import { TodayDepthLayerSection } from "@/components/today/composition/TodayDepthLayerSection";
import { buildTodayPromiseSuggestions, focusTopicLabel, isLowEnergyMood, shouldAskMorningFocus, shouldAskMorningMood } from "@/lib/todayDayDialogue";
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
import styles from "@/design-system/compositions/dsCompositionSurface.module.css";
import kitLayout from "@/design-system/compositions/dsCompositions.module.css";
import { DsButton, DsCard, DsListPanel, DsListRow, DsRitualGate, DsTarotFace } from "@/design-system";
import { DsTextField } from "@/design-system/primitives/DsForm";
import { joinClass } from "@/design-system/utils/joinClass";
import ds from "@/design-system/primitives/dsPrimitives.module.css";
import { getJson, postJson } from "@/lib/api";
import { PersonalizationDegradedBadge } from "@/components/product-ui/PersonalizationDegradedBadge";
import { buildDayEventsForNarrative } from "@/components/today/todayPageUtils";
import type { TodayRitualNarrativePayload } from "@/lib/todayNarrativeApi";
import {
  loadTodayGrowthTrackers,
  markAsceticCompletedToday,
  markHabitCompletedToday,
  type TodayProgressRow,
} from "@/lib/todayGrowthTrackers";
import { shiftDateISO } from "@/lib/moodMapModel";
import { resolveTodayDayColorGuide } from "@/lib/todayDayColorGuide";
import { canOfferFocusDeepen, resolveFocusDeepenTarget } from "@/lib/todayFocusDeepen";
import { formatRitualTarotPersonalToday, pickRitualPersonalLens } from "@/lib/ritualRevealCopy";
import { buildHandoffWelcomeGlass } from "@/lib/todayHandoffWelcome";
import { resolveWelcomeActivityTags } from "@/lib/todayWelcomeActivityTags";
import {
  buildMakeYoursProposals,
  makeYoursOccupiedFromProgress,
} from "@/lib/todayMakeYoursProposals";
import { syncDayPromiseToConnection } from "@/lib/todayPromiseSync";
import { pickTodayDepthMenu } from "@/lib/todayDepthMenuToday";
import {
  resolveTodayCapabilityFromProfile,
  TODAY_SCREEN_FLOW_CAPABILITY,
} from "@/lib/todayScreenFlowCapability";

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
  /** Auth/API transport degraded — personal acts must not render silent empty */
  networkDegraded?: boolean;
  dayLayerNarrativePayload?: Record<string, unknown> | null;
  dayLayerNarrativeLoading?: boolean;
  spheresNarrativePayload?: Record<string, unknown> | null;
  eveningNarrativePayload?: Record<string, unknown> | null;
  onRitualSpineComplete?: (ctx: TodayRitualNarrativePayload) => void;
  /** After First Today intent/reality chips — bias narrative / package. */
  onFirstTodayReactionComplete?: () => void;
  colorLine?: string | null;
  stoneLine?: string | null;
  coreProfile?: CoreProfile | null;
  onVisible?: () => void;
  onDayClosed?: () => void;
  /** When true, chrome is provided by TodayWebDashboard; only ritual/personalized blocks render. */
  embeddedInWebDashboard?: boolean;
  /** Day story is being rebuilt after symbol reveal — do not treat old text as updated. */
  dayStoryUpdating?: boolean;
  /** Parent guide generation id for deepen chain. */
  guideGenerationId?: number | null;
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
  const isEveningTime = useMemo(() => getTimeOfDayByHour() === "evening", []);
  const showEvening = eveningMode || isEveningTime;
  const [hydrated, setHydrated] = useState(false);
  const [reactionReady, setReactionReady] = useState(() =>
    typeof window === "undefined" ? !isFirstToday : !isFirstToday || firstTodayReactionComplete(),
  );
  const [continuityRecord, setContinuityRecord] = useState<DayContinuityRecord | null>(null);
  const [continuitySaving, setContinuitySaving] = useState(false);
  const [engagement, setEngagement] = useState(createEmptyDayEngagement);
  const [symbolHooksView, setSymbolHooksView] = useState<DaySymbolPublicView | null>(null);
  const [tarotPendingId, setTarotPendingId] = useState<number | null>(null);
  const [goalDraftOpen, setGoalDraftOpen] = useState(false);
  const [goalDraft, setGoalDraft] = useState("");
  const [recommendedPractice, setRecommendedPractice] = useState<PracticeResponse | null>(null);
  const [practiceCompleting, setPracticeCompleting] = useState(false);
  const [activeHabit, setActiveHabit] = useState<{ id: number; name: string } | null>(null);
  const [activeAscetic, setActiveAscetic] = useState<{ id: number; title: string } | null>(null);
  const [progressRows, setProgressRows] = useState<TodayProgressRow[]>([]);
  const [readingFocusSphere, setReadingFocusSphere] = useState<string | null>(null);
  const [preferredDepthTopic, setPreferredDepthTopic] = useState<TodayDepthTopicId | string | null>(null);
  const [autoPickDepthTopic, setAutoPickDepthTopic] = useState(false);
  const [habitMarking, setHabitMarking] = useState(false);
  const [asceticMarking, setAsceticMarking] = useState(false);
  const [ritualPickOpen, setRitualPickOpen] = useState<"tarot" | "number" | null>(null);
  const [portalReady, setPortalReady] = useState(false);
  const [screenFlowIndex, setScreenFlowIndex] = useState(0);
  const screenFlowEntryApplied = useRef(false);

  useEffect(() => {
    setPortalReady(true);
  }, []);

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

  const compositionTarotTags = useMemo(() => {
    const fromSymbols =
      symbolHooksView?.card?.hook_reveal?.base?.keywords ?? symbolHooksView?.card?.keywords ?? null;
    const fromMorning =
      props.morningRitualData?.tarot_card?.keywords ??
      props.morningRitualData?.tarot_explanation?.keywords ??
      null;
    const kws = Array.isArray(fromSymbols) && fromSymbols.length ? fromSymbols : fromMorning;
    return anchorTarotTags(Array.isArray(kws) ? kws : []);
  }, [
    symbolHooksView?.card?.hook_reveal?.base?.keywords,
    symbolHooksView?.card?.keywords,
    props.morningRitualData?.tarot_card?.keywords,
    props.morningRitualData?.tarot_explanation?.keywords,
  ]);

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
      decisionStyle: props.coreProfile?.profile_contract_v1?.decision_style ?? null,
      helpsFirst: props.coreProfile?.profile_contract_v1?.helps?.[0] ?? null,
      guideNarrativePayload: props.guideNarrativePayload ?? null,
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

  const useProductFoundation = !isFirstToday || reactionReady;
  const useLegacyStackedPath = !isFirstToday && !useProductFoundation;
  /** Day reading opens when scenario is ready — ritual complements, does not unlock. */
  const dayReadingReady =
    useProductFoundation &&
    (isDayScenarioReadyForChapters(props.contract) || story.personalizedReady);
  /**
   * Handoff v3.3: full 12-step presentation whenever foundation is on.
   * Content houses still honest-omit; we do not wait for day_scenario to start Priority→….
   * `dayReadingReady` remains for deepen / reading-specific slots.
   */
  const useProductPersonalized = useProductFoundation;
  const showRitualAsComplement = useProductFoundation && !story.personalizedReady;

  const showSymbolsAct = Boolean(
    useProductFoundation &&
      (showRitualAsComplement ||
        ((story.tarotImpact || story.numberImpact) && story.personalizedReady)),
  );
  const capabilityDepth = resolveTodayCapabilityFromProfile({
    authenticated: isAuthenticated,
    coreProfile: props.coreProfile,
  });
  const screenCapability = TODAY_SCREEN_FLOW_CAPABILITY[capabilityDepth];
  const showMyDayAct = useProductFoundation && screenCapability.myDay;
  const showPersonalTimeline = showMyDayAct && screenCapability.personalTimeline;
  const screenFlowLayout = useMemo(
    () => ({ showSymbols: showSymbolsAct, showMyDay: showMyDayAct, showEvening }),
    [showSymbolsAct, showMyDayAct, showEvening],
  );

  useEffect(() => {
    if (!useProductFoundation || screenFlowEntryApplied.current) return;
    screenFlowEntryApplied.current = true;
    if (typeof window === "undefined") return;
    const sp = new URLSearchParams(window.location.search);
    const stepCount = todayScreenFlowStepCount({
      showSymbols: showSymbolsAct,
      showMyDay: showMyDayAct,
      showEvening,
    });
    setScreenFlowIndex(resolveScreenFlowEntryIndex({ searchParams: sp, stepCount }));
  }, [useProductFoundation, showSymbolsAct, showMyDayAct, showEvening]);

  const onScreenFlowIndexChange = useCallback(
    (index: number, meta: { reason: ScreenFlowChangeReason }) => {
      setScreenFlowIndex(index);
      trackMeaningEvent({
        event_type: "screen_flow_step_reached",
        event_source: "today",
        local_date: dateISO,
        payload: { index, reason: meta.reason, surface: "today_screen_flow" },
        idempotency_key: `screen_flow_step_reached:${dateISO}:${index}:${meta.reason}`,
        refreshRings: false,
      });
    },
    [dateISO, trackMeaningEvent],
  );

  const goToNextFromToday = useCallback(() => {
    const idx = todayHandoffIndices(screenFlowLayout);
    const next =
      idx.ritual >= 0 ? idx.ritual : idx.myDay >= 0 ? idx.myDay : idx.evening >= 0 ? idx.evening : 0;
    onScreenFlowIndexChange(next, { reason: "select" });
  }, [onScreenFlowIndexChange, screenFlowLayout]);

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

  // Legacy peak/caution sphere grid — removed (TODAY_SCREEN_V1 R15–R17). Daily Focus lives on Glance.
  const showContextPanel = false;

  const showSkyCards = zones.astroContext && story.skyCards.length > 0;
  // Color lives in the sky summary grid (tap to expand) — never also as a full sibling card.
  const colorInSkyGrid = story.skyCards.some((c) => c.id === "color");
  const showColorGuide =
    zones.glance && Boolean(story.colorGuide) && !colorInSkyGrid && !showSkyCards;

  const promiseSuggestions = useMemo(
    () =>
      buildTodayPromiseSuggestions({
        primaryAction: props.contract.primary_action,
        focusTopicId: engagement.focusTopicId,
        developmentPoint: props.contract.personal_growth.development_point,
        todayMove: props.contract.day_story?.today_move,
        doItems: props.contract.day_story?.do ?? null,
      }),
    [
      props.contract.primary_action,
      props.contract.personal_growth.development_point,
      props.contract.day_story?.today_move,
      props.contract.day_story?.do,
      engagement.focusTopicId,
    ],
  );

  const strengthenTools = useMemo(
    () =>
      applyRecommendedPracticeToStrengthen(
        dayReadingReady ? story.strengthenLinked : story.strengthenPreview,
        dayReadingReady ? recommendedPractice : null,
        {
          lowEnergy: isLowEnergyMood(engagement.morningMoodId),
        },
      ),
    [
      dayReadingReady,
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
  const affirmationTool = useMemo(
    () => strengthenTools.find((tool) => tool.id === "affirmation") ?? null,
    [strengthenTools],
  );
  const supportTools = useMemo(
    () => strengthenTools.filter((tool) => tool.id !== "practice"),
    [strengthenTools],
  );

  const practiceRec = props.contract.day_story?.practice_recommendation;
  const preferAffirmationSlot = useMemo(() => {
    const key = dateISO || "0";
    let h = 0;
    for (let i = 0; i < key.length; i += 1) h = (h * 31 + key.charCodeAt(i)) >>> 0;
    return h % 2 === 1;
  }, [dateISO]);
  const showAffirmationSupport = Boolean(
    (practiceRec?.kind === "affirmation" && practiceRec.text) || affirmationTool,
  );
  const showPracticeSupport = Boolean(practiceTool || (practiceRec?.kind === "practice" && practiceRec.text));
  const supportSlot: "affirmation" | "practice" | null =
    showAffirmationSupport && showPracticeSupport
      ? preferAffirmationSlot
        ? "affirmation"
        : "practice"
      : showAffirmationSupport
        ? "affirmation"
        : showPracticeSupport
          ? "practice"
          : null;

  const practiceFrameTitle =
    supportSlot === "affirmation"
      ? (practiceRec?.kind === "affirmation" && practiceRec.text) || affirmationTool?.title || null
      : supportSlot === "practice"
        ? practiceTool?.title || (practiceRec?.kind === "practice" ? practiceRec.text : null) || null
        : null;
  const practiceFrameMeta =
    supportSlot === "practice"
      ? practiceTool?.duration || (practiceRec?.kind === "practice" ? practiceRec.reason : null) || null
      : supportSlot === "affirmation"
        ? (practiceRec?.kind === "affirmation" ? practiceRec.reason : null) || null
        : null;
  const practiceFrameCompleted =
    supportSlot === "affirmation" ? engagement.affirmationRead : engagement.practiceCompleted;
  const practiceFrameActionLabel =
    supportSlot === "affirmation"
      ? copy.markAffirmationDone
      : engagement.practiceStarted
        ? copy.practiceComplete
        : copy.practiceStart;

  const moveIfThen = useMemo(() => pickMoveIfThenFromContract(props.contract), [props.contract]);

  const prevContinuity = useMemo(() => {
    if (!hydrated) return null;
    return loadPreviousDayContinuity(dateISO);
  }, [hydrated, dateISO]);
  const memorySlot = useMemo(() => buildMemorySlotCopy(prevContinuity), [prevContinuity]);
    /** Only filled yesterday recall — never ship developer stub copy. */
  const showMemorySlot = hydrated && !isFirstToday && memorySlot.state === "filled";

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

  /** Server SoT for card+number — restores ritual across devices / fresh browsers. */
  useEffect(() => {
    if (!hydrated) return;
    let cancelled = false;
    const onReveal = props.onSymbolRevealResult;
    void fetchDaySymbolState(isAuthenticated)
      .then((view) => {
        if (cancelled || !view) return;
        setSymbolHooksView(view);
        setEngagement((prev) => {
          const merged = mergeEngagementWithDaySymbolState(prev, view, (id) => getTodayTarotCardRu(id)?.nameRu);
          if (
            merged.tarotPickedId === prev.tarotPickedId &&
            merged.tarotPickedName === prev.tarotPickedName &&
            merged.tarotOrientation === prev.tarotOrientation &&
            merged.numberConfirmed === prev.numberConfirmed
          ) {
            return prev;
          }
          saveDayEngagement(dateISO, merged, engagementProfileKey);
          return merged;
        });
        if (view.card?.revealed || view.number?.revealed) {
          const rawId = view.card?.id;
          const cardId =
            typeof rawId === "number"
              ? rawId
              : typeof rawId === "string" && Number.isFinite(Number(rawId))
                ? Number(rawId)
                : null;
          const base =
            loadRitualPersisted(dateISO) ??
            ({
              opened: true,
              numberRevealed: false,
              mood: null,
              headTopic: null,
              essentials: {},
              honestStep: null,
              numberRhythm: null,
              tarotMainId: null,
              tarotClarifierId: null,
              tarotApplied: false,
              tarotContinueAck: false,
              checkInSubmitted: false,
            } satisfies RitualPersistedState);
          saveRitualPersisted(dateISO, {
            ...base,
            opened: true,
            tarotMainId: cardId ?? base.tarotMainId,
            tarotApplied: Boolean(view.card?.revealed) || base.tarotApplied,
            tarotContinueAck: Boolean(view.card?.revealed) || base.tarotContinueAck,
            numberRevealed: Boolean(view.number?.revealed) || base.numberRevealed,
          });
        }
        onReveal?.(view);
      })
      .catch(() => {
        /* offline / guest sealed — keep local engagement */
      });
    return () => {
      cancelled = true;
    };
    // Intentionally omit onSymbolRevealResult identity — parent may recreate it each render.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- hydrate once per day/auth scope
  }, [hydrated, dateISO, engagementProfileKey, isAuthenticated]);

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
    if (!hydrated) return;
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
  }, [hydrated, dateISO]);

  const refreshGrowthTrackers = useCallback(async () => {
    if (!isAuthenticated) {
      setActiveHabit(null);
      setActiveAscetic(null);
      setProgressRows([]);
      return;
    }
    const trackers = await loadTodayGrowthTrackers(dateISO);
    setActiveHabit(trackers.habit);
    setActiveAscetic(trackers.ascetic);
    setProgressRows(trackers.progressRows);
    const patch: Parameters<typeof saveDayEngagement>[1] = {};
    if (trackers.habitDoneToday && trackers.habit) {
      patch.habitMarkedId = trackers.habit.id;
    }
    if (trackers.asceticDoneToday && trackers.ascetic) {
      patch.asceticMarkedId = trackers.ascetic.id;
    }
    if (Object.keys(patch).length > 0) {
      persistEngagement(patch);
    }
  }, [dateISO, isAuthenticated, persistEngagement]);

  useEffect(() => {
    if (!hydrated || !isAuthenticated) {
      setActiveHabit(null);
      setActiveAscetic(null);
      setProgressRows([]);
      return;
    }
    let cancelled = false;
    void loadTodayGrowthTrackers(dateISO).then((trackers) => {
      if (cancelled) return;
      setActiveHabit(trackers.habit);
      setActiveAscetic(trackers.ascetic);
      setProgressRows(trackers.progressRows);
      const patch: Parameters<typeof saveDayEngagement>[1] = {};
      if (trackers.habitDoneToday && trackers.habit) {
        patch.habitMarkedId = trackers.habit.id;
      }
      if (trackers.asceticDoneToday && trackers.ascetic) {
        patch.asceticMarkedId = trackers.ascetic.id;
      }
      if (Object.keys(patch).length > 0) {
        persistEngagement(patch);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [hydrated, isAuthenticated, dateISO, persistEngagement]);

  useEffect(() => {
    if (isFirstToday && !reactionReady) return;
    onVisible?.();
    if (!engagement.todayOpened) {
      persistEngagement({ todayOpened: true });
    }
  }, [onVisible, engagement.todayOpened, persistEngagement, isFirstToday, reactionReady]);

  const onReactionGateComplete = useCallback(() => {
    setReactionReady(true);
    props.onFirstTodayReactionComplete?.();
  }, [props.onFirstTodayReactionComplete]);

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
        orientation: engagement.tarotOrientation ?? undefined,
        isAuthenticated,
        source: "today_ritual",
        idempotencyKey: `tarot_reveal:${dateISO}:${id}:${isAuthenticated ? "u" : "g"}`,
      })
        .then((view) => {
          setSymbolHooksView(view);
          const orient =
            view.card?.orientation === "reversed"
              ? "reversed"
              : view.card?.orientation === "upright"
                ? "upright"
                : null;
          if (orient) persistEngagement({ tarotOrientation: orient });
          props.onSymbolRevealResult?.(view);
        })
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
    [
      dateISO,
      engagement.tarotOrientation,
      isAuthenticated,
      persistEngagement,
      props.onSymbolRevealResult,
      trackMeaningEvent,
    ],
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
    // ScreenFlow order is Number → Card; do not reopen number after card.
  }, [anchorTarotId, dateISO, engagement.tarotPickedId, persistEngagement, props.cardName, tarotPendingId]);

  const onNumberComplete = useCallback(() => {
    persistEngagement({ numberConfirmed: true });
    setRitualPickOpen(null);
    trackMeaningEvent({
      event_type: "number_selected",
      event_source: "today",
      local_date: dateISO,
      payload: { surface: "today_day_story_v3", experience_inline: true },
      refreshRings: false,
    });
  }, [dateISO, persistEngagement, trackMeaningEvent]);

  // Persist revealed digit so interpretation stays available if morning patch lags.
  const onNumberRevealRequest = useCallback(async () => {
    const view = await revealDayNumber({
      isAuthenticated,
      source: "today_ritual",
      idempotencyKey: `number_reveal:${dateISO}:${isAuthenticated ? "u" : "g"}`,
    });
    setSymbolHooksView(view);
    props.onSymbolRevealResult?.(view);
    const value = view.number?.value ?? view.number?.reduced_value;
    const display = value != null ? String(value) : "";
    if (display && display !== "—") {
      persistEngagement({ numberValue: display });
    }
    return {
      display,
      title: view.number?.title ?? null,
      meaning: view.number?.hook_reveal?.base?.meaning ?? view.number?.summary ?? props.numerologyMeaning ?? null,
      support: pickRitualPersonalLens(view.number?.hook_reveal, showMyDayAct),
    };
  }, [
    dateISO,
    isAuthenticated,
    persistEngagement,
    props.numerologyMeaning,
    props.onSymbolRevealResult,
    showMyDayAct,
  ]);

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
    void syncDayPromiseToConnection(dateISO, trimmed);
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

  const onPickPromise = useCallback(
    (text: string) => {
      const trimmed = text.replace(/\s+/g, " ").trim();
      if (!trimmed) return;
      persistEngagement({ dayGoal: trimmed });
      void syncDayPromiseToConnection(dateISO, trimmed);
      trackMeaningEvent({
        event_type: "action_option_selected",
        event_source: "today",
        local_date: dateISO,
        payload: {
          action: "day_promise_set",
          promise_text: trimmed.slice(0, 200),
          surface: "today_handoff_promise",
        },
        refreshRings: false,
      });
    },
    [dateISO, persistEngagement, trackMeaningEvent],
  );

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
      const trackers = await loadTodayGrowthTrackers(dateISO);
      setProgressRows(trackers.progressRows);
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

  const onNearestSelect = useCallback(
    (item: { driver_id: string; label_short: string; time_local: string }) => {
      trackMeaningEvent({
        event_type: "action_option_selected",
        event_source: "today",
        local_date: dateISO,
        payload: {
          action: "glance_nearest_practice",
          driver_id: item.driver_id,
          label_short: item.label_short.slice(0, 80),
          time_local: item.time_local,
          practice_id: recommendedPractice?.id ?? null,
          surface: "today_glance_nearest",
        },
        refreshRings: false,
      });
      if (recommendedPractice?.id) {
        if (typeof window !== "undefined") {
          window.location.assign(`/practices/${recommendedPractice.id}`);
        }
        return;
      }
      if (useProductPersonalized) {
        const practiceIndex = todayScreenFlowPracticeIndex(showSymbolsAct, showMyDayAct, showEvening);
        if (practiceIndex >= 0) setScreenFlowIndex(practiceIndex);
      }
    },
    [
      dateISO,
      onPracticeAction,
      recommendedPractice?.id,
      showSymbolsAct,
      showMyDayAct,
      showEvening,
      trackMeaningEvent,
      useProductPersonalized,
    ],
  );

  const onAffirmationDone = useCallback(() => {
    if (engagement.affirmationRead) return;
    persistEngagement({ affirmationRead: true });
    trackMeaningEvent({
      event_type: "affirmation_done",
      event_source: "today",
      local_date: dateISO,
      payload: { surface: "today_day_story_v3" },
      refreshRings: true,
    });
  }, [dateISO, engagement.affirmationRead, persistEngagement, trackMeaningEvent]);

  const onHabitMark = useCallback(async () => {
    if (!activeHabit || engagement.habitMarkedId === activeHabit.id || habitMarking) return;
    try {
      setHabitMarking(true);
      await markHabitCompletedToday(activeHabit.id, dateISO);
      persistEngagement({ habitMarkedId: activeHabit.id });
      void refreshGrowthTrackers();
      trackMeaningEvent({
        event_type: "habit_completed",
        event_source: "today",
        local_date: dateISO,
        payload: { habit_id: activeHabit.id, surface: "today_day_story_v3" },
        refreshRings: true,
      });
    } catch {
      /* retry */
    } finally {
      setHabitMarking(false);
    }
  }, [
    activeHabit,
    dateISO,
    engagement.habitMarkedId,
    habitMarking,
    persistEngagement,
    refreshGrowthTrackers,
    trackMeaningEvent,
  ]);

  const onAsceticMark = useCallback(async () => {
    if (!activeAscetic || engagement.asceticMarkedId === activeAscetic.id || asceticMarking) return;
    try {
      setAsceticMarking(true);
      await markAsceticCompletedToday(activeAscetic.id, dateISO);
      persistEngagement({ asceticMarkedId: activeAscetic.id });
      void refreshGrowthTrackers();
      trackMeaningEvent({
        event_type: "ascetic_step_done",
        event_source: "today",
        local_date: dateISO,
        payload: { contract_id: activeAscetic.id, surface: "today_day_story_v3" },
        refreshRings: true,
      });
    } catch {
      /* retry */
    } finally {
      setAsceticMarking(false);
    }
  }, [
    activeAscetic,
    asceticMarking,
    dateISO,
    engagement.asceticMarkedId,
    persistEngagement,
    refreshGrowthTrackers,
    trackMeaningEvent,
  ]);

  const dayClosed = isDayContinuityClosed(continuityRecord);
  const todayHeroSymbol = useMemo(() => buildTodayHeroSymbol(props.coreProfile), [props.coreProfile]);
  const todayHeroPillars = useMemo(() => buildTodayHeroPillars(props.coreProfile), [props.coreProfile]);
  const interpretationUnavailable = isTodayInterpretationUnavailable(props.contract);
  const themeLoading =
    !singleVoice &&
    !interpretationUnavailable &&
    props.guideNarrativeLoading &&
    !props.guideNarrativePayload;

  const dayTexture = useMemo(() => buildGlanceDayTexture(props.contract), [props.contract]);
  const glanceDailyFocus = useMemo(
    () => buildGlanceDailyFocus(props.contract, props.guideNarrativePayload ?? null),
    [props.contract, props.guideNarrativePayload],
  );
  const instructionBridge = useMemo(
    () => buildTodayInstructionBridgeModel(props.contract),
    [props.contract],
  );
  const glanceEnergy = useMemo(() => buildGlanceEnergyFromChorus(props.contract), [props.contract]);
  const plotNarrative = useMemo(() => buildPlotConflictNarrative(props.contract), [props.contract]);
  const plotBeats = useMemo(() => buildPlotStoryBeats(props.contract), [props.contract]);
  const energyLineDisplay = glanceEnergy?.effect || pulseDisplay;
  const energyCauseDisplay = glanceEnergy?.cause || null;

  const welcomeGlass = useMemo(() => {
    const nest = props.contract.welcome_glass;
    if (nest && (nest.mood_tags?.length || nest.reason || nest.good_for?.length)) {
      return {
        moodPills: (nest.mood_tags ?? []).slice(0, 2),
        reasonLine: nest.reason?.trim() || null,
        activityTags: (nest.good_for ?? []).slice(0, 3),
      };
    }
    const lunarRaw = props.morningRitualData?.celestial_events?.lunar_phase as
      | { name?: string; themes?: string; guidance?: string; phase_name?: string }
      | undefined;
    const lunarName = lunarRaw?.name || lunarRaw?.phase_name || null;
    const activityTags = resolveWelcomeActivityTags({
      contract: props.contract,
      morningPriorities: props.morningRitualData?.daily_recommendations?.priorities,
    });
    return buildHandoffWelcomeGlass({
      visualMode: props.contract.day_atmosphere?.visual_mode ?? null,
      lunarName,
      lunarThemes: lunarRaw?.themes ?? null,
      lunarGuidance: lunarRaw?.guidance ?? null,
      activityTags,
    });
  }, [props.contract, props.morningRitualData]);

  const progressRowsFromContract = useMemo((): TodayProgressRow[] | null => {
    const nest = props.contract.today_progress;
    if (!nest || !Array.isArray(nest.rows) || nest.rows.length === 0) return null;
    return nest.rows.map((row) => {
      const daysBool = Array.isArray(row.days_bool) ? row.days_bool.slice(0, 7) : [];
      while (daysBool.length < 7) daysBool.push(false);
      const window = daysBool.map((completed, i) => ({
        dateISO: shiftDateISO(dateISO, i - (daysBool.length - 1)),
        completed: Boolean(completed),
        isFuture: false,
      }));
      return {
        id: row.id,
        kind: (row.kind === "ascetic" || row.kind === "practice" ? row.kind : "habit") as TodayProgressRow["kind"],
        kindLabel: row.kind_label || row.kind,
        name: row.name,
        streakDays: Number(row.streak_days) || 0,
        days: window,
      };
    });
  }, [props.contract.today_progress, dateISO]);

  const depthMenuTopics = useMemo(() => {
    const menu = props.contract.depth_layer?.menu;
    if (!Array.isArray(menu)) return [] as string[];
    return menu.map((row) => String(row.topic || "").trim()).filter(Boolean);
  }, [props.contract.depth_layer?.menu]);

  const todayDepthLayerForFocus = useMemo(() => {
    const layer = props.contract.depth_layer;
    if (!layer || !Array.isArray(layer.menu) || layer.menu.length === 0) return null;
    const menu = pickTodayDepthMenu(layer.menu, props.contract);
    if (!menu.length) return null;
    return { ...layer, menu };
  }, [props.contract]);

  const showFocusDeepenCta = canOfferFocusDeepen({
    hasReading: useProductPersonalized,
    depthMenuTopics,
    focusTopicId: engagement.focusTopicId,
  });

  const onFocusDeepen = useCallback(() => {
    const target = resolveFocusDeepenTarget(engagement.focusTopicId, depthMenuTopics);
    setReadingFocusSphere(target.readingSphere);
    setPreferredDepthTopic(target.depthTopic);
    setAutoPickDepthTopic(Boolean(target.depthTopic));
    if (useProductPersonalized) {
      const readingIndex = todayScreenFlowReadingIndex(showSymbolsAct, showMyDayAct, showEvening);
      if (readingIndex >= 0) setScreenFlowIndex(readingIndex);
    } else {
      document
        .querySelector('[data-testid="today-depth-layer"]')
        ?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
    trackMeaningEvent({
      event_type: "focus_deepen_open",
      event_source: "today",
      local_date: dateISO,
      payload: {
        focus_topic_id: target.focusTopicId,
        reading_sphere: target.readingSphere,
        depth_topic: target.depthTopic,
        surface: "today_day_dialogue_v1",
      },
      refreshRings: false,
    });
  }, [
    dateISO,
    depthMenuTopics,
    engagement.focusTopicId,
    showSymbolsAct,
    showMyDayAct,
    showEvening,
    trackMeaningEvent,
    useProductPersonalized,
  ]);

  const ritualTarotMeaningText = useMemo(
    () =>
      symbolHooksView?.card?.hook_reveal?.base?.meaning ??
      props.cardMeaning ??
      story.tarotImpact?.body ??
      null,
    [props.cardMeaning, story.tarotImpact?.body, symbolHooksView?.card?.hook_reveal?.base?.meaning],
  );

  const ritualTarotPersonalText = useMemo(() => {
    const personalLine = pickRitualPersonalLens(symbolHooksView?.card?.hook_reveal, showMyDayAct);
    return formatRitualTarotPersonalToday({
      personalLine,
      dayNumber: engagement.numberValue || props.numerologyValue,
      dayNumberTitle: symbolHooksView?.number?.title ?? null,
    });
  }, [
    engagement.numberValue,
    props.numerologyValue,
    showMyDayAct,
    symbolHooksView?.card?.hook_reveal,
    symbolHooksView?.number?.title,
  ]);

  const ritualNumberMeaningText = useMemo(
    () =>
      symbolHooksView?.number?.hook_reveal?.base?.meaning ??
      symbolHooksView?.number?.summary ??
      props.numerologyMeaning ??
      story.numberImpact?.body ??
      null,
    [
      props.numerologyMeaning,
      story.numberImpact?.body,
      symbolHooksView?.number?.hook_reveal?.base?.meaning,
      symbolHooksView?.number?.summary,
    ],
  );

  const ritualNumberSupportText = useMemo(
    () => pickRitualPersonalLens(symbolHooksView?.number?.hook_reveal, showMyDayAct),
    [showMyDayAct, symbolHooksView?.number?.hook_reveal],
  );

  const ritualNumberTitle = useMemo(
    () => symbolHooksView?.number?.title ?? story.numberImpact?.headline ?? null,
    [story.numberImpact?.headline, symbolHooksView?.number?.title],
  );

  const makeYoursOccupied = useMemo(
    () =>
      makeYoursOccupiedFromProgress(
        (progressRowsFromContract ?? progressRows).map((r) => r.kind),
        {
          // Goal slot mirrors Promise until weekly-goal streak SoT exists.
          goal: Boolean(engagement.dayGoal?.trim()),
        },
      ),
    [progressRowsFromContract, progressRows, engagement.dayGoal],
  );

  const makeYoursProposals = useMemo(
    () =>
      buildMakeYoursProposals({
        contract: props.contract,
        occupied: makeYoursOccupied,
        dayGoal: engagement.dayGoal,
        promiseSuggestion: promiseSuggestions[0]?.text ?? null,
      }),
    [props.contract, makeYoursOccupied, engagement.dayGoal, promiseSuggestions],
  );

  const askMorningFocus = shouldAskMorningFocus({
    dateISO,
    focusTopicId: engagement.focusTopicId,
    focusTopicCapturedAtMs: engagement.focusTopicCapturedAtMs,
  });
  const askMorningMood = shouldAskMorningMood({
    dateISO,
    morningMoodId: engagement.morningMoodId,
    morningMoodCapturedAtMs: engagement.morningMoodCapturedAtMs,
  });

  // Priority step removed in v3.4 six blocks — no auto-advance from dialogue.

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
          activeHabit={activeHabit}
          activeAscetic={activeAscetic}
          habitMarked={engagement.habitMarkedId != null && activeHabit != null && engagement.habitMarkedId === activeHabit.id}
          asceticMarked={
            engagement.asceticMarkedId != null &&
            activeAscetic != null &&
            engagement.asceticMarkedId === activeAscetic.id
          }
          onHabitEveningDone={() => void onHabitMark()}
          onAsceticEveningDone={() => void onAsceticMark()}
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

  const morningDialogue =
    askMorningFocus || askMorningMood ? (
      <TodayDayDialogueMorning
        dateISO={dateISO}
        morningMoodId={engagement.morningMoodId}
        morningMoodCapturedAtMs={engagement.morningMoodCapturedAtMs}
        focusTopicId={engagement.focusTopicId}
        focusTopicCapturedAtMs={engagement.focusTopicCapturedAtMs}
        showDeepenCta={false}
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
          if (useProductPersonalized) {
            const myDayIndex = todayHandoffIndices(screenFlowLayout).instruction;
            if (myDayIndex >= 0) setScreenFlowIndex(myDayIndex);
          }
        }}
      />
    ) : null;

  const greetingParts = splitSalutation(story.greeting.salutation);
  // Glance expect/trap only when personalized narrative is not showing the same slots.
  const showGlance =
    zones.glance &&
    (story.glance.supported.length > 0 || story.glance.helpful.length > 0) &&
    !(useProductFoundation && story.personalizedReady);

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
      {/* Foundation path: date lives in topRow / dashboard chrome — avoid a second date line. */}
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
    <TodayScreenBlock testId="today-zone-pulse">
      {props.dayStoryUpdating ? (
        <p className={styles.pulseText} data-testid="today-day-story-updating" aria-live="polite">
          Обновляем описание дня…
        </p>
      ) : pulseDisplay ? (
        <p className={styles.pulseText}>{pulseDisplay}</p>
      ) : null}
      {story.ritualUnlockHint && !story.personalizedReady ? (
        <p className={styles.ritualUnlockHint}>{story.ritualUnlockHint}</p>
      ) : null}
    </TodayScreenBlock>
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

  const heroTheme =
    (story.hero.themeShort || story.hero.centralThought || "").replace(/[.!?]+$/u, "").trim();
  const heroSublineRaw = (story.hero.centralThought || "").replace(/[.!?]+$/u, "").trim();
  const heroSubline =
    heroTheme && heroSublineRaw && heroSublineRaw.toLowerCase() !== heroTheme.toLowerCase()
      ? story.hero.centralThought
      : null;

  const glanceEyebrow =
    buildGlanceThemeEyebrow(props.contract) || heroTheme || story.hero.centralThought || copy.themeLabel;

  const insightHeroText =
    plotBeats.find((b) => b.role === "turn")?.body ||
    plotNarrative?.why ||
    dayTexture ||
    null;

  const plotBeatsForStory = insightHeroText
    ? plotBeats.filter((b) => b.body !== insightHeroText)
    : plotBeats;

  const plotNarrativeSection =
    plotBeatsForStory.length > 0 ? (
      <section className={styles.plotStory} data-testid="today-zone-plot-narrative">
        <p className={styles.plotNarrativeEyebrow}>{copy.conflictLabel}</p>
        <div className={styles.plotBeats} data-testid="today-plot-beats">
          {plotBeatsForStory.map((beat) => (
            <article
              key={beat.id}
              className={styles.plotBeat}
              data-beat-role={beat.role}
              data-testid={`today-plot-beat-${beat.role}`}
            >
              <p className={styles.plotBeatLabel}>{beat.label}</p>
              <p className={styles.plotBeatBody}>{beat.body}</p>
            </article>
          ))}
        </div>
        {plotNarrative?.personal ? (
          <p className={styles.plotNarrativePersonal} data-testid="today-plot-personal">
            {plotNarrative.personal}
          </p>
        ) : null}
      </section>
    ) : plotNarrative && plotNarrative.why !== insightHeroText ? (
      <section className={styles.plotStory} data-testid="today-zone-plot-narrative">
        <p className={styles.plotNarrativeEyebrow}>{copy.conflictLabel}</p>
        {plotNarrative.tension ? (
          <p className={styles.plotNarrativeTension} data-testid="today-plot-tension">
            {plotNarrative.tension}
          </p>
        ) : null}
        {plotNarrative.why ? (
          <p className={styles.plotNarrativeWhy} data-testid="today-plot-why">
            {plotNarrative.why}
          </p>
        ) : null}
        {plotNarrative.personal ? (
          <p className={styles.plotNarrativePersonal} data-testid="today-plot-personal">
            {plotNarrative.personal}
          </p>
        ) : null}
      </section>
    ) : plotNarrative?.personal ? (
      <section className={styles.plotStory} data-testid="today-zone-plot-narrative">
        <p className={styles.plotNarrativePersonal} data-testid="today-plot-personal">
          {plotNarrative.personal}
        </p>
      </section>
    ) : null;

  const heroSection = zones.hero ? (
    useProductFoundation ? (
      <section className={styles.plotHero} data-testid="today-zone-hero">
        {themeLoading ? (
          <p className={styles.themeDarkLoading}>{copy.loadingDay}</p>
        ) : plotNarrative ? (
          <>
            <PersonalizationDegradedBadge
              contract={props.contract}
              narrativeRequestFailed={props.guideNarrativeRequestFailed}
            />
            <p className={styles.plotNarrativeEyebrow} id="today-day-theme-title">
              {copy.journey.actNavPlot}
            </p>
            <span className={styles.plotQuoteMark} aria-hidden>
              “
            </span>
          </>
        ) : (
          <>
            <PersonalizationDegradedBadge
              contract={props.contract}
              narrativeRequestFailed={props.guideNarrativeRequestFailed}
            />
            <h2
              id="today-day-theme-title"
              className={styles.themeDarkTitle}
              data-testid="today-entity-daily-theme"
            >
              {heroTheme || story.hero.centralThought}
            </h2>
            {heroSubline ? <p className={styles.themeDarkSubline}>{heroSubline}</p> : null}
          </>
        )}
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
          title={heroTheme || story.hero.centralThought}
          subline={heroSubline ?? undefined}
          symbol={todayHeroSymbol}
          pillars={todayHeroPillars}
          ariaLabel={heroTheme || story.hero.centralThought || copy.themeLabel}
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

  const tarotPickedId = engagement.tarotPickedId;

  const tarotPickExperience = (
    <RitualTarotPickExperience
      anchorCardId={anchorTarotId}
      resumeCommittedId={tarotPendingId ?? tarotPickedId}
      cardTitleRu={getTodayTarotCardRu(anchorTarotId)?.nameRu ?? props.cardName}
      tagLabels={compositionTarotTags}
      meaningText={ritualTarotMeaningText}
      personalTodayText={ritualTarotPersonalText}
      onCommitMain={onTarotCommit}
      onRevealed={onTarotRevealed}
      onContinue={onTarotContinue}
      reduceMotion={reduceMotion}
      startAtGrid
      allowSkipAnimation={false}
      gridSize={12}
    />
  );

  const numberPickExperience = (
    <RitualNumberPickExperience
      systemDisplay={engagement.numberValue || props.numerologyValue}
      numberTitle={ritualNumberTitle}
      numberMeaning={ritualNumberMeaningText}
      daySupport={ritualNumberSupportText}
      tileMode="symbol"
      reduceMotion={reduceMotion}
      onRevealRequest={onNumberRevealRequest}
      onComplete={onNumberComplete}
      alreadyConfirmed={Boolean(engagement.numberConfirmed)}
    />
  );

  const handoffEveningBody = (
    <TodayEveningGratitudeBlock
      dateISO={dateISO}
      manifestVersion={
        typeof props.contract.day_package_manifest?.today_contract_version === "string"
          ? props.contract.day_package_manifest.today_contract_version
          : null
      }
      onSaved={() => {
        trackMeaningEvent({
          event_type: "evening_reflection_submitted",
          event_source: "today",
          local_date: dateISO,
          payload: {
            surface: "today_screen_flow",
            kind: "gratitude",
            manifest_version: props.contract.day_package_manifest?.today_contract_version ?? null,
          },
          refreshRings: false,
        });
        onDayClosed?.();
      }}
    />
  );

  const displayProgressRows = progressRowsFromContract ?? progressRows;

  const handoffMakeYoursBody = (
    <TodayMakeYoursBlock
      dateISO={dateISO}
      progressRows={displayProgressRows}
      proposals={makeYoursProposals}
      occupiedCategoryIds={Object.keys(makeYoursOccupied).filter(
        (id) => makeYoursOccupied[id as keyof typeof makeYoursOccupied],
      )}
      onChanged={() => void refreshGrowthTrackers()}
    />
  );

  const handoffColorGuide =
    isTodayInterpretationUnavailable(props.contract)
      ? null
      : (() => {
      const nest = props.contract.color_guide;
      if (nest?.name) {
        return resolveTodayDayColorGuide({
          name: nest.name,
          scenario: {
            name: nest.name,
            intensity: nest.intensity,
            clothing: nest.clothing,
            accessory: nest.accessory,
            benefit: nest.intensity,
            note: null,
            avoidColor: nest.avoid,
            avoidWhy: nest.avoid_why,
          },
          api: nest.amount
            ? {
                name: nest.name,
                amount_ru: nest.amount,
                clothing_ru: nest.clothing ?? undefined,
                accessory_ru: nest.accessory ?? undefined,
                avoid_color_ru: nest.avoid ?? undefined,
                avoid_why_ru: nest.avoid_why ?? undefined,
              }
            : null,
        });
      }
      return story.colorGuide;
    })();

  const handoffPracticeBody =
    supportSlot === "practice" && practiceTool ? (
      <TodayPracticeGiftBlock
        title={practiceTool.title}
        detail={practiceTool.detail ?? null}
        duration={practiceTool.duration ?? null}
        practiceId={recommendedPractice?.id ?? null}
        practiceStarted={engagement.practiceStarted}
        practiceCompleted={engagement.practiceCompleted}
        practiceCompleting={practiceCompleting}
        onPracticeAction={() => void onPracticeAction()}
      />
    ) : null;

  const handoffColorBody = handoffColorGuide ? (
    <TodayDayColorGuideSection guide={handoffColorGuide} />
  ) : null;

  /** Handoff thin recap: priority · promise · practice started (not number/card). */
  const handoffRecapBody = (
    <TodayRecapAchievements
      items={[
        {
          id: "priority",
          label: "Приоритет",
          value: focusTopicLabel(engagement.focusTopicId) || "— не выбран",
          done: Boolean(engagement.focusTopicId),
        },
        {
          id: "promise",
          label: "Обещание",
          value: engagement.dayGoal?.trim()
            ? engagement.dayGoal.trim().length > 46
              ? `${engagement.dayGoal.trim().slice(0, 46)}…`
              : engagement.dayGoal.trim()
            : "— без обещания",
          done: Boolean(engagement.dayGoal?.trim()),
        },
        {
          id: "practice",
          label: "Практика",
          value: engagement.practiceCompleted
            ? "сделана ✓"
            : engagement.practiceStarted
              ? "начата ✓"
              : supportSlot === "practice"
                ? practiceTool?.title
                  ? `ещё нет · ${practiceTool.title}`
                  : "ещё нет"
                : "ещё нет",
          done: Boolean(engagement.practiceStarted || engagement.practiceCompleted),
        },
      ]}
    />
  );

  const ritualTarotImpactStage =
    story.tarotImpact && !story.personalizedReady ? (
      <div className={styles.ritualSpineStage} data-testid="today-zone-tarot-impact">
        <section className={styles.ritualReveal}>
          <p className={styles.ritualRevealKind}>Символ дня</p>
          {tarotPickedId != null && tarotCardFaceSrc(tarotPickedId) ? (
            <div className={styles.ritualRevealArt} data-testid="today-tarot-face-kept">
              <TarotPicture
                sources={tarotCardFacePicture(tarotPickedId)!}
                alt={story.tarotImpact.title}
                sizes="(max-width: 40rem) 52vw, 200px"
              />
            </div>
          ) : null}
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

  const ritualCardOpen = Boolean(engagement.tarotPickedName || engagement.tarotPickedId);
  const ritualNumberOpen = Boolean(engagement.numberConfirmed);
  const ritualCardTitle =
    engagement.tarotPickedName ||
    getTodayTarotCardRu(anchorTarotId)?.nameRu ||
    props.cardName ||
    copy.ritualCardLabel;
  const ritualCardFace =
    (engagement.tarotPickedId != null ? tarotCardFaceSrc(engagement.tarotPickedId) : null) ||
    (anchorTarotId != null ? tarotCardFaceSrc(anchorTarotId) : null);

  const ritualCardGate = (
    <DsRitualGate
      kind="tarot"
      title={copy.ritualTarotOpenCta}
      body={copy.ritualTarotPendingBody}
      testId="today-ritual-tarot-gate"
      onClick={() => setRitualPickOpen("tarot")}
    />
  );

  const ritualNumberGate = (
    <DsRitualGate
      kind="number"
      title={copy.ritualNumberOpenCta}
      body={copy.ritualNumberPendingBody}
      testId="today-ritual-number-gate"
      onClick={() => setRitualPickOpen("number")}
    />
  );

  const ritualCardKept = (
    <DsCard tone="glass" size="compact" className={kitLayout.ritualResultCard} testId="today-ritual-card-kept">
      {ritualCardFace ? (
        <DsTarotFace src={ritualCardFace} alt={ritualCardTitle} className={kitLayout.ritualResultFace} />
      ) : null}
      <DsListRow testId="today-ritual-card-kept-row" title={ritualCardTitle} subtitle={copy.ritualCardLabel} />
    </DsCard>
  );

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
    showRitualSpine && isFirstToday && reactionReady ? (
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

  const reactionGateSection =
    isFirstToday && !reactionReady ? (
      <ConversationTurn
        turnId="today_reaction"
        message={
          <>
            <h2>Сначала коротко о тебе сегодня</h2>
            <p>Два выбора — и Today соберётся под твой фокус и ритм.</p>
          </>
        }
        response={<FirstTodayReactionGate onComplete={onReactionGateComplete} />}
      />
    ) : null;

  const lunarHintRaw = props.morningRitualData?.celestial_events?.lunar_phase as
    | { id?: string; name?: string; phase_name?: string; cycle_day?: number }
    | null
    | undefined;
  const dayBriefModel = buildTodayDayBriefModel({
    contract: props.contract,
    dateLabel: props.displayDate,
    salutation: story.greeting.salutation,
    headline: story.greeting.line,
    welcomeGlass,
    energyLine: energyLineDisplay,
    energyCause: energyCauseDisplay,
    loading: themeLoading,
    lunarHint: lunarHintRaw
      ? {
          id: lunarHintRaw.id ?? null,
          name: lunarHintRaw.name || lunarHintRaw.phase_name || null,
          cycle_day: lunarHintRaw.cycle_day ?? null,
        }
      : null,
  });

  const dayStoryBrief = (
    <TodayDayBrief
      loading={themeLoading}
      pane="atmosphere"
      model={dayBriefModel}
      onContinue={goToNextFromToday}
    />
  );

  const dayTasksModel = buildTodayDayTasks({
    contract: props.contract,
    practiceTitle:
      supportSlot === "practice"
        ? practiceTool?.title || (practiceRec?.kind === "practice" ? practiceRec.text : null)
        : null,
    practiceDetail:
      supportSlot === "practice"
        ? practiceTool?.detail || (practiceRec?.kind === "practice" ? practiceRec.reason : null)
        : null,
    affirmationTitle:
      supportSlot === "affirmation"
        ? (practiceRec?.kind === "affirmation" && practiceRec.text) || affirmationTool?.title || null
        : null,
    affirmationDetail:
      supportSlot === "affirmation"
        ? (practiceRec?.kind === "affirmation" ? practiceRec.reason : null) || null
        : null,
    progressRows: displayProgressRows,
    maxToday: 2,
  });

  const affirmationTaskSlot =
    supportSlot === "affirmation" && practiceFrameTitle ? (
      <div data-testid="today-task-affirmation-slot">
        <p className={styles.sectionTitle}>{practiceFrameTitle}</p>
        {practiceFrameMeta ? <p className={styles.actionsLead}>{practiceFrameMeta}</p> : null}
        <DsButton
          type="button"
          variant="primary"
          disabled={engagement.affirmationRead}
          data-testid="today-tool-affirmation-done"
          onClick={onAffirmationDone}
        >
          {engagement.affirmationRead ? copy.affirmationDone : copy.markAffirmationDone}
        </DsButton>
      </div>
    ) : null;

  const handoffTasksBody = (
    <TodayDayTasksBlock
      todayTasks={dayTasksModel.today}
      progressRows={displayProgressRows}
      practiceSlot={handoffPracticeBody}
      affirmationSlot={affirmationTaskSlot}
    />
  );

  const myDayMeaningUnavailable = isTodayInterpretationUnavailable(props.contract);
  const myDayPriorities = myDayMeaningUnavailable
    ? []
    : (
    dayBriefModel.doItems.length
      ? dayBriefModel.doItems
      : glanceDailyFocus?.prioritize
        ? [glanceDailyFocus.prioritize]
        : []
  ).slice(0, 3);
  const myDayCautions = myDayMeaningUnavailable
    ? []
    : (
    dayBriefModel.avoidItems.length
      ? dayBriefModel.avoidItems
      : glanceDailyFocus?.avoid
        ? [glanceDailyFocus.avoid]
        : []
  )
    .filter((line) => !myDayPriorities.includes(line))
    .slice(0, 2);

  const myDayHeadline = myDayMeaningUnavailable ? null : dayBriefModel.personalLine;
  const myDayFocusTitle = myDayMeaningUnavailable
    ? null
    : pickPersonalFocusAxisLabel(props.contract);
  const myDayFocusBody = myDayMeaningUnavailable
    ? null
    : omitIfOverlapsHeadline(instructionBridge.lead, myDayHeadline);

  const myDayBody = (
    <TodayMyDayPane
      meaningUnavailable={myDayMeaningUnavailable}
      headline={myDayHeadline}
      focusTitle={myDayFocusTitle}
      focusBody={myDayFocusBody}
      priorities={myDayPriorities}
      cautions={myDayCautions}
      timeline={
        showMyDayAct && !myDayMeaningUnavailable ? (
          <TodayMyDayRhythm
            dateISO={dateISO}
            windows={props.contract.global_day?.windows ?? null}
            drivers={props.contract.global_day?.drivers ?? null}
            allowNatalFetch={showPersonalTimeline}
          />
        ) : null
      }
      colorCard={myDayMeaningUnavailable ? null : handoffColorBody}
      extraCards={handoffTasksBody}
      depthLayer={
        !myDayMeaningUnavailable && todayDepthLayerForFocus ? (
          <TodayDepthLayerSection
            dateISO={dateISO}
            depthLayer={todayDepthLayerForFocus}
            preferredTopic={preferredDepthTopic}
            autoPickPreferred={false}
            isActive={screenFlowIndex === todayHandoffIndices(screenFlowLayout).focus}
          />
        ) : null
      }
    />
  );

  const dayStoryFoundation =
    isFirstToday && !reactionReady ? (
      <ConversationThread testId="conversation-thread-first-today">
        {reactionGateSection}
      </ConversationThread>
    ) : (
      <TodayProductScreenFlow
      dateISO={dateISO}
      dateLabel={props.displayDate}
      dayBody={dayStoryBrief}
      showSymbols={showSymbolsAct}
      showMyDay={showMyDayAct}
      showEvening={showEvening}
      ritualCardOpen={ritualCardOpen}
      ritualNumberOpen={ritualNumberOpen}
      ritualResultBody={
        ritualNumberOpen && ritualCardOpen ? (
          <TodayRitualLensPair
            cardTitle={ritualCardTitle}
            cardFaceSrc={ritualCardFace}
            cardCatalog={ritualTarotMeaningText}
            cardLens={ritualTarotPersonalText}
            numberDisplay={engagement.numberValue || props.numerologyValue}
            numberTitle={ritualNumberTitle}
            numberCatalog={ritualNumberMeaningText}
            numberLens={ritualNumberSupportText}
          />
        ) : null
      }
      numberBody={ritualNumberGate}
      cardBody={ritualCardOpen ? ritualCardKept : ritualCardGate}
      myDayBody={myDayBody}
      eveningBody={handoffEveningBody}
      showPersonalized={useProductPersonalized}
      contract={props.contract}
      tapResponse={engagement.tapResponse}
      onTapRecorded={(response) => persistEngagement({ tapResponse: response })}
      onOpenEvening={onOpenEvening}
      dayPromise={engagement.dayGoal}
      onCloseOutcome={(outcome) => onSubmitEveningClose(outcome, null, "")}
      activeIndex={screenFlowIndex}
      onIndexChange={onScreenFlowIndexChange}
      embeddedInWebDashboard={embeddedInWebDashboard}
      topRowSection={topRowSection}
      greetingSection={null}
    />

  );

  const personalizedProps = {
    embeddedInWebDashboard,
    story,
    contract: props.contract,
    strengthenTools,
    promiseSuggestions,
    dayGoal: engagement.dayGoal,
    practiceCompleted: engagement.practiceCompleted,
    practiceStarted: engagement.practiceStarted,
    affirmationRead: engagement.affirmationRead,
    practiceCompleting,
    activeHabit,
    activeAscetic,
    habitMarked:
      engagement.habitMarkedId != null &&
      activeHabit != null &&
      engagement.habitMarkedId === activeHabit.id,
    asceticMarked:
      engagement.asceticMarkedId != null &&
      activeAscetic != null &&
      engagement.asceticMarkedId === activeAscetic.id,
    habitMarking,
    asceticMarking,
    goalDraftOpen,
    goalDraft,
    coreProfile: props.coreProfile,
    skyCards: story.skyCards,
    colorGuide: story.colorGuide,
    morningRitualData: props.morningRitualData,
    dateISO,
    tapResponse: engagement.tapResponse,
    progressRows,
    focusSphere: readingFocusSphere,
    preferredDepthTopic,
    autoPickDepthTopic,
    onTapRecorded: (response: "avoided_trap" | "fell_into_trap" | "not_applicable" | "skipped") => {
      persistEngagement({ tapResponse: response });
    },
    tarotDeepenHref:
      engagement.tarotPickedId != null
        ? buildTarotDeepenHref({
            cardId: engagement.tarotPickedId,
            orientation: engagement.tarotOrientation ?? "upright",
            source: "today" as const,
          })
        : null,
    onPickPromise: (text: string) => {
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
    },
    onOpenGoalDraft: () => {
      setGoalDraft(engagement.dayGoal ?? "");
      setGoalDraftOpen(true);
    },
    onGoalDraftChange: setGoalDraft,
    onSaveGoal,
    onPracticeAction: () => void onPracticeAction(),
    onAffirmationDone,
    onHabitMark: () => void onHabitMark(),
    onAsceticMark: () => void onAsceticMark(),
  };

  return (
    <>
      <div
        id={isFirstToday ? "today-first-day-surface" : "today-composition-surface"}
        data-testid={isFirstToday ? "today-composition-first-today" : "today-composition-surface"}
        className={`${styles.root} ${embeddedInWebDashboard ? styles.rootWebEmbed : ""}`}
      >
        {showMemorySlot ? (
          <div className={styles.continuityWrap} data-testid="today-zone-memory" data-memory-state={memorySlot.state}>
            <section
              className={styles.continuityPill}
              data-testid={
                memorySlot.state === "filled"
                  ? "today-entity-continuity-recall"
                  : "today-entity-memory-stub"
              }
            >
              <div className={styles.continuityInner}>
                <span className={styles.continuityAccent} aria-hidden />
                <div>
                  <p className={styles.continuityEyebrow}>{memorySlot.eyebrow}</p>
                  <p className={styles.continuityBody}>{memorySlot.body}</p>
                </div>
              </div>
              {memorySlot.state === "filled" ? (
                <span className={styles.continuityChevron} aria-hidden>
                  ›
                </span>
              ) : null}
            </section>
          </div>
        ) : null}

        {dayStoryFoundation}

        {useLegacyStackedPath && useProductPersonalized ? (
          <TodayPersonalizedProductSection {...personalizedProps} />
        ) : null}

        {/* Legacy stacked path — not first-today (ScreenFlow after reaction). */}
        {useLegacyStackedPath &&
        (story.tarotImpact || story.numberImpact) &&
        engagement.tarotPickedName ? (
          <div className={styles.personalSection} data-testid="today-zone-symbol-impacts">
            {story.tarotImpact ? (
              <section className={styles.ritualReveal} data-testid="today-zone-tarot-impact">
                <p className={styles.ritualRevealKind}>Символ дня · открыт</p>
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
                      orientation: engagement.tarotOrientation ?? "upright",
                      source: "today",
                    })}
                    className={joinClass(ds.btn, ds.btnMd, ds.btnSecondary, styles.ritualDeepenCta)}
                    data-testid="today-tarot-deepen"
                    onClick={() => {
                      trackMeaningEvent({
                        event_type: "tarot_deepen_started",
                        event_source: TAROT_DEEPEN_EVENT_SOURCE,
                        local_date: dateISO,
                        payload: buildTarotDeepenEventPayload({
                          cardId: engagement.tarotPickedId!,
                          orientation: engagement.tarotOrientation ?? "upright",
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
                <p className={styles.ritualRevealKind}>Число дня · открыто</p>
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
          </div>
        ) : null}

        {/* Depth/sky/context live on the legacy non-foundation path only.
            Product ScreenFlow owns the full surface — do not stack under greeting. */}
        {useLegacyStackedPath &&
        !useProductPersonalized &&
        !isDayNotReady(props.contract) &&
        todayDepthLayerForFocus ? (
          <TodayDepthLayerSection
            dateISO={dateISO}
            depthLayer={todayDepthLayerForFocus}
            guideGenerationId={props.guideGenerationId ?? null}
            preferredTopic={preferredDepthTopic}
            autoPickPreferred={autoPickDepthTopic}
          />
        ) : null}

        {useLegacyStackedPath && !useProductPersonalized && showSkyCards ? (
          <section className={styles.skySection} data-testid="today-zone-sky-influences">
            <h2 className={styles.sectionTitle}>{copy.astroContextTitle}</h2>
            <TodaySkyStoryCards cards={story.skyCards} />
          </section>
        ) : null}

        {useLegacyStackedPath && story.ritualTransformBanner ? (
          <p className={styles.ritualTransformBanner} data-testid="today-ritual-transform">
            {story.ritualTransformBanner}
          </p>
        ) : null}

        {useLegacyStackedPath && !useProductPersonalized && showColorGuide && story.colorGuide ? (
          <TodayDayColorGuideSection guide={story.colorGuide} />
        ) : null}

        {useLegacyStackedPath && !useProductPersonalized && showContextPanel ? (
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

        {useLegacyStackedPath && !useProductPersonalized && zones.strengthen && strengthenTools.length > 0 ? (
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
                  <DsButton
                    type="button"
                    variant="primary"
                    className={styles.toolActionPrimary}
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
                  </DsButton>
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
                        <DsButton
                          type="button"
                          variant="secondary"
                          className={styles.toolAction}
                          disabled={engagement.affirmationRead}
                          data-testid="today-tool-affirmation-done"
                          onClick={onAffirmationDone}
                        >
                          {engagement.affirmationRead ? copy.affirmationDone : copy.markAffirmationDone}
                        </DsButton>
                      ) : null}
                    </article>
                  ))}
                </div>
              ) : null}
            </div>
          </section>
        ) : null}

        {useLegacyStackedPath && !useProductPersonalized && story.personalizedReady ? (
        <div className={styles.personalSection} data-testid="today-zone-personal">

        {zones.whyStory && story.whyStory.length > 0 ? (
          <section className={styles.whyStory} data-testid="today-zone-why-story">
            <details className={styles.whyStoryDetails} data-testid="today-entity-why-expand">
              <summary className={styles.sectionTitle}>{copy.whyStoryTitle}</summary>
              <div className={styles.whyStoryBody}>
                {story.whyStory.map((line) => (
                  <p key={line} className={styles.whyStoryParagraph}>
                    {line}
                  </p>
                ))}
              </div>
            </details>
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
                  onClick={() => onPickPromise(s.text)}
                >
                  {s.text}
                </button>
              ))}
            </div>
            {goalDraftOpen ? (
              <div className={styles.goalForm} data-testid="today-entity-daily-goal">
                <DsTextField
                  id="day-goal-input"
                  label={copy.goalPrompt}
                  value={goalDraft}
                  onChange={setGoalDraft}
                  maxLength={200}
                  placeholder={copy.goalPlaceholder}
                />
                <DsButton type="button" variant="primary" onClick={onSaveGoal}>
                  {copy.goalSave}
                </DsButton>
              </div>
            ) : (
              <DsButton
                type="button"
                variant="secondary"
                className={styles.promiseCustom}
                onClick={() => {
                  setGoalDraft(engagement.dayGoal ?? "");
                  setGoalDraftOpen(true);
                }}
              >
                {engagement.dayGoal ? copy.editOwnPromise : copy.writeOwnPromise}
              </DsButton>
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

        {useLegacyStackedPath && !useProductPersonalized && story.isEveningSurface && zones.evening ? (
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

        {useLegacyStackedPath && !useProductPersonalized && zones.evening ? (
          <div className={styles.eveningZone} data-testid="today-zone-evening-entry">
            <p className={styles.eveningHint}>{story.isEveningSurface ? copy.eveningRecapTitle : copy.eveningHint}</p>
            <DsButton
              type="button"
              variant="primary"
              className={styles.eveningButton}
              data-testid="today-evening-open"
              onClick={onOpenEvening}
            >
              {copy.eveningCta}
            </DsButton>
          </div>
        ) : null}

        {props.guideNarrativeLoading ? (
          <div className={styles.loadingInline} role="status" aria-live="polite">
            <LoadingSpinner size="sm" />
            <span className={styles.loadingText}>{copy.loadingDay}</span>
          </div>
        ) : null}
      </div>

      {portalReady && ritualPickOpen === "tarot"
        ? createPortal(
            <div
              className={styles.pickOverlay}
              role="dialog"
              aria-modal="true"
              aria-label={copy.ritualTarotPendingTitle}
              data-testid="today-ritual-tarot-overlay"
              onPointerDown={(event) => event.stopPropagation()}
            >
              <div className={styles.pickSheet}>
                <div data-testid="today-ritual-tarot-pick">{tarotPickExperience}</div>
                <DsButton type="button" variant="secondary" className={styles.pickClose} onClick={() => setRitualPickOpen(null)}>
                  Закрыть
                </DsButton>
              </div>
            </div>,
            document.body,
          )
        : null}

      {portalReady && ritualPickOpen === "number"
        ? createPortal(
            <div
              className={styles.pickOverlay}
              role="dialog"
              aria-modal="true"
              aria-label={copy.ritualNumberPendingTitle}
              data-testid="today-ritual-number-overlay"
              onPointerDown={(event) => event.stopPropagation()}
            >
              <div className={styles.pickSheet}>
                <div data-testid="today-ritual-number-pick">{numberPickExperience}</div>
                <DsButton type="button" variant="secondary" className={styles.pickClose} onClick={() => setRitualPickOpen(null)}>
                  Закрыть
                </DsButton>
              </div>
            </div>,
            document.body,
          )
        : null}

    </>
  );
}
