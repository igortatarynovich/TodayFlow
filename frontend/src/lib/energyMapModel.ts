import { tempoLabelForEnergyScore } from "@/components/today/todayRitualCopy";
import { loadDayContinuity, previousDateISO } from "@/lib/todayDayContinuity";
import { loadDayEngagement } from "@/lib/todayDayEngagement";
import {
  mergeEnergyMapRecords,
  scanEnergyMapDayRecords,
  type EnergyMapDayRecord,
} from "@/lib/energyMapStorage";
import { buildMoodMapWindow, formatMoodMapDate, type MoodMapLocale, type MoodMapObservation } from "@/lib/moodMapModel";
import { isLowEnergyMood, TODAY_FOCUS_TOPICS, TODAY_MORNING_MOODS } from "@/lib/todayDayDialogue";

export const ENERGY_CELL_EMPTY = "rgba(180, 170, 158, 0.35)";

export type EnergyMapDayCell = {
  dateISO: string;
  record: EnergyMapDayRecord | null;
  color: string;
  tempoLabel: string | null;
  isFuture: boolean;
};

const MOOD_INFER_SCORE: Record<string, number> = {
  tired: 32,
  overloaded: 28,
  anxious: 36,
  calm: 56,
  driven: 78,
  inspired: 82,
};

export function energyCellColor(score: number): string {
  const s = Math.max(0, Math.min(100, Math.round(score)));
  if (s < 38) return "rgba(154, 132, 104, 0.72)";
  if (s < 58) return "rgba(191, 168, 120, 0.78)";
  if (s < 78) return "rgba(175, 138, 82, 0.88)";
  return "rgba(107, 143, 90, 0.92)";
}

export function inferEnergyFromMood(moodId: string): number | null {
  const score = MOOD_INFER_SCORE[moodId.trim().toLowerCase()];
  return typeof score === "number" ? score : isLowEnergyMood(moodId) ? 34 : null;
}

export function buildEnergyMapRecordsWithMoodFallback(): EnergyMapDayRecord[] {
  const stored = scanEnergyMapDayRecords();
  const byDate = new Map(stored.map((record) => [record.dateISO, record]));

  if (typeof window !== "undefined") {
    const prefix = "todayflow.day_engagement.v1.";
    for (let i = 0; i < window.localStorage.length; i += 1) {
      const key = window.localStorage.key(i);
      if (!key?.startsWith(prefix)) continue;
      const dateISO = key.slice(prefix.length);
      if (byDate.has(dateISO)) continue;
      const engagement = loadDayEngagement(dateISO);
      if (!engagement.morningMoodId) continue;
      const inferred = inferEnergyFromMood(engagement.morningMoodId);
      if (inferred == null) continue;
      byDate.set(dateISO, {
        dateISO,
        energyScore: inferred,
        tempoLabel: tempoLabelForEnergyScore(inferred),
        capturedAt: new Date(engagement.morningMoodCapturedAtMs ?? Date.now()).toISOString(),
        source: "mood_infer",
      });
    }
  }

  return mergeEnergyMapRecords(Array.from(byDate.values()));
}

export function buildEnergyMapCells(todayISO: string, windowDays = 35): EnergyMapDayCell[] {
  const byDate = new Map(buildEnergyMapRecordsWithMoodFallback().map((record) => [record.dateISO, record]));
  return buildMoodMapWindow(todayISO, windowDays).map((dateISO) => {
    const record = byDate.get(dateISO) ?? null;
    const isFuture = dateISO > todayISO;
    const tempoLabel = record ? record.tempoLabel ?? tempoLabelForEnergyScore(record.energyScore) : null;
    return {
      dateISO,
      record,
      tempoLabel,
      color: record ? energyCellColor(record.energyScore) : ENERGY_CELL_EMPTY,
      isFuture,
    };
  });
}

function moodLabelForId(moodId: string | null): string | null {
  if (!moodId) return null;
  return TODAY_MORNING_MOODS.find((m) => m.id === moodId)?.label ?? moodId;
}

export function buildEnergyDayStory(record: EnergyMapDayRecord, locale: MoodMapLocale): string {
  const engagement = loadDayEngagement(record.dateISO);
  const continuity = loadDayContinuity(record.dateISO);
  const prevContinuity = loadDayContinuity(previousDateISO(record.dateISO));
  const tempo = record.tempoLabel ?? tempoLabelForEnergyScore(record.energyScore);
  const parts: string[] = [];

  if (locale === "ru") {
    parts.push(`${formatMoodMapDate(record.dateISO, locale)} — ${tempo} темп дня.`);
    const moodLabel = moodLabelForId(engagement.morningMoodId);
    if (moodLabel) parts.push(`Утром отмечено: «${moodLabel}».`);
    if (engagement.focusTopicId) {
      const focusLabel =
        TODAY_FOCUS_TOPICS.find((topic) => topic.id === engagement.focusTopicId)?.label ??
        engagement.focusTopicId;
      parts.push(`Фокус дня — «${focusLabel}».`);
    }
    if (prevContinuity?.outcome === "done") {
      parts.push("Накануне день закрыли спокойно — часто после этого темп держится ровнее.");
    } else if (prevContinuity?.outcome === "not_done") {
      parts.push("Накануне день закрыли с незавершённым обещанием — телу могло понадобиться больше восстановления.");
    }
    if (continuity?.outcome === "done") parts.push("Вечером главное удалось закрыть.");
    if (continuity?.outcome === "not_done") parts.push("К вечеру обещание дня осталось открытым.");
    return parts.join(" ");
  }

  parts.push(`${formatMoodMapDate(record.dateISO, locale)} — a ${tempo} day tempo.`);
  const moodLabel = moodLabelForId(engagement.morningMoodId);
  if (moodLabel) parts.push(`Morning mark: “${moodLabel}”.`);
  if (prevContinuity?.outcome === "done") {
    parts.push("The day before closed well—tempo often steadies after that.");
  } else if (prevContinuity?.outcome === "not_done") {
    parts.push("The day before ended with an open promise—recovery may have taken more.");
  }
  if (continuity?.outcome === "done") parts.push("By evening, the main focus landed.");
  if (continuity?.outcome === "not_done") parts.push("By evening, the day’s promise stayed open.");
  return parts.join(" ");
}

export function buildEnergyMapObservation(records: EnergyMapDayRecord[], locale: MoodMapLocale): MoodMapObservation | null {
  if (records.length < 3) return null;

  const strong = records.filter((r) => r.energyScore >= 78).length;
  const quiet = records.filter((r) => r.energyScore < 38).length;
  const afterClosed = records.filter((record) => {
    const prev = loadDayContinuity(previousDateISO(record.dateISO));
    return prev?.outcome === "done" && record.energyScore >= 58;
  }).length;

  if (locale === "ru") {
    if (afterClosed >= 2 && afterClosed >= Math.ceil(records.length / 3)) {
      return {
        text: "Сильные дни чаще приходятся после спокойно закрытого предыдущего вечера.",
      };
    }
    if (strong >= quiet && strong >= 2) {
      return { text: "В последние отметки чаще выпадали подвижные и ровные дни — темп держится." };
    }
    if (quiet >= 2) {
      return { text: "В последние недели чаще были тихие дни — телу, возможно, нужен более мягкий ритм." };
    }
    return { text: "Темп дней постепенно складывается в узор — продолжай отмечать Today." };
  }

  if (afterClosed >= 2 && afterClosed >= Math.ceil(records.length / 3)) {
    return { text: "Stronger days often follow an evening when you closed the day well." };
  }
  if (strong >= quiet && strong >= 2) {
    return { text: "Lately steady and active days show up more often—your tempo is holding." };
  }
  if (quiet >= 2) {
    return { text: "Lately quieter days dominate—your body may be asking for a gentler rhythm." };
  }
  return { text: "Your day tempo is forming a pattern—keep living Today." };
}
