import type { FlowTrackerChromeBundle } from "@/components/today/flowPracticesMainTabChrome";
import { HEATMAP_THRESHOLDS } from "./heatmapTokens";
import { lineDone, type CalendarDayLite, type LineId } from "./trackingRhythm";
import type { TrackerTier } from "./trackerSpec";

export type HeatmapFilterMode = "all" | "goals" | "habits" | "ascetics" | "practices";

export type HeatmapCellKind =
  | "no_data"
  | "intensity_0"
  | "intensity_low"
  | "intensity_mid"
  | "intensity_high"
  | "entity_done"
  | "entity_miss";

export type CalendarGoalTrackLike = {
  id: number;
  title: string;
  completed: boolean;
  step_dates: string[];
};

export type CalendarHabitTrackLike = {
  id: number;
  name: string;
  is_active: boolean;
  completed_dates: string[];
};

export type CalendarAsceticTrackLike = {
  asceticism_id: string;
  title?: string | null;
  contract_status?: string | null;
  entries: { date: string; completed: boolean }[];
};

function asceticActive(a: CalendarAsceticTrackLike): boolean {
  const st = (a.contract_status || "").toLowerCase();
  return st !== "paused" && st !== "completed";
}

export function activeGoalList(goals: CalendarGoalTrackLike[]): CalendarGoalTrackLike[] {
  return goals.filter((g) => !g.completed);
}

export function activeHabitList(habits: CalendarHabitTrackLike[], selectedIds: Set<number> | null): CalendarHabitTrackLike[] {
  const act = habits.filter((h) => h.is_active);
  if (!selectedIds || selectedIds.size === 0) return act;
  return act.filter((h) => selectedIds.has(h.id));
}

export function activeAsceticList(ascetics: CalendarAsceticTrackLike[]): CalendarAsceticTrackLike[] {
  return ascetics.filter(asceticActive);
}

export function goalsForHeatmap(goals: CalendarGoalTrackLike[], selectedGoalIds: Set<number> | null): CalendarGoalTrackLike[] {
  const a = activeGoalList(goals);
  if (!selectedGoalIds || selectedGoalIds.size === 0) return a;
  return a.filter((g) => selectedGoalIds.has(g.id));
}

export function asceticsForHeatmap(
  ascetics: CalendarAsceticTrackLike[],
  selectedAsceticIds: Set<string> | null,
): CalendarAsceticTrackLike[] {
  const a = activeAsceticList(ascetics);
  if (!selectedAsceticIds || selectedAsceticIds.size === 0) return a;
  return a.filter((x) => selectedAsceticIds.has(x.asceticism_id));
}

export function addDaysIsoLocal(iso: string, deltaDays: number): string {
  const [y, m, d] = iso.split("-").map(Number);
  const dt = new Date(y, (m || 1) - 1, d || 1);
  dt.setDate(dt.getDate() + deltaDays);
  return toIsoLocalDate(dt);
}

export function monthAnchorIso(iso: string): string {
  const [y, m] = iso.split("-").map(Number);
  return `${y}-${String(m || 1).padStart(2, "0")}-01`;
}

export function toIsoLocalDate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/** Понедельник = 0 … воскресенье = 6 */
export function isoWeekdayMon0(iso: string): number {
  const d = new Date(iso + "T12:00:00").getDay();
  return d === 0 ? 6 : d - 1;
}

export type MonthCell = {
  date: string | null;
  /** день в пределах отображаемого месяца */
  inMonth: boolean;
};

/** Сетка недель (пн-вс), null = пустая клетка вне месяца */
export function buildMonthWeekGrid(year: number, monthIndex0: number): MonthCell[][] {
  const first = new Date(year, monthIndex0, 1);
  const last = new Date(year, monthIndex0 + 1, 0);
  const pad = isoWeekdayMon0(toIsoLocalDate(first));
  const daysInMonth = last.getDate();
  const cells: MonthCell[] = [];
  for (let i = 0; i < pad; i++) cells.push({ date: null, inMonth: false });
  for (let d = 1; d <= daysInMonth; d++) {
    const dt = new Date(year, monthIndex0, d);
    cells.push({ date: toIsoLocalDate(dt), inMonth: true });
  }
  while (cells.length % 7 !== 0) {
    cells.push({ date: null, inMonth: false });
  }
  const weeks: MonthCell[][] = [];
  for (let i = 0; i < cells.length; i += 7) {
    weeks.push(cells.slice(i, i + 7));
  }
  return weeks;
}

function dayMap(days: CalendarDayLite[]): Map<string, CalendarDayLite> {
  const m = new Map<string, CalendarDayLite>();
  for (const d of days) m.set(d.date, d);
  return m;
}

function countDoneGoals(date: string, list: CalendarGoalTrackLike[]): number {
  return list.filter((g) => g.step_dates.includes(date)).length;
}

function countDoneHabits(date: string, list: CalendarHabitTrackLike[]): number {
  return list.filter((h) => h.completed_dates.includes(date)).length;
}

function countDoneAscetics(date: string, list: CalendarAsceticTrackLike[]): number {
  let n = 0;
  for (const a of list) {
    const e = a.entries.find((x) => x.date === date);
    if (e?.completed) n += 1;
  }
  return n;
}

function practiceDone(day: CalendarDayLite | undefined): boolean {
  if (!day) return false;
  return lineDone(day, "practice" as LineId);
}

export function denominatorForMode(
  mode: HeatmapFilterMode,
  goals: CalendarGoalTrackLike[],
  habits: CalendarHabitTrackLike[],
  ascetics: CalendarAsceticTrackLike[],
  selectedGoalIds: Set<number> | null,
  selectedHabitIds: Set<number> | null,
  selectedAsceticIds: Set<string> | null,
): number {
  if (mode === "all") {
    const g = activeGoalList(goals).length;
    const h = activeHabitList(habits, null).length;
    const a = activeAsceticList(ascetics).length;
    const p = 1;
    return g + h + a + p;
  }
  if (mode === "goals") {
    return goalsForHeatmap(goals, selectedGoalIds).length;
  }
  if (mode === "habits") {
    return activeHabitList(habits, selectedHabitIds).length;
  }
  if (mode === "ascetics") {
    return asceticsForHeatmap(ascetics, selectedAsceticIds).length;
  }
  return 1;
}

export function numeratorForMode(
  date: string,
  mode: HeatmapFilterMode,
  goals: CalendarGoalTrackLike[],
  habits: CalendarHabitTrackLike[],
  ascetics: CalendarAsceticTrackLike[],
  dayRow: CalendarDayLite | undefined,
  selectedGoalIds: Set<number> | null,
  selectedHabitIds: Set<number> | null,
  selectedAsceticIds: Set<string> | null,
): number {
  if (mode === "all") {
    let n = countDoneGoals(date, activeGoalList(goals));
    n += countDoneHabits(date, activeHabitList(habits, null));
    n += countDoneAscetics(date, activeAsceticList(ascetics));
    if (practiceDone(dayRow)) n += 1;
    return n;
  }
  if (mode === "goals") {
    return countDoneGoals(date, goalsForHeatmap(goals, selectedGoalIds));
  }
  if (mode === "habits") {
    return countDoneHabits(date, activeHabitList(habits, selectedHabitIds));
  }
  if (mode === "ascetics") {
    return countDoneAscetics(date, asceticsForHeatmap(ascetics, selectedAsceticIds));
  }
  return practiceDone(dayRow) ? 1 : 0;
}

export function ratioToCellKind(ratio: number, total: number): HeatmapCellKind {
  if (total <= 0) return "intensity_0";
  const r = ratio;
  if (r <= HEATMAP_THRESHOLDS.lowMin) return "intensity_0";
  if (r < HEATMAP_THRESHOLDS.midMin) return "intensity_low";
  if (r < HEATMAP_THRESHOLDS.highMin) return "intensity_mid";
  return "intensity_high";
}

export function cellKindForDay(
  date: string,
  todayIso: string,
  mode: HeatmapFilterMode,
  entity: { type: "goal" | "habit" | "ascetic"; id: string } | null,
  goals: CalendarGoalTrackLike[],
  habits: CalendarHabitTrackLike[],
  ascetics: CalendarAsceticTrackLike[],
  days: CalendarDayLite[],
  selectedGoalIds: Set<number> | null,
  selectedHabitIds: Set<number> | null,
  selectedAsceticIds: Set<string> | null,
): HeatmapCellKind {
  if (date > todayIso) return "no_data";
  const dm = dayMap(days);
  const row = dm.get(date);

  if (entity) {
    if (entity.type === "goal") {
      const g = goals.find((x) => String(x.id) === entity.id);
      if (!g || g.completed) return "no_data";
      return g.step_dates.includes(date) ? "entity_done" : "entity_miss";
    }
    if (entity.type === "habit") {
      const h = habits.find((x) => String(x.id) === entity.id);
      if (!h || !h.is_active) return "no_data";
      return h.completed_dates.includes(date) ? "entity_done" : "entity_miss";
    }
    const a = ascetics.find((x) => x.asceticism_id === entity.id);
    if (!a) return "no_data";
    const e = a.entries.find((x) => x.date === date);
    if (!e) return "entity_miss";
    return e.completed ? "entity_done" : "entity_miss";
  }

  const total = denominatorForMode(mode, goals, habits, ascetics, selectedGoalIds, selectedHabitIds, selectedAsceticIds);
  if (total <= 0) return "no_data";
  const num = numeratorForMode(date, mode, goals, habits, ascetics, row, selectedGoalIds, selectedHabitIds, selectedAsceticIds);
  const ratio = num / total;
  return ratioToCellKind(ratio, total);
}

export type DayDrilldown = {
  date: string;
  goalsDone: number;
  goalsTotal: number;
  habitsDone: number;
  habitsTotal: number;
  asceticsDone: number;
  asceticsTotal: number;
  practiceDone: boolean;
  allTotal: number;
  allDone: number;
  caption: string;
};

export function buildDayDrilldown(
  date: string,
  todayIso: string,
  goals: CalendarGoalTrackLike[],
  habits: CalendarHabitTrackLike[],
  ascetics: CalendarAsceticTrackLike[],
  days: CalendarDayLite[],
  fc: FlowTrackerChromeBundle,
): DayDrilldown | null {
  if (date > todayIso) return null;
  const dm = dayMap(days);
  const row = dm.get(date);
  const gList = activeGoalList(goals);
  const hList = activeHabitList(habits, null);
  const aList = activeAsceticList(ascetics);
  const gDone = countDoneGoals(date, gList);
  const hDone = countDoneHabits(date, hList);
  const aDone = countDoneAscetics(date, aList);
  const pDone = practiceDone(row);
  const allTotal = gList.length + hList.length + aList.length + 1;
  const allDone = gDone + hDone + aDone + (pDone ? 1 : 0);
  let caption = "";
  if (allTotal === 0) caption = fc.heatmapDrillDayCaptionEmptyTracks;
  else if (allDone === 0) caption = fc.heatmapDrillDayCaptionQuietDay;
  else if (gList.length > 0 && gDone === 0) caption = fc.heatmapDrillDayCaptionGoalsNoStep;
  else if (allDone >= allTotal * 0.7) caption = fc.heatmapDrillDayCaptionStrongDay;
  else caption = fc.heatmapDrillDayCaptionPartialDay;

  return {
    date,
    goalsDone: gDone,
    goalsTotal: gList.length,
    habitsDone: hDone,
    habitsTotal: hList.length,
    asceticsDone: aDone,
    asceticsTotal: aList.length,
    practiceDone: pDone,
    allTotal,
    allDone,
    caption,
  };
}

export function heatmapInsightUnderMap(
  mode: HeatmapFilterMode,
  tier: TrackerTier,
  flatCells: { date: string | null; kind: HeatmapCellKind; inMonth: boolean }[],
  todayIso: string,
  fc: FlowTrackerChromeBundle,
): string {
  const kinds: HeatmapCellKind[] = [];
  for (const c of flatCells) {
    if (c.date && c.date <= todayIso && c.inMonth) kinds.push(c.kind);
  }
  const hasLow = kinds.some((k) => k === "intensity_0" || k === "intensity_low" || k === "entity_miss");
  const volatile =
    kinds.filter((k) => k === "intensity_high" || k === "entity_done").length > 0 &&
    kinds.filter((k) => k === "intensity_0" || k === "intensity_low").length > 2;

  const map: Record<HeatmapFilterMode, Record<TrackerTier, string>> = {
    all: {
      free: hasLow ? fc.heatmapUnderMapInsightAllFreeGaps : fc.heatmapUnderMapInsightAllFreeSteady,
      pro: volatile ? fc.heatmapUnderMapInsightAllProVolatile : fc.heatmapUnderMapInsightAllProSteady,
      premium:
        volatile && hasLow ? fc.heatmapUnderMapInsightAllPremiumStutter : fc.heatmapUnderMapInsightAllPremiumReadable,
    },
    habits: {
      free: hasLow ? fc.heatmapUnderMapInsightHabitsFreeGaps : fc.heatmapUnderMapInsightHabitsFreeSteady,
      pro: fc.heatmapUnderMapInsightHabitsPro,
      premium: fc.heatmapUnderMapInsightHabitsPremium,
    },
    goals: {
      free: hasLow ? fc.heatmapUnderMapInsightGoalsFreeGaps : fc.heatmapUnderMapInsightGoalsFreeSteady,
      pro: fc.heatmapUnderMapInsightGoalsPro,
      premium: fc.heatmapUnderMapInsightGoalsPremium,
    },
    ascetics: {
      free: hasLow ? fc.heatmapUnderMapInsightAsceticsFreeGaps : fc.heatmapUnderMapInsightAsceticsFreeSteady,
      pro: fc.heatmapUnderMapInsightAsceticsPro,
      premium: fc.heatmapUnderMapInsightAsceticsPremium,
    },
    practices: {
      free: hasLow ? fc.heatmapUnderMapInsightPracticesFreeGaps : fc.heatmapUnderMapInsightPracticesFreeSteady,
      pro: fc.heatmapUnderMapInsightPracticesPro,
      premium: fc.heatmapUnderMapInsightPracticesPremium,
    },
  };
  return map[mode][tier];
}
