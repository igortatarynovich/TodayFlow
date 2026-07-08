import {
  isDayContinuityClosed,
  loadDayContinuity,
  previousDateISO,
  scanClosedDayContinuityRecords,
  type DayFocusOutcome,
} from "@/lib/todayDayContinuity";
import { eveningHighlightLabel, loadDayEngagement } from "@/lib/todayDayEngagement";
import { TODAY_FOCUS_TOPICS, TODAY_MORNING_MOODS } from "@/lib/todayDayDialogue";
import { buildMoodMapWindow, formatMoodMapDate, type MoodMapLocale, type MoodMapObservation } from "@/lib/moodMapModel";

export const PROMISE_MAP_WINDOW_DAYS = 35;
export const PROMISE_CELL_EMPTY = "rgba(180, 170, 158, 0.35)";

export type PromiseMapOutcome = DayFocusOutcome | "open";

export type PromiseMapDayRecord = {
  dateISO: string;
  promiseText: string;
  outcome: PromiseMapOutcome;
  outcomeNote?: string;
  closedAt?: string;
};

export type PromiseMapDayCell = {
  dateISO: string;
  record: PromiseMapDayRecord | null;
  color: string;
  outcomeLabel: string | null;
  isFuture: boolean;
};

const OUTCOME_LABEL_RU: Record<PromiseMapOutcome, string> = {
  done: "сделал",
  partial: "частично",
  not_done: "не сделал",
  open: "открыто",
};

const OUTCOME_LABEL_EN: Record<PromiseMapOutcome, string> = {
  done: "done",
  partial: "partial",
  not_done: "not done",
  open: "open",
};

export function promiseCellColor(outcome: PromiseMapOutcome | null, isFuture: boolean): string {
  if (isFuture || !outcome) return PROMISE_CELL_EMPTY;
  if (outcome === "done") return "rgba(107, 143, 90, 0.92)";
  if (outcome === "partial") return "rgba(191, 151, 95, 0.9)";
  if (outcome === "not_done") return "rgba(180, 120, 100, 0.78)";
  return "rgba(214, 179, 122, 0.62)";
}

export function promiseOutcomeLabel(outcome: PromiseMapOutcome, locale: MoodMapLocale): string {
  return locale === "ru" ? OUTCOME_LABEL_RU[outcome] : OUTCOME_LABEL_EN[outcome];
}

/** Newest first. Merges evening close + open day promises from engagement. */
export function scanPromiseMapDayRecords(): PromiseMapDayRecord[] {
  if (typeof window === "undefined") return [];

  const byDate = new Map<string, PromiseMapDayRecord>();
  const continuityPrefix = "todayflow.day_continuity.v1.";
  const engagementPrefix = "todayflow.day_engagement.v1.";

  try {
    for (let i = 0; i < window.localStorage.length; i += 1) {
      const key = window.localStorage.key(i);
      if (!key?.startsWith(continuityPrefix)) continue;
      const dateISO = key.slice(continuityPrefix.length);
      const continuity = loadDayContinuity(dateISO);
      if (!continuity?.mainFocus?.trim()) continue;
      const closed = isDayContinuityClosed(continuity);
      byDate.set(dateISO, {
        dateISO,
        promiseText: continuity.mainFocus.trim(),
        outcome: closed && continuity.outcome ? continuity.outcome : "open",
        outcomeNote: continuity.outcomeNote,
        closedAt: continuity.closedAt,
      });
    }

    for (let i = 0; i < window.localStorage.length; i += 1) {
      const key = window.localStorage.key(i);
      if (!key?.startsWith(engagementPrefix)) continue;
      const dateISO = key.slice(engagementPrefix.length);
      if (byDate.has(dateISO)) continue;
      const engagement = loadDayEngagement(dateISO);
      if (!engagement.dayGoal?.trim()) continue;
      byDate.set(dateISO, {
        dateISO,
        promiseText: engagement.dayGoal.trim(),
        outcome: "open",
      });
    }
  } catch {
    return [];
  }

  return Array.from(byDate.values()).sort((a, b) => b.dateISO.localeCompare(a.dateISO));
}

export function buildPromiseMapCells(todayISO: string, windowDays = PROMISE_MAP_WINDOW_DAYS): PromiseMapDayCell[] {
  const byDate = new Map(scanPromiseMapDayRecords().map((record) => [record.dateISO, record]));
  const locale: MoodMapLocale = "ru";

  return buildMoodMapWindow(todayISO, windowDays).map((dateISO) => {
    const record = byDate.get(dateISO) ?? null;
    const isFuture = dateISO > todayISO;
    return {
      dateISO,
      record,
      outcomeLabel: record ? promiseOutcomeLabel(record.outcome, locale) : null,
      color: record ? promiseCellColor(record.outcome, isFuture) : PROMISE_CELL_EMPTY,
      isFuture,
    };
  });
}

function moodLabelForId(moodId: string | null): string | null {
  if (!moodId) return null;
  return TODAY_MORNING_MOODS.find((m) => m.id === moodId)?.label ?? moodId;
}

function focusLabelForId(focusId: string | null): string | null {
  if (!focusId) return null;
  return TODAY_FOCUS_TOPICS.find((f) => f.id === focusId)?.label ?? focusId;
}

export function buildPromiseDayStory(record: PromiseMapDayRecord, locale: MoodMapLocale): string {
  const engagement = loadDayEngagement(record.dateISO);
  const prevContinuity = loadDayContinuity(previousDateISO(record.dateISO));
  const parts: string[] = [];

  if (locale === "ru") {
    parts.push(`${formatMoodMapDate(record.dateISO, locale)} — обещание: «${record.promiseText}».`);
    if (record.outcome === "open") {
      parts.push("Вечер ещё не закрыт — исход дня пока открыт.");
    } else if (record.outcome === "done") {
      parts.push("К вечеру главное удалось закрыть.");
    } else if (record.outcome === "partial") {
      parts.push("К вечеру получилось частично — и это тоже честная точка на карте.");
    } else {
      parts.push("К вечеру обещание осталось открытым.");
    }
    if (record.outcomeNote?.trim()) parts.push(`Заметка: «${record.outcomeNote.trim()}».`);
    const moodLabel = moodLabelForId(engagement.morningMoodId);
    if (moodLabel) parts.push(`Утром: «${moodLabel}».`);
    const focusLabel = focusLabelForId(engagement.focusTopicId);
    if (focusLabel) parts.push(`Фокус дня — «${focusLabel}».`);
    const evening = eveningHighlightLabel(engagement.eveningHighlightId);
    if (evening) parts.push(`Вечером главным было: ${evening.toLowerCase()}.`);
    if (prevContinuity?.outcome === "done") {
      parts.push("Накануне обещание закрыли — часто после этого следующий день держится ровнее.");
    } else if (prevContinuity?.outcome === "not_done") {
      parts.push("Накануне обещание осталось открытым — сегодня мог быть день восстановления.");
    }
    return parts.join(" ");
  }

  parts.push(`${formatMoodMapDate(record.dateISO, locale)} — promise: “${record.promiseText}”.`);
  if (record.outcome === "open") {
    parts.push("Evening isn’t closed yet—the day’s outcome is still open.");
  } else if (record.outcome === "done") {
    parts.push("By evening, the main focus landed.");
  } else if (record.outcome === "partial") {
    parts.push("By evening it landed partly—an honest point on the map.");
  } else {
    parts.push("By evening the promise stayed open.");
  }
  if (record.outcomeNote?.trim()) parts.push(`Note: “${record.outcomeNote.trim()}”.`);
  const moodLabel = moodLabelForId(engagement.morningMoodId);
  if (moodLabel) parts.push(`Morning: “${moodLabel}”.`);
  const focusLabel = focusLabelForId(engagement.focusTopicId);
  if (focusLabel) parts.push(`Day focus — “${focusLabel}”.`);
  const evening = eveningHighlightLabel(engagement.eveningHighlightId);
  if (evening) parts.push(`By evening, ${evening.toLowerCase()} stood out.`);
  if (prevContinuity?.outcome === "done") {
    parts.push("The day before closed well—often the next day steadies after that.");
  } else if (prevContinuity?.outcome === "not_done") {
    parts.push("The day before ended with an open promise—today may have been recovery.");
  }
  return parts.join(" ");
}

export function buildPromiseMapObservation(records: PromiseMapDayRecord[], locale: MoodMapLocale): MoodMapObservation | null {
  const closed = records.filter((record) => record.outcome !== "open");
  if (closed.length < 3) return null;

  const done = closed.filter((record) => record.outcome === "done").length;
  const notDone = closed.filter((record) => record.outcome === "not_done").length;
  const afterPrevDone = closed.filter((record) => {
    const prev = loadDayContinuity(previousDateISO(record.dateISO));
    return prev?.outcome === "done" && record.outcome === "done";
  }).length;

  if (locale === "ru") {
    if (afterPrevDone >= 2 && afterPrevDone >= Math.ceil(closed.length / 3)) {
      return { text: "Выполненные обещания чаще идут подряд — после закрытого вечера следующий день держится ровнее." };
    }
    if (done >= notDone && done >= 2) {
      return { text: "В последние закрытые дни обещания чаще удавалось закрыть — ритм держится." };
    }
    if (notDone >= 2) {
      return { text: "Несколько дней подряд обещания оставались открытыми — может, стоит смягчить масштаб на Today." };
    }
    return { text: "История обещаний складывается — каждый вечер добавляет новую точку." };
  }

  if (afterPrevDone >= 2 && afterPrevDone >= Math.ceil(closed.length / 3)) {
    return { text: "Kept promises often come in pairs—after a closed evening, the next day steadies." };
  }
  if (done >= notDone && done >= 2) {
    return { text: "Lately you’ve closed more promises than you left open—your rhythm is holding." };
  }
  if (notDone >= 2) {
    return { text: "Several days ended with open promises—Today might work better with a gentler scale." };
  }
  return { text: "Your promise story is forming—each evening adds another point." };
}

/** Closed promise records only (for stats). */
export function scanClosedPromiseMapRecords(): PromiseMapDayRecord[] {
  return scanClosedDayContinuityRecords().map((record) => ({
    dateISO: record.dateISO,
    promiseText: record.mainFocus,
    outcome: record.outcome!,
    outcomeNote: record.outcomeNote,
    closedAt: record.closedAt,
  }));
}
