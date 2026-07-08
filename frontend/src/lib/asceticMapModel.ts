import { buildMoodMapWindow, formatMoodMapDate, type MoodMapLocale } from "@/lib/moodMapModel";

export type AsceticContractIn = {
  id: number;
  title: string;
  intention?: string | null;
  start_date: string;
  end_date?: string | null;
  status: string;
  streak_days: number;
  longest_streak_days: number;
  last_completed_date?: string | null;
};

export type AsceticCalendarTrackIn = {
  asceticism_id: string;
  title?: string | null;
  contract_status?: string | null;
  entries: { date: string; completed: boolean }[];
};

export type AsceticJourneyStep = {
  dateISO: string;
  completed: boolean;
  isFuture: boolean;
};

export type AsceticJourneyArc = {
  contractId: number;
  title: string;
  intention?: string | null;
  streakDays: number;
  longestStreak: number;
  status: string;
  steps: AsceticJourneyStep[];
};

export function buildAsceticJourneyArcs(
  contracts: AsceticContractIn[],
  tracks: AsceticCalendarTrackIn[],
  todayISO: string,
  windowDays = 35,
): AsceticJourneyArc[] {
  const window = buildMoodMapWindow(todayISO, windowDays);
  const entriesByAscetic = new Map<string, Map<string, boolean>>();
  for (const track of tracks) {
    const byDate = new Map<string, boolean>();
    for (const entry of track.entries) {
      if (window.includes(entry.date)) byDate.set(entry.date, entry.completed);
    }
    entriesByAscetic.set(track.asceticism_id, byDate);
  }

  const active = contracts.filter((c) => (c.status || "").toLowerCase() === "active");
  const pool = active.length ? active : contracts;

  return pool.map((contract) => {
    const track =
      tracks.find((t) => t.title === contract.title) ??
      tracks.find((t) => contract.intention && t.title?.includes(contract.title.slice(0, 12)));
    const byDate = track ? entriesByAscetic.get(track.asceticism_id) : undefined;
    const steps: AsceticJourneyStep[] = window.map((dateISO) => ({
      dateISO,
      completed: byDate?.get(dateISO) ?? false,
      isFuture: dateISO > todayISO,
    }));
    return {
      contractId: contract.id,
      title: contract.title,
      intention: contract.intention,
      streakDays: contract.streak_days,
      longestStreak: contract.longest_streak_days,
      status: contract.status,
      steps,
    };
  });
}

export function asceticJourneyStepColor(completed: boolean, isFuture: boolean): string {
  if (isFuture) return "rgba(180, 170, 158, 0.35)";
  if (completed) return "rgba(107, 143, 90, 0.92)";
  return "rgba(236, 228, 214, 0.55)";
}

export function buildAsceticJourneyObservation(arcs: AsceticJourneyArc[], locale: MoodMapLocale): string | null {
  if (!arcs.length) return null;
  const best = [...arcs].sort((a, b) => b.streakDays - a.streakDays)[0];
  if (locale === "ru") {
    if (best.streakDays >= 14) {
      return `«${best.title}» — уже ${best.streakDays} дней подряд. Тропа на карте заметна.`;
    }
    if (best.streakDays >= 3) {
      return `«${best.title}» держится ${best.streakDays} дня подряд — история аскезы складывается.`;
    }
    return "Первые отметки на тропе — каждый день добавляет новый камень.";
  }
  if (best.streakDays >= 14) {
    return `"${best.title}"—${best.streakDays} days in a row. The path on your map is clear.`;
  }
  if (best.streakDays >= 3) {
    return `"${best.title}" holds for ${best.streakDays} days—the ascetic story is taking shape.`;
  }
  return "First marks on the path—each day adds another stone.";
}

export function buildAsceticDayStory(arc: AsceticJourneyArc, dateISO: string, locale: MoodMapLocale): string {
  const step = arc.steps.find((s) => s.dateISO === dateISO);
  const dateLabel = formatMoodMapDate(dateISO, locale);
  if (!step || step.isFuture) {
    return locale === "ru" ? `${dateLabel} — день ещё впереди.` : `${dateLabel}—this day is still ahead.`;
  }
  if (locale === "ru") {
    return step.completed
      ? `${dateLabel} — «${arc.title}»: день отмечен на тропе.`
      : `${dateLabel} — «${arc.title}»: пауза, без отметки.`;
  }
  return step.completed
    ? `${dateLabel}—"${arc.title}": marked on the path.`
    : `${dateLabel}—"${arc.title}": a pause, no mark.`;
}

export function buildAsceticShareLine(arcs: AsceticJourneyArc[], locale: MoodMapLocale): string | null {
  const best = [...arcs].sort((a, b) => b.longestStreak - a.longestStreak)[0];
  if (!best) return null;
  if (locale === "ru") {
    return best.longestStreak >= 7
      ? `Моя тропа аскезы «${best.title}» — ${best.longestStreak} дней осознанного пути в TodayFlow.`
      : `Начинаю карту аскез «${best.title}» — история только складывается.`;
  }
  return best.longestStreak >= 7
    ? `My ascetic path "${best.title}"—${best.longestStreak} days of intentional practice in TodayFlow.`
    : `Starting my ascetic map "${best.title}"—the story is just beginning.`;
}
