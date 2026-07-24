/**
 * Локальное состояние взаимодействия с днём (цель, выбор карты/числа, практика).
 * Product output + learning events шлются из UI; здесь только persistence v0.
 */

import {
  TODAY_EVENING_HIGHLIGHTS,
  TODAY_FOCUS_TOPICS,
  TODAY_MORNING_MOODS,
} from "@/lib/todayDayDialogue";
import type { CoreProfile } from "@/lib/types";

export type DayEngagementState = {
  dayGoal: string | null;
  practiceStarted: boolean;
  practiceCompleted: boolean;
  recommendedPracticeId: string | null;
  tarotPickedId: number | null;
  tarotPickedName: string | null;
  numberConfirmed: boolean;
  affirmationRead: boolean;
  /** Growth A — habit/ascetic one-tap from Today (ids marked done today). */
  habitMarkedId: number | null;
  asceticMarkedId: number | null;
  todayOpened: boolean;
  /** Explicit L1 — when missing/stale, Today asks (learning signal). */
  morningMoodId: string | null;
  morningMoodCapturedAtMs: number | null;
  focusTopicId: string | null;
  focusTopicCapturedAtMs: number | null;
  /** Evening learning — what mattered most today. */
  eveningHighlightId: string | null;
  /** ILR v0 — post-ritual proximity chips (choice id). */
  tarotResonance: string | null;
  numberResonance: string | null;
  /** Soft indirect check-in under pulse — one per day. */
  softCheckInId: string | null;
};

const PREFIX = "todayflow.day_engagement.v1";

function storageKey(dateISO: string, profileScope?: string | null): string {
  if (profileScope) return `${PREFIX}.${dateISO}.p${profileScope}`;
  return `${PREFIX}.${dateISO}`;
}

/** Scope ritual/engagement persistence per natal profile when id is known. */
export function engagementProfileScope(profile?: CoreProfile | null): string | null {
  const id = profile?.astro?.profile_id ?? profile?.profiles?.selected_profile_id ?? null;
  return id != null ? String(id) : null;
}

const EMPTY: DayEngagementState = {
  dayGoal: null,
  practiceStarted: false,
  practiceCompleted: false,
  recommendedPracticeId: null,
  tarotPickedId: null,
  tarotPickedName: null,
  numberConfirmed: false,
  affirmationRead: false,
  habitMarkedId: null,
  asceticMarkedId: null,
  todayOpened: false,
  morningMoodId: null,
  morningMoodCapturedAtMs: null,
  focusTopicId: null,
  focusTopicCapturedAtMs: null,
  eveningHighlightId: null,
  tarotResonance: null,
  numberResonance: null,
  softCheckInId: null,
};

/** Stable empty state for SSR / pre-hydration (never read localStorage in useState initializer). */
export function createEmptyDayEngagement(): DayEngagementState {
  return { ...EMPTY };
}

export function loadDayEngagement(dateISO: string, profileScope?: string | null): DayEngagementState {
  if (typeof window === "undefined") return createEmptyDayEngagement();
  try {
    const raw = window.localStorage.getItem(storageKey(dateISO, profileScope));
    if (!raw) return { ...EMPTY };
    const p = JSON.parse(raw) as Partial<DayEngagementState>;
    return {
      dayGoal: typeof p.dayGoal === "string" ? p.dayGoal : null,
      practiceStarted: Boolean(p.practiceStarted),
      practiceCompleted: Boolean(p.practiceCompleted),
      recommendedPracticeId: typeof p.recommendedPracticeId === "string" ? p.recommendedPracticeId : null,
      tarotPickedId: typeof p.tarotPickedId === "number" ? p.tarotPickedId : null,
      tarotPickedName: typeof p.tarotPickedName === "string" ? p.tarotPickedName : null,
      numberConfirmed: Boolean(p.numberConfirmed),
      affirmationRead: Boolean(p.affirmationRead),
      habitMarkedId: typeof p.habitMarkedId === "number" ? p.habitMarkedId : null,
      asceticMarkedId: typeof p.asceticMarkedId === "number" ? p.asceticMarkedId : null,
      todayOpened: Boolean(p.todayOpened),
      morningMoodId: typeof p.morningMoodId === "string" ? p.morningMoodId : null,
      morningMoodCapturedAtMs:
        typeof p.morningMoodCapturedAtMs === "number" ? p.morningMoodCapturedAtMs : null,
      focusTopicId: typeof p.focusTopicId === "string" ? p.focusTopicId : null,
      focusTopicCapturedAtMs:
        typeof p.focusTopicCapturedAtMs === "number" ? p.focusTopicCapturedAtMs : null,
      eveningHighlightId: typeof p.eveningHighlightId === "string" ? p.eveningHighlightId : null,
      tarotResonance: typeof p.tarotResonance === "string" ? p.tarotResonance : null,
      numberResonance: typeof p.numberResonance === "string" ? p.numberResonance : null,
      softCheckInId: typeof p.softCheckInId === "string" ? p.softCheckInId : null,
    };
  } catch {
    return { ...EMPTY };
  }
}

export function saveDayEngagement(
  dateISO: string,
  patch: Partial<DayEngagementState>,
  profileScope?: string | null,
): DayEngagementState {
  const next = { ...loadDayEngagement(dateISO, profileScope), ...patch };
  if (typeof window !== "undefined") {
    try {
      window.localStorage.setItem(storageKey(dateISO, profileScope), JSON.stringify(next));
    } catch {
      /* quota */
    }
  }
  return next;
}

function parseCapturedAtMs(iso: string | null | undefined): number | null {
  if (!iso) return null;
  const ms = Date.parse(iso);
  return Number.isFinite(ms) ? ms : null;
}

/** Merge server CUM explicit state into local engagement (Profile read → Today give). */
export function mergeEngagementWithCompactUserModel(
  dateISO: string,
  local: DayEngagementState,
  cum: {
    current_state?: {
      mood_id?: string | null;
      mood_captured_at?: string | null;
      focus_topic_id?: string | null;
      focus_captured_at?: string | null;
      day_promise_text?: string | null;
    };
  } | null,
  profileScope?: string | null,
): DayEngagementState {
  const cs = cum?.current_state;
  if (!cs) return local;

  let next = { ...local };

  const serverMoodMs = parseCapturedAtMs(cs.mood_captured_at);
  const localMoodMs = local.morningMoodCapturedAtMs;
  if (
    cs.mood_id &&
    (localMoodMs == null || (serverMoodMs != null && serverMoodMs >= localMoodMs))
  ) {
    next = {
      ...next,
      morningMoodId: cs.mood_id,
      morningMoodCapturedAtMs: serverMoodMs ?? localMoodMs,
    };
  }

  const serverFocusMs = parseCapturedAtMs(cs.focus_captured_at);
  const localFocusMs = local.focusTopicCapturedAtMs;
  if (
    cs.focus_topic_id &&
    (localFocusMs == null || (serverFocusMs != null && serverFocusMs >= localFocusMs))
  ) {
    next = {
      ...next,
      focusTopicId: cs.focus_topic_id,
      focusTopicCapturedAtMs: serverFocusMs ?? localFocusMs,
    };
  }

  if (cs.day_promise_text && !local.dayGoal) {
    next = { ...next, dayGoal: cs.day_promise_text };
  }

  return next;
}

const ENGAGEMENT_STORAGE_PREFIX = "todayflow.day_engagement.v1.";

export type MoodMapDayRecord = {
  dateISO: string;
  moodId: string;
  moodLabel: string;
  focusTopicId: string | null;
  focusLabel: string | null;
  eveningHighlightId: string | null;
  dayGoal: string | null;
};

/** All days with morning mood from local persistence (newest first). */
export function scanMoodMapDayRecords(): MoodMapDayRecord[] {
  if (typeof window === "undefined") return [];

  const moodLabelById = new Map(TODAY_MORNING_MOODS.map((m) => [m.id, m.label]));
  const focusLabelById = new Map(TODAY_FOCUS_TOPICS.map((f) => [f.id, f.label]));

  const records: MoodMapDayRecord[] = [];
  try {
    for (let i = 0; i < window.localStorage.length; i += 1) {
      const key = window.localStorage.key(i);
      if (!key?.startsWith(ENGAGEMENT_STORAGE_PREFIX)) continue;
      const dateISO = key.slice(ENGAGEMENT_STORAGE_PREFIX.length);
      const engagement = loadDayEngagement(dateISO);
      if (!engagement.morningMoodId) continue;
      const moodId = engagement.morningMoodId;
      records.push({
        dateISO,
        moodId,
        moodLabel: moodLabelById.get(moodId) ?? moodId,
        focusTopicId: engagement.focusTopicId,
        focusLabel: engagement.focusTopicId
          ? (focusLabelById.get(engagement.focusTopicId) ?? engagement.focusTopicId)
          : null,
        eveningHighlightId: engagement.eveningHighlightId,
        dayGoal: engagement.dayGoal,
      });
    }
  } catch {
    return [];
  }

  records.sort((a, b) => b.dateISO.localeCompare(a.dateISO));
  return records;
}

export function eveningHighlightLabel(id: string | null | undefined): string | null {
  if (!id) return null;
  return TODAY_EVENING_HIGHLIGHTS.find((h) => h.id === id)?.label ?? id;
}
