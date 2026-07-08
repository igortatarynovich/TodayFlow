import type { FlowTrackerChromeBundle } from "@/components/today/flowPracticesMainTabChrome";
import type {
  GoalCategoryTone,
  HabitCategoryTone,
  AsceticCategoryTone,
  PracticeCategoryTone,
  ScreenHeroKind,
} from "./entityTrackerSpec";

function fmtCatSummary(tpl: string, vars: Record<string, number>): string {
  return tpl.replace(/\{\{(\w+)\}\}/g, (_, k) => String(vars[k] ?? ""));
}

export type GoalEntityStatus = "active_progress" | "unstable" | "stalled" | "completed";
export type HabitEntityStatus = "active" | "unstable" | "dropped";
export type AsceticEntityStatus = "holding" | "breaks" | "failed" | "stopped";

export type CalendarGoalTrackIn = {
  id: number;
  title: string;
  scope: string;
  completed: boolean;
  step_dates: string[];
};

export type CalendarHabitTrackIn = {
  id: number;
  name: string;
  target_frequency: string;
  target_per_period: number;
  is_active: boolean;
  completed_dates: string[];
};

export type CalendarAsceticTrackIn = {
  asceticism_id: string;
  title?: string | null;
  contract_status?: string | null;
  entries: { date: string; completed: boolean }[];
};

export type AttentionItem = {
  kind: "goal" | "habit" | "ascetic";
  id: string;
  name: string;
  line: string;
  score: number;
};

export type BestItem = {
  kind: "goal" | "habit" | "ascetic";
  id: string;
  name: string;
  line: string;
  score: number;
};

function parseIso(d: string): number {
  return new Date(d + "T12:00:00").getTime();
}

function diffDaysLater(from: string, to: string): number {
  return Math.round((parseIso(to) - parseIso(from)) / 86400000);
}

function addDays(iso: string, delta: number): string {
  const t = new Date(iso + "T12:00:00");
  t.setDate(t.getDate() + delta);
  return t.toISOString().split("T")[0];
}

function inRollingWindow(d: string, todayIso: string, days: number): boolean {
  const start = addDays(todayIso, -(days - 1));
  return d >= start && d <= todayIso;
}

export function stepsInLastNDays(dates: string[], todayIso: string, n: number): number {
  return dates.filter((d) => inRollingWindow(d, todayIso, n)).length;
}

export function lastActivityGapDays(dates: string[], todayIso: string): number {
  if (!dates.length) return 999;
  const sorted = [...dates].sort();
  const last = sorted[sorted.length - 1];
  return Math.max(0, diffDaysLater(last, todayIso));
}

export function computeGoalEntityStatus(g: CalendarGoalTrackIn, todayIso: string): GoalEntityStatus {
  if (g.completed) return "completed";
  const gap = lastActivityGapDays(g.step_dates, todayIso);
  const last5 = stepsInLastNDays(g.step_dates, todayIso, 5);
  const last7 = stepsInLastNDays(g.step_dates, todayIso, 7);
  if (gap >= 7 || (last7 === 0 && gap >= 3)) return "stalled";
  if (last5 >= 2 && gap <= 3) return "active_progress";
  if (last7 >= 1) return "unstable";
  return "stalled";
}

export function expectedHabitSlots(h: CalendarHabitTrackIn, windowDays: number): number {
  if ((h.target_frequency || "daily") === "daily") return windowDays;
  return Math.min(windowDays, Math.max(1, h.target_per_period || 1));
}

export function computeHabitEntityStatus(h: CalendarHabitTrackIn, todayIso: string): HabitEntityStatus {
  if (!h.is_active) return "dropped";
  const window = 7;
  const done = h.completed_dates.filter((d) => inRollingWindow(d, todayIso, window));
  const expected = expectedHabitSlots(h, window);
  const actual = done.length;
  const consistency = expected > 0 ? actual / expected : 0;
  const gap = lastActivityGapDays(h.completed_dates.filter((d) => d <= todayIso), todayIso);
  if (consistency < 0.3 || gap >= 5) return "dropped";
  if (consistency >= 0.7 && gap <= 2) return "active";
  if ((consistency >= 0.3 && consistency < 0.7) || (gap >= 3 && gap <= 4)) return "unstable";
  return "unstable";
}

function asceticEntriesInWindow(
  entries: { date: string; completed: boolean }[],
  todayIso: string,
  days: number,
): { date: string; completed: boolean }[] {
  const start = addDays(todayIso, -(days - 1));
  return [...entries].filter((e) => e.date >= start && e.date <= todayIso).sort((a, b) => a.date.localeCompare(b.date));
}

function consecutiveViolationsFromEnd(sorted: { date: string; completed: boolean }[]): number {
  let c = 0;
  for (let i = sorted.length - 1; i >= 0; i--) {
    if (!sorted[i].completed) c += 1;
    else break;
  }
  return c;
}

export function computeAsceticEntityStatus(a: CalendarAsceticTrackIn, todayIso: string): AsceticEntityStatus {
  const st = (a.contract_status || "").toLowerCase();
  if (st === "paused" || st === "completed") return "stopped";
  const w = asceticEntriesInWindow(a.entries, todayIso, 14);
  if (!w.length && st === "active") return "holding";
  const w7 = asceticEntriesInWindow(a.entries, todayIso, 7);
  const violations = w7.filter((e) => !e.completed).length;
  const consec = consecutiveViolationsFromEnd(w7);
  if (consec >= 2) return "failed";
  if (violations >= 1) return "breaks";
  if (w7.some((e) => e.completed)) return "holding";
  return "holding";
}

function goalCategoryTone(goals: CalendarGoalTrackIn[], todayIso: string): GoalCategoryTone {
  const active = goals.filter((g) => !g.completed);
  if (!active.length) {
    if (!goals.length) return "empty";
    return "strong";
  }
  if (active.length >= 4) return "overloaded";
  const st = active.map((g) => computeGoalEntityStatus(g, todayIso));
  const stalled = st.filter((s) => s === "stalled").length;
  const good = st.filter((s) => s === "active_progress").length;
  if (stalled / active.length >= 0.5) return "weak";
  if (good / active.length >= 0.7) return "strong";
  return "mixed";
}

function habitCategoryTone(habits: CalendarHabitTrackIn[], todayIso: string): HabitCategoryTone {
  const active = habits.filter((h) => h.is_active);
  if (!active.length) return habits.length ? "weak" : "empty";
  const st = active.map((h) => computeHabitEntityStatus(h, todayIso));
  const dropped = st.filter((s) => s === "dropped").length;
  const ok = st.filter((s) => s === "active").length;
  if (dropped / active.length >= 0.5) return "weak";
  if (ok / active.length >= 0.7) return "strong";
  return "mixed";
}

function asceticCategoryTone(asc: CalendarAsceticTrackIn[], todayIso: string): AsceticCategoryTone {
  if (!asc.length) return "empty";
  const st = asc.map((a) => computeAsceticEntityStatus(a, todayIso));
  const bad = st.filter((s) => s === "failed" || s === "stopped").length;
  const ok = st.filter((s) => s === "holding").length;
  if (bad / asc.length >= 0.5) return "weak";
  if (ok / asc.length >= 0.7) return "strong";
  return "mixed";
}

function practiceCategoryTone(pct: number): PracticeCategoryTone {
  if (pct >= 60) return "active";
  if (pct < 30) return "ignored";
  if (pct === 0) return "empty";
  return "neutral";
}

type GoodBad = "good" | "mid" | "bad";

function goalBucket(s: GoalEntityStatus): GoodBad {
  if (s === "completed") return "good";
  if (s === "active_progress") return "good";
  if (s === "unstable") return "mid";
  return "bad";
}

function habitBucket(s: HabitEntityStatus): GoodBad {
  if (s === "active") return "good";
  if (s === "unstable") return "mid";
  return "bad";
}

function asceticBucket(s: AsceticEntityStatus): GoodBad {
  if (s === "holding") return "good";
  if (s === "breaks") return "mid";
  return "bad";
}

function practiceBucket(pct: number): GoodBad {
  if (pct >= 60) return "good";
  if (pct < 30) return "bad";
  return "mid";
}

export function countActiveTracks(
  goals: CalendarGoalTrackIn[],
  habits: CalendarHabitTrackIn[],
  ascetics: CalendarAsceticTrackIn[],
): number {
  const g = goals.filter((x) => !x.completed).length;
  const h = habits.filter((x) => x.is_active).length;
  const a = ascetics.filter((x) => {
    const st = (x.contract_status || "").toLowerCase();
    return st !== "paused" && st !== "completed";
  }).length;
  return g + h + a;
}

export function computeScreenHero(
  goals: CalendarGoalTrackIn[],
  habits: CalendarHabitTrackIn[],
  ascetics: CalendarAsceticTrackIn[],
  practicePct: number,
  todayIso: string,
): ScreenHeroKind {
  const totalActive = countActiveTracks(goals, habits, ascetics);
  const buckets: GoodBad[] = [];

  goals
    .filter((g) => !g.completed)
    .forEach((g) => buckets.push(goalBucket(computeGoalEntityStatus(g, todayIso))));
  habits
    .filter((h) => h.is_active)
    .forEach((h) => buckets.push(habitBucket(computeHabitEntityStatus(h, todayIso))));
  ascetics
    .filter((a) => {
      const st = (a.contract_status || "").toLowerCase();
      return st !== "paused" && st !== "completed";
    })
    .forEach((a) => buckets.push(asceticBucket(computeAsceticEntityStatus(a, todayIso))));
  buckets.push(practiceBucket(practicePct));

  if (!goals.length && !habits.length && !ascetics.length && practicePct < 5) return "empty";

  if (totalActive > 7) return "overloaded";

  const good = buckets.filter((b) => b === "good").length;
  const bad = buckets.filter((b) => b === "bad").length;
  const n = buckets.length;
  if (bad / n >= 0.6) return "dropped";
  if (good / n >= 0.6 && bad / n <= 0.25) return "in_flow";
  return "unstable";
}

export function categorySummaryLines(
  goals: CalendarGoalTrackIn[],
  habits: CalendarHabitTrackIn[],
  ascetics: CalendarAsceticTrackIn[],
  practicePct: number,
  todayIso: string,
  fc: FlowTrackerChromeBundle,
): {
  goals: { headline: string; tone: GoalCategoryTone };
  habits: { headline: string; tone: HabitCategoryTone };
  ascetics: { headline: string; tone: AsceticCategoryTone };
  practices: { headline: string; tone: PracticeCategoryTone };
} {
  const gTone = goalCategoryTone(goals, todayIso);
  const hTone = habitCategoryTone(habits, todayIso);
  const aTone = asceticCategoryTone(ascetics, todayIso);
  const pTone = practiceCategoryTone(practicePct);

  const gActive = goals.filter((x) => !x.completed);
  const gSt = gActive.map((g) => computeGoalEntityStatus(g, todayIso));
  const goalsHead =
    gActive.length === 0
      ? fc.trackingCatSummaryGoalsZero
      : fmtCatSummary(fc.trackingCatSummaryGoalsCounts, {
          total: gActive.length,
          inProgress: gSt.filter((s) => s === "active_progress").length,
          stalled: gSt.filter((s) => s === "stalled").length,
        });

  const hAct = habits.filter((h) => h.is_active);
  const hSt = hAct.map((h) => computeHabitEntityStatus(h, todayIso));
  const habitsHead =
    hAct.length === 0
      ? fc.trackingCatSummaryHabitsZero
      : fmtCatSummary(fc.trackingCatSummaryHabitsCounts, {
          total: hAct.length,
          holding: hSt.filter((s) => s === "active").length,
          unstable: hSt.filter((s) => s === "unstable").length,
        });

  const aAct = ascetics.filter((a) => {
    const st = (a.contract_status || "").toLowerCase();
    return st !== "paused" && st !== "completed";
  });
  const aSt = aAct.map((a) => computeAsceticEntityStatus(a, todayIso));
  const ascHead =
    aAct.length === 0
      ? fc.trackingCatSummaryAsceticsZero
      : fmtCatSummary(fc.trackingCatSummaryAsceticsCounts, {
          total: aAct.length,
          holding: aSt.filter((s) => s === "holding").length,
          broken: aSt.filter((s) => s === "breaks" || s === "failed").length,
        });

  const prHead =
    pTone === "empty"
      ? fc.trackingCatSummaryPracticesEmpty
      : fc.trackingCatSummaryPracticesPrefix +
        (pTone === "active"
          ? fc.trackingCatSummaryPracticesActive
          : pTone === "ignored"
            ? fc.trackingCatSummaryPracticesIgnored
            : fc.trackingCatSummaryPracticesNeutral);

  return {
    goals: { headline: goalsHead, tone: gTone },
    habits: { headline: habitsHead, tone: hTone },
    ascetics: { headline: ascHead, tone: aTone },
    practices: { headline: prHead, tone: pTone },
  };
}

function priorityGoal(g: CalendarGoalTrackIn, todayIso: string): number {
  const st = computeGoalEntityStatus(g, todayIso);
  const gap = lastActivityGapDays(g.step_dates, todayIso);
  const w = st === "stalled" ? 80 : st === "unstable" ? 40 : 5;
  return w + gap * 3 + 30; // goals weight
}

function priorityHabit(h: CalendarHabitTrackIn, todayIso: string): number {
  const st = computeHabitEntityStatus(h, todayIso);
  const gap = lastActivityGapDays(h.completed_dates, todayIso);
  const w = st === "dropped" ? 70 : st === "unstable" ? 35 : 5;
  return w + gap * 2 + 20;
}

function priorityAsc(a: CalendarAsceticTrackIn, todayIso: string): number {
  const st = computeAsceticEntityStatus(a, todayIso);
  const w7 = asceticEntriesInWindow(a.entries, todayIso, 7);
  const viol = w7.filter((e) => !e.completed).length;
  const w = st === "failed" ? 90 : st === "breaks" ? 50 : st === "stopped" ? 15 : 5;
  return w + viol * 10 + 25;
}

export function buildAttentionItems(
  goals: CalendarGoalTrackIn[],
  habits: CalendarHabitTrackIn[],
  ascetics: CalendarAsceticTrackIn[],
  todayIso: string,
  fc: FlowTrackerChromeBundle,
  limit = 3,
): AttentionItem[] {
  const items: AttentionItem[] = [];

  goals
    .filter((g) => !g.completed)
    .forEach((g) => {
      const st = computeGoalEntityStatus(g, todayIso);
      if (st === "stalled" || st === "unstable") {
        const gap = lastActivityGapDays(g.step_dates, todayIso);
        items.push({
          kind: "goal",
          id: String(g.id),
          name: g.title,
          line:
            st === "stalled"
              ? fmtCatSummary(fc.trackingAttentionGoalStalledLine, { days: gap })
              : fc.trackingAttentionUnstableShort,
          score: priorityGoal(g, todayIso),
        });
      }
    });

  habits
    .filter((h) => h.is_active)
    .forEach((h) => {
      const st = computeHabitEntityStatus(h, todayIso);
      if (st === "dropped" || st === "unstable") {
        const gap = lastActivityGapDays(h.completed_dates, todayIso);
        items.push({
          kind: "habit",
          id: String(h.id),
          name: h.name,
          line:
            st === "dropped"
              ? fmtCatSummary(fc.trackingAttentionHabitDroppedLine, { days: gap })
              : fc.trackingAttentionUnstableShort,
          score: priorityHabit(h, todayIso),
        });
      }
    });

  ascetics.forEach((a) => {
    const st = computeAsceticEntityStatus(a, todayIso);
    if (st === "breaks" || st === "failed") {
      const w7 = asceticEntriesInWindow(a.entries, todayIso, 7);
      const viol = w7.filter((e) => !e.completed).length;
      items.push({
        kind: "ascetic",
        id: a.asceticism_id,
        name: a.title || a.asceticism_id,
        line:
          st === "failed"
            ? fmtCatSummary(fc.trackingAttentionAsceticFailedLine, { count: viol })
            : fc.trackingAttentionAsceticBreaksLine,
        score: priorityAsc(a, todayIso),
      });
    }
  });

  return items.sort((a, b) => b.score - a.score).slice(0, limit);
}

export function habitTailStreak(completedDates: string[], todayIso: string): number {
  const set = new Set(completedDates.filter((d) => d <= todayIso));
  let streak = 0;
  let cursor = todayIso;
  for (let i = 0; i < 120; i++) {
    if (set.has(cursor)) streak += 1;
    else break;
    cursor = addDays(cursor, -1);
  }
  return streak;
}

export function asceticHoldingStreak(entries: { date: string; completed: boolean }[], todayIso: string): number {
  const sorted = [...entries].filter((e) => e.date <= todayIso).sort((a, b) => b.date.localeCompare(a.date));
  let streak = 0;
  for (const e of sorted) {
    if (e.completed) streak += 1;
    else break;
  }
  return streak;
}

export function buildBestItems(
  goals: CalendarGoalTrackIn[],
  habits: CalendarHabitTrackIn[],
  ascetics: CalendarAsceticTrackIn[],
  todayIso: string,
  fc: FlowTrackerChromeBundle,
  limit = 2,
): BestItem[] {
  const items: BestItem[] = [];

  habits
    .filter((h) => h.is_active)
    .forEach((h) => {
      const st = computeHabitEntityStatus(h, todayIso);
      if (st !== "active") return;
      const str = habitTailStreak(h.completed_dates, todayIso);
      if (str >= 3)
        items.push({
          kind: "habit",
          id: String(h.id),
          name: h.name,
          line: fmtCatSummary(fc.trackingBestHabitStreakLine, { n: str }),
          score: str * 10,
        });
    });

  ascetics.forEach((a) => {
    const st = computeAsceticEntityStatus(a, todayIso);
    if (st !== "holding") return;
    const str = asceticHoldingStreak(a.entries, todayIso);
    if (str >= 3)
      items.push({
        kind: "ascetic",
        id: a.asceticism_id,
        name: a.title || a.asceticism_id,
        line: fmtCatSummary(fc.trackingBestAsceticHoldLine, { n: str }),
        score: str * 9,
      });
  });

  goals
    .filter((g) => !g.completed)
    .forEach((g) => {
      const st = computeGoalEntityStatus(g, todayIso);
      if (st !== "active_progress") return;
      const n5 = stepsInLastNDays(g.step_dates, todayIso, 5);
      if (n5 >= 2)
        items.push({
          kind: "goal",
          id: String(g.id),
          name: g.title,
          line: fmtCatSummary(fc.trackingBestGoalSteps5dLine, { n: n5 }),
          score: n5 * 8,
        });
    });

  return items.sort((a, b) => b.score - a.score).slice(0, limit);
}
