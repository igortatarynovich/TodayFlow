"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { buildOnboardingRitualContext, readOnboardingContext, todayDayKey } from "@/lib/onboardingContext";
import { GuestFirstTodayScreen } from "@/components/onboarding/valueFirst/GuestFirstTodayScreen";
import { hasGuestPreview, readGuestProfileDraft } from "@/lib/guestProfileDraft";
import { markFirstTodayCompleted } from "@/lib/firstTodayState";
import { getJson, postJson, putJson } from "@/lib/api";
import {
  CORE_PROFILE_UPDATED_EVENT,
  type CoreProfileUpdatedDetail,
  resolveCoreProfileAgainstSessionCache,
  writeCoreProfileToCache,
} from "@/lib/coreProfileCacheStorage";
import type { AccountProfile, CoreProfile, MeaningRingsResponse, QuestionsHubContextResponse, UserSettings } from "@/lib/types";
import { insightDepthFromProfile } from "@/lib/insightDepth";
import {
  type NarrativeDepthLevel,
  effectiveNarrativeDepth,
} from "@/lib/todayNarrativeDepthUi";
import { TodayNarrativeDepthControl } from "@/components/today/TodayNarrativeDepthControl";
import { TodayWebDashboard } from "@/components/product-ui/TodayWebDashboard";
import { ProductPageScreen } from "@/components/product-ui/ProductPageScreen";
import {
  buildTodayWebPractices,
  buildTodayWebStreak,
  buildTodayWebTimeline,
  buildTodayWebWeeklyActivity,
} from "@/lib/buildTodayWebDashboardData";
import { TodayCompositionSurface } from "@/components/today/composition/TodayCompositionSurface";
import { TodayExperienceSurface } from "@/components/today/experience/TodayExperienceSurface";
import { TODAY_CONTRACT_COPY } from "@/components/today/contract/todayContractCopy";
import { TodayRitualFlow } from "@/components/today/TodayRitualFlow";
import { EntityCreateWizard } from "@/app/tracking/calendar/EntityCreateWizard";
import {
  buildDailyNudge,
  buildDayEnergySummary,
  buildNextAction,
  buildTodayActionPlan,
  getWeekStart,
  inferPreferredSection,
  mergeFullTodayCycleLayers,
  normalizeTodayPayload,
  selectPriorityWeeklyGoal,
  type FusionResponse,
  type MorningRitualData,
  type PracticeResponse,
  type ThinkingMode,
  type TodayCycleData,
  type WeeklyGoal,
  parseTodayFlowTab,
  type TodayFlowTab,
} from "@/components/today/todayPageUtils";
import { useToast } from "@/components/ToastProvider";
import { useTodayCycle } from "@/components/providers/TodayCycleProvider";
import {
  narrativeProfileSelectorPayload,
  narrativeString,
  type TodayGuideRitualContext,
  type TodayRitualNarrativePayload,
} from "@/lib/todayNarrativeApi";
import { fetchTodayNarrativeCached } from "@/lib/todayNarrativeCache";
import { parseCoreMessageFromGuide } from "@/components/today/todayGuideActionable";
import type { TrackerEntityKind } from "@/app/tracking/calendar/trackerEntityCatalog";
import { flushMeaningOutbox, getCachedMeaningRings, refreshMeaningRings } from "@/lib/meaningRuntime";
import { useMeaningRuntime } from "@/hooks/useMeaningRuntime";
import {
  fetchTodayContractV1,
  buildFallbackTodayContract,
  refreshTodayStory,
  type TodayContractV1,
} from "@/lib/todayContract";
import {
  shouldRefreshStoryAfterReveal,
  type DaySymbolPublicView,
} from "@/lib/daySymbolReveal";
import {
  dayStoryHeadline,
  dayStoryLeadParagraph,
  parseContractGenerationId,
  usesDayStorySingleVoice,
} from "@/lib/todayContractMapper";
import {
  buildRitualAvoidSignals,
  buildRitualPossibleSignals,
  buildRitualSupportSignals,
  guidanceSummaryForRitual,
} from "@/components/today/todayRitualSignals";
import { isGarbageRitualActionCue } from "@/components/today/ritualCueSanitizer";
import {
  RITUAL_COPY,
  formatRitualCardNumberBridgePageFallback,
} from "@/components/today/todayRitualCopy";
import { persistEnergyFromFusionResponse } from "@/lib/energyMapStorage";
import { getTodayTarotCardRu } from "@/components/today/todayTarotCardsRu";
import { resolveDailyTarotDeckIndex } from "@/lib/tarotCardAssets";
import { isRuUserFacingText } from "@/lib/todaySynthesisTextPolicy";

export default function TodayPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const firstTodayMode = searchParams.get("first") === "1";
  const coreLoopViabilityMode =
    searchParams.get("core_loop") === "1" || firstTodayMode;
  const todayExperienceMode = searchParams.get("full") !== "1";
  const ritualExperienceMode = searchParams.get("experience") === "1";
  const toast = useToast();
  const { trackMeaningEvent } = useMeaningRuntime();
  const { refetchToday, cycle, todayHeavyLayersPending } = useTodayCycle();
  const cycleRef = useRef<TodayCycleData | null>(null);
  const guidanceFollowupToastShown = useRef(false);
  const experienceVisibleTrackedRef = useRef(false);
  useEffect(() => {
    cycleRef.current = cycle;
  }, [cycle]);

  useEffect(() => {
    if (guidanceFollowupToastShown.current) return;
    if (searchParams.get("from_guidance") !== "1") return;
    guidanceFollowupToastShown.current = true;
    toast.info(RITUAL_COPY.todayToastGuidanceFollowup);
    const next = new URLSearchParams(searchParams.toString());
    next.delete("from_guidance");
    next.delete("flow");
    const q = next.toString();
    router.replace(q ? `/today?${q}` : "/today", { scroll: false });
  }, [searchParams, router, toast]);

  const todayIso = useMemo(() => new Date().toISOString().split("T")[0], []);
  const [loading, setLoading] = useState(true);
  const [todayData, setTodayData] = useState<TodayCycleData | null>(null);
  const [todayContract, setTodayContract] = useState<TodayContractV1 | null>(null);
  const [dayStoryUpdating, setDayStoryUpdating] = useState(false);
  const dayStoryRefreshInFlight = useRef(false);
  const dayStorySingleVoice = useMemo(
    () => usesDayStorySingleVoice(todayContract),
    [todayContract],
  );

  const onSymbolRevealResult = useCallback(async (view: DaySymbolPublicView) => {
    if (!shouldRefreshStoryAfterReveal(view)) return;
    if (dayStoryRefreshInFlight.current) return;
    dayStoryRefreshInFlight.current = true;
    setDayStoryUpdating(true);
    try {
      const result = await refreshTodayStory({ localDate: view.local_date });
      if (result.contract) {
        setTodayContract(result.contract);
      }
    } catch {
      /* keep previous story; symbols already shown; do not pretend story matches new symbols */
    } finally {
      dayStoryRefreshInFlight.current = false;
      setDayStoryUpdating(false);
    }
  }, []);
  const [morningRitualData, setMorningRitualData] = useState<MorningRitualData | null>(null);
  const [fusionData, setFusionData] = useState<FusionResponse | null>(null);
  const [quickPractice, setQuickPractice] = useState<PracticeResponse | null>(null);
  const [coreProfile, setCoreProfile] = useState<CoreProfile | null>(null);
  const loadTodayRef = useRef<(opts?: { force?: boolean }) => Promise<void>>(() => Promise.resolve());
  const [error, setError] = useState<string | null>(null);
  const [expandedSection, setExpandedSection] = useState<string | null>("morning");
  const [todayTab, setTodayTab] = useState<TodayFlowTab>("guide");
  const [eveningSaving, setEveningSaving] = useState(false);
  const [eveningMarkedDone, setEveningMarkedDone] = useState(false);
  const [eveningReflectionInput, setEveningReflectionInput] = useState("");
  const [eveningCustomPhrase, setEveningCustomPhrase] = useState("");
  const [eveningObservations, setEveningObservations] = useState({
    noticed: "",
    hardest: "",
    easier_than_expected: "",
  });
  const [timerSeconds, setTimerSeconds] = useState(0);
  const [timerRunning, setTimerRunning] = useState(false);
  /** Нижняя панель таймера только после явного «Начать 20 минут» на Today. */
  const [todayFocusChromeActive, setTodayFocusChromeActive] = useState(false);
  const [practiceCompleting, setPracticeCompleting] = useState(false);
  const [practiceCompleted, setPracticeCompleted] = useState(false);
  const [weeklyGoals, setWeeklyGoals] = useState<WeeklyGoal[]>([]);
  const [thinkingState, setThinkingState] = useState<{
    active: boolean;
    mode: ThinkingMode;
    startedAt: number;
  } | null>(null);
  const hasLoadedOnceRef = useRef(false);
  const loadTodayInFlightRef = useRef<Promise<void> | null>(null);
  const narrativeDateRef = useRef<string | null>(null);
  const ritualGuideRefreshKeyRef = useRef<string | null>(null);
  /** Последний ritual_context после ритуала — для day_layer / spheres / evening (intent + head_topic). */
  const lastRitualNarrativeContextRef = useRef<TodayGuideRitualContext | null>(null);
  const guideProfileSelectorRef = useRef<Record<string, unknown> | null>(null);
  const eveningProfileSelectorRef = useRef<Record<string, unknown> | null>(null);
  /** После progressive opening+bundle подменяем локальный снимок целиком на полный `/today`. */
  const progressiveFullHydrateRef = useRef(false);

  const [guideGenerationId, setGuideGenerationId] = useState<number | null>(null);
  const [dayLayerGenerationId, setDayLayerGenerationId] = useState<number | null>(null);
  const [spheresGenerationId, setSpheresGenerationId] = useState<number | null>(null);
  const [eveningGenerationId, setEveningGenerationId] = useState<number | null>(null);
  const [guideNarrativePayload, setGuideNarrativePayload] = useState<Record<string, unknown> | null>(null);
  const [guideNarrativeRequestFailed, setGuideNarrativeRequestFailed] = useState(false);
  const [guideNarrativeLoading, setGuideNarrativeLoading] = useState(false);
  const [dayLayerPayload, setDayLayerPayload] = useState<Record<string, unknown> | null>(null);
  const [dayLayerLoading, setDayLayerLoading] = useState(false);
  const [spheresPayload, setSpheresPayload] = useState<Record<string, unknown> | null>(null);
  const [eveningPayload, setEveningPayload] = useState<Record<string, unknown> | null>(null);
  const [eveningLoading, setEveningLoading] = useState(false);
  const [questionsHubContext, setQuestionsHubContext] = useState<QuestionsHubContextResponse | null>(null);
  const [entityWizardOpen, setEntityWizardOpen] = useState(false);
  const [entityWizardKind, setEntityWizardKind] = useState<TrackerEntityKind | null>(null);
  const hiddenQuestionsTabAppliedRef = useRef(false);
  const [supplementaryLoading, setSupplementaryLoading] = useState(false);
  const [meaningRingsData, setMeaningRingsData] = useState<MeaningRingsResponse | null>(null);
  const [accountMe, setAccountMe] = useState<AccountProfile | null>(null);
  const [narrativeDepthLevel, setNarrativeDepthLevel] = useState<NarrativeDepthLevel>("normal");
  const [narrativeDepthLoaded, setNarrativeDepthLoaded] = useState(false);
  const [narrativeDepthSaving, setNarrativeDepthSaving] = useState(false);
  /** Сдвиг зависимостей `fetchTodayNarrativeCached(guide)` после смены DE-8 на экране Today. */
  const [narrativeDepthSeq, setNarrativeDepthSeq] = useState(0);

  const narrativeDepthForRequest = narrativeDepthLoaded ? narrativeDepthLevel : undefined;

  useEffect(() => {
    if (todayHeavyLayersPending) progressiveFullHydrateRef.current = true;
  }, [todayHeavyLayersPending]);

  /** Hydrate from provider cache on remount — skip full-screen spinner when day is warm. */
  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    if (cycle?.date === todayIso) {
      setTodayData(normalizeTodayPayload(cycle));
      setLoading(false);
    }
  }, [isAuthenticated, cycle, todayIso]);

  /** Провайдер: progressive слой → полный `/today`; синхронизируем `todayData` с кэшем. */
  useEffect(() => {
    if (!isAuthenticated || !cycle?.date || !todayData?.date) return;
    if (cycle.date !== todayData.date) return;

    if (progressiveFullHydrateRef.current && !todayHeavyLayersPending) {
      progressiveFullHydrateRef.current = false;
      setTodayData(normalizeTodayPayload(cycle));
      return;
    }

    setTodayData((prev) => mergeFullTodayCycleLayers(prev, cycle));
  }, [isAuthenticated, cycle, todayData?.date, todayHeavyLayersPending]);

  /** Persist fusion energy score for Energy Map when server data is available. */
  useEffect(() => {
    if (typeof fusionData?.scores?.energy !== "number" || !Number.isFinite(fusionData.scores.energy)) return;
    persistEnergyFromFusionResponse(todayIso, fusionData, "today_fusion");
  }, [fusionData, todayIso]);

  useEffect(() => {
    getJson<QuestionsHubContextResponse>("/questions/context")
      .then(setQuestionsHubContext)
      .catch((error) => console.error("Failed to load questions context for today", error));
  }, []);

  useEffect(() => {
    if (typeof window === "undefined" || !isAuthenticated) return;
    const onCoreProfileUpdated = (ev: Event) => {
      const ce = ev as CustomEvent<CoreProfileUpdatedDetail>;
      const next = ce.detail?.profile;
      if (!next) return;
      const astroId = ce.detail?.astroProfileId ?? next.astro?.profile_id ?? null;
      setCoreProfile(next);
      writeCoreProfileToCache(next, astroId);
      setNarrativeDepthSeq((s) => s + 1);
      void loadTodayRef.current({ force: true });
    };
    window.addEventListener(CORE_PROFILE_UPDATED_EVENT, onCoreProfileUpdated);
    return () => window.removeEventListener(CORE_PROFILE_UPDATED_EVENT, onCoreProfileUpdated);
  }, [isAuthenticated]);

  /** Провайдер подмешивает полный `/today`; не затираем свежий core из sessionStorage старым вложенным снимком. */
  useEffect(() => {
    if (!isAuthenticated) {
      setCoreProfile(null);
      return;
    }
    if (!cycle?.date) return;
    const embedded = cycle.core_profile ?? null;
    const resolved = resolveCoreProfileAgainstSessionCache(embedded, null);
    if (resolved != null) {
      setCoreProfile(resolved);
      writeCoreProfileToCache(resolved, null);
    }
  }, [isAuthenticated, cycle?.date, cycle?.core_profile]);

  useEffect(() => {
    if (!isAuthenticated) return;
    flushMeaningOutbox().catch(() => undefined);
    refreshMeaningRings(28).catch(() => undefined);
    const onOnline = () => {
      flushMeaningOutbox().catch(() => undefined);
      refreshMeaningRings(28).catch(() => undefined);
    };
    window.addEventListener("online", onOnline);
    return () => window.removeEventListener("online", onOnline);
  }, [isAuthenticated]);

  const navigateTodayTab = useCallback(
    (tab: TodayFlowTab) => {
      setTodayTab(tab);
      if (tab === "morning" || tab === "day" || tab === "evening") {
        setExpandedSection(tab);
      }
      const next = new URLSearchParams(searchParams.toString());
      next.set("step", tab);
      router.replace(`/today?${next.toString()}`, { scroll: false });
    },
    [router, searchParams],
  );

  const openEntityWizard = useCallback((kind: TrackerEntityKind) => {
    setEntityWizardKind(kind);
    setEntityWizardOpen(true);
  }, []);

  const onFirstTodayVisible = useCallback(() => {
    markFirstTodayCompleted(todayDayKey());
    if (experienceVisibleTrackedRef.current) return;
    experienceVisibleTrackedRef.current = true;
    trackMeaningEvent({
      event_type: "core_loop_viability_surface_visible",
      event_source: "today",
      payload: { instrument: "first_today_v1", first_today: true },
      idempotency_key: `first-today-visible-${new Date().toISOString().split("T")[0]}`,
      refreshRings: false,
    });
  }, [trackMeaningEvent]);

  const onExperienceSurfaceVisible = useCallback(() => {
    if (experienceVisibleTrackedRef.current) return;
    experienceVisibleTrackedRef.current = true;
    trackMeaningEvent({
      event_type: "core_loop_viability_surface_visible",
      event_source: "today",
      payload: { instrument: "experience_v0" },
      idempotency_key: `today-experience-visible-${new Date().toISOString().split("T")[0]}`,
    });
  }, [trackMeaningEvent]);

  const onExperienceActionComplete = useCallback(() => {
    const dateKey = todayData?.date ?? new Date().toISOString().split("T")[0];
    trackMeaningEvent({
      event_type: "action_option_selected",
      event_source: "today",
      payload: { experience_v0: true, primary_step: true },
      idempotency_key: `today-experience-action-${dateKey}`,
    });
  }, [trackMeaningEvent, todayData?.date]);

  const loadToday = useCallback(
    async (opts?: { force?: boolean }) => {
      const force = Boolean(opts?.force);
      if (!force && loadTodayInFlightRef.current) {
        return loadTodayInFlightRef.current;
      }

      const run = (async () => {
        const initialLoad = !hasLoadedOnceRef.current;
        const startedAt = initialLoad ? Date.now() : null;
        const warmCache = cycleRef.current?.date === todayIso;
        try {
          if (initialLoad && !warmCache) {
            setLoading(true);
            setThinkingState({ active: true, mode: "initial", startedAt: startedAt || Date.now() });
          }
          setError(null);
          const todayIso = new Date().toISOString().split("T")[0];
          const experienceMode = searchParams.get("full") !== "1";
          const ritualPromise = getJson<MorningRitualData>(
            `/morning-ritual/today?target_date=${encodeURIComponent(todayIso)}`,
          ).catch(() => null);
          const contractPromise = fetchTodayContractV1(todayIso).catch(() => null);
          let data: TodayCycleData | null = null;
          if (!force) {
            const cached = cycleRef.current;
            if (cached?.date === todayIso) {
              data = cached;
            }
          }
          if (!data) {
            data = await refetchToday({ force });
          }
          const ritualPayload = await ritualPromise;
          let contractPayload = await contractPromise;
          if (!data) {
            throw new Error(RITUAL_COPY.todayPageLoadError);
          }
          const normalized = normalizeTodayPayload(data);
          const core = resolveCoreProfileAgainstSessionCache(
            normalized.core_profile ?? null,
            normalized.core_profile?.astro?.profile_id ?? null,
          );
          if (!contractPayload) {
            contractPayload = buildFallbackTodayContract({ coreProfile: core });
          }
          setTodayData(normalized);
          setTodayContract(contractPayload);
          // C1: baseline first; poll enrichment without blocking paint.
          const lcRaw = (contractPayload?.progress as Record<string, unknown> | undefined)
            ?.generation_lifecycle;
          const jobId =
            lcRaw && typeof lcRaw === "object" && typeof (lcRaw as { job_id?: unknown }).job_id === "number"
              ? (lcRaw as { job_id: number }).job_id
              : null;
          const lcStatus =
            lcRaw && typeof lcRaw === "object"
              ? String((lcRaw as { status?: unknown }).status || "")
              : "";
          if (jobId != null && (lcStatus === "enrichment_pending" || lcStatus === "stale")) {
            setDayStoryUpdating(true);
            void import("@/lib/pollGenerationJob").then(({ pollTodayJob }) =>
              pollTodayJob(jobId).then((polled) => {
                if (polled?.lifecycle.status === "enriched" && polled.contract) {
                  setTodayContract(polled.contract as typeof contractPayload);
                }
                setDayStoryUpdating(false);
              }),
            );
          }
          setCoreProfile(core);
          if (core) {
            writeCoreProfileToCache(core, core.astro?.profile_id ?? null);
          }
          const morningFromCycle = (normalized.morning as MorningRitualData) || null;
          if (ritualPayload) {
            setMorningRitualData({
              ...morningFromCycle,
              ...ritualPayload,
              celestial_events:
                ritualPayload.celestial_events ?? morningFromCycle?.celestial_events ?? undefined,
              daily_horoscope:
                ritualPayload.daily_horoscope ?? morningFromCycle?.daily_horoscope ?? undefined,
            });
          } else {
            setMorningRitualData(morningFromCycle);
          }
          setLoading(false);
          if (initialLoad) {
            setThinkingState(null);
          }
          hasLoadedOnceRef.current = true;

          if (!experienceMode) {
            const weekStart = getWeekStart(todayIso);
            const monthStart = `${todayIso.slice(0, 7)}-01`;
            setSupplementaryLoading(true);
            Promise.all([
              getJson<FusionResponse>(`/tracking/fusion/${todayIso}`).catch(() => null),
              getJson<PracticeResponse>("/practices/current")
                .catch(async () => {
                  const fallback = await getJson<PracticeResponse[]>("/practices?limit=1").catch(() => []);
                  return fallback.length ? fallback[0] : null;
                }),
              getJson<WeeklyGoal[]>(`/tracking/weekly-goals?week_start=${weekStart}&scope=week`).catch(() => []),
              getJson<WeeklyGoal[]>(`/tracking/weekly-goals?week_start=${monthStart}&scope=month`).catch(() => []),
            ])
              .then(([fusion, practice, weekGoals, monthGoals]) => {
                setFusionData(fusion);
                setQuickPractice(practice);
                const wg = Array.isArray(weekGoals) ? weekGoals : [];
                const mg = Array.isArray(monthGoals) ? monthGoals : [];
                const merged = [...wg, ...mg];
                const byId = new Map(merged.map((g) => [g.id, g]));
                setWeeklyGoals(Array.from(byId.values()));
                if (practice?.duration_minutes && practice.duration_minutes > 0) {
                  setTimerSeconds(practice.duration_minutes * 60);
                } else {
                  setTimerSeconds(300);
                }
                setTimerRunning(false);
                setPracticeCompleted(false);
              })
              .catch((err) => {
                console.warn("Supplementary today data failed to load", err);
              })
              .finally(() => {
                setSupplementaryLoading(false);
              });
          }
      } catch (err: any) {
        console.error("Error loading today:", err);
        setError(err?.message || RITUAL_COPY.todayPageLoadError);
        setLoading(false);
        setSupplementaryLoading(false);
        if (initialLoad) {
          setThinkingState(null);
        }
      }
      })();

      if (!force) {
        loadTodayInFlightRef.current = run;
      }
      try {
        await run;
      } finally {
        if (loadTodayInFlightRef.current === run) {
          loadTodayInFlightRef.current = null;
        }
      }
    },
    [refetchToday, searchParams, todayIso],
  );

  loadTodayRef.current = loadToday;

  const onRitualSpineComplete = useCallback(
    async (ctx: TodayRitualNarrativePayload) => {
      if (dayStorySingleVoice) return;
      const d = todayData?.date;
      if (!d) return;
      const key = `${d}-${ctx.tarot_main_id}-${ctx.numerology_value}-${ctx.head_topic ?? ""}`;
      if (ritualGuideRefreshKeyRef.current === key) return;
      ritualGuideRefreshKeyRef.current = key;
      const ritual_context: TodayGuideRitualContext = {
        tarot_main_id: ctx.tarot_main_id,
        tarot_name_ru: ctx.tarot_name_ru,
        numerology_value: ctx.numerology_value,
        day_events: ctx.day_events,
        ...(ctx.mood ? { mood: ctx.mood } : {}),
        ...(ctx.head_topic ? { head_topic: ctx.head_topic } : {}),
      };
      lastRitualNarrativeContextRef.current = ritual_context;
      setGuideNarrativeLoading(true);
      try {
        const r = await fetchTodayNarrativeCached(
          {
            target_date: d,
            surface: "guide",
            ritual_context,
            ...(narrativeDepthForRequest ? { depth_level: narrativeDepthForRequest } : {}),
          },
          { force: true },
        );
        setGuideGenerationId(r.generation_id);
        guideProfileSelectorRef.current = narrativeProfileSelectorPayload(r.profile_selector);
        setDayLayerGenerationId(null);
        setSpheresGenerationId(null);
        setEveningGenerationId(null);
        setGuideNarrativePayload(r.payload);
        setDayLayerPayload(null);
        setSpheresPayload(null);
        setEveningPayload(null);
      } catch {
        /* сохраняем предыдущий guide при сетевой ошибке */
      } finally {
        setGuideNarrativeLoading(false);
      }
    },
    [todayData?.date, dayStorySingleVoice, narrativeDepthForRequest],
  );

  useEffect(() => {
    if (!isAuthenticated || !todayData?.date) return;
    if (searchParams.get("first") !== "1") return;
    const onboardingRitual = buildOnboardingRitualContext();
    if (!onboardingRitual) return;
    lastRitualNarrativeContextRef.current = onboardingRitual;
  }, [isAuthenticated, todayData?.date, searchParams]);

  useEffect(() => {
    if (!isAuthenticated) return;
    loadToday();
  }, [isAuthenticated, loadToday]);

  useEffect(() => {
    if (!isAuthenticated) {
      setAccountMe(null);
      setNarrativeDepthLoaded(false);
      setNarrativeDepthLevel("normal");
      return;
    }
    let cancelled = false;
    setNarrativeDepthLoaded(false);
    Promise.all([getJson<UserSettings>("/account/profile"), getJson<AccountProfile>("/auth/me").catch(() => null)])
      .then(([prof, me]) => {
        if (cancelled) return;
        setAccountMe(me);
        const tier = insightDepthFromProfile(me);
        setNarrativeDepthLevel(effectiveNarrativeDepth(prof.today_narrative_depth_level, tier));
        setNarrativeDepthLoaded(true);
      })
      .catch(() => {
        if (!cancelled) setNarrativeDepthLoaded(true);
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated) {
      setMeaningRingsData(null);
      return;
    }
    const cached = getCachedMeaningRings();
    if (cached?.rings?.length) {
      setMeaningRingsData({ window_days: cached.window_days, generated_at: cached.generated_at, rings: cached.rings });
    }
    void refreshMeaningRings(28)
      .then((r) => {
        if (r) setMeaningRingsData(r);
      })
      .catch(() => undefined);
  }, [isAuthenticated, todayData?.date]);

  /** Провайдер мог обновить `/today` после смены дня — подтягиваем экран без лишнего запроса, если даты уже совпали с кэшем. */
  useEffect(() => {
    if (!isAuthenticated || !cycle?.date || !todayData?.date) return;
    if (todayData.date === cycle.date) return;
    const todayIso = new Date().toISOString().split("T")[0];
    if (cycle.date !== todayIso) return;
    void loadToday();
  }, [isAuthenticated, cycle?.date, todayData?.date, loadToday]);

  useEffect(() => {
    const d = todayData?.date;
    if (!d) return;
    if (narrativeDateRef.current === d) return;
    narrativeDateRef.current = d;
    ritualGuideRefreshKeyRef.current = null;
    lastRitualNarrativeContextRef.current = null;
    guideProfileSelectorRef.current = null;
    eveningProfileSelectorRef.current = null;
    setGuideGenerationId(null);
    setDayLayerGenerationId(null);
    setSpheresGenerationId(null);
    setEveningGenerationId(null);
    setGuideNarrativePayload(null);
    setGuideNarrativeRequestFailed(false);
    setDayLayerPayload(null);
    setSpheresPayload(null);
    setEveningPayload(null);
  }, [todayData?.date]);

  useEffect(() => {
    if (!isAuthenticated || !todayData?.date) return;
    if (dayStorySingleVoice && todayContract) {
      setGuideGenerationId(parseContractGenerationId(todayContract));
      setGuideNarrativePayload(null);
      setGuideNarrativeRequestFailed(false);
      setGuideNarrativeLoading(false);
      setDayLayerPayload(null);
      setSpheresPayload(null);
      setEveningPayload(null);
      setDayLayerLoading(false);
      setEveningLoading(false);
      return;
    }
    let cancelled = false;
    setGuideNarrativeLoading(true);
    void fetchTodayNarrativeCached({
      target_date: todayData.date,
      surface: "guide",
      ...(narrativeDepthForRequest ? { depth_level: narrativeDepthForRequest } : {}),
    })
      .then((r) => {
        if (cancelled) return;
        setGuideGenerationId(r.generation_id);
        guideProfileSelectorRef.current = narrativeProfileSelectorPayload(r.profile_selector);
        setGuideNarrativePayload(r.payload);
        setGuideNarrativeRequestFailed(false);
      })
      .catch(() => {
        if (!cancelled) {
          setGuideGenerationId(null);
          guideProfileSelectorRef.current = null;
          setGuideNarrativePayload(null);
          setGuideNarrativeRequestFailed(true);
        }
      })
      .finally(() => {
        if (!cancelled) setGuideNarrativeLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, todayData?.date, narrativeDepthSeq, narrativeDepthForRequest, dayStorySingleVoice, todayContract]);

  const saveNarrativeDepthFromToday = useCallback(
    async (next: NarrativeDepthLevel) => {
      const tier = insightDepthFromProfile(accountMe);
      if (next === "deep" && tier === "free") {
        toast.error(RITUAL_COPY.narrativeDepthDeepSubscriptionRequired);
        return;
      }
      const effective = effectiveNarrativeDepth(next, tier);
      if (effective === narrativeDepthLevel) return;
      setNarrativeDepthSaving(true);
      try {
        await putJson("/account/profile", { today_narrative_depth_level: effective });
        setNarrativeDepthLevel(effective);
        setNarrativeDepthSeq((s) => s + 1);
        trackMeaningEvent({
          event_type: "today_narrative_depth_changed",
          event_source: "today",
          quality_score: 0.55,
          local_date: todayData?.date ?? null,
          payload: { depth_level: effective, source: "today_page" },
        });
        toast.success(RITUAL_COPY.narrativeDepthSaveSuccessToast);
      } catch (err) {
        toast.error(err instanceof Error ? err.message : RITUAL_COPY.narrativeDepthSaveErrorToast);
      } finally {
        setNarrativeDepthSaving(false);
      }
    },
    [accountMe, narrativeDepthLevel, todayData?.date, toast, trackMeaningEvent],
  );

  useEffect(() => {
    if (!isAuthenticated || !todayData?.date) return;
    if (dayStorySingleVoice) return;
    if (guideNarrativeLoading) return;
    let cancelled = false;
    setDayLayerLoading(true);
    void fetchTodayNarrativeCached({
      target_date: todayData.date,
      surface: "day_layer",
      parent_generation_id: guideGenerationId ?? undefined,
      ritual_context: lastRitualNarrativeContextRef.current ?? undefined,
      ...(narrativeDepthForRequest ? { depth_level: narrativeDepthForRequest } : {}),
    })
      .then((r) => {
        if (!cancelled) {
          setDayLayerGenerationId(r.generation_id);
          setDayLayerPayload(r.payload);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setDayLayerGenerationId(null);
          setDayLayerPayload(null);
        }
      })
      .finally(() => {
        if (!cancelled) setDayLayerLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, todayData?.date, guideNarrativeLoading, guideGenerationId, dayStorySingleVoice, narrativeDepthForRequest]);

  useEffect(() => {
    if (!isAuthenticated || !todayData?.date) return;
    if (dayStorySingleVoice) return;
    if (guideNarrativeLoading) return;
    let cancelled = false;
    void fetchTodayNarrativeCached({
      target_date: todayData.date,
      surface: "spheres",
      parent_generation_id: guideGenerationId ?? undefined,
      ritual_context: lastRitualNarrativeContextRef.current ?? undefined,
      ...(narrativeDepthForRequest ? { depth_level: narrativeDepthForRequest } : {}),
    })
      .then((r) => {
        if (!cancelled) {
          setSpheresGenerationId(r.generation_id);
          setSpheresPayload(r.payload);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setSpheresGenerationId(null);
          setSpheresPayload(null);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, todayData?.date, guideNarrativeLoading, guideGenerationId, dayStorySingleVoice, narrativeDepthForRequest]);

  useEffect(() => {
    if (!isAuthenticated || !todayData?.date) return;
    if (dayStorySingleVoice) return;
    if (guideNarrativeLoading) return;
    let cancelled = false;
    setEveningLoading(true);
    void fetchTodayNarrativeCached({
      target_date: todayData.date,
      surface: "evening",
      parent_generation_id: guideGenerationId ?? undefined,
      ritual_context: lastRitualNarrativeContextRef.current ?? undefined,
      ...(narrativeDepthForRequest ? { depth_level: narrativeDepthForRequest } : {}),
    })
      .then((r) => {
        if (!cancelled) {
          setEveningGenerationId(r.generation_id);
          eveningProfileSelectorRef.current = narrativeProfileSelectorPayload(r.profile_selector);
          setEveningPayload(r.payload);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setEveningGenerationId(null);
          eveningProfileSelectorRef.current = null;
          setEveningPayload(null);
        }
      })
      .finally(() => {
        if (!cancelled) setEveningLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, todayData?.date, guideNarrativeLoading, guideGenerationId, dayStorySingleVoice, narrativeDepthForRequest]);

  useEffect(() => {
    if (!todayData) return;
    const preferredSection = inferPreferredSection(new Date().getHours(), todayData);
    setExpandedSection(preferredSection);
    setEveningMarkedDone(todayData.evening_completed);
    setEveningReflectionInput(todayData.day_connection?.evening_reflection || "");
    setEveningCustomPhrase(
      todayData.evening?.custom_closing_phrase || todayData.evening?.closing_phrase_text || "",
    );
    setEveningObservations({
      noticed:
        todayData.day_connection?.evening_observations?.noticed ||
        todayData.evening?.observations?.noticed ||
        "",
      hardest:
        todayData.day_connection?.evening_observations?.hardest ||
        todayData.evening?.observations?.hardest ||
        "",
      easier_than_expected:
        todayData.day_connection?.evening_observations?.easier_than_expected ||
        todayData.evening?.observations?.easier_than_expected ||
        "",
    });
  }, [todayData]);

  const saveTodaySignal = async (payload: {
    ritual_feedback?: "yes" | "partial" | "no";
    quick_decision_answer?: "yes" | "no" | "unclear";
    question_of_day_answer?: string;
  }) => {
    if (!todayData) return;
    try {
      await postJson(`/day-connection/${todayData.date}`, payload);
      const gid = guideGenerationId;
      const guidePs = guideProfileSelectorRef.current;
      const guideMeta = {
        day_key: todayData.date,
        surface: "guide" as const,
        ...(guidePs ? { profile_selector: guidePs } : {}),
      };
      if (gid != null && payload.ritual_feedback) {
        void postJson("/learning/feedback", {
          generation_log_id: gid,
          signal: `today_guide_ritual_${payload.ritual_feedback}`,
          metadata: guideMeta,
        }).catch(() => undefined);
      }
      if (gid != null && payload.quick_decision_answer != null) {
        void postJson("/learning/feedback", {
          generation_log_id: gid,
          signal: `today_guide_quick_decision_${payload.quick_decision_answer}`,
          metadata: { day_key: todayData.date, ...(guidePs ? { profile_selector: guidePs } : {}) },
        }).catch(() => undefined);
      }
      if (gid != null && payload.question_of_day_answer != null && String(payload.question_of_day_answer).trim()) {
        void postJson("/learning/feedback", {
          generation_log_id: gid,
          signal: "today_guide_question_answered",
          note: String(payload.question_of_day_answer).trim().slice(0, 4000),
          metadata: { day_key: todayData.date, ...(guidePs ? { profile_selector: guidePs } : {}) },
        }).catch(() => undefined);
      }
      setTodayData((prev) =>
        prev
          ? {
              ...prev,
              day_connection: prev.day_connection
                ? { ...prev.day_connection, ...payload }
                : {
                    id: 0,
                    date: todayData.date,
                    morning_intention: null,
                    morning_focus: null,
                    evening_reflection: null,
                    evening_observations: null,
                    connection_thread: null,
                    morning_completed: false,
                    day_completed: false,
                    evening_completed: false,
                    ...payload,
                  },
            }
          : prev,
      );
    } catch (err: any) {
      toast.error(err?.message || RITUAL_COPY.todaySaveDayConnectionError);
      throw err;
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr + "T12:00:00");
    return date.toLocaleDateString("ru-RU", {
      weekday: "long",
      day: "numeric",
      month: "long",
    });
  };

  useEffect(() => {
    if (!timerRunning) return;
    if (timerSeconds <= 0) {
      setTimerRunning(false);
      return;
    }
    const timerId = window.setInterval(() => {
      setTimerSeconds((prev) => {
        if (prev <= 1) {
          window.clearInterval(timerId);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => window.clearInterval(timerId);
  }, [timerRunning, timerSeconds]);

  const completeQuickPractice = async () => {
    if (!quickPractice) return;
    try {
      setPracticeCompleting(true);
      await postJson(`/practices/${quickPractice.id}/complete`, {});
      setPracticeCompleted(true);
      setTimerRunning(false);
      trackMeaningEvent({
        event_type: "practice_completed",
        event_source: "today",
        payload: { practice_id: quickPractice.id, duration_minutes: quickPractice.duration_minutes || null },
      });
    } catch (err: any) {
      toast.error(err?.message || RITUAL_COPY.todayCompletePracticeError);
    } finally {
      setPracticeCompleting(false);
    }
  };

  const resetTimer = () => {
    if (!quickPractice?.duration_minutes) {
      setTimerSeconds(300);
      setTimerRunning(false);
      return;
    }
    setTimerSeconds(quickPractice.duration_minutes * 60);
    setTimerRunning(false);
  };

  const saveEveningRitualInline = async () => {
    if (!todayData || eveningSaving) return;
    const noticed = eveningObservations.noticed.trim();
    const hardest = eveningObservations.hardest.trim();
    const easier = eveningObservations.easier_than_expected.trim();
    const observationsPayload = noticed || hardest || easier
      ? { noticed: noticed || null, hardest: hardest || null, easier_than_expected: easier || null }
      : null;
    const reflection = eveningReflectionInput.trim();
    const customPhrase = eveningCustomPhrase.trim();

    try {
      setEveningSaving(true);
      await postJson("/tracking/ritual", {
        date: todayData.date,
        completed: eveningMarkedDone,
        sufficiency_confirmed: eveningMarkedDone,
        ritual_type: customPhrase ? "combined" : "template",
        custom_closing_phrase: customPhrase || null,
        observations: observationsPayload,
        day_connection_id: todayData.day_connection?.id || null,
      });
      await postJson(`/day-connection/${todayData.date}`, {
        evening_reflection: reflection || null,
        evening_observations: observationsPayload,
        evening_completed: eveningMarkedDone,
      });
      if (eveningGenerationId != null) {
        const evPs = eveningProfileSelectorRef.current;
        void postJson("/learning/feedback", {
          generation_log_id: eveningGenerationId,
          signal: eveningMarkedDone ? "today_evening_closure_done" : "today_evening_closure_saved",
          note: reflection ? reflection.slice(0, 4000) : null,
          metadata: {
            day_key: todayData.date,
            evening_completed: eveningMarkedDone,
            surface: "evening",
            ...(evPs ? { profile_selector: evPs } : {}),
          },
        }).catch(() => undefined);
      }
      trackMeaningEvent({
        event_type: "evening_reflection_submitted",
        event_source: "today",
        payload: {
          ...(eveningGenerationId != null && eveningGenerationId > 0 ? { generation_id: eveningGenerationId } : {}),
          evening_completed: eveningMarkedDone,
          has_reflection: Boolean(reflection),
          day_key: todayData.date,
        },
      });
      await loadToday({ force: true });
    } catch (err: any) {
      toast.error(err?.message || RITUAL_COPY.todaySaveEveningCloseError);
    } finally {
      setEveningSaving(false);
    }
  };

  const revealSection = useCallback((section: "morning" | "day" | "evening") => {
    const targetId =
      section === "morning" ? "today-ritual-hero" : section === "day" ? "today-ritual-checkin" : "today-ritual-evening";
    window.setTimeout(() => {
      document.getElementById(targetId)?.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 80);
  }, []);

  const startTodayFocus20 = useCallback(() => {
    setTodayFocusChromeActive(true);
    setTimerSeconds(20 * 60);
    setTimerRunning(true);
    toast.info(RITUAL_COPY.focusTimerToastInfo);
  }, [toast]);

  useEffect(() => {
    const step = parseTodayFlowTab(searchParams.get("step"));
    if (step) {
      setTodayTab(step);
      if (step === "morning" || step === "day" || step === "evening") setExpandedSection(step);
    }
  }, [searchParams]);

  useEffect(() => {
    if (!todayData || typeof window === "undefined") return;
    if (parseTodayFlowTab(searchParams.get("step"))) return;
    const slotParam = new URLSearchParams(window.location.search).get("slot");
    if (slotParam === "morning" || slotParam === "day" || slotParam === "evening") {
      window.setTimeout(() => revealSection(slotParam), 60);
      return;
    }
    const legacyHash = window.location.hash;
    if (legacyHash === "#morning-section" || legacyHash === "#meaning-section") window.setTimeout(() => revealSection("morning"), 60);
    if (legacyHash === "#day-section" || legacyHash === "#checkin-section") window.setTimeout(() => revealSection("day"), 60);
    if (legacyHash === "#evening-section" || legacyHash === "#closing-section") window.setTimeout(() => revealSection("evening"), 60);
  }, [todayData, searchParams, revealSection]);

  useEffect(() => {
    if (hiddenQuestionsTabAppliedRef.current) return;
    if (parseTodayFlowTab(searchParams.get("step"))) return;
    if (todayTab !== "guide") return;

    const lane = questionsHubContext?.preferred_lane;
    if (lane === "love" || lane === "money_career") {
      hiddenQuestionsTabAppliedRef.current = true;
      setTodayTab("spheres");
      return;
    }
    if (lane === "state" || lane === "pattern" || lane === "decision") {
      hiddenQuestionsTabAppliedRef.current = true;
      setTodayTab("day");
    }
  }, [questionsHubContext?.preferred_lane, searchParams, todayTab]);

  /** Cycle cache can paint `todayData` before `loadToday` finishes `/today/contract`. */
  const awaitingInitialLoad = !todayData && !error;
  const contractPending = Boolean(todayData && !todayContract && !error);

  // Guests never load `todayData` (loadToday runs only for authenticated users), so the
  // data gate must be scoped to authenticated sessions — otherwise guests get stuck on an
  // infinite "building your day" spinner and never reach the guest/auth branches below.
  if (authLoading || (isAuthenticated && (loading || awaitingInitialLoad || contractPending))) {
    return (
      <ProductPageScreen
        testId="today-loading"
        title="Сегодня"
        loading
        loadingLabel={authLoading ? RITUAL_COPY.todayPageLoadingSession : RITUAL_COPY.todayPageLoadingDay}
        hideDatePill
      />
    );
  }

  const guestDraft = readGuestProfileDraft();
  const guestFirstTodayMode = !isAuthenticated && firstTodayMode && hasGuestPreview(guestDraft);
  if (guestFirstTodayMode && guestDraft) {
    return <GuestFirstTodayScreen draft={guestDraft} />;
  }

  if (!isAuthenticated) {
    return (
      <ProductPageScreen
        testId="today-guest-gate"
        title="Сегодня"
        guest={{
          message: RITUAL_COPY.todayPageAuthRequired,
          ctaHref: "/auth?mode=login",
          ctaLabel: "Войти",
        }}
        hideDatePill
      />
    );
  }

  if (error || !todayData || !todayContract) {
    return (
      <ProductPageScreen
        testId="today-error"
        title="Сегодня"
        error={{
          message: error || RITUAL_COPY.todayPageDataMissing,
          retryLabel: RITUAL_COPY.todayPageRetryCta,
          onRetry: () => void loadToday({ force: true }),
        }}
        hideDatePill
      />
    );
  }

  const dailySteps = [
    { key: "meaning", label: RITUAL_COPY.todayDailyStepMeaningLabel, done: todayData.morning_completed },
    {
      key: "focus",
      label: RITUAL_COPY.todayDailyStepFocusLabel,
      done: practiceCompleted || todayData.day_trackers.length > 0 || todayData.day_journal_entries.length > 0,
    },
    { key: "closing", label: RITUAL_COPY.todayDailyStepClosingLabel, done: todayData.evening_completed },
  ];
  const completedSteps = dailySteps.filter((step) => step.done).length;
  const progressPercent = Math.round((completedSteps / dailySteps.length) * 100);
  const currentHour = new Date().getHours();
  const nudge = buildDailyNudge({
    currentHour,
    progressPercent,
    fusion: fusionData,
    hasQuickActionDone: practiceCompleted || todayData.day_trackers.length > 0 || todayData.day_journal_entries.length > 0,
    eveningCompleted: todayData.evening_completed,
  });
  const priorityWeeklyGoal = selectPriorityWeeklyGoal({
    goals: weeklyGoals,
    nudgeLevel: nudge.level,
    fusion: fusionData,
  });
  const nextAction = buildNextAction({
    todayData,
    practiceCompleted,
    hasPractice: !!quickPractice,
    weeklyGoal: priorityWeeklyGoal,
  });
  const weekGoalCount = weeklyGoals.filter((goal) => goal.scope !== "month").length;
  const monthGoalCount = weeklyGoals.filter((goal) => goal.scope === "month").length;
  const serverEnergyScore =
    todayData.morning?.decision_engine?.hero?.energy_score ?? fusionData?.scores?.energy ?? undefined;
  const energyScoreIsPlaceholder = serverEnergyScore === undefined;
  // Never invent 50 as a real energy score in production UI.
  const energyScore = serverEnergyScore ?? 0;
  const energySummary = energyScoreIsPlaceholder
    ? { score: 0, label: "", guidance: "" }
    : buildDayEnergySummary(energyScore);
  const actionPlan = buildTodayActionPlan({
    todayData,
    quickPractice,
    weeklyGoal: priorityWeeklyGoal,
  });
  const firstActionForGuidance = actionPlan.length ? String(actionPlan[0]) : null;
  const guidanceSummaryRitual = guidanceSummaryForRitual({
    morning: todayData.morning,
    actionPlanFirstLine: firstActionForGuidance,
  });
  const spineAxis = String(todayData.morning?.daily_horoscope?.spine?.day_axis || "").trim();
  const forecastText = String(todayData.morning?.daily_forecast_summary?.summary || "").trim();
  const firstMoveLineRaw = String(todayData.morning?.daily_horoscope?.spine?.first_move || "").trim();
  const firstMoveLine = firstMoveLineRaw && !isGarbageRitualActionCue(firstMoveLineRaw) ? firstMoveLineRaw : "";
  const guideHeadline =
    spineAxis ||
    (forecastText ? (forecastText.split(/[.!?]\s/)[0]?.trim() || forecastText.slice(0, 140)) : "") ||
    (energyScoreIsPlaceholder ? "" : energySummary.guidance);
  const guideSubline =
    firstMoveLine ||
    (forecastText && forecastText !== guideHeadline ? forecastText.slice(0, 280) : "") ||
    nextAction.message;
  const spine = todayData.morning?.daily_horoscope?.spine;
  const firstNameRitual = coreProfile?.person?.first_name || coreProfile?.person?.display_name || null;
  const bestModeRitual = String(spine?.best_mode || "").trim();
  const dayLabelRitual = bestModeRitual || guideHeadline || RITUAL_COPY.ritualGuideDayLabelFallback;
  const subtitleRitual = guideSubline || energySummary.guidance;
  const narrativeGuideHeadline = narrativeString(guideNarrativePayload?.headline);
  const narrativeGuideSubline = narrativeString(guideNarrativePayload?.subline);
  const coreGuideLead =
    parseCoreMessageFromGuide(guideNarrativePayload)?.split(/\n\s*\n/).map((p) => p.trim()).find(Boolean) ?? "";
  const contractStoryHeadline =
    dayStorySingleVoice && todayContract ? dayStoryHeadline(todayContract) : null;
  const contractStoryLead =
    dayStorySingleVoice && todayContract ? dayStoryLeadParagraph(todayContract) : null;
  const summaryTitleMerged = contractStoryHeadline || narrativeGuideHeadline || guideHeadline;
  const subtitleMerged = contractStoryLead || coreGuideLead || narrativeGuideSubline || subtitleRitual;
  /** Dashboard chrome must stay short — full day_story belongs in the reading, not the header. */
  const dashboardGreetingLine =
    (todayContract?.day_story?.theme || "").trim() ||
    (summaryTitleMerged && summaryTitleMerged.length <= 72 ? summaryTitleMerged : undefined) ||
    undefined;
  const numerologyValueRitual = String(
    todayData.morning?.numerology_number?.value ?? todayData.morning?.numerology_number?.reduced_value ?? "—",
  );
  const numerologyMeaningRitual = String(
    todayData.morning?.numerology_number?.title ||
      todayData.morning?.numerology_explanation?.summary ||
      RITUAL_COPY.numerologyMeaningFallbackShort,
  );
  const apiSymbols = morningRitualData?.celestial_events?.daily_symbols;
  const colorLineResolved = apiSymbols?.color?.name ?? null;
  const stoneLineResolved = apiSymbols?.stone?.name ?? null;
  const numerologyLucky = {
    time: "",
    color: colorLineResolved ?? "",
    stone: stoneLineResolved ?? "",
  };
  const mTarot = todayData.morning as { tarot_card?: { name?: string; id?: number | string } } | undefined;
  const rawTarotName = String(morningRitualData?.tarot_card?.name || mTarot?.tarot_card?.name || RITUAL_COPY.cardEyebrow);
  const tarotAnchorId = resolveDailyTarotDeckIndex({
    morningTarotCardId: morningRitualData?.tarot_card?.id ?? mTarot?.tarot_card?.id ?? null,
    morningTarotName: rawTarotName,
    cardName: rawTarotName,
    dateISO: todayData.date,
  });
  const tarotRu = getTodayTarotCardRu(tarotAnchorId);
  const cardNameRitual = tarotRu?.nameRu ?? rawTarotName;
  const apiMeaning = morningRitualData?.tarot_explanation?.meaning || morningRitualData?.tarot_explanation?.summary || null;
  const cardMeaningRitual = isRuUserFacingText(apiMeaning) ? apiMeaning : tarotRu?.leadRu ?? null;
  const possibleRitual = buildRitualPossibleSignals(todayData.morning);
  const avoidRitual = buildRitualAvoidSignals(todayData.morning);
  const supportRitual = buildRitualSupportSignals(bestModeRitual, guidanceSummaryRitual);
  const cardNumberBridgeRitual = formatRitualCardNumberBridgePageFallback(cardNameRitual, numerologyValueRitual);
  const actionPlanRings = [RITUAL_COPY.todayActionPlanRingCloseness, RITUAL_COPY.todayActionPlanRingFocus, RITUAL_COPY.todayActionPlanRingMoney];
  const actionItemsRitual = actionPlan.map((a, i) => ({
    text: String(a),
    ring: actionPlanRings[i % actionPlanRings.length],
  }));
  const lunarPhaseForWhy =
    (todayData.morning as MorningRitualData | null | undefined)?.celestial_events?.lunar_phase ??
    morningRitualData?.celestial_events?.lunar_phase;
  /** Без префикса «Фаза:» — подпись «Луна и фон дня» уже задаёт контекст (паритет с iOS). */
  const whyMoonRitual = lunarPhaseForWhy?.name ? String(lunarPhaseForWhy.name).trim() : null;
  const whyLunarRitual = lunarPhaseForWhy?.themes ? String(lunarPhaseForWhy.themes) : null;

  const profileMetaParts = [
    coreProfile?.numerology?.life_path != null ? `Путь ${coreProfile.numerology.life_path}` : null,
    coreProfile?.astro?.sun_sign ? `Солнце ${coreProfile.astro.sun_sign}` : null,
  ].filter(Boolean);
  const profileMetaDashboard = profileMetaParts.length > 0 ? profileMetaParts.join(" · ") : null;
  const themeTagsDashboard = [bestModeRitual, energySummary.label].filter(Boolean).slice(0, 3) as string[];
  const dashboardPractices = buildTodayWebPractices({
    quickPractice,
    practiceCompleted,
    actionPlan,
  });
  const dashboardTimeline = buildTodayWebTimeline(morningRitualData);
  const dashboardWeekly = buildTodayWebWeeklyActivity({ dailySteps, fusion: fusionData });
  const dashboardStreak = buildTodayWebStreak(todayData);

  const formatFocusTimer = (totalSeconds: number) => {
    const m = Math.floor(Math.max(0, totalSeconds) / 60);
    const s = Math.max(0, totalSeconds) % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  };

  const todayDashboardLayout = todayExperienceMode ? "composition" : "ritual";

  return (
    <>
      <TodayWebDashboard
        displayName={firstNameRitual}
        displayDate={formatDate(todayData.date)}
        greetingLine={dashboardGreetingLine}
        profileMeta={profileMetaDashboard}
        themeTitle={summaryTitleMerged}
        themeTags={themeTagsDashboard}
        themeBody={dashboardGreetingLine}
        cardName={cardNameRitual}
        cardMeaning={cardMeaningRitual}
        moonLine={whyMoonRitual}
        numerologyValue={numerologyValueRitual}
        numerologyMeaning={numerologyMeaningRitual}
        practices={dashboardPractices}
        timelineEvents={dashboardTimeline}
        weeklyActivity={dashboardWeekly}
        streakDays={dashboardStreak}
        layout={todayDashboardLayout}
        coreProfile={coreProfile}
      >
        {supplementaryLoading && !todayExperienceMode ? (
          <p className="orbit-body-xs" style={{ margin: 0, color: "#7a623d" }}>
            {RITUAL_COPY.todaySupplementaryLoadingHint}
          </p>
        ) : null}
        {narrativeDepthLoaded && !loading && !todayExperienceMode ? (
          <TodayNarrativeDepthControl
            value={narrativeDepthLevel}
            saving={narrativeDepthSaving}
            canPickDeep={insightDepthFromProfile(accountMe) !== "free"}
            onChange={(next) => void saveNarrativeDepthFromToday(next)}
          />
        ) : null}
        {todayExperienceMode && todayContract && !ritualExperienceMode ? (
          <TodayCompositionSurface
            embeddedInWebDashboard
            variant={firstTodayMode ? "firstToday" : "default"}
            dateISO={todayData.date}
            displayDate={formatDate(todayData.date)}
            todayData={todayData}
            morningRitualData={morningRitualData}
            contract={todayContract}
            cardName={cardNameRitual}
            cardMeaning={cardMeaningRitual}
            numerologyValue={numerologyValueRitual}
            numerologyMeaning={numerologyMeaningRitual}
            guideNarrativeLoading={guideNarrativeLoading}
            guideNarrativePayload={guideNarrativePayload}
            guideNarrativeRequestFailed={guideNarrativeRequestFailed}
            dayLayerNarrativePayload={dayLayerPayload}
            dayLayerNarrativeLoading={dayLayerLoading}
            spheresNarrativePayload={spheresPayload}
            eveningNarrativePayload={eveningPayload}
            onRitualSpineComplete={onRitualSpineComplete}
            colorLine={colorLineResolved}
            stoneLine={stoneLineResolved}
            coreProfile={coreProfile}
            dayStoryUpdating={dayStoryUpdating}
            onSymbolRevealResult={onSymbolRevealResult}
            onVisible={firstTodayMode ? onFirstTodayVisible : onExperienceSurfaceVisible}
          />
        ) : todayExperienceMode && todayContract ? (
          <TodayExperienceSurface
            dateISO={todayData.date}
            displayDate={formatDate(todayData.date)}
            firstName={firstNameRitual}
            todayData={todayData}
            morningRitualData={morningRitualData}
            contract={todayContract}
            fusion={fusionData}
            cardName={cardNameRitual}
            numerologyValue={numerologyValueRitual}
            numerologyMeaning={numerologyMeaningRitual}
            guideNarrativeLoading={guideNarrativeLoading}
            guideNarrativePayload={guideNarrativePayload}
            guideGenerationId={guideGenerationId}
            onRitualSpineComplete={onRitualSpineComplete}
            onVisible={onExperienceSurfaceVisible}
          />
        ) : !todayExperienceMode ? (
          <TodayRitualFlow
            firstName={firstNameRitual}
            profileGender={coreProfile?.person?.gender ?? null}
            displayDate={formatDate(todayData.date)}
            todayData={todayData}
            morningRitualData={morningRitualData}
            fusion={fusionData}
            meaningRings={meaningRingsData}
            energyScore={energyScore}
            energyScoreIsPlaceholder={energyScoreIsPlaceholder}
            dayLabel={dayLabelRitual}
            subtitle={subtitleMerged}
            cardName={cardNameRitual}
            cardMeaning={cardMeaningRitual}
            numerologyValue={numerologyValueRitual}
            numerologyMeaning={numerologyMeaningRitual}
            numerologyLucky={numerologyLucky}
            cardNumberBridge={cardNumberBridgeRitual}
            summaryTitle={summaryTitleMerged}
            possible={possibleRitual}
            avoid={avoidRitual}
            support={supportRitual}
            whyMoon={whyMoonRitual}
            whyLunar={whyLunarRitual}
            actionItems={actionItemsRitual}
            weeklyGoals={weeklyGoals}
            onOpenHabit={openEntityWizard}
            onStartFocus20Minutes={startTodayFocus20}
            onTrackMood={() => undefined}
            guideNarrativeLoading={guideNarrativeLoading}
            guideNarrativePayload={guideNarrativePayload}
            spheresNarrativePayload={spheresPayload}
            dayLayerNarrativePayload={dayLayerPayload}
            dayLayerNarrativeLoading={dayLayerLoading}
            eveningPayload={eveningPayload}
            eveningNarrativeLoading={eveningLoading}
            eveningCustomPhrase={eveningCustomPhrase}
            eveningMarkedDone={eveningMarkedDone}
            eveningObservations={eveningObservations}
            eveningReflectionInput={eveningReflectionInput}
            eveningSaving={eveningSaving}
            onEveningCustomPhraseChange={setEveningCustomPhrase}
            onEveningMarkedDoneChange={setEveningMarkedDone}
            onEveningObservationChange={(field, value) => setEveningObservations((prev) => ({ ...prev, [field]: value }))}
            onEveningReflectionChange={setEveningReflectionInput}
            onSaveEvening={saveEveningRitualInline}
            onRefreshToday={() => void loadToday({ force: true })}
            onEveningPhaseSaved={() => void loadToday({ force: true })}
            onRitualSpineComplete={onRitualSpineComplete}
            coreLoopViabilityMode={coreLoopViabilityMode}
            todayContract={todayContract}
            dayStoryUpdating={dayStoryUpdating}
            onSymbolRevealResult={onSymbolRevealResult}
            narrativeGenerationIds={{
              guide: guideGenerationId,
              day_layer: dayLayerGenerationId,
              spheres: spheresGenerationId,
              evening: eveningGenerationId,
            }}
          />
        ) : null}
      </TodayWebDashboard>
      {todayFocusChromeActive && (timerRunning || timerSeconds > 0) ? (
        <div
          role="status"
          aria-live="polite"
          style={{
            position: "fixed",
            bottom: 0,
            left: 0,
            right: 0,
            zIndex: 80,
            padding: "0.65rem 1rem calc(0.65rem + env(safe-area-inset-bottom, 0px))",
            background: "linear-gradient(180deg, rgba(45,36,28,0) 0%, rgba(45,36,28,0.88) 28%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "0.75rem",
            maxWidth: "32rem",
            margin: "0 auto",
            boxSizing: "border-box",
          }}
        >
          <p className="orbit-body-sm" style={{ margin: 0, color: "#fff8f2", fontWeight: 700 }}>
            {RITUAL_COPY.focusTimerChromeLine(formatFocusTimer(timerSeconds))}
          </p>
          <div style={{ display: "flex", gap: "0.45rem" }}>
            <button
              type="button"
              className="orbit-button orbit-button-secondary orbit-button-sm"
              onClick={() => setTimerRunning((r) => !r)}
              style={{ borderRadius: 999 }}
            >
              {timerRunning ? RITUAL_COPY.focusTimerPauseCta : RITUAL_COPY.ritualContinueCta}
            </button>
            <button
              type="button"
              className="orbit-button orbit-button-primary orbit-button-sm"
              onClick={() => {
                setTimerRunning(false);
                setTimerSeconds(0);
                setTodayFocusChromeActive(false);
              }}
              style={{ borderRadius: 999 }}
            >
              {RITUAL_COPY.focusTimerStopCta}
            </button>
          </div>
        </div>
      ) : null}
      <EntityCreateWizard
        open={entityWizardOpen}
        onClose={() => {
          setEntityWizardOpen(false);
          setEntityWizardKind(null);
        }}
        todayIso={todayData.date}
        onCreated={async () => {
          await loadToday({ force: true });
        }}
        goalCountWeek={weekGoalCount}
        goalCountMonth={monthGoalCount}
        initialKind={entityWizardKind}
      />
    </>
  );
}
