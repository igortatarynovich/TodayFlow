import { scanClosedDayContinuityRecords, type DayFocusOutcome } from "@/lib/todayDayContinuity";
import { buildMoodMapObservation } from "@/lib/moodMapModel";
import { scanMoodMapDayRecords } from "@/lib/todayDayEngagement";
import { buildPromiseMapObservation, scanPromiseMapDayRecords } from "@/lib/promiseMapModel";
import { formatCumThemeLabel } from "@/lib/profilePage/cumThemeLabels";

export type FocusMapSeedPoint = {
  dateISO: string;
  outcome: DayFocusOutcome;
};

export type ProfileMapsPreviewModel = {
  totalSeeds: number;
  /** Oldest → newest for left-to-right dot strip. */
  recentSeeds: FocusMapSeedPoint[];
  hasSeeds: boolean;
};

export const PROFILE_MAPS_PREVIEW_COPY = {
  /** MP-1 / PROFILE_SCREEN_MASTER §7 — section band label (not tracker language). */
  sectionLabel: "Как меняется моя жизнь",
  sectionLead: "Узоры из Today — карты рисуются сами, без ручной статистики.",
  /** @deprecated use sectionLabel on section band; kept for inner aria where band omitted */
  label: "Как меняется моя жизнь",
  title: "Мои карты",
  focusMapTitle: "Карта фокуса",
  emptyLead: "Закрой день в Today — появится первая точка на личной карте.",
  seededLead: (count: number) =>
    count === 1
      ? "Один закрытый день уже на карте. Продолжай — история складывается сама."
      : `${count} закрытых дней уже на карте. Каждый вечер добавляет новую точку.`,
  legendDone: "Сделал",
  legendPartial: "Частично",
  legendNotDone: "Не сделал",
  exploreLabel: "Открыть карты",
  exploreHub: "Все карты",
  /** @deprecated flat links replaced by ProfileMapExploreGrid */
  exploreHabits: "Карта привычек",
  exploreMood: "Карта настроения",
  exploreEnergy: "Карта энергии",
  explorePromise: "Карта обещаний",
  exploreRhythm: "Карта ритма",
  exploreAscetic: "Карта аскез",
  exploreWish: "Карта желаний",
  exploreRelationship: "Карта связей",
  exploreTarot: "Карта таро",
  heatmapsLead: "35 дней — настроение, энергия и обещания дня. Нажми на день, чтобы увидеть историю.",
  habitWeaveTitle: "Привычки",
  habitWeaveLead: "Каждая привычка — свой цвет на карте за 35 дней. Нажми на отмеченный день.",
  heatmapDrillEmpty: "Выбери день с отметкой на карте.",
} as const;

export function buildProfileMapsPreviewModel(maxRecent = 7): ProfileMapsPreviewModel {
  const all = scanClosedDayContinuityRecords();
  const totalSeeds = all.length;
  const recentNewestFirst = all.slice(0, maxRecent);
  const recentSeeds: FocusMapSeedPoint[] = recentNewestFirst
    .slice()
    .reverse()
    .flatMap((record) => (record.outcome ? [{ dateISO: record.dateISO, outcome: record.outcome }] : []));

  return {
    totalSeeds,
    recentSeeds,
    hasSeeds: totalSeeds > 0,
  };
}

export function focusMapSeedTone(outcome: DayFocusOutcome): "done" | "partial" | "notDone" {
  if (outcome === "done") return "done";
  if (outcome === "partial") return "partial";
  return "notDone";
}

type LivingObservationInput = {
  livingSummary?: string | null;
  cycleObservation?: string | null;
  cum?: {
    behavioral_patterns?: { hints?: string[] };
    active_themes?: Array<{ id?: string }>;
  } | null;
};

/** Cross-map observation from local Today data — no API / LLM. */
export function buildProfileMapsLocalObservation(): string | null {
  const closed = scanClosedDayContinuityRecords();
  if (closed.length >= 3) {
    const done = closed.filter((r) => r.outcome === "done").length;
    if (done >= 2) {
      return "Вечером дни чаще закрываются с главным сделанным — на картах это уже заметно.";
    }
    if (closed.length >= 5) {
      return `${closed.length} закрытых дней на карте — история складывается без ручной статистики.`;
    }
  }

  const moodObs = buildMoodMapObservation(scanMoodMapDayRecords(), "ru");
  if (moodObs?.text) return moodObs.text;

  const promiseObs = buildPromiseMapObservation(scanPromiseMapDayRecords(), "ru");
  if (promiseObs?.text) return promiseObs.text;

  if (closed.length === 1) {
    return "Первая точка на карте — продолжай отмечать Today, узор проявится сам.";
  }

  return null;
}

/** Cross-map observation for Living Maps block — living layer, CUM, then local maps. */
export function buildProfileLivingObservation(input: LivingObservationInput): string | null {
  const summary = input.livingSummary?.trim();
  if (summary) return summary;

  const hint = input.cum?.behavioral_patterns?.hints?.find((item) => item.trim());
  if (hint) return hint.trim();

  const themeId = input.cum?.active_themes?.[0]?.id?.trim();
  if (themeId) {
    const label = formatCumThemeLabel(themeId);
    return `Сейчас чаще всего всплывает тема «${label}».`;
  }

  const cycle = input.cycleObservation?.trim();
  if (cycle) return cycle;

  return buildProfileMapsLocalObservation();
}
