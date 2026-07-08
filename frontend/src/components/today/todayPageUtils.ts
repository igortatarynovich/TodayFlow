"use client";

import type { CSSProperties } from "react";
import type { CoreProfile } from "@/lib/types";
import type { RewardMilestone, RewardsSnapshot } from "@/lib/rewards";
import {
  formatActionPlanQuickPractice,
  formatActionPlanWeeklyStep,
  formatDailyRewardStreakBadge,
  formatDayEventsJournalCount,
  formatLifeNowDisciplineBodyAscetic,
  formatLifeNowDisciplineBodyHabit,
  formatLifeNowDisciplineStatusAscetic,
  formatLifeNowDisciplineStatusHabit,
  formatLifeNowDisciplineStatusMinutes,
  formatPersonalInsightChipEnergy,
  formatPersonalInsightChipFocus,
  formatPersonalInsightChipNumber,
  formatPersonalInsightChipStreak,
  formatPersonalInsightChipTarot,
  formatPersonalInsightMessageHighNoAnchor,
  formatPersonalInsightMessageHighWithAnchor,
  formatPersonalInsightMessageMidNoAnchor,
  formatPersonalInsightMessageMidWithAnchor,
  formatPersonalInsightMessageStartNoAnchor,
  formatPersonalInsightMessageStartWithAnchor,
  formatRewardsCardArchetypeBadge,
  formatRewardsCardAsceticBadge,
  formatRewardsCardDisciplineBadge,
  formatRewardsCardHabitsBadge,
  formatRewardsCardStreakBadge,
  formatRitualEntrySublineCalendarLine,
  formatRitualEntrySublineFocusSnippet,
  formatRitualEntrySublineIntentionSnippet,
  formatRitualEntrySublineLunarOnly,
  formatRitualEntrySublineProfileSunMoon,
  formatRitualEntrySublineProfileSunOnly,
  formatTodayCriticalLimitAmplify,
  isDiscardableMorningFocus,
  rhythmTierLabelForScore,
  buildRitualQuestionOfDayDefaultCards,
  RITUAL_COPY,
  RITUAL_QUESTION_OF_DAY_LOW_ENERGY_CARDS,
} from "@/components/today/todayRitualCopy";
import {
  humanizeFocusSlugForUi,
  isGarbageRitualActionCue,
  repairRitualDoNotEnterLine,
  replaceQuotedEnSlugsForRuDisplay,
} from "@/components/today/ritualCueSanitizer";

/** Экраны страницы «Сегодня» (порядок прохождения дня). */
export type TodayFlowTab = "guide" | "spheres" | "morning" | "day" | "evening";

export const TODAY_FLOW_TABS: { id: TodayFlowTab; label: string; description: string }[] = [
  { id: "guide", label: RITUAL_COPY.todayFlowTabGuideLabel, description: RITUAL_COPY.todayFlowTabGuideDesc },
  { id: "spheres", label: RITUAL_COPY.todayFlowTabSpheresLabel, description: RITUAL_COPY.todayFlowTabSpheresDesc },
  { id: "morning", label: RITUAL_COPY.todayFlowTabMorningLabel, description: RITUAL_COPY.todayFlowTabMorningDesc },
  { id: "day", label: RITUAL_COPY.todayFlowTabDayLabel, description: RITUAL_COPY.todayFlowTabDayDesc },
  { id: "evening", label: RITUAL_COPY.todayFlowTabEveningLabel, description: RITUAL_COPY.todayFlowTabEveningDesc },
];

export function parseTodayFlowTab(raw: string | null | undefined): TodayFlowTab | null {
  if (!raw) return null;
  const v = raw.toLowerCase().trim();
  if (v === "guide" || v === "spheres" || v === "morning" || v === "day" || v === "evening") return v;
  return null;
}

/**
 * Личные ссылки из сфер дня: полный `/compatibility` с двумя профилями не подменяем,
 * но быстрые расчёты по знакам/датам ведём как есть — второй человек в аккаунте не нужен.
 */
export function sanitizePersonalDayHref(href: string): string {
  const h = (href || "").trim();
  if (!h) return "/profile";
  if (
    h.startsWith("/compatibility/signs") ||
    h.startsWith("/compatibility/birthdates")
  ) {
    return h;
  }
  if (h.includes("/compatibility")) {
    if (h.includes("family") || h.includes("relation_mode=family")) return "/journal";
    return "/tarot?topic=relationships";
  }
  return h;
}

export type TodayCycleData = {
  date: string;
  morning: any | null;
  morning_completed: boolean;
  day_connection: {
    id: number;
    date: string;
    morning_intention: string | null;
    morning_focus: string | null;
    evening_reflection: string | null;
    evening_observations: any | null;
    connection_thread: string | null;
    ritual_feedback?: "yes" | "partial" | "no" | null;
    quick_decision_answer?: "yes" | "no" | "unclear" | null;
    question_of_day_answer?: string | null;
    morning_completed: boolean;
    day_completed: boolean;
    evening_completed: boolean;
  } | null;
  day_trackers: any[];
  day_journal_entries: any[];
  day_completed: boolean;
  evening: any | null;
  evening_completed: boolean;
  morning_available: boolean;
  day_available: boolean;
  evening_available: boolean;
  core_profile?: CoreProfile | null;
  rewards?: RewardsSnapshot | null;
  reward_milestones?: RewardMilestone[];
};

/** Паритет с `GET /tracking/fusion/{date}` — опционально то, что использует UI позже. */
export type FusionRhythmContextResponse = {
  goals: Array<{ title: string; scope: string; completed: boolean }>;
  habits: Array<{
    name: string;
    category: string | null;
    frequency: string;
    completed_today: boolean;
  }>;
  ascetics: Array<{
    title: string;
    streak_days: number;
    completed_today: boolean;
  }>;
  diary: {
    has_entry_today: boolean;
    entries_last_7_days: number;
  };
};

/** DE-9: тот же контракт, что `history_layer_v0` / DayContext.layers.history. */
export type FusionDayHistoryTrailing7dAxisSummary = {
  avg: number;
  min: number;
  max: number;
  days: number;
};

export type FusionDayHistoryV0 = {
  contract_version: string;
  yesterday: {
    date: string;
    fusion_scores: Record<string, number>;
    day_flow?: Record<string, boolean> | null;
    /** DE-9 v1.4: счётчики meaning_events за вчера (только >0). */
    meaning_day_signals?: Record<string, number> | null;
    meaning_completions_total?: number | null;
    meaning_active?: boolean | null;
    /** DE-9 v1.5: урезанный DayConnection за вчера. */
    reflection_excerpt?: {
      contract_version?: string;
      evening_reflection?: string | null;
      evening_observations?: Record<string, string> | null;
      morning_intention?: string | null;
      question_of_day_answer?: string | null;
      quick_decision_answer?: string | null;
      has_reflection?: boolean | null;
    } | null;
  };
  fusion_score_delta_vs_yesterday: Record<string, number>;
  /** O7: false, если вчера не было отметок Flow под формулу fusion — UI не показывает дельту «к сегодня». */
  fusion_score_delta_trustworthy?: boolean;
  /** O7: дублирует смысл trustworthy; для аналитики / отладки. */
  yesterday_fusion_has_flow_markers?: boolean;
  /** O7: за окно 7 дней — сколько дней имели отметки Flow (сервер). */
  trailing_7d_flow_days?: number;
  /** O7: `false` — не показывать недельную сводку (все дни без опоры → дефолтные 50). */
  trailing_7d_summary_trustworthy?: boolean;
  /** DE-9 v1.4: дней в окне 7 с meaning_active или day_flow. */
  trailing_7d_meaning_active_days?: number;
  /** Серия fusion scores за 7 календарных дней до `target_date` (включая вчера). */
  fusion_scores_trailing_7d?: Array<{
    date: string;
    scores: Record<string, number>;
    meaning_completions_total?: number;
    meaning_active?: boolean;
  }>;
  trailing_7d_summary?: {
    energy: FusionDayHistoryTrailing7dAxisSummary;
    emotional_balance: FusionDayHistoryTrailing7dAxisSummary;
    focus: FusionDayHistoryTrailing7dAxisSummary;
  };
};

export type FusionResponse = {
  scores: {
    energy: number;
    emotional_balance: number;
    focus: number;
  };
  recommendations: string[];
  encouragement: string;
  rhythm_context?: FusionRhythmContextResponse;
  /** DE-7: счётчики meaning_events за день (сервер), см. `guide_flow_signals`. */
  activity_context?: {
    guide_meaning_completions_today?: Record<string, number> | null;
  } | null;
  /** DE-9: вчера + дельта к сегодняшним fusion scores (из GET /tracking/fusion/{date}). */
  day_history?: FusionDayHistoryV0 | null;
};

export type PracticeResponse = {
  id: string;
  title: string;
  description: string;
  duration_minutes?: number;
};

export type MorningRitualData = {
  date: string;
  tarot_card?: {
    id?: string;
    name?: string;
    orientation?: string;
    meaning?: string;
  } | null;
  tarot_explanation?: {
    meaning?: string;
    /** Базовый слой (бесплатный тариф) вместо полного набора полей */
    summary?: string;
    keywords?: string[];
    personalized?: boolean;
    what_to_do?: string;
    what_to_avoid?: string;
    possible_events?: string;
    how_day_looks?: string;
    why_this_card?: string;
  } | null;
  numerology_number?: {
    value?: number;
    reduced_value?: number;
    title?: string;
    summary?: string;
  } | null;
  numerology_explanation?: {
    meaning?: string;
    summary?: string;
    title?: string;
    personalized?: boolean;
    what_to_do?: string;
    what_to_avoid?: string;
    possible_events?: string;
    how_day_looks?: string;
    why_this_number?: string;
  } | null;
  celestial_events?: {
    lunar_phase?: {
      name?: string;
      themes?: string;
      guidance?: string;
      cycle_day?: number;
      next_phase?: {
        name?: string;
        in_days?: number;
      };
    };
    retrogrades?: Array<{
      planet?: string;
      planet_ru?: string;
      story_ru?: string;
    }>;
    sky_aspects?: Array<{
      id?: string;
      aspect?: string;
      title?: string;
      story_ru?: string;
      tension_level?: string | null;
    }>;
    personal_transits?: Array<{
      id?: string;
      title?: string;
      story_ru?: string;
      aspect?: string;
      strength?: string | null;
    }>;
    ingresses?: Array<{
      planet_ru?: string;
      sign_ru?: string;
      story_ru?: string;
    }>;
    daily_symbols?: {
      color?: {
        name?: string;
        story_ru?: string;
        benefit_ru?: string;
        clothing_ru?: string;
        accessory_ru?: string;
        amount_ru?: string;
        avoid_color_ru?: string;
        avoid_why_ru?: string;
      };
      stone?: { name?: string; story_ru?: string };
      totem?: { id?: string; name?: string; emoji?: string; story_ru?: string };
    };
  } | null;
  daily_horoscope?: {
    headline?: string;
    profile_prism?: string;
    spine?: {
      best_mode?: string | null;
      first_move?: string | null;
      main_risk?: string | null;
      do_not_enter?: string | null;
      day_axis?: string | null;
      next_action?: string | null;
      growth_hint?: string | null;
    } | null;
    scenarios?: unknown[];
  } | null;
  daily_horoscope_generation_log_id?: number | null;
  decision_engine?: {
    version?: string;
    hero?: {
      energy_score?: number;
      energy_label?: string;
      focus?: string[];
      risk?: string;
    } | null;
    actions?: string[];
    limits?: string[];
    signals?: Record<string, unknown>;
  } | null;
};

export type WeeklyGoal = {
  id: number;
  week_start: string;
  title: string;
  completed: boolean;
  progress_days: number;
  last_progress_date: string | null;
  scope?: string;
  period_end?: string | null;
};

export type ProgressTrackerEntry = {
  date: string;
  completed: boolean;
  state?: string | null;
  state_scale?: number | null;
  note?: string | null;
};

export type PracticeHistoryEntry = {
  completed_at: string;
};

export type JournalEntrySummary = {
  day?: string | null;
  created_at: string;
};

export type RhythmMeta = {
  progress: boolean;
  state: boolean;
  note: boolean;
  practice: boolean;
  journal: boolean;
};

export type ThinkingMode = "initial" | "refresh" | "reveal";

export type DailyReturnCadence = {
  title: string;
  message: string;
  ctaLabel: string;
  section: "morning" | "day" | "evening";
  chip: string;
};

export type DayEnergySummary = {
  score: number;
  label: string;
  guidance: string;
};

export type DayFocusSummary = {
  primary: string[];
  label: string;
};

export type DayRiskSummary = {
  label: string;
  detail: string;
};

export type DayQuestionOption = {
  id: string;
  label: string;
  response: string;
};

export type DayQuestionCard = {
  prompt: string;
  options: DayQuestionOption[];
};

export type WeeklyPatternMap = {
  moodTrend: "up" | "down" | "stable";
  avgStateScale: number | null;
  trackedDays: number;
  journalDays: number;
  improvements: string[];
  regressions: string[];
  recommendation: string;
};

const asArray = <T,>(value: unknown): T[] => (Array.isArray(value) ? value : []);

export function normalizeTodayPayload(payload: TodayCycleData): TodayCycleData {
  return {
    ...payload,
    day_trackers: asArray(payload?.day_trackers),
    day_journal_entries: asArray(payload?.day_journal_entries),
  };
}

/** Короткие строки для `ritual_context.day_events` в POST /today/narrative (guide). */
export function buildDayEventsForNarrative(td: TodayCycleData): string[] {
  const out: string[] = [];
  const focus = td.day_connection?.morning_focus?.trim();
  if (focus && !isDiscardableMorningFocus(focus)) {
    out.push(`${RITUAL_COPY.dayEventsMorningFocusPrefix}${focus.slice(0, 160)}`);
  }
  const intention = td.day_connection?.morning_intention?.trim();
  if (intention) out.push(`${RITUAL_COPY.dayEventsIntentionPrefix}${intention.slice(0, 160)}`);
  for (const t of td.day_trackers ?? []) {
    const rec = t && typeof t === "object" ? (t as Record<string, unknown>) : null;
    const title =
      typeof rec?.title === "string"
        ? rec.title.trim()
        : typeof rec?.name === "string"
          ? String(rec.name).trim()
          : "";
    if (title) out.push(`${RITUAL_COPY.dayEventsTrackerPrefix}${title.slice(0, 200)}`);
    if (out.length >= 14) break;
  }
  const jc = td.day_journal_entries?.length ?? 0;
  if (jc > 0) out.push(formatDayEventsJournalCount(jc));
  if (td.day_completed) out.push(RITUAL_COPY.dayEventsDayCycleCompleted);
  return out.slice(0, 24);
}

/**
 * Подзаголовок входа в ритуал: фокус, календарь, профиль, луна — без выдуманных деталей.
 * Пустая строка → в UI подставляют общий fallback `RITUAL_COPY.ritualEntryBody`.
 */
export function buildRitualEntrySubline(td: TodayCycleData, firstName: string | null): string {
  const name = firstName?.trim();
  const sentences: string[] = [];
  const focus = td.day_connection?.morning_focus?.trim();
  const intention = td.day_connection?.morning_intention?.trim();
  if (focus && !isDiscardableMorningFocus(focus)) {
    const s = focus.length > 140 ? `${focus.slice(0, 139)}…` : focus;
    sentences.push(formatRitualEntrySublineFocusSnippet(s));
  } else if (intention) {
    const s = intention.length > 140 ? `${intention.slice(0, 139)}…` : intention;
    sentences.push(formatRitualEntrySublineIntentionSnippet(s));
  }
  for (const t of td.day_trackers ?? []) {
    const rec = t && typeof t === "object" ? (t as Record<string, unknown>) : null;
    const title =
      typeof rec?.title === "string"
        ? rec.title.trim()
        : typeof rec?.name === "string"
          ? String(rec.name).trim()
          : "";
    if (title) {
      const line = title.length > 100 ? `${title.slice(0, 99)}…` : title;
      sentences.push(formatRitualEntrySublineCalendarLine(line));
      break;
    }
  }
  const sun = td.core_profile?.astro?.sun_sign?.trim();
  const m = td.morning;
  let lunarName: string | null = null;
  if (m && typeof m === "object") {
    const ce = (m as Record<string, unknown>).celestial_events as Record<string, unknown> | undefined;
    const lp = ce?.lunar_phase as Record<string, unknown> | undefined;
    lunarName = typeof lp?.name === "string" ? lp.name.trim() : null;
  }
  if (sun) {
    sentences.push(lunarName ? formatRitualEntrySublineProfileSunMoon(sun, lunarName) : formatRitualEntrySublineProfileSunOnly(sun));
  } else if (lunarName) {
    sentences.push(formatRitualEntrySublineLunarOnly(lunarName));
  }
  const hook = sentences.slice(0, 2).join(" ");
  if (!hook) return "";
  const prefix = name ? `${name}, ` : "";
  return `${prefix}${hook} ${RITUAL_COPY.ritualEntrySublineClosing}`;
}

/**
 * Восстанавливает объект утра как в `MorningRitualResponse` из тела `GET /today/bundle`
 * (обратно к объединению `TodayCoreResponse` + `TodayScenariosResponse` на бэкенде).
 */
export function buildMorningFromTodayBundle(bundle: unknown): Record<string, unknown> | null {
  if (!bundle || typeof bundle !== "object") return null;
  const b = bundle as Record<string, unknown>;
  const coreRaw = b.core;
  if (!coreRaw || typeof coreRaw !== "object") return null;
  const c = coreRaw as Record<string, unknown>;
  const scenariosRaw = b.scenarios;
  const scenarios =
    scenariosRaw && typeof scenariosRaw === "object" ? (scenariosRaw as Record<string, unknown>) : undefined;

  const foundationRaw = c.daily_foundation;
  const foundation =
    foundationRaw && typeof foundationRaw === "object" ? (foundationRaw as Record<string, unknown>) : undefined;

  const spine = foundation?.spine;
  const headline = scenarios?.headline ?? foundation?.headline;
  const profilePrism = scenarios?.profile_prism ?? foundation?.profile_prism;
  const scenList = scenarios?.scenarios;

  const daily_horoscope: Record<string, unknown> = {};
  if (typeof headline === "string" && headline.trim()) daily_horoscope.headline = headline;
  if (typeof profilePrism === "string" && profilePrism.trim()) daily_horoscope.profile_prism = profilePrism;
  if (spine && typeof spine === "object") daily_horoscope.spine = spine;
  if (Array.isArray(scenList)) daily_horoscope.scenarios = scenList;

  const morning: Record<string, unknown> = {
    date: String(b.date ?? c.date ?? ""),
    tarot_card: c.tarot_card,
    tarot_explanation: c.tarot_explanation,
    numerology_number: c.numerology_number,
    numerology_explanation: c.numerology_explanation,
    daily_forecast_link: c.daily_forecast_link,
    daily_forecast_summary: c.daily_forecast_summary,
    daily_horoscope_generation_log_id: c.daily_horoscope_generation_log_id ?? scenarios?.daily_horoscope_generation_log_id,
    celestial_events: c.celestial_events,
    daily_recommendations: c.daily_recommendations,
    decision_engine: c.decision_engine,
    consistency: c.consistency,
    core_profile: c.core_profile,
  };

  if (Object.keys(daily_horoscope).length > 0) {
    morning.daily_horoscope = daily_horoscope;
  }

  return morning.date ? morning : null;
}

/**
 * Первый кадр дня как у нативного клиента: `GET /today/opening` + `GET /today/bundle`
 * → тот же контракт, что позже дополняет полный `GET /today`.
 */
export function assembleTodayCycleFromProgressive(opening: unknown, bundle: unknown): TodayCycleData | null {
  const morning = buildMorningFromTodayBundle(bundle);
  if (!morning) return null;

  const o = opening && typeof opening === "object" ? (opening as Record<string, unknown>) : {};
  const b = bundle && typeof bundle === "object" ? (bundle as Record<string, unknown>) : {};
  const date = String(o.date ?? b.date ?? "");
  if (!date) return null;

  const dc = (o.day_connection ?? null) as TodayCycleData["day_connection"];
  const coreRaw = b.core;
  const core = coreRaw && typeof coreRaw === "object" ? (coreRaw as Record<string, unknown>) : null;

  return normalizeTodayPayload({
    date,
    morning,
    morning_completed: Boolean(o.morning_completed),
    day_connection: dc,
    day_trackers: [],
    day_journal_entries: [],
    day_completed: Boolean(o.day_completed),
    evening: null,
    evening_completed: Boolean(o.evening_completed),
    morning_available: o.morning_available !== false,
    day_available: Boolean(o.day_available),
    evening_available: Boolean(o.evening_available),
    core_profile: (core?.core_profile ?? null) as TodayCycleData["core_profile"],
    rewards: null,
    reward_milestones: [],
  });
}

/** Подмешивает полный `GET /today` в снимок после первого прогрессивного слоя (bundle/light). */
export function mergeFullTodayCycleLayers(prev: TodayCycleData | null, cycle: TodayCycleData): TodayCycleData {
  if (!prev || prev.date !== cycle.date) {
    return normalizeTodayPayload(cycle);
  }
  let changed = false;
  const next: TodayCycleData = { ...prev };

  if (cycle.evening != null && prev.evening == null) {
    next.evening = cycle.evening;
    changed = true;
  }
  const ct = cycle.day_trackers?.length ?? 0;
  const pt = prev.day_trackers?.length ?? 0;
  if (ct > pt) {
    next.day_trackers = cycle.day_trackers;
    changed = true;
  }
  const cj = cycle.day_journal_entries?.length ?? 0;
  const pj = prev.day_journal_entries?.length ?? 0;
  if (cj > pj) {
    next.day_journal_entries = cycle.day_journal_entries;
    changed = true;
  }
  if (cycle.rewards != null && prev.rewards == null) {
    next.rewards = cycle.rewards;
    changed = true;
  }
  const cm = cycle.reward_milestones?.length ?? 0;
  const pm = prev.reward_milestones?.length ?? 0;
  if (cm > pm) {
    next.reward_milestones = cycle.reward_milestones;
    changed = true;
  }
  if (cycle.evening_completed !== prev.evening_completed) {
    next.evening_completed = cycle.evening_completed;
    changed = true;
  }

  const cCore = cycle.core_profile;
  if (
    cCore != null &&
    (prev.core_profile == null || prev.core_profile.profile_hash !== cCore.profile_hash)
  ) {
    next.core_profile = cCore;
    changed = true;
  }

  return changed ? normalizeTodayPayload(next) : prev;
}

export function getHoroscopeScenarioMeta(slug: string): { icon: string; accent: string } {
  switch (slug) {
    case "love":
      return { icon: "♥", accent: "#d16a8d" };
    case "family":
      return { icon: "⌂", accent: "#0f9d7a" };
    case "career":
      return { icon: "↗", accent: "#6d5bd0" };
    case "money":
      return { icon: "◌", accent: "#8a6f49" };
    default:
      return { icon: "✦", accent: "#c89a5c" };
  }
}

/** Продолжить тему дня лично (без совместимостей). */
export function getHoroscopeScenarioRoute(slug: string): { href: string; label: string } {
  switch (slug) {
    case "love":
      return { href: "/tarot?topic=relationships", label: RITUAL_COPY.horoscopeScenarioRouteLove };
    case "family":
      return { href: "/journal", label: RITUAL_COPY.horoscopeScenarioRouteFamily };
    case "career":
      return { href: "/tarot?topic=money", label: RITUAL_COPY.horoscopeScenarioRouteCareer };
    case "money":
      return { href: "/tarot?topic=money", label: RITUAL_COPY.horoscopeScenarioRouteMoney };
    default:
      return { href: "/profile", label: RITUAL_COPY.horoscopeScenarioRouteDefault };
  }
}

export function withDaySpineTracking(href: string, generationLogId?: number | null, actionKind?: string, actionLabel?: string) {
  if (!href) return href;
  try {
    const url = new URL(href, "https://todayflow.local");
    if (generationLogId && Number.isFinite(generationLogId)) {
      url.searchParams.set("day_spine_log_id", String(generationLogId));
    }
    if (actionKind) url.searchParams.set("day_spine_action", actionKind);
    if (actionLabel) url.searchParams.set("day_spine_label", actionLabel);
    url.searchParams.set("day_spine_surface", "today_daily_foundation");
    url.searchParams.set("day_spine_target", href);
    return `${url.pathname}${url.search}${url.hash}`;
  } catch {
    return href;
  }
}

export function formatTimer(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  const mm = String(minutes).padStart(2, "0");
  const ss = String(seconds).padStart(2, "0");
  return `${mm}:${ss}`;
}

export const thinkingMessages: Record<ThinkingMode, { title: string; message: string; status: string }> = {
  initial: {
    title: RITUAL_COPY.todayPageThinkingInitialTitle,
    message: RITUAL_COPY.todayPageThinkingInitialMessage,
    status: RITUAL_COPY.todayPageThinkingInitialStatus,
  },
  refresh: {
    title: RITUAL_COPY.todayPageThinkingRefreshTitle,
    message: RITUAL_COPY.todayPageThinkingRefreshMessage,
    status: RITUAL_COPY.todayPageThinkingRefreshStatus,
  },
  reveal: {
    title: RITUAL_COPY.todayPageThinkingRevealTitle,
    message: RITUAL_COPY.todayPageThinkingRevealMessage,
    status: RITUAL_COPY.todayPageThinkingRevealStatus,
  },
};

export async function ensureThinkingDuration(startedAt: number, minimumMs: number = 1100): Promise<void> {
  const elapsed = Date.now() - startedAt;
  if (elapsed >= minimumMs) return;
  await new Promise((resolve) => window.setTimeout(resolve, minimumMs - elapsed));
}

export function getWeekStart(isoDate: string): string {
  const [year, month, day] = isoDate.split("-").map(Number);
  const date = new Date(year, (month || 1) - 1, day || 1);
  const dayOfWeek = date.getDay();
  const diff = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
  date.setDate(date.getDate() + diff);
  return date.toISOString().split("T")[0];
}

export function shiftDate(isoDate: string, days: number): string {
  const [year, month, day] = isoDate.split("-").map(Number);
  const date = new Date(year, (month || 1) - 1, day || 1);
  date.setDate(date.getDate() + days);
  return date.toISOString().split("T")[0];
}

export function selectPriorityWeeklyGoal({
  goals,
  nudgeLevel,
  fusion,
}: {
  goals: WeeklyGoal[];
  nudgeLevel: "low" | "medium" | "high";
  fusion: FusionResponse | null;
}): WeeklyGoal | null {
  if (!goals.length) return null;
  const candidates = goals.filter((goal) => !goal.completed);
  const pool = candidates.length ? candidates : goals;
  const sorted = [...pool].sort((a, b) => {
    const aScore = scoreGoalForToday(a.title, nudgeLevel, fusion);
    const bScore = scoreGoalForToday(b.title, nudgeLevel, fusion);
    if (aScore !== bScore) return bScore - aScore;
    return a.title.localeCompare(b.title, "ru-RU");
  });
  return sorted[0] || null;
}

function scoreGoalForToday(title: string, nudgeLevel: "low" | "medium" | "high", fusion: FusionResponse | null): number {
  const text = title.toLowerCase();
  let score = 0;
  if (nudgeLevel === "high" && hasAny(text, ["дых", "восстанов", "щад", "ритуал", "пауза"])) score += 3;
  if (nudgeLevel === "medium" && hasAny(text, ["фокус", "блок", "чек", "дневник", "прогресс"])) score += 3;
  if (nudgeLevel === "low" && hasAny(text, ["результат", "приоритет", "стрик", "задач"])) score += 2;
  if (fusion && fusion.scores.energy < 45 && hasAny(text, ["энерг", "дых", "восстанов", "пауза"])) score += 2;
  if (fusion && fusion.scores.focus < 45 && hasAny(text, ["фокус", "задач", "блок"])) score += 2;
  if (fusion && fusion.scores.emotional_balance < 45 && hasAny(text, ["рефлекс", "дневник", "ритуал", "чек"])) score += 2;
  return score;
}

function hasAny(text: string, needles: string[]): boolean {
  return needles.some((needle) => text.includes(needle));
}

export function calculateDailyStreak(activeDates: Set<string>, anchorDate: string): number {
  let streak = 0;
  let cursor = anchorDate;
  while (activeDates.has(cursor)) {
    streak += 1;
    cursor = shiftDate(cursor, -1);
  }
  return streak;
}

export function buildRhythmWindow(
  activeDates: Set<string>,
  anchorDate: string,
  length: number,
): Array<{ date: string; label: string; active: boolean; isToday: boolean }> {
  const window: Array<{ date: string; label: string; active: boolean; isToday: boolean }> = [];
  for (let offset = length - 1; offset >= 0; offset -= 1) {
    const date = shiftDate(anchorDate, -offset);
    const [year, month, day] = date.split("-").map(Number);
    const dayDate = new Date(year, (month || 1) - 1, day || 1);
    window.push({
      date,
      label: dayDate.toLocaleDateString("ru-RU", { weekday: "short", day: "numeric" }),
      active: activeDates.has(date),
      isToday: date === anchorDate,
    });
  }
  return window;
}

function toIsoDateFromDateTime(dateTime: string): string | null {
  if (!dateTime) return null;
  const parsed = new Date(dateTime);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toISOString().split("T")[0];
}

export function buildRhythmMetaByDate({
  progressEntries,
  practiceHistory,
  journalEntries,
  todayIso,
}: {
  progressEntries: ProgressTrackerEntry[];
  practiceHistory: PracticeHistoryEntry[];
  journalEntries: JournalEntrySummary[];
  todayIso: string;
}): Record<string, RhythmMeta> {
  const fromDate = shiftDate(todayIso, -20);
  const metaByDate: Record<string, RhythmMeta> = {};
  const ensure = (date: string): RhythmMeta => {
    if (!metaByDate[date]) {
      metaByDate[date] = {
        progress: false,
        state: false,
        note: false,
        practice: false,
        journal: false,
      };
    }
    return metaByDate[date];
  };

  progressEntries.forEach((entry) => {
    const date = entry.date;
    if (date < fromDate || date > todayIso) return;
    const meta = ensure(date);
    if (entry.completed) meta.progress = true;
    if (entry.state || entry.state_scale) meta.state = true;
    if (entry.note) meta.note = true;
  });

  practiceHistory.forEach((entry) => {
    const date = toIsoDateFromDateTime(entry.completed_at);
    if (!date || date < fromDate || date > todayIso) return;
    ensure(date).practice = true;
  });

  journalEntries.forEach((entry) => {
    const date = entry.day || toIsoDateFromDateTime(entry.created_at);
    if (!date || date < fromDate || date > todayIso) return;
    ensure(date).journal = true;
  });

  return metaByDate;
}

export function buildRhythmDayTooltip(date: string, label: string, meta: RhythmMeta | undefined, active: boolean): string {
  const lines: string[] = [`${label} (${date})`];
  if (meta) {
    if (meta.progress) lines.push(RITUAL_COPY.rhythmTooltipProgressMark);
    if (meta.state) lines.push(RITUAL_COPY.rhythmTooltipStateMark);
    if (meta.note) lines.push(RITUAL_COPY.rhythmTooltipNoteMark);
    if (meta.practice) lines.push(RITUAL_COPY.rhythmTooltipPracticeMark);
    if (meta.journal) lines.push(RITUAL_COPY.rhythmTooltipJournalMark);
  }
  if (lines.length === 1) lines.push(RITUAL_COPY.rhythmTooltipNoActivity);
  lines.push(active ? RITUAL_COPY.rhythmTooltipClickUnmarkDay : RITUAL_COPY.rhythmTooltipClickMarkDay);
  return lines.join("\n");
}

export function buildDailyReward({
  streakDays,
  progressPercent,
  practiceCompleted,
  weeklyGoalSteppedToday,
  eveningCompleted,
}: {
  streakDays: number;
  progressPercent: number;
  practiceCompleted: boolean;
  weeklyGoalSteppedToday: boolean;
  eveningCompleted: boolean;
}): { level: "bronze" | "silver" | "gold"; title: string; message: string; badges: string[] } {
  const badges: string[] = [];
  if (streakDays >= 3) badges.push(formatDailyRewardStreakBadge(streakDays));
  if (practiceCompleted) badges.push(RITUAL_COPY.dailyRewardBadgePractice);
  if (weeklyGoalSteppedToday) badges.push(RITUAL_COPY.dailyRewardBadgeWeeklyStep);
  if (eveningCompleted) badges.push(RITUAL_COPY.dailyRewardBadgeDayClosed);

  if (progressPercent >= 75 && streakDays >= 5) {
    return {
      level: "gold",
      title: RITUAL_COPY.dailyRewardGoldTitle,
      message: RITUAL_COPY.dailyRewardGoldMessage,
      badges: badges.length ? badges : [RITUAL_COPY.dailyRewardGoldFallbackBadge],
    };
  }

  if (progressPercent >= 50 || streakDays >= 3) {
    return {
      level: "silver",
      title: RITUAL_COPY.dailyRewardSilverTitle,
      message: RITUAL_COPY.dailyRewardSilverMessage,
      badges: badges.length ? badges : [RITUAL_COPY.dailyRewardSilverFallbackBadge],
    };
  }

  return {
    level: "bronze",
    title: RITUAL_COPY.dailyRewardBronzeTitle,
    message: RITUAL_COPY.dailyRewardBronzeMessage,
    badges: badges.length ? badges : [RITUAL_COPY.dailyRewardBronzeFallbackBadge],
  };
}

export function buildRewardsCard(rewards: RewardsSnapshot): { level: "bronze" | "silver" | "gold"; title: string; message: string; badges: string[] } {
  const score = rewards.evolution_index;
  const level: "bronze" | "silver" | "gold" = score >= 75 ? "gold" : score >= 50 ? "silver" : "bronze";
  const title =
    level === "gold"
      ? RITUAL_COPY.rewardsCardTitleGold
      : level === "silver"
        ? RITUAL_COPY.rewardsCardTitleSilver
        : RITUAL_COPY.rewardsCardTitleBronze;
  const badges = [
    formatRewardsCardStreakBadge(rewards.streaks.daily_current),
    formatRewardsCardArchetypeBadge(rewards.archetype_level),
    formatRewardsCardDisciplineBadge(rewards.scores.discipline),
  ];
  if (rewards.streaks.habit_best > 0) badges.push(formatRewardsCardHabitsBadge(rewards.streaks.habit_best));
  if (rewards.streaks.ascetic_best > 0) badges.push(formatRewardsCardAsceticBadge(rewards.streaks.ascetic_best));
  return {
    level,
    title,
    message: rewards.message,
    badges,
  };
}

export function buildPersonalInsight({
  profileEmail,
  coreProfile,
  morning,
  fusion,
  nudgeLevel,
  streakDays,
  progressPercent,
}: {
  profileEmail: string | null;
  coreProfile: CoreProfile | null;
  morning: any | null;
  fusion: FusionResponse | null;
  nudgeLevel: "low" | "medium" | "high";
  streakDays: number;
  progressPercent: number;
}): { title: string; message: string; chips: string[]; ctaLabel: string; ctaHref: string } {
  const chips: string[] = [];
  const localName = profileEmail ? profileEmail.split("@")[0] : RITUAL_COPY.personalInsightLocalNameFallback;
  const identity = coreProfile?.interpretation?.identity;
  const dailyLens = coreProfile?.daily_interpretation?.daily_lenses?.general;
  const profileAnchor = identity || dailyLens;

  if (morning?.tarot_card?.name) chips.push(formatPersonalInsightChipTarot(morning.tarot_card.name));
  if (morning?.numerology_number?.value || morning?.numerology_number?.reduced_value) {
    chips.push(
      formatPersonalInsightChipNumber(morning.numerology_number.value || morning.numerology_number.reduced_value),
    );
  }
  if (fusion) {
    chips.push(formatPersonalInsightChipEnergy(rhythmTierLabelForScore(fusion.scores.energy)));
    chips.push(formatPersonalInsightChipFocus(rhythmTierLabelForScore(fusion.scores.focus)));
  }
  if (streakDays >= 2) chips.push(formatPersonalInsightChipStreak(streakDays));

  if (nudgeLevel === "high") {
    return {
      title: RITUAL_COPY.personalInsightTitleHigh,
      message: profileAnchor
        ? formatPersonalInsightMessageHighWithAnchor(localName, profileAnchor)
        : formatPersonalInsightMessageHighNoAnchor(localName),
      chips: chips.length ? chips : [RITUAL_COPY.personalInsightChipFallbackLow],
      ctaLabel: RITUAL_COPY.personalInsightCtaReturnMap,
      ctaHref: "/profile",
    };
  }

  if (progressPercent >= 50 && nudgeLevel === "low") {
    return {
      title: RITUAL_COPY.personalInsightTitleMid,
      message: profileAnchor
        ? formatPersonalInsightMessageMidWithAnchor(localName, profileAnchor)
        : formatPersonalInsightMessageMidNoAnchor(localName),
      chips: chips.length ? chips : [RITUAL_COPY.personalInsightChipFallbackStable],
      ctaLabel: RITUAL_COPY.personalInsightCtaOpenMap,
      ctaHref: "/profile",
    };
  }

  return {
    title: RITUAL_COPY.personalInsightTitleStart,
    message: profileAnchor
      ? formatPersonalInsightMessageStartWithAnchor(localName, profileAnchor)
      : formatPersonalInsightMessageStartNoAnchor(localName),
    chips: chips.length ? chips : [RITUAL_COPY.personalInsightChipFallbackStep],
    ctaLabel: RITUAL_COPY.personalInsightCtaViewMap,
    ctaHref: "/profile",
  };
}

export function buildNextAction({
  todayData,
  practiceCompleted,
  hasPractice,
  weeklyGoal,
}: {
  todayData: TodayCycleData;
  practiceCompleted: boolean;
  hasPractice: boolean;
  weeklyGoal: WeeklyGoal | null;
}): { label: string; href: string; message: string } {
  if (!todayData.day_connection?.morning_intention) {
    return {
      label: RITUAL_COPY.nextActionChooseFocusLabel,
      href: "#meaning-section",
      message: RITUAL_COPY.nextActionChooseFocusMessage,
    };
  }

  if (!practiceCompleted) {
    return {
      label: hasPractice ? RITUAL_COPY.nextActionDoPracticeLabel : RITUAL_COPY.nextActionChoosePracticeLabel,
      href: hasPractice ? "#checkin-section" : "/practices",
      message: RITUAL_COPY.nextActionPracticeMessage,
    };
  }

  if (weeklyGoal && !weeklyGoal.completed && weeklyGoal.last_progress_date !== todayData.date) {
    return {
      label: RITUAL_COPY.nextActionWeeklyStepLabel,
      href: "#checkin-section",
      message: RITUAL_COPY.nextActionWeeklyStepMessage,
    };
  }

  if (!todayData.evening_completed) {
    return {
      label: RITUAL_COPY.nextActionEveningLabel,
      href: "#closing-section",
      message: RITUAL_COPY.nextActionEveningMessage,
    };
  }

  return {
    label: RITUAL_COPY.nextActionStateLabel,
    href: "/flow",
    message: RITUAL_COPY.nextActionStateMessage,
  };
}

export function stagePanelStyle(done: boolean, expanded: boolean): CSSProperties {
  return {
    background: "linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(255,250,244,0.94) 100%)",
    borderRadius: "18px",
    border: "1px solid",
    borderColor: done ? "rgba(202, 177, 137, 0.58)" : "rgba(202, 177, 137, 0.34)",
    padding: expanded ? "var(--orbit-space-2xl)" : "var(--orbit-space-xl)",
    boxShadow: done ? "0 10px 28px rgba(198, 160, 102, 0.17)" : "0 8px 24px rgba(125, 100, 63, 0.11)",
    transition: "box-shadow 180ms ease, border-color 180ms ease",
  };
}

export function buildDailyNudge({
  currentHour,
  progressPercent,
  fusion,
  hasQuickActionDone,
  eveningCompleted,
}: {
  currentHour: number;
  progressPercent: number;
  fusion: FusionResponse | null;
  hasQuickActionDone: boolean;
  eveningCompleted: boolean;
}): { level: "low" | "medium" | "high"; message: string; ctaHref: string; ctaLabel: string } {
  let riskScore = 0;
  if (fusion) {
    if (fusion.scores.energy < 40) riskScore += 2;
    if (fusion.scores.emotional_balance < 45) riskScore += 1;
    if (fusion.scores.focus < 45) riskScore += 1;
  } else {
    riskScore += 1;
  }
  if (progressPercent < 35) riskScore += 1;
  if (currentHour >= 17 && progressPercent < 50) riskScore += 1;
  if (currentHour >= 20 && !eveningCompleted) riskScore += 1;
  if (!hasQuickActionDone && currentHour >= 13) riskScore += 1;

  const level: "low" | "medium" | "high" = riskScore >= 5 ? "high" : riskScore >= 3 ? "medium" : "low";

  if (level === "high") {
    return {
      level,
      message: RITUAL_COPY.dailyNudgeHighMessage,
      ctaHref: "#checkin-section",
      ctaLabel: RITUAL_COPY.dailyNudgeHighCta,
    };
  }

  if (level === "medium") {
    return {
      level,
      message: RITUAL_COPY.dailyNudgeMediumMessage,
      ctaHref: "#checkin-section",
      ctaLabel: RITUAL_COPY.dailyNudgeMediumCta,
    };
  }

  if (currentHour < 12) {
    return {
      level,
      message: RITUAL_COPY.dailyNudgeLowMorningMessage,
      ctaHref: "#meaning-section",
      ctaLabel: RITUAL_COPY.dailyNudgeLowMorningCta,
    };
  }

  if (currentHour < 19) {
    return {
      level,
      message: RITUAL_COPY.dailyNudgeLowDayMessage,
      ctaHref: "#checkin-section",
      ctaLabel: RITUAL_COPY.dailyNudgeLowDayCta,
    };
  }

  return {
    level,
    message: RITUAL_COPY.dailyNudgeLowEveningMessage,
    ctaHref: "#closing-section",
    ctaLabel: RITUAL_COPY.dailyNudgeLowEveningCta,
  };
}

export function buildDayEnergySummary(score: number): DayEnergySummary {
  if (score <= 30) {
    return {
      score,
      label: RITUAL_COPY.dayEnergyLabelCareful,
      guidance: RITUAL_COPY.dayEnergyGuidanceCareful,
    };
  }
  if (score <= 70) {
    return {
      score,
      label: RITUAL_COPY.dayEnergyLabelStable,
      guidance: RITUAL_COPY.dayEnergyGuidanceStable,
    };
  }
  return {
    score,
    label: RITUAL_COPY.dayEnergyLabelActive,
    guidance: RITUAL_COPY.dayEnergyGuidanceActive,
  };
}

function dedupeStrings(values: Array<string | null | undefined>): string[] {
  const seen = new Set<string>();
  const result: string[] = [];
  values.forEach((value) => {
    const normalized = (value || "").trim();
    if (!normalized) return;
    const key = normalized.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    result.push(normalized);
  });
  return result;
}

function normalizeFocusLabel(raw: string): string {
  const value = raw.toLowerCase();
  if (value.includes("работ")) return RITUAL_COPY.dayFocusThemeWork;
  if (value.includes("деньг") || value.includes("доход")) return RITUAL_COPY.dayFocusThemeMoney;
  if (value.includes("отнош") || value.includes("люб")) return RITUAL_COPY.dayFocusThemeRelationships;
  if (value.includes("сем")) return RITUAL_COPY.dayFocusThemeRelationships;
  if (value.includes("восстанов") || value.includes("энерг") || value.includes("ритм") || value.includes("состоя")) {
    return RITUAL_COPY.dayFocusThemeRecovery;
  }
  if (value.includes("заверш")) return RITUAL_COPY.dayFocusThemeClosure;
  return raw;
}

export function buildDayFocusSummary({
  todayData,
  weeklyGoal,
  quickPractice,
  coreProfile,
}: {
  todayData: TodayCycleData;
  weeklyGoal: WeeklyGoal | null;
  quickPractice: PracticeResponse | null;
  coreProfile: CoreProfile | null;
}): DayFocusSummary {
  const engineFocus = Array.isArray(todayData.morning?.decision_engine?.hero?.focus)
    ? todayData.morning.decision_engine.hero.focus
        .map((item: unknown) => String(item || "").trim())
        .filter(Boolean)
        .slice(0, 2)
    : [];
  if (engineFocus.length) {
    return {
      primary: engineFocus,
      label: engineFocus.join(", "),
    };
  }

  const scenarioTitles = Array.isArray(todayData.morning?.daily_horoscope?.scenarios)
    ? todayData.morning.daily_horoscope.scenarios
        .map((item: any) => {
          const title = String(item?.title ?? "").trim();
          if (title) return title;
          const slug = String(item?.slug ?? "").trim();
          if (!slug) return "";
          return humanizeFocusSlugForUi(slug);
        })
        .filter(Boolean)
    : [];
  const lifeAreaKeys = coreProfile?.interpretation?.life_areas
    ? Object.entries(coreProfile.interpretation.life_areas)
        .filter(([, value]) => !!value)
        .map(([key]) => key)
    : [];
  const goalFocus = weeklyGoal?.title ? [weeklyGoal.title] : [];
  const practiceFocus = quickPractice?.title ? [quickPractice.title] : [];

  const primary = dedupeStrings([...scenarioTitles, ...goalFocus, ...practiceFocus, ...lifeAreaKeys])
    .map(normalizeFocusLabel)
    .slice(0, 2);

  return {
    primary: primary.length ? primary : [RITUAL_COPY.dayFocusFallbackPrimary1, RITUAL_COPY.dayFocusFallbackPrimary2],
    label: primary.length ? primary.join(", ") : RITUAL_COPY.dayFocusFallbackLabel,
  };
}

export function buildDayRiskSummary({
  todayData,
  fusion,
}: {
  todayData: TodayCycleData;
  fusion: FusionResponse | null;
}): DayRiskSummary {
  const engineRisk = String(todayData.morning?.decision_engine?.hero?.risk || "").trim();
  if (engineRisk) {
    return {
      label: engineRisk,
      detail: engineRisk,
    };
  }

  const explicitRiskRaw =
    todayData.morning?.daily_horoscope?.spine?.main_risk ||
    todayData.morning?.daily_horoscope?.spine?.do_not_enter ||
    todayData.morning?.daily_recommendations?.what_to_avoid ||
    "";
  const explicitRisk = explicitRiskRaw ? repairRitualDoNotEnterLine(String(explicitRiskRaw).trim()) : "";

  if (explicitRisk) {
    const short = explicitRisk.split(/[.!?]/)[0]?.trim() || explicitRisk.trim();
    return {
      label: short,
      detail: explicitRisk,
    };
  }

  if ((fusion?.scores?.emotional_balance ?? 50) < 45) {
    return {
      label: RITUAL_COPY.dayRiskFusionEmotionalLabel,
      detail: RITUAL_COPY.dayRiskFusionEmotionalDetail,
    };
  }
  if ((fusion?.scores?.focus ?? 50) < 45) {
    return {
      label: RITUAL_COPY.dayRiskFusionFocusLabel,
      detail: RITUAL_COPY.dayRiskFusionFocusDetail,
    };
  }
  if ((fusion?.scores?.energy ?? 50) < 35) {
    return {
      label: RITUAL_COPY.dayRiskFusionEnergyLabel,
      detail: RITUAL_COPY.dayRiskFusionEnergyDetail,
    };
  }
  return {
    label: RITUAL_COPY.dayRiskFusionDefaultLabel,
    detail: RITUAL_COPY.dayRiskFusionDefaultDetail,
  };
}

export function buildTodayActionPlan({
  todayData,
  quickPractice,
  weeklyGoal,
}: {
  todayData: TodayCycleData;
  quickPractice: PracticeResponse | null;
  weeklyGoal: WeeklyGoal | null;
}): string[] {
  const engineActions = Array.isArray(todayData.morning?.decision_engine?.actions)
    ? dedupeStrings(todayData.morning.decision_engine.actions.map((item: unknown) => String(item || ""))).slice(0, 3)
    : [];
  if (engineActions.length) {
    return engineActions;
  }

  const fm = replaceQuotedEnSlugsForRuDisplay(String(todayData.morning?.daily_horoscope?.spine?.first_move || "").trim());
  const wtd = replaceQuotedEnSlugsForRuDisplay(String(todayData.morning?.daily_recommendations?.what_to_do || "").trim());
  const bestMode = replaceQuotedEnSlugsForRuDisplay(
    String(todayData.morning?.daily_horoscope?.spine?.best_mode || "").trim(),
  );
  return dedupeStrings([
    fm && !isGarbageRitualActionCue(fm) ? fm : null,
    bestMode || null,
    wtd && !isGarbageRitualActionCue(wtd) ? wtd : null,
    weeklyGoal && !weeklyGoal.completed ? formatActionPlanWeeklyStep(weeklyGoal.title) : null,
    quickPractice ? formatActionPlanQuickPractice(quickPractice.title) : null,
  ]).slice(0, 3);
}

export function buildTodayCriticalLimits({
  todayData,
  risk,
}: {
  todayData: TodayCycleData;
  risk: DayRiskSummary;
}): string[] {
  const engineLimits = Array.isArray(todayData.morning?.decision_engine?.limits)
    ? dedupeStrings(todayData.morning.decision_engine.limits.map((item: unknown) => String(item || ""))).slice(0, 3)
    : [];
  if (engineLimits.length) {
    return engineLimits;
  }

  const dne = repairRitualDoNotEnterLine(String(todayData.morning?.daily_horoscope?.spine?.do_not_enter || "").trim());
  const wta = replaceQuotedEnSlugsForRuDisplay(
    String(todayData.morning?.daily_recommendations?.what_to_avoid || "").trim(),
  );
  return dedupeStrings([
    dne || null,
    wta || null,
    risk.label ? formatTodayCriticalLimitAmplify(risk.label) : null,
  ]).slice(0, 3);
}

export function buildQuestionOfDay({
  focus: _focus,
  fusion,
  dateIso,
}: {
  focus: DayFocusSummary;
  fusion: FusionResponse | null;
  dateIso?: string;
}): DayQuestionCard {
  const lowEnergy = (fusion?.scores?.energy ?? 50) < 45;
  const lowFocus = (fusion?.scores?.focus ?? 50) < 45;
  const seedSource = dateIso || new Date().toISOString().slice(0, 10);
  const seed = seedSource.split("-").reduce((acc, part) => acc + Number(part || 0), 0);
  const randomIndex = (size: number) => (size > 0 ? Math.abs(seed) % size : 0);

  const pool = lowEnergy ? RITUAL_QUESTION_OF_DAY_LOW_ENERGY_CARDS : buildRitualQuestionOfDayDefaultCards(lowFocus);
  return pool[randomIndex(pool.length)];
}

export function buildWeeklyPatternMap({
  progressEntries,
  journalEntries,
  todayIso,
}: {
  progressEntries: ProgressTrackerEntry[];
  journalEntries: JournalEntrySummary[];
  todayIso: string;
}): WeeklyPatternMap {
  const weekStart = shiftDate(todayIso, -6);
  const weekProgress = progressEntries.filter((entry) => entry.date >= weekStart && entry.date <= todayIso);
  const scales = weekProgress.map((entry) => Number(entry.state_scale)).filter((v) => Number.isFinite(v) && v > 0);
  const avgStateScale = scales.length ? Math.round((scales.reduce((a, b) => a + b, 0) / scales.length) * 10) / 10 : null;
  const firstHalf = scales.slice(0, Math.max(1, Math.floor(scales.length / 2)));
  const secondHalf = scales.slice(Math.floor(scales.length / 2));
  const firstAvg = firstHalf.length ? firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length : 0;
  const secondAvg = secondHalf.length ? secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length : 0;
  const moodTrend: "up" | "down" | "stable" =
    secondAvg - firstAvg > 0.35 ? "up" : firstAvg - secondAvg > 0.35 ? "down" : "stable";

  const journalDaysSet = new Set(
    journalEntries
      .map((entry) => (entry.day || entry.created_at.split("T")[0] || "").trim())
      .filter((day) => day >= weekStart && day <= todayIso),
  );
  const journalDays = journalDaysSet.size;
  const trackedDays = new Set(weekProgress.map((entry) => entry.date)).size;

  const improvements: string[] = [];
  const regressions: string[] = [];

  if (moodTrend === "up") improvements.push(RITUAL_COPY.weeklyPatternMoodUp);
  if (moodTrend === "down") regressions.push(RITUAL_COPY.weeklyPatternMoodDown);
  if (trackedDays >= 4) improvements.push(RITUAL_COPY.weeklyPatternTrackedOften);
  if (trackedDays < 3) regressions.push(RITUAL_COPY.weeklyPatternTrackedRare);
  if (journalDays >= 3) improvements.push(RITUAL_COPY.weeklyPatternJournalHelps);
  if (journalDays === 0) regressions.push(RITUAL_COPY.weeklyPatternJournalNone);

  const recommendation =
    moodTrend === "down"
      ? RITUAL_COPY.weeklyPatternRecCareful3d
      : moodTrend === "up"
        ? RITUAL_COPY.weeklyPatternRecKeepRhythm
        : RITUAL_COPY.weeklyPatternRecNeutral;

  return { moodTrend, avgStateScale, trackedDays, journalDays, improvements, regressions, recommendation };
}

export function buildLifeNowSummary({
  weeklyGoal,
  quickPractice,
  rewards,
}: {
  weeklyGoal: WeeklyGoal | null;
  quickPractice: PracticeResponse | null;
  rewards: RewardsSnapshot | null;
}): {
  weeklyFocus: { title: string; body: string } | null;
  discipline: { title: string; body: string; status: string } | null;
} {
  const weeklyFocus = weeklyGoal
    ? {
        title: weeklyGoal.title,
        body: weeklyGoal.completed
          ? RITUAL_COPY.lifeNowWeeklyCompletedBody
          : weeklyGoal.last_progress_date
            ? RITUAL_COPY.lifeNowWeeklyProgressStaleBody
            : RITUAL_COPY.lifeNowWeeklyProgressFreshBody,
      }
    : null;

  const discipline =
    quickPractice || rewards?.streaks?.habit_best || rewards?.streaks?.ascetic_best
      ? {
          title: quickPractice?.title || RITUAL_COPY.lifeNowDisciplineTitleFallback,
          body: quickPractice
            ? RITUAL_COPY.lifeNowDisciplineBodyPractice
            : rewards?.streaks?.ascetic_best
              ? formatLifeNowDisciplineBodyAscetic(rewards.streaks.ascetic_best)
              : formatLifeNowDisciplineBodyHabit(rewards?.streaks?.habit_best ?? 0),
          status: quickPractice
            ? formatLifeNowDisciplineStatusMinutes(quickPractice.duration_minutes || 5)
            : rewards?.streaks?.ascetic_best
              ? formatLifeNowDisciplineStatusAscetic(rewards.streaks.ascetic_best)
              : formatLifeNowDisciplineStatusHabit(rewards?.streaks?.habit_best ?? 0),
        }
      : null;

  return { weeklyFocus, discipline };
}

export function buildDailyReturnCadence({
  currentHour,
  todayData,
}: {
  currentHour: number;
  todayData: TodayCycleData;
}): DailyReturnCadence {
  const hasQuickActionDone =
    todayData.day_completed ||
    todayData.day_trackers.length > 0 ||
    todayData.day_journal_entries.length > 0;

  if (!todayData.morning_completed) {
    return {
      title: currentHour < 12 ? RITUAL_COPY.dailyReturnMorningEarlyTitle : RITUAL_COPY.dailyReturnMorningLateTitle,
      message:
        currentHour < 12 ? RITUAL_COPY.dailyReturnMorningEarlyMessage : RITUAL_COPY.dailyReturnMorningLateMessage,
      ctaLabel: RITUAL_COPY.dailyReturnMorningCta,
      section: "morning",
      chip: RITUAL_COPY.dailyReturnMorningChip,
    };
  }

  if (!hasQuickActionDone) {
    return {
      title: RITUAL_COPY.dailyReturnDayTitle,
      message: currentHour < 15 ? RITUAL_COPY.dailyReturnDayMessageEarly : RITUAL_COPY.dailyReturnDayMessageDefault,
      ctaLabel: RITUAL_COPY.dailyReturnDayCta,
      section: "day",
      chip: RITUAL_COPY.dailyReturnDayChip,
    };
  }

  if (!todayData.evening_completed) {
    return {
      title:
        currentHour >= 18 ? RITUAL_COPY.dailyReturnEveningTitleLate : RITUAL_COPY.dailyReturnEveningTitlePrepare,
      message:
        currentHour >= 18 ? RITUAL_COPY.dailyReturnEveningMessageLate : RITUAL_COPY.dailyReturnEveningMessageDefault,
      ctaLabel: RITUAL_COPY.dailyReturnEveningCta,
      section: "evening",
      chip: RITUAL_COPY.dailyReturnEveningChip,
    };
  }

  return {
    title: RITUAL_COPY.dailyReturnAllSetTitle,
    message: RITUAL_COPY.dailyReturnAllSetMessage,
    ctaLabel: RITUAL_COPY.dailyReturnAllSetCta,
    section: "morning",
    chip: RITUAL_COPY.dailyReturnAllSetChip,
  };
}

export function inferPreferredSection(
  currentHour: number,
  todayData: Pick<
    TodayCycleData,
    | "morning_completed"
    | "day_completed"
    | "evening_completed"
    | "day_trackers"
    | "day_journal_entries"
    | "morning_available"
    | "day_available"
    | "evening_available"
  >,
): "morning" | "day" | "evening" {
  const hasQuickActionDone =
    todayData.day_completed ||
    todayData.day_trackers.length > 0 ||
    todayData.day_journal_entries.length > 0;

  if (!todayData.morning_completed && todayData.morning_available) return "morning";
  if (currentHour >= 18 && !todayData.evening_completed && todayData.evening_available) return "evening";
  if (!hasQuickActionDone && todayData.day_available) return "day";
  if (!todayData.evening_completed && currentHour >= 15 && todayData.evening_available) return "evening";
  if (todayData.day_available) return "day";
  if (todayData.morning_available) return "morning";
  return "evening";
}
