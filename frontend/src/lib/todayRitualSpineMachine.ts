/**
 * Конечный автомат хребта Today (карта → число → настроение → чек-ин → «Твой день»).
 * Логика 1:1 с iOS `TodayFlow/Design/TodayRitualStateMachine.swift` (фазы, допустимость, reducer, эффекты).
 * DOM-якоря — через `mapRitualSpineScrollToDomId` (iOS id → веб `id`).
 */

import type { MeaningEventSource, MeaningEventType } from "@/lib/types";

export type TodayRitualSpineSnapshot = {
  dayOpened: boolean;
  tarotContinueAck: boolean;
  numberRevealed: boolean;
  tarotMainId: number | null;
  tarotMainResolved: boolean;
  selectedMoodId: string | null;
  checkInSubmitted: boolean;
  guideNarrativeLoading: boolean;
};

/** Паритет с `isRitualSpineComplete` в `todayRitualPersisted.ts` (включая `tarotContinueAck`). */
export function isRitualSpineSnapshotComplete(s: TodayRitualSpineSnapshot): boolean {
  return Boolean(
    s.tarotMainId != null &&
      s.tarotMainResolved &&
      s.tarotContinueAck &&
      s.numberRevealed &&
      s.selectedMoodId != null &&
      s.checkInSubmitted,
  );
}

export type TodayRitualSpinePhase =
  | { kind: "notStarted" }
  | { kind: "tarotInteractive" }
  | { kind: "numberSelecting" }
  | { kind: "checkIn" }
  | { kind: "dayReady"; narrativeRefreshing: boolean };

export function ritualSpinePhaseForSnapshot(s: TodayRitualSpineSnapshot): TodayRitualSpinePhase {
  if (!s.dayOpened) return { kind: "notStarted" };
  if (isRitualSpineSnapshotComplete(s)) {
    return { kind: "dayReady", narrativeRefreshing: s.guideNarrativeLoading };
  }
  if (!s.tarotContinueAck) return { kind: "tarotInteractive" };
  if (!s.numberRevealed) return { kind: "numberSelecting" };
  return { kind: "checkIn" };
}

export function ritualSpineConsistencyIssues(s: TodayRitualSpineSnapshot): string[] {
  const issues: string[] = [];
  if (s.tarotContinueAck && !s.dayOpened) issues.push("tarot_continue_without_opened_day");
  if (s.numberRevealed && !s.dayOpened) issues.push("number_without_opened_day");
  if (s.checkInSubmitted && !s.numberRevealed) issues.push("checkin_without_number");
  if (s.checkInSubmitted && s.selectedMoodId == null) issues.push("checkin_without_mood");
  if (isRitualSpineSnapshotComplete(s) && !s.tarotMainResolved) {
    issues.push("spine_complete_without_resolved_tarot");
  }
  return issues;
}

export type TodayRitualSpineUserEvent =
  | { type: "openedDay" }
  | { type: "continuedPastTarot" }
  | { type: "revealedNumber" }
  | { type: "selectedMood"; moodId: string }
  | { type: "submittedCheckIn" };

/** Якоря как в iOS `TodayRitualSpineEffects` — маппинг на DOM в `mapRitualSpineScrollToDomId`. */
export type RitualSpineScrollIos = "ritualDeck" | "ritualNumber" | "ritualCheckin" | "ritualYourDay";

/** Паритет iOS `TodayRitualSpineAnalyticsHint` — детали события задаёт `executeRitualSpineAnalytics`. */
export type RitualSpineAnalyticsHint =
  | { kind: "none" }
  | { kind: "numberRevealed" }
  | { kind: "moodSelected"; moodId: string };

export type TodayRitualSpineEffects = {
  saveOpenedDay: boolean;
  saveNumberRevealed: boolean;
  persistRitualExtras: boolean;
  resetNumberExtraSteps: boolean;
  scrollToAnchorId: RitualSpineScrollIos | null;
  scrollAfterNarrativeRefresh: RitualSpineScrollIos | null;
  analyticsHint: RitualSpineAnalyticsHint;
};

export function emptyRitualSpineEffects(): TodayRitualSpineEffects {
  return {
    saveOpenedDay: false,
    saveNumberRevealed: false,
    persistRitualExtras: false,
    resetNumberExtraSteps: false,
    scrollToAnchorId: null,
    scrollAfterNarrativeRefresh: null,
    analyticsHint: { kind: "none" },
  };
}

/** Прикрепить `generation_id` ответа guide, если он уже известен (таро, хребёт, DE-9 visibility). */
export function withOptionalGuideGenerationId(
  payload: Record<string, unknown>,
  guideGenerationId?: number | null,
): Record<string, unknown> {
  if (typeof guideGenerationId === "number" && guideGenerationId > 0) {
    return { ...payload, generation_id: guideGenerationId };
  }
  return payload;
}

/** Единая точка `trackMeaningEvent` / `onTrackMood` после reducer (паритет iOS `applySpineEffects`). */
export function executeRitualSpineAnalytics(
  hint: RitualSpineAnalyticsHint,
  ctx: {
    numerologyValue: string;
    /** Если guide за день уже загружен — связываем шаги хребта с `generation_logs` (§5.2). */
    guideGenerationId?: number | null;
    trackMeaningEvent: (e: {
      event_type: MeaningEventType;
      event_source: MeaningEventSource;
      payload?: Record<string, unknown> | null;
    }) => void;
    onTrackMood?: (id: string) => void;
  },
): void {
  switch (hint.kind) {
    case "none":
      return;
    case "numberRevealed":
      ctx.trackMeaningEvent({
        event_type: "number_selected",
        event_source: "today",
        payload: withOptionalGuideGenerationId(
          { revealed: true, numerology_value: ctx.numerologyValue },
          ctx.guideGenerationId,
        ),
      });
      return;
    case "moodSelected":
      ctx.onTrackMood?.(hint.moodId);
      ctx.trackMeaningEvent({
        event_type: "mood_selected",
        event_source: "today",
        payload: withOptionalGuideGenerationId(
          { mood_id: hint.moodId, source: "today_ritual" },
          ctx.guideGenerationId,
        ),
      });
      return;
    default:
      return;
  }
}

export function ritualSpineTransitionAllows(
  event: TodayRitualSpineUserEvent,
  before: TodayRitualSpineSnapshot,
): boolean {
  const phase = ritualSpinePhaseForSnapshot(before);
  switch (event.type) {
    case "openedDay":
      return phase.kind === "notStarted" && !before.dayOpened;
    case "continuedPastTarot":
      return phase.kind === "tarotInteractive" && before.dayOpened && !before.tarotContinueAck;
    case "revealedNumber":
      return phase.kind === "numberSelecting" && before.tarotContinueAck && !before.numberRevealed;
    case "selectedMood":
      return before.numberRevealed && !before.checkInSubmitted;
    case "submittedCheckIn":
      if (!before.numberRevealed || before.checkInSubmitted || before.selectedMoodId == null) return false;
      return before.tarotMainResolved;
    default:
      return false;
  }
}

export function applyTodayRitualSpineReducer(
  event: TodayRitualSpineUserEvent,
  before: TodayRitualSpineSnapshot,
): { after: TodayRitualSpineSnapshot; effects: TodayRitualSpineEffects } | null {
  if (!ritualSpineTransitionAllows(event, before)) return null;
  const after: TodayRitualSpineSnapshot = { ...before };
  const effects = emptyRitualSpineEffects();
  switch (event.type) {
    case "openedDay":
      after.dayOpened = true;
      effects.saveOpenedDay = true;
      effects.scrollToAnchorId = "ritualDeck";
      break;
    case "continuedPastTarot":
      after.tarotContinueAck = true;
      effects.persistRitualExtras = true;
      effects.scrollToAnchorId = "ritualNumber";
      break;
    case "revealedNumber":
      after.numberRevealed = true;
      effects.saveNumberRevealed = true;
      effects.resetNumberExtraSteps = true;
      effects.scrollToAnchorId = "ritualCheckin";
      effects.analyticsHint = { kind: "numberRevealed" };
      break;
    case "selectedMood":
      after.selectedMoodId = event.moodId;
      effects.persistRitualExtras = true;
      effects.analyticsHint = { kind: "moodSelected", moodId: event.moodId };
      break;
    case "submittedCheckIn":
      after.checkInSubmitted = true;
      effects.persistRitualExtras = true;
      effects.scrollAfterNarrativeRefresh = "ritualYourDay";
      break;
    default:
      return null;
  }
  return { after, effects };
}

/** iOS якорь → `document.getElementById` на вебе. */
export const RITUAL_SPINE_SCROLL_IOS_TO_WEB: Record<RitualSpineScrollIos, string> = {
  ritualDeck: "today-ritual-card",
  ritualNumber: "today-ritual-number",
  ritualCheckin: "today-ritual-checkin",
  ritualYourDay: "today-ritual-your-day",
};

export function mapRitualSpineScrollToDomId(ios: RitualSpineScrollIos): string {
  return RITUAL_SPINE_SCROLL_IOS_TO_WEB[ios] ?? ios;
}

export function scrollToRitualSpineDomAnchor(ios: RitualSpineScrollIos, delayMs = 80): void {
  if (typeof window === "undefined") return;
  const id = mapRitualSpineScrollToDomId(ios);
  window.setTimeout(() => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, delayMs);
}
