"use client";

import type { CSSProperties } from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { RitualEntryHeroIllustration } from "@/components/today/ritual/RitualEntryHeroIllustration";
import { RitualNumberPickExperience } from "@/components/today/ritual/RitualNumberPickExperience";
import { RitualTarotPickExperience } from "@/components/today/ritual/RitualTarotPickExperience";
import { ritualEntryEyebrowLine } from "@/lib/todayRitualEntryIllustration";
import {
  resolveDailyTarotDeckIndex,
  tarotCardDisplayHeightPx,
  tarotCardFaceSrc,
  TAROT_CARD_PIXEL_HEIGHT,
  TAROT_CARD_PIXEL_WIDTH,
  TAROT_RITUAL_REVEAL_MAX_WIDTH_PX,
  TAROT_SPINE_THUMB_WIDTH_PX,
} from "@/lib/tarotCardAssets";
import { TodayDayLogicCallout } from "@/components/today/TodayDayLogicCallout";
import { TodayDayHistoryStrip } from "@/components/today/TodayDayHistoryStrip";
import { TodayCoreLoopViabilitySurface } from "@/components/today/TodayCoreLoopViabilitySurface";
import { TodayResultView } from "@/components/today/TodayResultView";
import type { TodayCycleData } from "@/components/today/todayPageUtils";
import type { MorningRitualData } from "@/components/today/todayPageUtils";
import type { FusionResponse } from "@/components/today/todayPageUtils";
import type { MeaningRingsResponse } from "@/lib/types";
import type { WeeklyGoal } from "@/components/today/todayPageUtils";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import { useAuth } from "@/lib/useAuth";
import { revealDayCard, revealDayNumber, type DaySymbolPublicView } from "@/lib/daySymbolReveal";
import type { TodayRitualNarrativePayload } from "@/lib/todayNarrativeApi";
import type { TodayContractV1 } from "@/lib/todayContract";
import {
  dayStoryActionTitles,
  dayStoryAvoidItems,
  dayStoryDoItems,
  dayStoryEveningPayload,
  dayStoryHeadline,
  dayStoryParagraphs,
  dayStoryPrimaryAction,
  dayStoryWhyLines,
  usesDayStorySingleVoice,
} from "@/lib/todayContractMapper";
import { LoadingSpinner } from "@/components/orbit";
import type { TrackerEntityKind } from "@/app/tracking/calendar/trackerEntityCatalog";
import {
  applyTarotSphereBias,
  buildTodayFourAreas,
  computeSphereScoresProvisional,
} from "@/components/today/todayFourAreas";
import { buildDayEventsForNarrative, buildRitualEntrySubline } from "@/components/today/todayPageUtils";
import {
  getTodayTarotCardRu,
  mergeTarotSphereBumps,
} from "@/components/today/todayTarotCardsRu";
import { randomTarotDeckIndexExclude } from "@/components/today/todayTarotDraw";
import {
  parseCoreMessageForUi,
  parseActionOptionsRich,
  parseDayEngineBriefFromGuide,
  parseDayModelBriefFromGuide,
  parseSphereTriadFromGuide,
  parseSupportHooksFromGuide,
  sphereTriadFallbackFromAreas,
} from "@/components/today/todayGuideActionable";
import {
  RITUAL_CARD_HONEST_STEP_CHIPS,
  RITUAL_COPY,
  RITUAL_HEAD_TOPIC_CHIPS,
  RITUAL_MOOD_GRID,
  RITUAL_MOOD_LABELS,
  RITUAL_NUMBER_RHYTHM_CHIPS,
  essentialsForMood,
  isLowEnergyRitualMood,
  formatFusionDayHistoryRu,
  formatFusionDayHistoryWeekSummaryRu,
  formatFusionDayHistoryMeaningLineRu,
  formatFusionDayHistoryReflectionLineRu,
  isFusionDayHistoryDeltaUntrustworthy,
  formatRitualCardNumberBridgeWithTarotPicked,
  formatRitualCardNumberDetailEyebrow,
  formatRitualEntryProgressTarotNumberHint,
  inferGuidanceLead,
  ritualAvoidHeadingForUserGender,
  buildRitualWhyLinesWeb,
  formatLunarRitualSummaryLine,
  personalDayRhythmBridgeSuffix,
  pickFirstDistinctLine,
  lineRedundantWithAny,
  anchorTarotTagsFromLead,
  numberDayTagTriad,
  rhythmTierLabelForScore,
  ritualGoalSuggestions,
  tempoLabelForEnergyScore,
} from "@/components/today/todayRitualCopy";
import { isGarbageRitualActionCue, repairRitualDoNotEnterLine } from "@/components/today/ritualCueSanitizer";
import {
  isRitualSpineComplete,
  loadRitualPersisted,
  saveRitualPersisted,
  shouldAutoOpenRitualOnDesktopFirstVisit,
  type RitualPersistedState,
} from "@/lib/todayRitualPersisted";
import {
  applyTodayRitualSpineReducer,
  executeRitualSpineAnalytics,
  scrollToRitualSpineDomAnchor,
  withOptionalGuideGenerationId,
  type TodayRitualSpineSnapshot,
} from "@/lib/todayRitualSpineMachine";

function labelForRitualMoodId(id: string): string {
  const g = RITUAL_MOOD_GRID.find((m) => m.id === id);
  if (g) return g.label;
  return RITUAL_MOOD_LABELS.find((m) => m.id === id)?.label ?? id;
}

/** Длинные строки в ритуале не выходят за колонку / карточку (flex + узкие экраны). */
const ritualTextWrap: CSSProperties = {
  overflowWrap: "anywhere",
  wordBreak: "break-word",
};

/** Секции в сетке не раздувают родителя по ширине. */
const ritualSectionContain: CSSProperties = {
  minWidth: 0,
  maxWidth: "100%",
  overflow: "hidden",
  boxSizing: "border-box",
};

/** Чипы и вторичные кнопки с длинными подписями переносятся многострочно. */
const ritualChipWrap: CSSProperties = {
  ...ritualTextWrap,
  whiteSpace: "normal",
  maxWidth: "100%",
};

function narrativeString(payload: Record<string, unknown> | null | undefined, key: string): string | null {
  if (!payload || typeof payload !== "object") return null;
  const v = payload[key];
  return typeof v === "string" && v.trim() ? v.trim() : null;
}

function min100(n: number) {
  return Math.max(0, Math.min(100, Math.round(n)));
}

/** Снимок хребта ритуала для `applyTodayRitualSpineReducer` — паритет iOS `TodayRitualSpineSnapshot`. */
function buildRitualSpineSnapshotWeb(input: {
  showCardSection: boolean;
  tarotContinueAck: boolean;
  numberRevealed: boolean;
  tarotMainId: number | null;
  mood: string | null;
  checkInSubmitted: boolean;
  guideNarrativeLoading: boolean;
}): TodayRitualSpineSnapshot {
  const tarotMainResolved =
    input.tarotMainId != null && getTodayTarotCardRu(input.tarotMainId) != null;
  return {
    dayOpened: input.showCardSection,
    tarotContinueAck: input.tarotContinueAck,
    numberRevealed: input.numberRevealed,
    tarotMainId: input.tarotMainId,
    tarotMainResolved,
    selectedMoodId: input.mood,
    checkInSubmitted: input.checkInSubmitted,
    guideNarrativeLoading: input.guideNarrativeLoading,
  };
}

type Props = {
  firstName: string | null;
  displayDate: string;
  todayData: TodayCycleData;
  morningRitualData: MorningRitualData | null;
  fusion: FusionResponse | null;
  meaningRings: MeaningRingsResponse | null;
  energyScore: number;
  /** Нет значения с бэка (ни decision_engine, ни fusion) — не подставляем запасной 50 в подпись. */
  energyScoreIsPlaceholder?: boolean;
  dayLabel: string;
  subtitle: string;
  cardName: string;
  cardMeaning: string | null;
  numerologyValue: string;
  numerologyMeaning: string;
  numerologyLucky: { time: string; color: string; stone: string };
  cardNumberBridge: string;
  summaryTitle: string;
  possible: string[];
  avoid: string[];
  support: string[];
  whyMoon: string | null;
  whyLunar: string | null;
  actionItems: { text: string; ring: string }[];
  weeklyGoals: WeeklyGoal[];
  onOpenHabit: (k: TrackerEntityKind) => void;
  /** Старт 20-минутного фокуса (таймер на странице Today). */
  onStartFocus20Minutes?: () => void;
  onTrackMood: (mood: string) => void;
  guideNarrativeLoading: boolean;
  guideNarrativePayload: Record<string, unknown> | null;
  /** Поверхность `spheres` из `/today/narrative` — те же поля, что в iOS `todaySpheresNarrative`. */
  spheresNarrativePayload: Record<string, unknown> | null;
  dayLayerNarrativePayload: Record<string, unknown> | null;
  dayLayerNarrativeLoading: boolean;
  // evening (full block kept, collapsed)
  eveningPayload: Record<string, unknown> | null;
  eveningNarrativeLoading: boolean;
  eveningCustomPhrase: string;
  eveningMarkedDone: boolean;
  eveningObservations: { noticed: string; hardest: string; easier_than_expected: string };
  eveningReflectionInput: string;
  eveningSaving: boolean;
  onEveningCustomPhraseChange: (v: string) => void;
  onEveningMarkedDoneChange: (v: boolean) => void;
  onEveningObservationChange: (field: "noticed" | "hardest" | "easier_than_expected", value: string) => void;
  onEveningReflectionChange: (v: string) => void;
  onSaveEvening: () => void;
  onRefreshToday: () => void;
  onEveningPhaseSaved: () => void;
  /** После карты + числа + настроения — запрос guide с ritual_context (карта, число, события, профиль на бэке). */
  onRitualSpineComplete?: (ctx: TodayRitualNarrativePayload) => void;
  /** `generation_id` ответов `POST /today/narrative` по surface — для meaning events и learning feedback. */
  narrativeGenerationIds?: {
    guide: number | null;
    day_layer: number | null;
    spheres: number | null;
    evening: number | null;
  };
  /** `core-profile` → `person.gender` — заголовок блока «не дожимать» в сводке ритуала. */
  profileGender?: string | null;
  /** Phase 3 · G1-surface — Theme → Action → Progress без ritual gate (`?core_loop=1` / `?first=1`). */
  coreLoopViabilityMode?: boolean;
  /** P0.1 wire — domain lenses из GET /today/contract. */
  todayContract?: TodayContractV1 | null;
  dayStoryUpdating?: boolean;
  onSymbolRevealResult?: (view: DaySymbolPublicView) => void;
};

export function TodayRitualFlow(props: Props) {
  const { trackMeaningEvent } = useMeaningRuntime();
  const { isAuthenticated } = useAuth();
  const singleVoice = usesDayStorySingleVoice(props.todayContract);
  const guideNarrativeLoading = singleVoice ? false : props.guideNarrativeLoading;
  const guideNarrativePayload = singleVoice ? null : props.guideNarrativePayload;
  const spheresNarrativePayload = singleVoice ? null : props.spheresNarrativePayload;
  const eveningPayload = useMemo(() => {
    if (!singleVoice) return props.eveningPayload;
    return props.todayContract ? dayStoryEveningPayload(props.todayContract) : null;
  }, [singleVoice, props.eveningPayload, props.todayContract]);
  const eveningNarrativeLoading = singleVoice ? false : props.eveningNarrativeLoading;
  const daySummaryAvoidTitle = useMemo(
    () => ritualAvoidHeadingForUserGender(props.profileGender),
    [props.profileGender],
  );
  const fusionDayHistoryLine = useMemo(
    () => formatFusionDayHistoryRu(props.fusion?.day_history),
    [props.fusion?.day_history],
  );
  const fusionDayHistoryWeekLine = useMemo(
    () => formatFusionDayHistoryWeekSummaryRu(props.fusion?.day_history),
    [props.fusion?.day_history],
  );
  const fusionDayHistoryMeaningLine = useMemo(
    () => formatFusionDayHistoryMeaningLineRu(props.fusion?.day_history),
    [props.fusion?.day_history],
  );
  const fusionDayHistoryReflectionLine = useMemo(
    () => formatFusionDayHistoryReflectionLineRu(props.fusion?.day_history),
    [props.fusion?.day_history],
  );
  const onDayHistoryStripFirstVisibleRitual = useCallback(() => {
    const gid = props.narrativeGenerationIds?.guide ?? null;
    trackMeaningEvent({
      event_type: "today_day_history_first_visible",
      event_source: "today",
      quality_score: 0.45,
      payload: withOptionalGuideGenerationId({ surface: "ritual_after_callout" }, gid),
    });
  }, [props.narrativeGenerationIds?.guide, trackMeaningEvent]);
  const dateISO = props.todayData.date;
  const onRitualSpineComplete = props.onRitualSpineComplete;
  const ritualNumerologyValue = props.numerologyValue;
  const ritualTodayData = props.todayData;
  const coreLoopViabilityMode = Boolean(props.coreLoopViabilityMode);

  const [hydrated, setHydrated] = useState(false);
  const [showCardSection, setShowCardSection] = useState(false);
  const [tarotMainId, setTarotMainId] = useState<number | null>(null);
  const [tarotClarifierId, setTarotClarifierId] = useState<number | null>(null);
  const [tarotApplied, setTarotApplied] = useState(false);
  const [tarotMeaningOpen, setTarotMeaningOpen] = useState(false);
  const [numberRevealed, setNumberRevealed] = useState(false);
  const [mood, setMood] = useState<string | null>(null);
  const [moodNote, setMoodNote] = useState<string | null>(null);
  const lowEnergyRitualMood = useMemo(() => isLowEnergyRitualMood(mood), [mood]);
  const fusionDayHistoryWeekLineForUi = useMemo(
    () => (lowEnergyRitualMood ? null : fusionDayHistoryWeekLine),
    [lowEnergyRitualMood, fusionDayHistoryWeekLine],
  );
  const fusionDayHistoryFooterHint = useMemo(
    () => (isFusionDayHistoryDeltaUntrustworthy(props.fusion?.day_history) ? null : undefined),
    [props.fusion?.day_history],
  );
  const [essentials, setEssentials] = useState<Record<string, boolean>>({});
  const [headTopic, setHeadTopic] = useState<string | null>(null);
  const [honestStep, setHonestStep] = useState<string | null>(null);
  const [numberRhythm, setNumberRhythm] = useState<string | null>(null);
  const [selectedActionOption, setSelectedActionOption] = useState(0);
  const [focusSessionHint, setFocusSessionHint] = useState(false);
  const [focusSavedAck, setFocusSavedAck] = useState(false);
  const [reduceMotion, setReduceMotion] = useState(false);
  const [ritualEntryEyebrow, setRitualEntryEyebrow] = useState(props.displayDate);
  const [tarotContinueAck, setTarotContinueAck] = useState(false);
  const [checkInSubmitted, setCheckInSubmitted] = useState(false);
  const [cardNumberDetailOpen, setCardNumberDetailOpen] = useState(false);
  const [dayWhyOpen, setDayWhyOpen] = useState(false);
  const ritualNarrativePostKeyRef = useRef<string | null>(null);
  const ritualHeroUnlockPrevRef = useRef(false);

  useEffect(() => {
    setRitualEntryEyebrow(ritualEntryEyebrowLine(props.displayDate, new Date()));
  }, [props.displayDate]);

  useEffect(() => {
    ritualNarrativePostKeyRef.current = null;
  }, [dateISO]);

  useEffect(() => {
    if (isLowEnergyRitualMood(mood)) {
      setSelectedActionOption((i) => (i > 0 ? 0 : i));
    }
  }, [mood]);

  useEffect(() => {
    if (singleVoice || !onRitualSpineComplete) return;
    const spine = isRitualSpineComplete({
      tarotMainId,
      tarotContinueAck,
      numberRevealed,
      mood,
      checkInSubmitted,
    });
    if (!spine || tarotMainId == null || mood == null) return;
    const drawn = getTodayTarotCardRu(tarotMainId);
    if (!drawn) return;
    const key = `${dateISO}|${tarotMainId}|${mood}|${ritualNumerologyValue}|${headTopic ?? ""}`;
    if (ritualNarrativePostKeyRef.current === key) return;
    ritualNarrativePostKeyRef.current = key;
    onRitualSpineComplete({
      tarot_main_id: tarotMainId,
      tarot_name_ru: drawn.nameRu,
      numerology_value: ritualNumerologyValue,
      mood,
      day_events: buildDayEventsForNarrative(ritualTodayData),
      head_topic: headTopic ?? undefined,
    });
  }, [
    tarotMainId,
    numberRevealed,
    mood,
    ritualNumerologyValue,
    ritualTodayData,
    onRitualSpineComplete,
    dateISO,
    tarotContinueAck,
    checkInSubmitted,
    headTopic,
    singleVoice,
  ]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const apply = () => setReduceMotion(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, []);

  useEffect(() => {
    const p = loadRitualPersisted(dateISO);
    if (p) {
      setShowCardSection(p.opened);
      setNumberRevealed(p.numberRevealed);
      setTarotMainId(p.tarotMainId);
      setTarotClarifierId(p.tarotClarifierId);
      setTarotApplied(p.tarotApplied);
      setTarotContinueAck(p.tarotContinueAck);
      setMood(p.mood);
      if (p.mood) {
        if (p.mood === "other") setMoodNote(null);
        else if (p.mood === "motivated" || p.mood === "move_wish" || p.mood === "driven") setMoodNote(RITUAL_COPY.moodAckDrive);
        else setMoodNote(RITUAL_COPY.moodAck);
      } else {
        setMoodNote(null);
      }
      setEssentials(p.essentials ?? {});
      setHeadTopic(p.headTopic);
      setHonestStep(p.honestStep);
      setNumberRhythm(p.numberRhythm);
      setCheckInSubmitted(p.checkInSubmitted);
    } else {
      setShowCardSection(false);
      setNumberRevealed(false);
      setTarotMainId(null);
      setTarotClarifierId(null);
      setTarotApplied(false);
      setTarotContinueAck(false);
      setCheckInSubmitted(false);
      setMood(null);
      setMoodNote(null);
      setEssentials({});
      setHeadTopic(null);
      setHonestStep(null);
      setNumberRhythm(null);
    }
    if (!p && shouldAutoOpenRitualOnDesktopFirstVisit()) {
      setShowCardSection(true);
    }
    setFocusSavedAck(false);
    setFocusSessionHint(false);
    setHydrated(true);
  }, [dateISO]);

  useEffect(() => {
    if (!hydrated) return;
    const snapshot: RitualPersistedState = {
      opened: showCardSection,
      numberRevealed,
      mood,
      headTopic,
      essentials,
      honestStep,
      numberRhythm,
      tarotMainId,
      tarotClarifierId,
      tarotApplied,
      tarotContinueAck,
      checkInSubmitted,
    };
    saveRitualPersisted(dateISO, snapshot);
  }, [
    hydrated,
    dateISO,
    showCardSection,
    numberRevealed,
    mood,
    headTopic,
    essentials,
    honestStep,
    numberRhythm,
    tarotMainId,
    tarotClarifierId,
    tarotApplied,
    tarotContinueAck,
    checkInSubmitted,
  ]);

  const spine =
    (props.todayData.morning?.daily_horoscope?.spine as
      | { best_mode?: string; main_risk?: string; first_move?: string; do_not_enter?: string }
      | undefined) || null;

  const tarotBumpMerged = useMemo(() => {
    if (!tarotApplied || tarotMainId == null) return null;
    const main = getTodayTarotCardRu(tarotMainId)?.sphereBump;
    const clar =
      tarotClarifierId != null ? getTodayTarotCardRu(tarotClarifierId)?.sphereBump : undefined;
    const merged = mergeTarotSphereBumps(main, clar);
    return Object.keys(merged).length ? merged : null;
  }, [tarotApplied, tarotMainId, tarotClarifierId]);

  const fourAll = useMemo(() => {
    const sc = props.todayData.morning?.daily_horoscope?.scenarios;
    const scenarios = Array.isArray(sc) ? (sc as Record<string, unknown>[]) : undefined;
    const rec = props.todayData.morning?.daily_recommendations as
      | { what_to_avoid?: string; what_to_do?: string }
      | undefined;
    const built = buildTodayFourAreas({
      rings: props.meaningRings?.rings,
      fusion: props.fusion,
      spine,
      scenarios,
      possible: props.possible,
      support: props.support,
      spheresNarrative: spheresNarrativePayload,
      mood,
      recommendations: rec ?? null,
    });
    return tarotBumpMerged ? applyTarotSphereBias(built, tarotBumpMerged) : built;
  }, [
    props.fusion,
    props.meaningRings,
    props.todayData.morning,
    spine,
    props.possible,
    props.support,
    spheresNarrativePayload,
    mood,
    tarotBumpMerged,
  ]);

  const sphereScoresProvisional = useMemo(
    () => computeSphereScoresProvisional(props.meaningRings?.rings, props.fusion ?? null),
    [props.meaningRings?.rings, props.fusion],
  );

  const drawnTarotMain = tarotMainId != null ? getTodayTarotCardRu(tarotMainId) : undefined;
  const drawnTarotClarifier = tarotClarifierId != null ? getTodayTarotCardRu(tarotClarifierId) : undefined;

  const anchorTarotId = useMemo(
    () =>
      resolveDailyTarotDeckIndex({
        morningTarotCardId: props.morningRitualData?.tarot_card?.id ?? null,
        morningTarotName: props.morningRitualData?.tarot_card?.name ?? null,
        cardName: props.cardName,
        dateISO,
      }),
    [
      dateISO,
      props.cardName,
      props.morningRitualData?.tarot_card?.id,
      props.morningRitualData?.tarot_card?.name,
    ],
  );

  const anchorTarotRecord = useMemo(() => getTodayTarotCardRu(anchorTarotId), [anchorTarotId]);

  const anchorTarotTags = useMemo(() => anchorTarotTagsFromLead(anchorTarotRecord?.leadRu ?? ""), [anchorTarotRecord]);

  const displayActionItems = useMemo(() => {
    if (!tarotApplied || !drawnTarotMain?.focusRu) return props.actionItems;
    const hint = drawnTarotMain.focusRu.trim();
    if (!hint) return props.actionItems;
    return [{ text: hint, ring: RITUAL_COPY.todayActionPlanRingTarot }, ...props.actionItems];
  }, [props.actionItems, tarotApplied, drawnTarotMain]);

  const guidePayload = guideNarrativePayload;

  const coreForUi = useMemo(() => parseCoreMessageForUi(guidePayload ?? null), [guidePayload]);

  const coreMessageParagraphs = useMemo(() => {
    if (singleVoice && props.todayContract) {
      return dayStoryParagraphs(props.todayContract);
    }
    if (!coreForUi) return [] as string[];
    if (coreForUi.kind === "paragraphs") return coreForUi.paragraphs;
    const p: string[] = [coreForUi.body];
    if (coreForUi.risk) p.push(`${RITUAL_COPY.heroRiskLabel}: ${coreForUi.risk}`);
    if (coreForUi.best_move) p.push(`${RITUAL_COPY.heroBestMoveLabel}: ${coreForUi.best_move}`);
    return p;
  }, [coreForUi, singleVoice, props.todayContract]);

  const actionOptionsRich = useMemo(() => {
    if (singleVoice && props.todayContract) {
      const fromStory = dayStoryActionTitles(props.todayContract).map((title) => ({ title }));
      if (fromStory.length >= 1) {
        const out = [...fromStory];
        while (out.length < 3) {
          out.push({ title: RITUAL_COPY.focusFallbackLine });
        }
        return out.slice(0, 3);
      }
    }
    const fromGuide = parseActionOptionsRich(guidePayload ?? null);
    if (fromGuide.length >= 3) return fromGuide.slice(0, 3);
    const out = [...fromGuide];
    const fallbackTitles = displayActionItems.map((x) => x.text).filter(Boolean);
    for (const t of fallbackTitles) {
      if (out.length >= 3) break;
      if (!out.some((o) => o.title === t)) out.push({ title: t });
    }
    while (out.length < 3) {
      out.push({ title: RITUAL_COPY.focusFallbackLine });
    }
    return out.slice(0, 3);
  }, [guidePayload, displayActionItems, singleVoice, props.todayContract]);

  const sphereTriadRows = useMemo(() => {
    const parsed = parseSphereTriadFromGuide(guidePayload ?? null);
    if (parsed) return parsed;
    const fb = sphereTriadFallbackFromAreas(fourAll, RITUAL_COPY.relationshipSphereLabel);
    return fb.length === 3 ? fb : [];
  }, [guidePayload, fourAll]);

  const numerologyReduced = props.todayData.morning?.numerology_number?.reduced_value ?? null;
  const numerologyDetailForWhy = useMemo(() => {
    const ex =
      props.morningRitualData?.numerology_explanation ?? props.todayData.morning?.numerology_explanation;
    const raw = (ex?.why_this_number || ex?.how_day_looks || ex?.meaning || ex?.summary || "").trim();
    return raw.length >= 36 ? raw : null;
  }, [props.morningRitualData, props.todayData.morning?.numerology_explanation]);

  const dayFocusLine = useMemo(() => {
    if (tarotApplied && drawnTarotMain?.focusRu?.trim()) return drawnTarotMain.focusRu.trim();
    return spine?.best_mode?.trim() || props.summaryTitle || "—";
  }, [tarotApplied, drawnTarotMain, spine, props.summaryTitle]);

  const coreTextsForDedup = useMemo(() => {
    if (singleVoice && props.todayContract) {
      return dayStoryParagraphs(props.todayContract);
    }
    const acc: string[] = [];
    if (coreForUi?.kind === "structured") {
      if (coreForUi.headline) acc.push(coreForUi.headline);
      acc.push(coreForUi.body);
      if (coreForUi.risk) acc.push(coreForUi.risk);
      if (coreForUi.best_move) acc.push(coreForUi.best_move);
    } else if (coreForUi?.kind === "paragraphs") {
      acc.push(...coreForUi.paragraphs);
    }
    return acc;
  }, [coreForUi, singleVoice, props.todayContract]);

  const displayDoLine = useMemo(() => {
    if (singleVoice && props.todayContract) {
      const primary = dayStoryPrimaryAction(props.todayContract);
      if (primary) return primary;
      const firstDo = dayStoryDoItems(props.todayContract)[0];
      if (firstDo) return firstDo;
    }
    const candidates = [
      ...props.possible.map((x) => x.trim()).filter(Boolean).filter((x) => !isGarbageRitualActionCue(x)),
      spine?.first_move?.trim(),
      props.subtitle.trim(),
    ].filter(Boolean).filter((x) => !isGarbageRitualActionCue(x)) as string[];
    const avoid: string[] = [
      dayFocusLine,
      props.summaryTitle,
      props.subtitle,
      ...coreTextsForDedup,
      ...(props.possible ?? []),
    ];
    return pickFirstDistinctLine(candidates, avoid);
  }, [props.possible, props.subtitle, props.summaryTitle, spine?.first_move, dayFocusLine, coreTextsForDedup, singleVoice, props.todayContract]);

  const dayDontLine = useMemo(() => {
    if (singleVoice && props.todayContract) {
      const avoidItems = dayStoryAvoidItems(props.todayContract);
      if (avoidItems.length) return avoidItems.join(" ");
      const abstain = props.todayContract.day_story?.abstain?.trim();
      if (abstain) return abstain;
    }
    const parts = props.avoid.map((x) => x.trim()).filter(Boolean);
    if (parts.length) return parts.join(" ");
    const dne = repairRitualDoNotEnterLine(spine?.do_not_enter?.trim() || "");
    return dne || "—";
  }, [props.avoid, spine, singleVoice, props.todayContract]);

  const ritualNarrativeAvoidPool = useMemo(() => {
    const acc: string[] = [
      props.summaryTitle,
      props.subtitle,
      displayDoLine,
      dayDontLine,
      dayFocusLine,
      ...props.possible,
      ...props.avoid,
      ...props.support,
    ];
    if (spine?.main_risk) acc.push(spine.main_risk);
    if (spine?.best_mode) acc.push(spine.best_mode);
    if (spine?.first_move) acc.push(spine.first_move);
    if (spine?.do_not_enter) acc.push(spine.do_not_enter);
    acc.push(...coreTextsForDedup);
    const seen = new Set<string>();
    const out: string[] = [];
    for (const s of acc) {
      const t = s.trim();
      if (t.length < 2) continue;
      const k = t.toLowerCase();
      if (seen.has(k)) continue;
      seen.add(k);
      out.push(t);
    }
    return out;
  }, [
    props.summaryTitle,
    props.subtitle,
    displayDoLine,
    dayDontLine,
    dayFocusLine,
    props.possible,
    props.avoid,
    props.support,
    spine,
    coreTextsForDedup,
  ]);

  const dayWhyContent = useMemo(
    () => {
      if (singleVoice && props.todayContract) {
        return {
          headline: dayStoryHeadline(props.todayContract),
          lines: dayStoryWhyLines(props.todayContract),
        };
      }
      return buildRitualWhyLinesWeb({
        summaryTitle: props.summaryTitle,
        possible: props.possible,
        guidePayload: guidePayload ?? null,
        spine,
        numerologyValue: props.numerologyValue,
        reducedValue: numerologyReduced,
        numerologyDetailLine: numerologyDetailForWhy,
        morningFocus:
          typeof props.todayData.day_connection?.morning_focus === "string"
            ? props.todayData.day_connection.morning_focus
            : undefined,
        whyMoon: props.whyMoon,
        whyLunar: props.whyLunar,
        avoidLines: ritualNarrativeAvoidPool,
      });
    },
    [
      singleVoice,
      props.todayContract,
      props.summaryTitle,
      props.possible,
      guidePayload,
      spine,
      props.numerologyValue,
      numerologyReduced,
      numerologyDetailForWhy,
      props.todayData.day_connection?.morning_focus,
      props.whyMoon,
      props.whyLunar,
      ritualNarrativeAvoidPool,
    ],
  );

  const dayMoonLine = useMemo(
    () => formatLunarRitualSummaryLine(props.whyMoon, props.whyLunar, guidePayload ?? null, 160),
    [guidePayload, props.whyMoon, props.whyLunar],
  );

  const showPracticalFocusRow = useMemo(() => {
    if (!dayFocusLine || dayFocusLine === "—") return false;
    return !lineRedundantWithAny(dayFocusLine, [displayDoLine, ...coreTextsForDedup]);
  }, [dayFocusLine, displayDoLine, coreTextsForDedup]);

  const supportHooksList = useMemo(() => parseSupportHooksFromGuide(guidePayload ?? null), [guidePayload]);

  const dayEngineBrief = useMemo(
    () =>
      guidePayload && typeof guidePayload === "object"
        ? parseDayEngineBriefFromGuide(guidePayload as Record<string, unknown>)
        : null,
    [guidePayload],
  );

  const dayModelBrief = useMemo(
    () =>
      guidePayload && typeof guidePayload === "object"
        ? parseDayModelBriefFromGuide(guidePayload as Record<string, unknown>)
        : null,
    [guidePayload],
  );

  const actionOptionsRichKey = useMemo(() => actionOptionsRich.map((o) => o.title).join("|"), [actionOptionsRich]);

  useEffect(() => {
    setSelectedActionOption(0);
  }, [actionOptionsRichKey]);

  const effectiveCardNumberBridge = useMemo(() => {
    if (!tarotMainId || !drawnTarotMain) return props.cardNumberBridge;
    const rhythm = personalDayRhythmBridgeSuffix(numerologyReduced, props.numerologyValue);
    return formatRitualCardNumberBridgeWithTarotPicked(
      drawnTarotMain.nameRu,
      props.numerologyValue,
      rhythm,
      drawnTarotClarifier?.nameRu,
    );
  }, [tarotMainId, drawnTarotMain, drawnTarotClarifier, props.cardNumberBridge, props.numerologyValue, numerologyReduced]);

  const showCardBridgeInWhy = useMemo(() => {
    const hl = dayWhyContent.headline;
    const pool = [...ritualNarrativeAvoidPool, ...dayWhyContent.lines, ...(hl ? [hl] : [])];
    return !lineRedundantWithAny(effectiveCardNumberBridge, pool);
  }, [effectiveCardNumberBridge, ritualNarrativeAvoidPool, dayWhyContent.headline, dayWhyContent.lines]);

  const eveningTarotLine = useMemo(() => {
    if (!tarotApplied || !drawnTarotMain?.eveningRu) return null;
    const cl = drawnTarotClarifier?.eveningRu?.trim();
    return cl ? `${drawnTarotMain.eveningRu} ${cl}` : drawnTarotMain.eveningRu;
  }, [tarotApplied, drawnTarotMain, drawnTarotClarifier]);

  const essentialsList = useMemo(() => essentialsForMood(mood), [mood]);

  const guidanceLead = useMemo(
    () => inferGuidanceLead(props.summaryTitle, props.possible, props.avoid, props.support),
    [props.summaryTitle, props.possible, props.avoid, props.support],
  );

  const goalIdeas = useMemo(() => [...ritualGoalSuggestions(guidanceLead)], [guidanceLead]);

  const onHeroCta = useCallback(() => {
    const snap = buildRitualSpineSnapshotWeb({
      showCardSection,
      tarotContinueAck,
      numberRevealed,
      tarotMainId,
      mood,
      checkInSubmitted,
      guideNarrativeLoading: guideNarrativeLoading,
    });
    const out = applyTodayRitualSpineReducer({ type: "openedDay" }, snap);
    if (!out) return;
    setShowCardSection(out.after.dayOpened);
    if (out.effects.scrollToAnchorId) scrollToRitualSpineDomAnchor(out.effects.scrollToAnchorId);
  }, [
    showCardSection,
    tarotContinueAck,
    numberRevealed,
    tarotMainId,
    mood,
    checkInSubmitted,
    guideNarrativeLoading,
  ]);

  const commitTarotMain = useCallback(
    (id: number) => {
      setTarotMeaningOpen(false);
      setTarotMainId(id);
      void revealDayCard({
        cardId: id,
        isAuthenticated,
        source: "today_ritual_flow",
        idempotencyKey: `tarot_reveal:${dateISO}:${id}:u`,
      })
        .then((view) => props.onSymbolRevealResult?.(view))
        .catch(() => undefined);
      const gid = props.narrativeGenerationIds?.guide ?? null;
      trackMeaningEvent({
        event_type: "tarot_selected",
        event_source: "today",
        payload: withOptionalGuideGenerationId({ role: "main", card_index: id }, gid),
      });
    },
    [dateISO, isAuthenticated, props.narrativeGenerationIds?.guide, props.onSymbolRevealResult, trackMeaningEvent],
  );

  const onDrawTarot = useCallback(() => {
    setTarotMeaningOpen(false);
    if (tarotMainId == null) return;
    if (tarotClarifierId == null) {
      const id = randomTarotDeckIndexExclude([tarotMainId]);
      setTarotClarifierId(id);
      const gid = props.narrativeGenerationIds?.guide ?? null;
      trackMeaningEvent({
        event_type: "tarot_selected",
        event_source: "today",
        payload: withOptionalGuideGenerationId({ role: "clarifier", card_index: id }, gid),
      });
    }
  }, [tarotMainId, tarotClarifierId, props.narrativeGenerationIds?.guide, trackMeaningEvent]);

  const onApplyTarotToToday = useCallback(() => {
    if (tarotMainId == null || !getTodayTarotCardRu(tarotMainId)) return;
    setTarotApplied(true);
    const gid = props.narrativeGenerationIds?.guide ?? null;
    trackMeaningEvent({
      event_type: "tarot_selected",
      event_source: "today",
      payload: withOptionalGuideGenerationId(
        {
          applied_to_today: true,
          main_card_index: tarotMainId,
          clarifier_card_index: tarotClarifierId,
        },
        gid,
      ),
    });
  }, [tarotMainId, tarotClarifierId, props.narrativeGenerationIds?.guide, trackMeaningEvent]);

  const onRevealNumber = useCallback(() => {
    const snap = buildRitualSpineSnapshotWeb({
      showCardSection,
      tarotContinueAck,
      numberRevealed,
      tarotMainId,
      mood,
      checkInSubmitted,
      guideNarrativeLoading: guideNarrativeLoading,
    });
    const out = applyTodayRitualSpineReducer({ type: "revealedNumber" }, snap);
    if (!out) return;
    setNumberRevealed(out.after.numberRevealed);
    void revealDayNumber({
      isAuthenticated,
      source: "today_ritual_flow",
      idempotencyKey: `number_reveal:${dateISO}:u`,
    })
      .then((view) => props.onSymbolRevealResult?.(view))
      .catch(() => undefined);
    if (out.effects.scrollToAnchorId) scrollToRitualSpineDomAnchor(out.effects.scrollToAnchorId);
    executeRitualSpineAnalytics(out.effects.analyticsHint, {
      numerologyValue: props.numerologyValue,
      guideGenerationId: props.narrativeGenerationIds?.guide ?? null,
      trackMeaningEvent,
    });
  }, [
    showCardSection,
    tarotContinueAck,
    numberRevealed,
    tarotMainId,
    mood,
    checkInSubmitted,
    guideNarrativeLoading,
    dateISO,
    isAuthenticated,
    props.narrativeGenerationIds?.guide,
    props.numerologyValue,
    props.onSymbolRevealResult,
    trackMeaningEvent,
  ]);

  const onContinueFromTarotReveal = useCallback(() => {
    const snap = buildRitualSpineSnapshotWeb({
      showCardSection,
      tarotContinueAck,
      numberRevealed,
      tarotMainId,
      mood,
      checkInSubmitted,
      guideNarrativeLoading: guideNarrativeLoading,
    });
    const out = applyTodayRitualSpineReducer({ type: "continuedPastTarot" }, snap);
    if (!out) return;
    setTarotContinueAck(out.after.tarotContinueAck);
    if (out.effects.scrollToAnchorId) scrollToRitualSpineDomAnchor(out.effects.scrollToAnchorId);
  }, [
    showCardSection,
    tarotContinueAck,
    numberRevealed,
    tarotMainId,
    mood,
    checkInSubmitted,
    guideNarrativeLoading,
  ]);

  const onContinueFromNumber = useCallback(() => {
    document.getElementById("today-ritual-checkin")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const onMood = useCallback(
    (id: string) => {
      const snap = buildRitualSpineSnapshotWeb({
        showCardSection,
        tarotContinueAck,
        numberRevealed,
        tarotMainId,
        mood,
        checkInSubmitted,
        guideNarrativeLoading: guideNarrativeLoading,
      });
      const out = applyTodayRitualSpineReducer({ type: "selectedMood", moodId: id }, snap);
      if (!out) return;
      setMood(out.after.selectedMoodId);
      setHeadTopic(null);
      if (RITUAL_MOOD_LABELS.some((x) => x.id === id)) {
        if (id === "other") setMoodNote(null);
        else if (id === "motivated" || id === "move_wish" || id === "driven") setMoodNote(RITUAL_COPY.moodAckDrive);
        else setMoodNote(RITUAL_COPY.moodAck);
      }
      executeRitualSpineAnalytics(out.effects.analyticsHint, {
        numerologyValue: props.numerologyValue,
        guideGenerationId: props.narrativeGenerationIds?.guide ?? null,
        trackMeaningEvent,
        onTrackMood: props.onTrackMood,
      });
    },
    [
      showCardSection,
      tarotContinueAck,
      numberRevealed,
      tarotMainId,
      mood,
      checkInSubmitted,
      props,
      trackMeaningEvent,
    ],
  );

  const essentialsListForProgress = useMemo(
    () => (lowEnergyRitualMood ? essentialsList.slice(0, 1) : essentialsList),
    [lowEnergyRitualMood, essentialsList],
  );
  const essentialsCount = useMemo(
    () => essentialsListForProgress.filter((e) => essentials[e.id]).length,
    [essentialsListForProgress, essentials],
  );
  const essentialsProgress =
    essentialsListForProgress.length > 0
      ? (essentialsCount / essentialsListForProgress.length) * 100
      : 0;

  const hasGoals = props.weeklyGoals.length > 0;

  const ritualSpineComplete = isRitualSpineComplete({
    tarotMainId,
    tarotContinueAck,
    numberRevealed,
    mood,
    checkInSubmitted,
  });
  const ritualDayUnlocked = ritualSpineComplete && !guideNarrativeLoading;
  const ritualEntrySubline = useMemo(
    () => buildRitualEntrySubline(ritualTodayData, props.firstName) || RITUAL_COPY.ritualEntryBody,
    [ritualTodayData, props.firstName],
  );
  /** Компакт только после «Продолжить» с карты и открытого числа — иначе ломается пошаговый UI. */
  const tarotRitualCompact = tarotContinueAck && numberRevealed && tarotMainId != null;
  /** После «Готово» в чек-ине — блок числа как напоминание (паритет с iOS). */
  const numberRitualCompact = Boolean(checkInSubmitted);

  useEffect(() => {
    if (!hydrated || !showCardSection) return;
    if (ritualDayUnlocked && !ritualHeroUnlockPrevRef.current) {
      ritualHeroUnlockPrevRef.current = true;
      window.setTimeout(() => {
        document.getElementById("today-ritual-your-day")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 140);
    }
    if (!ritualDayUnlocked) ritualHeroUnlockPrevRef.current = false;
  }, [hydrated, showCardSection, ritualDayUnlocked]);

  const coreLoopViabilityVisibleTrackedRef = useRef(false);
  useEffect(() => {
    if (!coreLoopViabilityMode || !hydrated || coreLoopViabilityVisibleTrackedRef.current) return;
    coreLoopViabilityVisibleTrackedRef.current = true;
    trackMeaningEvent({
      event_type: "core_loop_viability_surface_visible",
      event_source: "today",
      payload: {
        instrument: "g1_surface",
      },
    });
  }, [coreLoopViabilityMode, hydrated, trackMeaningEvent]);

  const eveningHourCompact = useMemo(() => new Date().getHours() < 19, []);

  return (
    <div
      className="today-ritual-root today-ritual-root--premium"
      style={{ minWidth: 0, maxWidth: "100%", boxSizing: "border-box" }}
    >
      <style jsx global>{`
        .today-ritual-root--premium {
          max-width: 28rem;
          margin-left: auto;
          margin-right: auto;
        }
        @media (min-width: 640px) {
          .today-ritual-root--premium {
            max-width: 32rem;
          }
        }
        @media (min-width: 1024px) {
          .today-web-page .today-ritual-root--premium {
            max-width: none;
            width: 100%;
          }
        }
        @keyframes todayRitualBreath {
          0%,
          100% {
            transform: scale(0.99);
            filter: drop-shadow(0 0 22px rgba(201, 168, 115, 0.35));
          }
          50% {
            transform: scale(1.02);
            filter: drop-shadow(0 0 34px rgba(201, 168, 115, 0.55));
          }
        }
        @keyframes todayRitualShimmer {
          0% {
            opacity: 0.4;
          }
          100% {
            opacity: 0.95;
          }
        }
        .today-ritual-sphere {
          animation: todayRitualBreath 4.2s ease-in-out infinite;
        }
        /* Card Flip lives in design-system/motion (MotionFlip) via RitualTarotPickExperience */
        .today-ritual-sphere-card:focus-visible {
          outline: 2px solid rgba(214, 142, 122, 0.65);
          outline-offset: 2px;
        }
        .today-ritual-sphere-card:focus:not(:focus-visible) {
          outline: none;
        }
      `}</style>

      {/* BLOCK 1 — Hero: персональное резюме дня + короткий статус */}
      <section
        id="today-ritual-hero"
        className="today-ritual-hero todayflow-inset-hero"
        style={{
          minHeight: !showCardSection && !coreLoopViabilityMode ? "min(72dvh, 600px)" : undefined,
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-start",
          minWidth: 0,
          maxWidth: "100%",
          boxSizing: "border-box",
        }}
      >
        {coreLoopViabilityMode ? (
          <TodayCoreLoopViabilitySurface
            displayDate={props.displayDate}
            guideNarrativeLoading={guideNarrativeLoading}
            guideNarrativePayload={guideNarrativePayload}
            onOpenOptionalRitual={!showCardSection ? onHeroCta : undefined}
            ritualTextWrap={ritualTextWrap}
          />
        ) : null}
        {!showCardSection && !coreLoopViabilityMode ? (
          <>
            <div
              style={{
                position: "relative",
                borderRadius: 0,
                overflow: "hidden",
                minHeight: "min(44vh, 380px)",
                marginLeft: "calc(50% - 50vw)",
                marginRight: "calc(50% - 50vw)",
                width: "100vw",
                maxWidth: "100vw",
                background: "linear-gradient(180deg, #fff4e8 0%, #f9e8dc 42%, #e8d4c4 100%)",
              }}
            >
              <div
                aria-hidden
                style={{
                  position: "absolute",
                  left: "8%",
                  top: "6%",
                  width: "clamp(72px, 18vw, 120px)",
                  height: "clamp(72px, 18vw, 120px)",
                  borderRadius: "50%",
                  background: "radial-gradient(circle, rgba(255, 220, 160, 0.95) 0%, rgba(255, 200, 120, 0.35) 45%, transparent 70%)",
                  filter: "blur(0.5px)",
                  pointerEvents: "none",
                  zIndex: 1,
                }}
              />
              <RitualEntryHeroIllustration dateISO={dateISO} energyScore={props.energyScore} />
              <div
                style={{
                  position: "relative",
                  zIndex: 2,
                  padding: "1.25rem 1.25rem 1.75rem",
                  textAlign: "center",
                  background: "linear-gradient(180deg, transparent 0%, rgba(255,248,242,0.72) 35%, rgba(255,244,236,0.96) 100%)",
                }}
              >
                <p
                  className="todayflow-eyebrow"
                  style={{ margin: "0 0 0.55rem", position: "relative", ...ritualTextWrap }}
                >
                  {ritualEntryEyebrow}
                </p>
                <h1
                  className="todayflow-title-hero"
                  style={{
                    position: "relative",
                    fontSize: "clamp(1.65rem, 4.2vw, 2.15rem)",
                    lineHeight: 1.18,
                    margin: 0,
                    maxWidth: "24rem",
                    marginLeft: "auto",
                    marginRight: "auto",
                    ...ritualTextWrap,
                  }}
                >
                  {RITUAL_COPY.ritualEntryTitle}
                </h1>
                <div
                  aria-hidden
                  style={{
                    position: "relative",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "0.65rem",
                    margin: "0.75rem auto 0",
                    maxWidth: "18rem",
                    opacity: 0.55,
                  }}
                >
                  <span style={{ flex: 1, height: 1, background: "rgba(180, 140, 100, 0.35)" }} />
                  <span style={{ fontSize: "0.75rem", color: "#a08060" }}>✦</span>
                  <span style={{ flex: 1, height: 1, background: "rgba(180, 140, 100, 0.35)" }} />
                </div>
                <p
                  className="orbit-body-sm"
                  style={{
                    position: "relative",
                    margin: "0.75rem auto 0",
                    color: "#5f4930",
                    lineHeight: 1.65,
                    maxWidth: "22rem",
                    paddingLeft: "max(0px, env(safe-area-inset-left))",
                    paddingRight: "max(0px, env(safe-area-inset-right))",
                    ...ritualTextWrap,
                  }}
                >
                  {ritualEntrySubline}
                </p>
              </div>
            </div>
            <div className="today-web-hero__cta">
              <button
                type="button"
                onClick={onHeroCta}
                className="orbit-button orbit-button-primary"
                style={{
                  width: "100%",
                  justifyContent: "center",
                  padding: "0.95rem 1.25rem",
                  fontSize: "1.05rem",
                  background: "linear-gradient(90deg, #c97a65 0%, #d9a08d 42%, #e8b8a4 100%)",
                  border: "1px solid rgba(255, 255, 255, 0.35)",
                  color: "#fffdfb",
                  textShadow: "0 1px 2px rgba(60, 36, 24, 0.2)",
                  fontWeight: 700,
                  ...ritualTextWrap,
                }}
              >
                {RITUAL_COPY.ritualEntryCta}
              </button>
              <p
                className="orbit-body-xs"
                style={{ margin: "0.55rem 0 0", color: "#a89880", lineHeight: 1.45, textAlign: "center", ...ritualTextWrap }}
              >
                {RITUAL_COPY.ritualEntryTiming}
              </p>
            </div>
          </>
        ) : ritualDayUnlocked ? (
          <>
            <div style={{ minWidth: 0, maxWidth: "100%" }}>
              <p className="todayflow-eyebrow" style={{ margin: "0 0 0.5rem", ...ritualTextWrap }}>
                {props.displayDate}
              </p>
              <h1
                className="todayflow-title-hero"
                style={{ fontSize: "clamp(1.45rem, 3.6vw, 2rem)", lineHeight: 1.2, ...ritualTextWrap }}
              >
                {RITUAL_COPY.todayYourDayTitle}
              </h1>
              {tarotMainId != null ? (
                <div
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "0.75rem",
                    flexWrap: "wrap",
                    marginTop: "0.65rem",
                    minWidth: 0,
                    padding: "0.75rem 0.85rem",
                    borderRadius: 16,
                    background: "rgba(255,255,255,0.45)",
                    border: "1px solid rgba(201,168,115,0.22)",
                    boxSizing: "border-box",
                  }}
                >
                  {tarotCardFaceSrc(tarotMainId) ? (
                    <div
                      style={{
                        width: 52,
                        height: tarotCardDisplayHeightPx(52),
                        flexShrink: 0,
                        borderRadius: 10,
                        overflow: "hidden",
                        border: "1px solid rgba(214,142,122,0.35)",
                        background: "#faf6f2",
                      }}
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={tarotCardFaceSrc(tarotMainId)!}
                        alt=""
                        width={TAROT_CARD_PIXEL_WIDTH}
                        height={TAROT_CARD_PIXEL_HEIGHT}
                        style={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }}
                        draggable={false}
                      />
                    </div>
                  ) : null}
                  <div
                    style={{
                      width: 44,
                      height: 44,
                      borderRadius: "50%",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontFamily: "var(--orbit-font-display)",
                      fontWeight: 700,
                      fontSize: "1.05rem",
                      color: "#2d241c",
                      background: "rgba(255, 237, 228, 0.85)",
                      border: "1px solid rgba(214,142,122,0.35)",
                      flexShrink: 0,
                    }}
                  >
                    {props.numerologyValue}
                  </div>
                  <div style={{ flex: "1 1 12rem", minWidth: 0 }}>
                    <p className="todayflow-eyebrow" style={{ margin: "0 0 0.35rem", ...ritualTextWrap }}>
                      {RITUAL_COPY.daySummaryMarkersEyebrow}
                    </p>
                    <p className="orbit-body-xs" style={{ margin: "0.15rem 0", color: "#5f4930", lineHeight: 1.45, ...ritualTextWrap }}>
                      <strong style={{ color: "#a89880" }}>{RITUAL_COPY.dayMarkerCard}:</strong>{" "}
                      {drawnTarotMain?.nameRu ?? props.cardName}
                    </p>
                    <p className="orbit-body-xs" style={{ margin: "0.15rem 0", color: "#5f4930", lineHeight: 1.45, ...ritualTextWrap }}>
                      <strong style={{ color: "#a89880" }}>{RITUAL_COPY.dayMarkerNumber}:</strong> {props.numerologyValue}
                    </p>
                    <p className="orbit-body-xs" style={{ margin: "0.15rem 0", color: "#5f4930", lineHeight: 1.45, ...ritualTextWrap }}>
                      <strong style={{ color: "#a89880" }}>{RITUAL_COPY.dayMarkerMoon}:</strong> {dayMoonLine}
                    </p>
                    <p className="orbit-body-xs" style={{ margin: "0.15rem 0", color: "#5f4930", lineHeight: 1.45, ...ritualTextWrap }}>
                      <strong style={{ color: "#a89880" }}>{RITUAL_COPY.dayMarkerMood}:</strong>{" "}
                      {mood ? labelForRitualMoodId(mood) : "—"}
                    </p>
                  </div>
                </div>
              ) : null}
              <button
                type="button"
                onClick={() => {
                  setCardNumberDetailOpen(true);
                  trackMeaningEvent({
                    event_type: "number_selected",
                    event_source: "today",
                    payload: { card_number_detail_open: true },
                  });
                }}
                className="orbit-button orbit-button-secondary orbit-button-sm"
                style={{ marginTop: "0.65rem", borderRadius: 999, ...ritualChipWrap }}
              >
                {RITUAL_COPY.todayShowCardNumberCta}
              </button>
              <TodayDayLogicCallout
                variant="ritual"
                dayEngineBrief={dayEngineBrief}
                dayModelBrief={dayModelBrief}
                wrap={ritualTextWrap}
              />
              {fusionDayHistoryLine ? (
                <TodayDayHistoryStrip
                  line={fusionDayHistoryLine}
                  footerHint={fusionDayHistoryFooterHint}
                  weekSummaryLine={fusionDayHistoryWeekLineForUi}
                  meaningLine={fusionDayHistoryMeaningLine}
                  reflectionLine={fusionDayHistoryReflectionLine}
                  onFirstVisible={onDayHistoryStripFirstVisibleRitual}
                  ritualTextWrap={ritualTextWrap}
                  ritualSectionContain={ritualSectionContain}
                  style={{ marginTop: "0.75rem" }}
                />
              ) : null}
              <p className="todayflow-eyebrow" style={{ margin: "0.85rem 0 0.35rem", ...ritualTextWrap }}>
                {RITUAL_COPY.daySummaryShortEyebrow}
              </p>
              {coreForUi?.kind === "structured" && coreForUi.headline ? (
                <p className="orbit-body-sm" style={{ margin: "0 0 0.35rem", color: "#4a3d2e", fontWeight: 600, ...ritualTextWrap }}>
                  {coreForUi.headline}
                </p>
              ) : null}
              {coreForUi?.kind === "structured" ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                  <p
                    className="orbit-body-sm"
                    style={{
                      margin: 0,
                      color: "#3f3428",
                      lineHeight: 1.58,
                      maxWidth: "40rem",
                      fontWeight: 600,
                      ...ritualTextWrap,
                    }}
                  >
                    {coreForUi.body}
                  </p>
                  {coreForUi.risk ? (
                    <p className="orbit-body-sm" style={{ margin: 0, color: "#4a3d2e", lineHeight: 1.55, ...ritualTextWrap }}>
                      <strong>{RITUAL_COPY.heroRiskLabel}:</strong> {coreForUi.risk}
                    </p>
                  ) : null}
                  {coreForUi.best_move ? (
                    <p className="orbit-body-sm" style={{ margin: 0, color: "#4a3d2e", lineHeight: 1.55, ...ritualTextWrap }}>
                      <strong>{RITUAL_COPY.heroBestMoveLabel}:</strong> {coreForUi.best_move}
                    </p>
                  ) : null}
                </div>
              ) : props.dayStoryUpdating ? (
                <p
                  className="orbit-body-sm"
                  data-testid="today-day-story-updating"
                  aria-live="polite"
                  style={{ margin: 0, color: "#7a623d", lineHeight: 1.55, ...ritualTextWrap }}
                >
                  Обновляем описание дня…
                </p>
              ) : coreMessageParagraphs.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                  {coreMessageParagraphs.map((para, i) => (
                    <p
                      key={i}
                      className="orbit-body-sm"
                      style={{
                        margin: 0,
                        color: "#3f3428",
                        lineHeight: 1.58,
                        maxWidth: "40rem",
                        fontWeight: i === 0 ? 600 : 500,
                        ...ritualTextWrap,
                      }}
                    >
                      {para}
                    </p>
                  ))}
                </div>
              ) : (
                <p
                  className="orbit-body-sm"
                  style={{
                    margin: 0,
                    color: "#5f4930",
                    lineHeight: 1.6,
                    maxWidth: "40rem",
                    ...ritualTextWrap,
                  }}
                >
                  {props.subtitle}
                </p>
              )}
              <p className="todayflow-eyebrow" style={{ margin: "0.85rem 0 0.35rem", ...ritualTextWrap }}>
                {RITUAL_COPY.daySummaryDoTitle}
              </p>
              <p className="orbit-body-sm" style={{ margin: 0, color: "#3f3428", lineHeight: 1.55, maxWidth: "40rem", ...ritualTextWrap }}>
                {displayDoLine}
              </p>
              <p className="todayflow-eyebrow" style={{ margin: "0.75rem 0 0.35rem", ...ritualTextWrap }}>
                {daySummaryAvoidTitle}
              </p>
              <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.55, maxWidth: "40rem", ...ritualTextWrap }}>
                {dayDontLine}
              </p>
              <p className="todayflow-eyebrow" style={{ margin: "0.75rem 0 0.35rem", ...ritualTextWrap }}>
                {RITUAL_COPY.daySummaryPracticalEyebrow}
              </p>
              <div
                className="todayflow-surface-soft"
                style={{
                  marginTop: "0.35rem",
                  padding: "0.65rem 0.75rem",
                  borderRadius: 14,
                  border: "1px solid rgba(201,168,115,0.18)",
                  minWidth: 0,
                  maxWidth: "40rem",
                }}
              >
                <p className="orbit-body-xs" style={{ margin: "0.12rem 0", color: "#5f4930", ...ritualTextWrap }}>
                  <strong style={{ color: "#a89880" }}>{RITUAL_COPY.numerologyBestTimeLabel}:</strong>{" "}
                  {props.numerologyLucky.time}
                </p>
                <p className="orbit-body-xs" style={{ margin: "0.12rem 0", color: "#5f4930", ...ritualTextWrap }}>
                  <strong style={{ color: "#a89880" }}>{RITUAL_COPY.numerologyColorLabel}:</strong> {props.numerologyLucky.color}
                </p>
                <p className="orbit-body-xs" style={{ margin: "0.12rem 0", color: "#5f4930", ...ritualTextWrap }}>
                  <strong style={{ color: "#a89880" }}>{RITUAL_COPY.numerologyStoneLabel}:</strong> {props.numerologyLucky.stone}
                </p>
                <p className="orbit-body-xs" style={{ margin: "0.12rem 0", color: "#5f4930", ...ritualTextWrap }}>
                  <strong style={{ color: "#a89880" }}>{RITUAL_COPY.heroTempoLabel}:</strong> {tempoLabelForEnergyScore(props.energyScore)}
                </p>
                {showPracticalFocusRow ? (
                  <p className="orbit-body-xs" style={{ margin: "0.12rem 0", color: "#5f4930", ...ritualTextWrap }}>
                    <strong style={{ color: "#a89880" }}>{RITUAL_COPY.heroFocusLabel}:</strong> {dayFocusLine}
                  </p>
                ) : null}
              </div>
              <button
                type="button"
                onClick={() => {
                  setDayWhyOpen((v) => {
                    const next = !v;
                    if (next) {
                      const gid = props.narrativeGenerationIds?.guide;
                      const payload: Record<string, unknown> = { surface: "ritual_day_summary" };
                      if (typeof gid === "number" && gid > 0) {
                        payload.generation_id = gid;
                      }
                      trackMeaningEvent({
                        event_type: "today_guide_why_opened",
                        event_source: "today",
                        quality_score: 0.55,
                        payload,
                      });
                    }
                    return next;
                  });
                }}
                className="orbit-button orbit-button-secondary orbit-button-sm"
                style={{ marginTop: "0.75rem", borderRadius: 999, ...ritualChipWrap }}
              >
                {dayWhyOpen ? RITUAL_COPY.daySummaryWhyCollapse : RITUAL_COPY.daySummaryWhyCta}
              </button>
              {dayWhyOpen ? (
                <div
                  className="todayflow-surface-soft"
                  style={{
                    marginTop: "0.45rem",
                    padding: "0.75rem 0.85rem",
                    borderRadius: 14,
                    border: "1px solid rgba(201,168,115,0.22)",
                    minWidth: 0,
                    maxWidth: "40rem",
                  }}
                >
                  {dayWhyContent.headline ? (
                    <p className="orbit-body-sm" style={{ margin: "0 0 0.45rem", fontWeight: 600, color: "#2d241c", ...ritualTextWrap }}>
                      {dayWhyContent.headline}
                    </p>
                  ) : null}
                  {dayWhyContent.lines.map((line, i) => (
                    <p key={i} className="orbit-body-xs" style={{ margin: "0.25rem 0", color: "#5f4930", lineHeight: 1.5, ...ritualTextWrap }}>
                      {line}
                    </p>
                  ))}
                  {showCardBridgeInWhy ? (
                    <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#6a5132", lineHeight: 1.5, ...ritualTextWrap }}>
                      {effectiveCardNumberBridge}
                    </p>
                  ) : null}
                </div>
              ) : null}
              <p className="orbit-body-xs" style={{ margin: "0.65rem 0 0", color: "#7a6242", lineHeight: 1.45, ...ritualTextWrap }}>
                {RITUAL_COPY.ritualDayReadyFootnote}
              </p>
            </div>

            <div className="today-web-hero__cta">
              <button
                type="button"
                onClick={() => props.onRefreshToday()}
                className="orbit-button orbit-button-secondary"
                style={{
                  width: "100%",
                  justifyContent: "center",
                  padding: "0.85rem 1.2rem",
                  fontSize: "1rem",
                  ...ritualTextWrap,
                }}
              >
                {RITUAL_COPY.refreshDayCta}
              </button>
              <p
                className="orbit-body-xs"
                style={{ margin: "0.5rem 0 0", color: "#a89880", lineHeight: 1.45, ...ritualTextWrap }}
              >
                {props.energyScoreIsPlaceholder ? (
                  <>
                    {RITUAL_COPY.heroRhythmCaption}: {RITUAL_COPY.heroRhythmScorePending}
                  </>
                ) : (
                  <>
                    {RITUAL_COPY.heroRhythmCaption}: {rhythmTierLabelForScore(props.energyScore)} ·{" "}
                    {RITUAL_COPY.heroScoreFootnote(min100(props.energyScore))}
                  </>
                )}
              </p>
            </div>
          </>
        ) : (
          <>
            <div
              className="todayflow-surface-soft"
              style={{
                borderRadius: 20,
                padding: "1.1rem 1.15rem",
                border: "1px solid rgba(201,168,115,0.22)",
                minWidth: 0,
                maxWidth: "100%",
                boxSizing: "border-box",
              }}
            >
              <p className="todayflow-eyebrow" style={{ margin: "0 0 0.45rem", ...ritualTextWrap }}>
                {props.displayDate}
              </p>
              <h1
                className="todayflow-title-hero"
                style={{ fontSize: "clamp(1.35rem, 3.4vw, 1.75rem)", lineHeight: 1.22, margin: 0, ...ritualTextWrap }}
              >
                {ritualSpineComplete && guideNarrativeLoading
                  ? RITUAL_COPY.ritualComposeLoadingTitle
                  : RITUAL_COPY.ritualEntryTitle}
              </h1>
              <p className="orbit-body-sm" style={{ margin: "0.55rem 0 0", color: "#5f4930", lineHeight: 1.55, ...ritualTextWrap }}>
                {ritualSpineComplete && guideNarrativeLoading
                  ? RITUAL_COPY.ritualComposeLoadingBody
                  : formatRitualEntryProgressTarotNumberHint({
                      drawnTarotNameRu: drawnTarotMain?.nameRu,
                      numerologyValue: props.numerologyValue,
                      numberRevealed,
                    })}
              </p>
            </div>
            <div className="today-web-hero__cta">
              <p className="orbit-body-xs" style={{ margin: 0, color: "#a89880", lineHeight: 1.5, textAlign: "center", ...ritualTextWrap }}>
                {props.energyScoreIsPlaceholder ? (
                  <>
                    {RITUAL_COPY.heroRhythmCaption}: {RITUAL_COPY.heroRhythmScorePending}
                  </>
                ) : (
                  <>
                    {RITUAL_COPY.heroRhythmCaption}: {rhythmTierLabelForScore(props.energyScore)} ·{" "}
                    {RITUAL_COPY.heroScoreFootnote(min100(props.energyScore))}
                  </>
                )}
              </p>
            </div>
          </>
        )}
      </section>

      {showCardSection && (
        <>
          {ritualSpineComplete && guideNarrativeLoading ? (
            <div
              id="today-ritual-compose"
              role="status"
              aria-live="polite"
              style={{
                position: "fixed",
                inset: 0,
                zIndex: 60,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                padding: "1.5rem",
                background: "rgba(28, 22, 18, 0.38)",
                backdropFilter: "blur(10px)",
                WebkitBackdropFilter: "blur(10px)",
              }}
            >
              <div
                style={{
                  maxWidth: "20rem",
                  width: "100%",
                  borderRadius: 22,
                  padding: "1.35rem 1.25rem",
                  textAlign: "center",
                  background: "linear-gradient(165deg, rgba(255,252,248,0.98), rgba(255,236,218,0.94))",
                  border: "1px solid rgba(201,168,115,0.35)",
                  boxShadow: "0 18px 48px rgba(60, 40, 28, 0.2)",
                }}
              >
                <LoadingSpinner size="md" />
                <p
                  className="orbit-heading-3"
                  style={{
                    margin: "0.85rem 0 0.35rem",
                    fontFamily: "var(--orbit-font-display, Georgia, serif)",
                    color: "#2d241c",
                    ...ritualTextWrap,
                  }}
                >
                  {RITUAL_COPY.ritualComposeLoadingTitle}
                </p>
                <p className="orbit-body-sm" style={{ margin: 0, color: "#5f4930", lineHeight: 1.55, ...ritualTextWrap }}>
                  {RITUAL_COPY.ritualComposeLoadingBody}
                </p>
              </div>
            </div>
          ) : null}
          {!ritualSpineComplete ? (
            <>
          <div className="today-web-card-grid" style={{ marginTop: "1.25rem", minWidth: 0, width: "100%" }}>
          {/* BLOCK 2a — Карта дня (пошаговый ритуал, как на макете — раньше числа) */}
          <section id="today-ritual-card" className="todayflow-surface-primary todayflow-inset" style={{ marginTop: 0, ...ritualSectionContain }}>
            <h2
              className="orbit-heading-3"
              style={{
                margin: "0 0 0.45rem",
                fontFamily: "var(--orbit-font-display, Georgia, serif)",
                color: "#2d241c",
                ...ritualTextWrap,
              }}
            >
              {RITUAL_COPY.cardEyebrow}
            </h2>
            <p className="orbit-body-sm" style={{ margin: "0 0 0.75rem", color: "#5f4930", lineHeight: 1.55, ...ritualTextWrap }}>
              {tarotRitualCompact ? RITUAL_COPY.tarotCardSubheadAfterPick : RITUAL_COPY.tarotCardSubhead}
            </p>
            {tarotRitualCompact && drawnTarotMain ? (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.85rem",
                  minWidth: 0,
                  padding: "0.25rem 0 0.15rem",
                }}
              >
                {tarotMainId != null && tarotCardFaceSrc(tarotMainId) ? (
                  <div
                    style={{
                      width: TAROT_SPINE_THUMB_WIDTH_PX,
                      height: tarotCardDisplayHeightPx(TAROT_SPINE_THUMB_WIDTH_PX),
                      flexShrink: 0,
                      borderRadius: 10,
                      overflow: "hidden",
                      border: "1px solid rgba(214,142,122,0.35)",
                      background: "#faf6f2",
                    }}
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={tarotCardFaceSrc(tarotMainId)!}
                      alt=""
                      width={TAROT_CARD_PIXEL_WIDTH}
                      height={TAROT_CARD_PIXEL_HEIGHT}
                      style={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }}
                      draggable={false}
                    />
                  </div>
                ) : null}
                <div style={{ minWidth: 0 }}>
                  <p className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#2d241c", ...ritualTextWrap }}>
                    {drawnTarotMain.nameRu}
                  </p>
                  <p className="orbit-body-xs" style={{ margin: "0.25rem 0 0", color: "#6a5132", lineHeight: 1.5, ...ritualTextWrap }}>
                    {RITUAL_COPY.tarotCompactHint}
                  </p>
                </div>
              </div>
            ) : (
            <div style={{ minHeight: tarotMainId == null ? 240 : "auto", minWidth: 0, maxWidth: "100%" }}>
              {!tarotContinueAck ? (
                <RitualTarotPickExperience
                  anchorCardId={anchorTarotId}
                  resumeCommittedId={tarotMainId}
                  cardTitleRu={anchorTarotRecord?.nameRu ?? props.cardName}
                  tagLabels={anchorTarotTags}
                  reduceMotion={reduceMotion}
                  onCommitMain={commitTarotMain}
                  onContinue={onContinueFromTarotReveal}
                />
              ) : !numberRevealed ? (
                <p className="orbit-body-sm" style={{ margin: "0.15rem 0 0", color: "#5f4930", lineHeight: 1.55, ...ritualTextWrap }}>
                  {RITUAL_COPY.tarotBridgeToNumber}
                </p>
              ) : null}
            </div>
            )}
            {!tarotContinueAck && tarotMainId == null ? (
              <p className="orbit-body-xs" style={{ margin: "0.75rem 0 0", color: "#7a6a52", lineHeight: 1.45, ...ritualTextWrap }}>
                {RITUAL_COPY.tarotAnimationTroubleHint}{" "}
                <button
                  type="button"
                  onClick={() => {
                    commitTarotMain(anchorTarotId);
                  }}
                  className="orbit-button orbit-button-secondary orbit-button-sm"
                  style={{ marginTop: 6, ...ritualTextWrap }}
                >
                  {RITUAL_COPY.tarotCommitWithoutRitualCta}
                </button>
              </p>
            ) : null}
          </section>

          {/* BLOCK 2b — Число дня */}
          <section
            id="today-ritual-number"
            className="todayflow-surface-soft todayflow-inset"
            style={{ marginTop: 0, ...ritualSectionContain }}
          >
            <h2
              className="orbit-heading-3"
              style={{
                margin: "0 0 0.45rem",
                fontFamily: "var(--orbit-font-display, Georgia, serif)",
                color: "#2d241c",
                ...ritualTextWrap,
              }}
            >
              {RITUAL_COPY.numberDayLead}
            </h2>
            {!numberRevealed ? (
              <>
                <p className="orbit-body-sm" style={{ margin: "0 0 0.65rem", color: "#4a3d2e", lineHeight: 1.55, ...ritualTextWrap }}>
                  {RITUAL_COPY.numberDaySubPick}
                </p>
                <RitualNumberPickExperience
                  systemDisplay={props.numerologyValue}
                  reduceMotion={reduceMotion}
                  onComplete={onRevealNumber}
                />
              </>
            ) : numberRitualCompact ? (
              <div
                className="todayflow-surface-soft"
                style={{
                  marginTop: "0.15rem",
                  padding: "0.75rem 0.85rem",
                  borderRadius: 16,
                  background: "rgba(255,252,247,0.95)",
                  border: "1px solid rgba(201,168,115,0.22)",
                  ...ritualTextWrap,
                }}
              >
                <p className="orbit-body-sm" style={{ margin: 0, color: "#2d241c", lineHeight: 1.45, ...ritualTextWrap }}>
                  <span style={{ fontWeight: 800, fontVariantNumeric: "tabular-nums", fontSize: "1.4rem" }}>{props.numerologyValue}</span>
                  <span style={{ color: "#6a5132", fontWeight: 600 }}> · </span>
                  <span style={{ color: "#4a3d2e", fontWeight: 600 }}>{RITUAL_COPY.numberRevealScreenTitle}</span>
                </p>
                <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#6a5132", lineHeight: 1.5, ...ritualTextWrap }}>
                  {RITUAL_COPY.numberCompactFootnote}
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.3rem", marginTop: "0.45rem" }}>
                  {numberDayTagTriad(props.numerologyValue).map((t) => (
                    <span
                      key={t}
                      style={{
                        fontSize: "0.68rem",
                        fontWeight: 600,
                        color: "#5f4930",
                        padding: "0.16rem 0.45rem",
                        borderRadius: 999,
                        background: "rgba(255, 237, 228, 0.75)",
                        border: "1px solid rgba(214,142,122,0.28)",
                      }}
                    >
                      {t}
                    </span>
                  ))}
                </div>
                <p className="orbit-body-xs" style={{ margin: "0.45rem 0 0", color: "#7a6242", lineHeight: 1.45, ...ritualTextWrap }}>
                  <strong>{RITUAL_COPY.numerologyBestTimeLabel}</strong> — {props.numerologyLucky.time} ·{" "}
                  <strong>{RITUAL_COPY.numerologyColorLabel}</strong> — {props.numerologyLucky.color} ·{" "}
                  <strong>{RITUAL_COPY.numerologyStoneLabel}</strong> — {props.numerologyLucky.stone}
                </p>
              </div>
            ) : (
              <>
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    textAlign: "center",
                    margin: "0.15rem 0 0.5rem",
                  }}
                >
                  <div style={{ position: "relative", width: "100%", maxWidth: 200, minHeight: 96 }}>
                    <div
                      aria-hidden
                      style={{
                        position: "absolute",
                        left: "50%",
                        top: "52%",
                        transform: "translate(-50%, -50%)",
                        width: "min(120px, 42vw)",
                        height: "min(120px, 42vw)",
                        borderRadius: "50%",
                        background: "radial-gradient(circle, rgba(255, 210, 170, 0.55) 0%, rgba(255, 230, 210, 0.22) 42%, transparent 68%)",
                        filter: "blur(10px)",
                        pointerEvents: "none",
                      }}
                    />
                    <p
                      className="orbit-display-sm"
                      style={{
                        position: "relative",
                        margin: 0,
                        paddingTop: "0.35rem",
                        color: "#2b2118",
                        fontSize: "clamp(2.1rem, 6vw, 2.85rem)",
                        fontWeight: 700,
                        fontFamily: "var(--orbit-font-display, Georgia, serif)",
                        textShadow: "0 0 22px rgba(255, 200, 160, 0.55)",
                        ...ritualTextWrap,
                      }}
                    >
                      {props.numerologyValue}
                    </p>
                  </div>
                  <h2
                    className="orbit-heading-3"
                    style={{
                      margin: "0.35rem 0 0.25rem",
                      fontFamily: "var(--orbit-font-display, Georgia, serif)",
                      ...ritualTextWrap,
                    }}
                  >
                    {RITUAL_COPY.numberRevealScreenTitle}
                  </h2>
                </div>
                <p className="orbit-body-sm" style={{ margin: 0, color: "#4a3d2e", lineHeight: 1.6, ...ritualTextWrap }}>
                  {props.numerologyMeaning}
                </p>
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "0.35rem",
                    marginTop: "0.55rem",
                  }}
                >
                  {numberDayTagTriad(props.numerologyValue).map((t) => (
                    <span
                      key={t}
                      style={{
                        fontSize: "0.72rem",
                        fontWeight: 600,
                        color: "#5f4930",
                        padding: "0.2rem 0.55rem",
                        borderRadius: 999,
                        background: "rgba(255, 237, 228, 0.75)",
                        border: "1px solid rgba(214,142,122,0.32)",
                      }}
                    >
                      {t}
                    </span>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={onContinueFromNumber}
                  className="orbit-button orbit-button-primary"
                  style={{
                    width: "100%",
                    marginTop: "0.65rem",
                    background: "linear-gradient(90deg, #d9a78d 0%, #e6beae 52%, #edc5b8 100%)",
                    border: "1px solid rgba(200, 130, 100, 0.35)",
                    color: "#2d1f18",
                    fontWeight: 700,
                    ...ritualTextWrap,
                  }}
                >
                  {RITUAL_COPY.ritualContinueCta}
                </button>
                <div
                  className="orbit-body-xs"
                  style={{
                    display: "grid",
                    gap: "0.25rem",
                    margin: "0.9rem 0 0",
                    color: "#6a5132",
                    lineHeight: 1.45,
                    padding: "0.7rem 0.75rem",
                    background: "rgba(255,255,255,0.65)",
                    borderRadius: 14,
                    border: "1px solid rgba(201,168,115,0.2)",
                    ...ritualTextWrap,
                  }}
                >
                  <div style={ritualTextWrap}>
                    <strong>{RITUAL_COPY.numerologyBestTimeLabel}</strong> — {props.numerologyLucky.time}
                  </div>
                  <div style={ritualTextWrap}>
                    <strong>{RITUAL_COPY.numerologyColorLabel}</strong> — {props.numerologyLucky.color} ·{" "}
                    <strong>{RITUAL_COPY.numerologyStoneLabel}</strong> — {props.numerologyLucky.stone}
                  </div>
                </div>
                {effectiveCardNumberBridge ? (
                  <p className="orbit-body-xs" style={{ margin: "0.8rem 0 0", color: "#5f4930", lineHeight: 1.55, ...ritualTextWrap }}>
                    {effectiveCardNumberBridge}
                  </p>
                ) : null}
                <div style={{ marginTop: "0.85rem", paddingTop: "0.85rem", borderTop: "1px solid rgba(201,168,115,0.18)" }}>
                  <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", color: "#6a5132", fontWeight: 700, ...ritualTextWrap }}>
                    {RITUAL_COPY.numberRhythmQuestion}
                  </p>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                    {RITUAL_NUMBER_RHYTHM_CHIPS.map((c) => (
                      <button
                        key={c.id}
                        type="button"
                        onClick={() => {
                          setNumberRhythm(c.id);
                          trackMeaningEvent({
                            event_type: "number_selected",
                            event_source: "today",
                            payload: { rhythm_need: c.id },
                          });
                        }}
                        className={`orbit-button orbit-button-sm ${numberRhythm === c.id ? "orbit-button-primary" : "orbit-button-secondary"}`}
                        style={{ ...ritualChipWrap, borderRadius: 999, padding: "0.35rem 0.75rem" }}
                      >
                        {c.label}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
          </section>
          </div>

          {tarotContinueAck && numberRevealed && tarotMainId != null && drawnTarotMain ? (
            <section
              id="today-ritual-tarot-depth"
              className="todayflow-surface-soft todayflow-inset"
              style={{ marginTop: "1.25rem", ...ritualSectionContain }}
            >
              <h2
                className="orbit-heading-3"
                style={{
                  margin: "0 0 0.5rem",
                  textAlign: "center",
                  fontFamily: "var(--orbit-font-display, Georgia, serif)",
                  color: "#2d241c",
                  ...ritualTextWrap,
                }}
              >
                {RITUAL_COPY.tarotRevealScreenTitle}
              </h2>
              {tarotCardFaceSrc(tarotMainId) ? (
                <div
                  style={{
                    position: "relative",
                    maxWidth: `min(${TAROT_RITUAL_REVEAL_MAX_WIDTH_PX}px, 90vw)`,
                    margin: "0 auto 0.5rem",
                    aspectRatio: `${TAROT_CARD_PIXEL_WIDTH} / ${TAROT_CARD_PIXEL_HEIGHT}`,
                    borderRadius: 16,
                    overflow: "hidden",
                    border: "1px solid rgba(214,142,122,0.28)",
                    background: "#faf6f2",
                    boxSizing: "border-box",
                    boxShadow: "0 0 48px 14px rgba(255, 200, 160, 0.35), 0 12px 28px rgba(90, 52, 44, 0.1)",
                  }}
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={tarotCardFaceSrc(tarotMainId)!}
                    alt=""
                    width={TAROT_CARD_PIXEL_WIDTH}
                    height={TAROT_CARD_PIXEL_HEIGHT}
                    style={{ width: "100%", height: "100%", objectFit: "contain", objectPosition: "center", display: "block" }}
                    draggable={false}
                  />
                </div>
              ) : null}
              <p
                className="orbit-heading-3"
                style={{
                  margin: "0.15rem 0 0.35rem",
                  textAlign: "center",
                  fontFamily: "var(--orbit-font-display, Georgia, serif)",
                  fontSize: "clamp(1.25rem, 4vw, 1.45rem)",
                  color: "#2d241c",
                  ...ritualTextWrap,
                }}
              >
                {drawnTarotMain.nameRu}
              </p>
              {anchorTarotTagsFromLead(drawnTarotMain.leadRu).length > 0 ? (
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: "0.35rem",
                    justifyContent: "center",
                    marginBottom: "0.45rem",
                  }}
                >
                  {anchorTarotTagsFromLead(drawnTarotMain.leadRu).map((t) => (
                    <span
                      key={t}
                      style={{
                        fontSize: "0.72rem",
                        fontWeight: 600,
                        color: "#5f4930",
                        padding: "0.2rem 0.55rem",
                        borderRadius: 999,
                        background: "rgba(255, 237, 228, 0.75)",
                        border: "1px solid rgba(214,142,122,0.32)",
                      }}
                    >
                      {t}
                    </span>
                  ))}
                </div>
              ) : null}
              <p className="orbit-body-sm" style={{ margin: 0, lineHeight: 1.55, color: "#3f3428", ...ritualTextWrap }}>
                {drawnTarotMain.leadRu}
              </p>
              <p className="orbit-body-sm" style={{ margin: "0.35rem 0 0", lineHeight: 1.55, color: "#4a3d2e", ...ritualTextWrap }}>
                {drawnTarotMain.bodyRu}
              </p>
              {drawnTarotClarifier ? (
                <div
                  style={{
                    marginTop: "0.35rem",
                    padding: "0.65rem 0.75rem",
                    borderRadius: 14,
                    background: "rgba(255,255,255,0.55)",
                    border: "1px solid rgba(201,168,115,0.2)",
                    minWidth: 0,
                    maxWidth: "100%",
                    overflow: "hidden",
                    boxSizing: "border-box",
                  }}
                >
                  <p
                    className="orbit-body-xs"
                    style={{ margin: "0 0 0.35rem", color: "#6a5132", fontWeight: 700, ...ritualTextWrap }}
                  >
                    {RITUAL_COPY.tarotClarifierEyebrow}: {drawnTarotClarifier.nameRu}
                  </p>
                  <p className="orbit-body-xs" style={{ margin: 0, color: "#5f4930", lineHeight: 1.55, ...ritualTextWrap }}>
                    {drawnTarotClarifier.leadRu} {drawnTarotClarifier.bodyRu}
                  </p>
                </div>
              ) : null}
              <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7a6242", lineHeight: 1.5, ...ritualTextWrap }}>
                {RITUAL_COPY.tarotQuestionEyebrow}: {drawnTarotMain.questionRu}
              </p>
              <p className="orbit-body-xs" style={{ margin: 0, color: "#7a6242", lineHeight: 1.5, ...ritualTextWrap }}>
                {RITUAL_COPY.cardRevealedHint}
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem", marginTop: "0.55rem" }}>
                <button
                  type="button"
                  onClick={() => setTarotMeaningOpen(true)}
                  className="orbit-button orbit-button-secondary orbit-button-sm"
                  style={{ ...ritualChipWrap, borderRadius: 999, padding: "0.35rem 0.75rem" }}
                >
                  {RITUAL_COPY.cardWhatMeansButton}
                </button>
                <button
                  type="button"
                  onClick={onApplyTarotToToday}
                  disabled={tarotApplied}
                  className="orbit-button orbit-button-primary orbit-button-sm"
                  style={{ ...ritualChipWrap, borderRadius: 999, padding: "0.35rem 0.75rem" }}
                >
                  {RITUAL_COPY.tarotApplyToTodayCta}
                </button>
                <button
                  type="button"
                  onClick={onDrawTarot}
                  disabled={tarotClarifierId != null}
                  className="orbit-button orbit-button-secondary orbit-button-sm"
                  style={{ ...ritualChipWrap, borderRadius: 999, padding: "0.35rem 0.75rem" }}
                  title={RITUAL_COPY.tarotDrawAnotherHint}
                >
                  {RITUAL_COPY.tarotDrawAnotherCta}
                </button>
              </div>
              {tarotClarifierId != null ? (
                <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#7a6a52", lineHeight: 1.45, ...ritualTextWrap }}>
                  {RITUAL_COPY.tarotDrawAnotherHint}
                </p>
              ) : null}
              {tarotApplied ? (
                <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#5f4930", lineHeight: 1.5, ...ritualTextWrap }}>
                  {RITUAL_COPY.tarotAppliedAck}
                </p>
              ) : null}
              <div style={{ marginTop: "0.85rem", paddingTop: "0.85rem", borderTop: "1px solid rgba(201,168,115,0.22)" }}>
                <p className="orbit-body-xs" style={{ margin: "0 0 0.45rem", color: "#6a5132", fontWeight: 700, ...ritualTextWrap }}>
                  {RITUAL_COPY.cardHonestStepQuestion}
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
                  {RITUAL_CARD_HONEST_STEP_CHIPS.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => {
                        setHonestStep(c.id);
                        trackMeaningEvent({
                          event_type: "sphere_feedback",
                          event_source: "today",
                          payload: { tarot_honest_step: c.id },
                        });
                      }}
                      className={`orbit-button orbit-button-sm ${honestStep === c.id ? "orbit-button-primary" : "orbit-button-secondary"}`}
                      style={{ ...ritualChipWrap, borderRadius: 999, padding: "0.35rem 0.75rem" }}
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setFocusSavedAck(true);
                    trackMeaningEvent({
                      event_type: "focus_started",
                      event_source: "today",
                      payload: { from_tarot_depth: true, honest_step: honestStep || "unset" },
                    });
                  }}
                  className="orbit-button orbit-button-secondary orbit-button-sm"
                  style={{ width: "100%", marginTop: "0.55rem", justifyContent: "center", ...ritualTextWrap }}
                >
                  {RITUAL_COPY.cardSaveFocus}
                </button>
                {focusSavedAck ? (
                  <p className="orbit-body-xs" style={{ margin: "0.35rem 0 0", color: "#5f4930", lineHeight: 1.5, ...ritualTextWrap }}>
                    {RITUAL_COPY.cardSaveFocusDone}
                  </p>
                ) : null}
              </div>
            </section>
          ) : null}

          {/* BLOCK 5 — Check-in (после числа: паритет iOS `TodayRitualSpineTransition` / конечный автомат) */}
          {numberRevealed ? (
          <section
            id="today-ritual-checkin"
            className="todayflow-surface-soft todayflow-inset"
            style={{ marginTop: "1.25rem", ...ritualSectionContain }}
          >
            <h2
              className="orbit-heading-3"
              style={{
                margin: "0 0 0.35rem",
                fontFamily: "var(--orbit-font-display, Georgia, serif)",
                ...ritualTextWrap,
              }}
            >
              {RITUAL_COPY.checkInTitle}
            </h2>
            <p className="orbit-body-sm" style={{ margin: "0 0 0.75rem", color: "#5f4930", lineHeight: 1.55, ...ritualTextWrap }}>
              {mood ? RITUAL_COPY.moodCheckSubDone : RITUAL_COPY.moodCheckSub}
            </p>
            {mood ? (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.55rem",
                  flexWrap: "wrap",
                  padding: "0.55rem 0.7rem",
                  borderRadius: 14,
                  background: "rgba(255,252,247,0.95)",
                  border: "1px solid rgba(201,168,115,0.28)",
                  maxWidth: "100%",
                  boxSizing: "border-box",
                }}
              >
                <span aria-hidden style={{ fontSize: "1.05rem", lineHeight: 1 }}>
                  {RITUAL_MOOD_GRID.find((x) => x.id === mood)?.icon ?? "✓"}
                </span>
                <span className="orbit-body-sm" style={{ margin: 0, fontWeight: 700, color: "#2d241c", ...ritualTextWrap }}>
                  {labelForRitualMoodId(mood)}
                </span>
                <span className="orbit-body-xs" style={{ margin: 0, color: "#7a6242" }}>
                  {RITUAL_COPY.checkInMoodMarkedTail}
                </span>
              </div>
            ) : (
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                  gap: "0.4rem",
                  maxWidth: "min(20.5rem, 100%)",
                  width: "100%",
                  margin: "0 auto",
                }}
              >
                {RITUAL_MOOD_GRID.map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => onMood(m.id)}
                    className={`orbit-button orbit-button-sm ${mood === m.id ? "orbit-button-primary" : "orbit-button-secondary"}`}
                    style={{
                      ...ritualChipWrap,
                      borderRadius: 12,
                      padding: "0.42rem 0.32rem",
                      minHeight: "4.1rem",
                      border: "1px solid rgba(201, 168, 115, 0.32)",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "0.22rem",
                    }}
                  >
                    <span style={{ fontSize: "1rem", lineHeight: 1, fontWeight: 300, opacity: 0.92 }} aria-hidden>
                      {m.icon}
                    </span>
                    <span style={{ fontSize: "0.72rem", fontWeight: 600, textAlign: "center", lineHeight: 1.2 }}>{m.label}</span>
                  </button>
                ))}
              </div>
            )}
            {mood && moodNote && (
              <p className="orbit-body-sm" style={{ margin: "0.6rem 0 0", color: "#4a3d2e", ...ritualTextWrap }}>
                {moodNote}
              </p>
            )}
            {mood ? (
              <div style={{ marginTop: "0.85rem" }}>
                <p className="todayflow-eyebrow" style={{ margin: "0 0 0.35rem", ...ritualTextWrap }}>
                  {RITUAL_COPY.checkInMicroEyebrow}
                </p>
                <p className="orbit-body-sm" style={{ margin: "0 0 0.55rem", color: "#5f4930", lineHeight: 1.55, ...ritualTextWrap }}>
                  {RITUAL_COPY.checkInMicroHint}
                </p>
                {headTopic ? (
                  <p className="orbit-body-sm" style={{ margin: 0, color: "#3f3428", fontWeight: 600, ...ritualTextWrap }}>
                    {RITUAL_COPY.headTopicSavedLabel}:{" "}
                    {RITUAL_HEAD_TOPIC_CHIPS.find((t) => t.id === headTopic)?.label ?? headTopic}
                  </p>
                ) : (
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                    {RITUAL_HEAD_TOPIC_CHIPS.map((t) => (
                      <button
                        key={t.id}
                        type="button"
                        onClick={() => {
                          setHeadTopic(t.id);
                          trackMeaningEvent({
                            event_type: "head_topic_selected",
                            event_source: "today",
                            payload: { topic_id: t.id },
                          });
                        }}
                        className={`orbit-button orbit-button-sm ${headTopic === t.id ? "orbit-button-primary" : "orbit-button-secondary"}`}
                        style={{ ...ritualChipWrap, borderRadius: 999, padding: "0.4rem 0.85rem" }}
                      >
                        {t.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : null}
            {mood ? (
              <button
                type="button"
                onClick={() => {
                  const snap = buildRitualSpineSnapshotWeb({
                    showCardSection,
                    tarotContinueAck,
                    numberRevealed,
                    tarotMainId,
                    mood,
                    checkInSubmitted,
                    guideNarrativeLoading: guideNarrativeLoading,
                  });
                  const out = applyTodayRitualSpineReducer({ type: "submittedCheckIn" }, snap);
                  if (!out) return;
                  setCheckInSubmitted(out.after.checkInSubmitted);
                }}
                className="orbit-button orbit-button-primary"
                style={{
                  width: "100%",
                  marginTop: "0.85rem",
                  background: "linear-gradient(90deg, #d9a78d 0%, #e6beae 52%, #edc5b8 100%)",
                  border: "1px solid rgba(200, 130, 100, 0.35)",
                  color: "#2d1f18",
                  fontWeight: 700,
                  ...ritualTextWrap,
                }}
              >
                {RITUAL_COPY.ritualMoodDoneCta}
              </button>
            ) : null}
          </section>
          ) : null}
            </>
          ) : null}
          {ritualSpineComplete && ritualDayUnlocked ? (
            <TodayResultView
              ritualTextWrap={ritualTextWrap}
              ritualSectionContain={ritualSectionContain}
              ritualChipWrap={ritualChipWrap}
              fourAll={fourAll}
              sphereTriadRows={sphereTriadRows}
              mood={mood}
              lowEnergyRitualMood={lowEnergyRitualMood}
              actionOptionsRich={actionOptionsRich}
              selectedActionOption={selectedActionOption}
              onSelectActionOption={setSelectedActionOption}
              focusSessionHint={focusSessionHint}
              setFocusSessionHint={setFocusSessionHint}
              onOpenHabit={props.onOpenHabit}
              onStartFocus20Minutes={props.onStartFocus20Minutes}
              supportHooksList={supportHooksList}
              hasGoals={hasGoals}
              weeklyGoals={props.weeklyGoals}
              goalIdeas={goalIdeas}
              essentials={essentials}
              setEssentials={setEssentials}
              essentialsList={essentialsList}
              essentialsCount={essentialsCount}
              essentialsProgress={essentialsProgress}
              todayData={props.todayData}
              eveningPayload={eveningPayload}
              eveningNarrativeLoading={eveningNarrativeLoading}
              eveningCustomPhrase={props.eveningCustomPhrase}
              eveningMarkedDone={props.eveningMarkedDone}
              eveningObservations={props.eveningObservations}
              eveningReflectionInput={props.eveningReflectionInput}
              eveningSaving={props.eveningSaving}
              onEveningCustomPhraseChange={props.onEveningCustomPhraseChange}
              onEveningMarkedDoneChange={props.onEveningMarkedDoneChange}
              onEveningObservationChange={props.onEveningObservationChange}
              onEveningReflectionChange={props.onEveningReflectionChange}
              onSaveEvening={props.onSaveEvening}
              onRefreshToday={props.onRefreshToday}
              onEveningPhaseSaved={props.onEveningPhaseSaved}
              eveningTarotLine={eveningTarotLine}
              eveningHourCompact={eveningHourCompact}
              narrativeGenerationIds={props.narrativeGenerationIds}
              guideMeaningCompletionsToday={props.fusion?.activity_context?.guide_meaning_completions_today ?? null}
              fusionDayHistoryLine={fusionDayHistoryLine}
              fusionDayHistoryWeekLine={fusionDayHistoryWeekLineForUi}
              fusionDayHistoryMeaningLine={fusionDayHistoryMeaningLine}
              fusionDayHistoryReflectionLine={fusionDayHistoryReflectionLine}
              fusionDayHistoryFooterHint={fusionDayHistoryFooterHint}
              sphereScoresProvisional={sphereScoresProvisional}
              todayContract={props.todayContract}
            />
          ) : null}
        </>
      )}

      {cardNumberDetailOpen && tarotMainId != null && drawnTarotMain ? (
        <div
          role="dialog"
          aria-modal
          aria-labelledby="today-card-number-detail-title"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 52,
            background: "rgba(15, 15, 15, 0.35)",
            display: "flex",
            alignItems: "flex-end",
            justifyContent: "center",
          }}
          onClick={() => setCardNumberDetailOpen(false)}
        >
          <div
            className="todayflow-surface-primary todayflow-inset"
            onClick={(e) => e.stopPropagation()}
            style={{
              width: "100%",
              maxWidth: 560,
              maxHeight: "78vh",
              overflow: "auto",
              borderRadius: "20px 20px 0 0",
              marginBottom: 0,
            }}
          >
            <h3 id="today-card-number-detail-title" className="orbit-heading-3" style={{ margin: "0 0 0.5rem", ...ritualTextWrap }}>
              {RITUAL_COPY.ritualCardNumberDetailTitle}
            </h3>
            {tarotCardFaceSrc(tarotMainId) ? (
              <div
                style={{
                  position: "relative",
                  maxWidth: `min(${TAROT_RITUAL_REVEAL_MAX_WIDTH_PX}px, 88vw)`,
                  margin: "0 auto 0.65rem",
                  aspectRatio: `${TAROT_CARD_PIXEL_WIDTH} / ${TAROT_CARD_PIXEL_HEIGHT}`,
                  borderRadius: 16,
                  overflow: "hidden",
                  border: "1px solid rgba(214,142,122,0.28)",
                  background: "#faf6f2",
                }}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={tarotCardFaceSrc(tarotMainId)!}
                  alt=""
                  width={TAROT_CARD_PIXEL_WIDTH}
                  height={TAROT_CARD_PIXEL_HEIGHT}
                  style={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }}
                  draggable={false}
                />
              </div>
            ) : null}
            <p className="orbit-body-sm" style={{ margin: "0 0 0.35rem", fontWeight: 700, color: "#2d241c", ...ritualTextWrap }}>
              {drawnTarotMain.nameRu}
            </p>
            <p className="orbit-body-sm" style={{ margin: "0 0 0.75rem", color: "#3f3428", lineHeight: 1.55, ...ritualTextWrap }}>
              {drawnTarotMain.leadRu} {drawnTarotMain.bodyRu}
            </p>
            <p className="todayflow-eyebrow" style={{ margin: "0 0 0.35rem", ...ritualTextWrap }}>
              {formatRitualCardNumberDetailEyebrow(props.numerologyValue)}
            </p>
            <p className="orbit-body-sm" style={{ margin: "0 0 0.75rem", color: "#4a3d2e", lineHeight: 1.55, ...ritualTextWrap }}>
              {props.numerologyMeaning}
            </p>
            <p className="orbit-body-xs" style={{ margin: "0 0 1rem", color: "#6a5132", lineHeight: 1.45, ...ritualTextWrap }}>
              <strong>{RITUAL_COPY.numerologyBestTimeLabel}</strong> — {props.numerologyLucky.time} ·{" "}
              <strong>{RITUAL_COPY.numerologyColorLabel}</strong> — {props.numerologyLucky.color} ·{" "}
              <strong>{RITUAL_COPY.numerologyStoneLabel}</strong> — {props.numerologyLucky.stone}
            </p>
            {effectiveCardNumberBridge ? (
              <p className="orbit-body-xs" style={{ margin: "0 0 1rem", color: "#5f4930", lineHeight: 1.55, ...ritualTextWrap }}>
                {effectiveCardNumberBridge}
              </p>
            ) : null}
            <button
              type="button"
              onClick={() => setCardNumberDetailOpen(false)}
              className="orbit-button orbit-button-primary"
              style={{ width: "100%", ...ritualTextWrap }}
            >
              {RITUAL_COPY.sheetCloseCta}
            </button>
          </div>
        </div>
      ) : null}

      {/* Tarot card meaning (не «почему система выбрала», а что означает символ, который ты вытянула) */}
      {tarotMeaningOpen && (
        <div
          role="dialog"
          aria-modal
          aria-labelledby="today-tarot-meaning-title"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 50,
            background: "rgba(15, 15, 15, 0.35)",
            display: "flex",
            alignItems: "flex-end",
            justifyContent: "center",
          }}
          onClick={() => setTarotMeaningOpen(false)}
        >
          <div
            className="todayflow-surface-primary todayflow-inset"
            onClick={(e) => e.stopPropagation()}
            style={{ width: "100%", maxWidth: 560, maxHeight: "55vh", overflow: "auto", borderRadius: "20px 20px 0 0", marginBottom: 0 }}
          >
            <h3 id="today-tarot-meaning-title" className="orbit-heading-3" style={{ margin: "0 0 0.5rem", ...ritualTextWrap }}>
              {RITUAL_COPY.cardMeaningPopoverTitle}
            </h3>
            <p className="orbit-body-sm" style={{ margin: "0 0 1rem", color: "#3f3428", lineHeight: 1.6, ...ritualTextWrap }}>
              {RITUAL_COPY.cardMeaningPopoverBody}
            </p>
            <button
              type="button"
              onClick={() => setTarotMeaningOpen(false)}
              className="orbit-button orbit-button-primary"
              style={{ width: "100%", ...ritualTextWrap }}
            >
              {RITUAL_COPY.cardMeaningAckCta}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
