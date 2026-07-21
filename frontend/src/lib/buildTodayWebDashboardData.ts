import type { DsTimelineEvent } from "@/design-system";
import type {
  FusionResponse,
  MorningRitualData,
  PracticeResponse,
  TodayCycleData,
} from "@/components/today/todayPageUtils";
import type { TodayWebPractice } from "@/components/product-ui/TodayWebDashboard";

const DEFAULT_TIMES = ["07:30", "11:15", "15:00", "19:30"];

export function buildTodayWebTimeline(morning?: MorningRitualData | null): DsTimelineEvent[] {
  const celestial = morning?.celestial_events;
  const events: DsTimelineEvent[] = [];
  let timeIndex = 0;

  for (const aspect of celestial?.sky_aspects?.slice(0, 3) ?? []) {
    events.push({
      time: DEFAULT_TIMES[timeIndex] ?? "12:00",
      title: aspect.title?.trim() || aspect.aspect?.trim() || "Небесный аспект",
      active: timeIndex === 0,
    });
    timeIndex += 1;
  }

  for (const transit of celestial?.personal_transits?.slice(0, 2) ?? []) {
    events.push({
      time: DEFAULT_TIMES[timeIndex] ?? "18:00",
      title: transit.title?.trim() || "Персональный транзит",
    });
    timeIndex += 1;
  }

  // PR-2: no generic Утро/День/Вечер filler when sky data is absent.
  return events;
}

/**
 * Weekly rhythm for Today rail. Returns null when there is no real per-day signal
 * (PR-2: no synthetic wave bars).
 */
export function buildTodayWebWeeklyActivity(input: {
  dailySteps: Array<{ done: boolean }>;
  fusion?: FusionResponse | null;
}): number[] | null {
  const steps = input.dailySteps;
  if (steps.length >= 7) {
    return steps.slice(-7).map((step) => (step.done ? 1 : 0));
  }
  if (steps.length > 0) {
    const padded = Array.from({ length: 7 }, (_, index) => {
      const step = steps[index];
      return step ? (step.done ? 1 : 0) : 0;
    });
    // Only surface when at least one real done step exists.
    return padded.some((v) => v > 0) ? padded : null;
  }
  return null;
}

export function buildTodayWebStreak(todayData: TodayCycleData): number {
  return todayData.rewards?.streaks?.daily_current ?? 0;
}

export function buildTodayWebPractices(input: {
  quickPractice?: PracticeResponse | null;
  practiceCompleted?: boolean;
  actionPlan?: string[];
}): TodayWebPractice[] {
  const fromPlan = (input.actionPlan ?? []).slice(0, 3).map((title, index) => ({
    id: `plan-${index}`,
    title,
    durationLabel: undefined,
    completed: input.practiceCompleted && index === 0,
  }));

  if (fromPlan.length >= 2) return fromPlan;

  if (input.quickPractice) {
    return [
      {
        id: String(input.quickPractice.id),
        title: input.quickPractice.title,
        durationLabel: input.quickPractice.duration_minutes
          ? `${input.quickPractice.duration_minutes} мин`
          : undefined,
        completed: input.practiceCompleted,
      },
      ...fromPlan.filter((item) => item.title !== input.quickPractice?.title),
    ];
  }

  return fromPlan;
}
