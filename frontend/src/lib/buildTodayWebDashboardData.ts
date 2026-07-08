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

  if (events.length > 0) return events;

  const lunarName = celestial?.lunar_phase?.name?.trim();
  return [
    { time: "Утро", title: lunarName || "Начало дня", active: true },
    { time: "День", title: "Фокус и действия" },
    { time: "Вечер", title: "Рефлексия дня" },
  ];
}

export function buildTodayWebWeeklyActivity(input: {
  dailySteps: Array<{ done: boolean }>;
  fusion?: FusionResponse | null;
}): number[] {
  const todayRatio =
    input.dailySteps.length > 0
      ? input.dailySteps.filter((step) => step.done).length / input.dailySteps.length
      : 0;
  const diaryEntries = input.fusion?.rhythm_context?.diary?.entries_last_7_days ?? 0;
  const baseline = Math.min(diaryEntries / 7, 1) * 0.65;

  return Array.from({ length: 7 }, (_, index) => {
    if (index === 6) return todayRatio;
    const wave = ((index % 3) + 1) * 0.08;
    return Math.min(1, Math.max(0.12, baseline + wave));
  });
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
