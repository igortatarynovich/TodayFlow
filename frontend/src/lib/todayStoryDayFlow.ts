/**
 * Story-deck «Поток дня» — full day arc + real glance timed windows.
 *
 * Always: Утро → (окна / дневной ритм) → Вечер → Ночь.
 * Timed rows come from `glance_timeline` (exact sky windows). Morning/evening/night
 * come from day energy / focus signals — framing, not invented fake calm on transport fail.
 */

import type { GlanceTimelineItem } from "@/lib/todayGlanceTimeline";
import { formatGlanceClock } from "@/lib/todayGlanceTimeline";

export type StoryDayFlowValence = "favorable" | "caution" | "neutral";

export type StoryDayFlowPoint = {
  id: string;
  /** Left rail: «Утро» / «04:45» / «Вечер» / «Ночь». */
  phase: string;
  /** What this part of the day is for. */
  body: string;
  valence: StoryDayFlowValence;
  /** Cue: Старт / Благоприятно / Осторожнее / Итог / Отдых. */
  cue: string;
  /** True when phase is a clock from glance_timeline. */
  timed?: boolean;
};

export type BuildStoryDayFlowInput = {
  energyLine?: string | null;
  prioritize?: string | null;
  avoid?: string | null;
  moveDo?: string | null;
  moveAvoid?: string | null;
  /** Real exact-time windows from day_facts.glance_timeline. */
  glanceWindows?: GlanceTimelineItem[] | null;
};

const MAX_TIMED_WINDOWS = 3;

function clean(text: string | null | undefined): string {
  return (text || "").replace(/\s+/g, " ").trim();
}

function shorten(text: string, max = 90): string {
  const t = clean(text);
  if (!t) return "";
  if (t.length <= max) return t.replace(/[.!?]+$/u, "");
  return `${t.slice(0, max - 1).trim()}…`;
}

function energyTone(energyLine: string | null | undefined): "soft" | "fast" | "steady" {
  const e = clean(energyLine).toLowerCase();
  if (!e) return "steady";
  if (/спад|низк|береж|тих|мало сил|устал|ватн|мягк|лун|минус/.test(e)) return "soft";
  if (/быстр|импульс|драйв|разгон|высок|темп ввер|заряд/.test(e)) return "fast";
  return "steady";
}

function talkCaution(avoid: string, moveAvoid: string): boolean {
  const blob = `${avoid} ${moveAvoid}`.toLowerCase();
  return /слов|разговор|спор|диалог|письм|переписк|конфликт|острые тем/.test(blob);
}

function taskFocus(prioritize: string, moveDo: string): string | null {
  const raw = shorten(prioritize) || shorten(moveDo);
  return raw || null;
}

function asValence(raw: string | undefined): StoryDayFlowValence {
  if (raw === "favorable") return "favorable";
  if (raw === "caution") return "caution";
  return "neutral";
}

function expandWindowBody(label: string, valence: StoryDayFlowValence): string {
  const t = clean(label);
  if (!t) return valence === "caution" ? "В это окно лучше короче шаг." : "В это окно удобнее опереться.";
  const low = t.toLowerCase();
  if (/задач|импульс|ход/.test(low)) {
    return valence === "caution"
      ? `${t} — без разгона и лишних фронтов.`
      : `${t} — удобное окно для быстрых дел.`;
  }
  if (/диалог|письм|слов|контакт/.test(low)) {
    return valence === "caution"
      ? `${t} — мягче и короче, без острых тем.`
      : `${t} — хорошее окно для разговоров.`;
  }
  if (/отдых|пауза|настроен/.test(low)) {
    return `${t} — лучше снизить темп.`;
  }
  return valence === "caution" ? `${t} — тише и короче.` : `${t} — окно, на которое можно опереться.`;
}

function morningPoint(tone: "soft" | "fast" | "steady"): StoryDayFlowPoint {
  if (tone === "soft") {
    return {
      id: "morning",
      phase: "Утро",
      cue: "Старт",
      valence: "caution",
      body: "Тяжёлое или медленное утро — без разгона: сначала тело, потом дела.",
    };
  }
  if (tone === "fast") {
    return {
      id: "morning",
      phase: "Утро",
      cue: "Старт",
      valence: "favorable",
      body: "Быстрое утро: энергия уже есть — направь её в одно ясное дело.",
    };
  }
  return {
    id: "morning",
    phase: "Утро",
    cue: "Старт",
    valence: "favorable",
    body: "Лёгкое утро, без спешки — день ещё открыт.",
  };
}

function dayFallbackPoints(input: {
  tone: "soft" | "fast" | "steady";
  task: string | null;
  softTalk: boolean;
}): StoryDayFlowPoint[] {
  const tasks: StoryDayFlowPoint = {
    id: "day-tasks",
    phase: "День",
    cue: input.tone === "soft" ? "Осторожнее" : "Благоприятно",
    valence: input.tone === "soft" ? "caution" : "favorable",
    body: input.task
      ? `Задачи: ${input.task[0]!.toLowerCase()}${input.task.slice(1)}.`
      : input.tone === "soft"
        ? "Днём — задачи покороче и по одному фронту."
        : "Днём удобнее задачи, где нужна ясность.",
  };
  const dialogues: StoryDayFlowPoint = input.softTalk
    ? {
        id: "day-talk",
        phase: "Диалоги",
        cue: "Осторожнее",
        valence: "caution",
        body: "Разговоры — короче и мягче; острые темы лучше не разгонять.",
      }
    : {
        id: "day-talk",
        phase: "Диалоги",
        cue: "Благоприятно",
        valence: "favorable",
        body: "Днём хорошо идут диалоги и гибкость в общении.",
      };
  return [tasks, dialogues];
}

function timedPoints(windows: GlanceTimelineItem[]): StoryDayFlowPoint[] {
  const sorted = [...windows].sort((a, b) =>
    formatGlanceClock(a.time_local).localeCompare(formatGlanceClock(b.time_local)),
  );
  return sorted.slice(0, MAX_TIMED_WINDOWS).map((row, i) => {
    const valence = asValence(String(row.valence || ""));
    const label = clean(row.label_short) || "Окно дня";
    return {
      id: `window-${row.driver_id || i}`,
      phase: formatGlanceClock(row.time_local),
      cue: valence === "favorable" ? "Благоприятно" : valence === "caution" ? "Осторожнее" : "Окно",
      valence,
      body: expandWindowBody(label, valence),
      timed: true,
    };
  });
}

/**
 * Full-day Поток: morning + real timed windows (or day fallback) + evening + night rest.
 */
export function buildStoryDayFlow(input: BuildStoryDayFlowInput = {}): StoryDayFlowPoint[] {
  const tone = energyTone(input.energyLine);
  const prioritize = clean(input.prioritize);
  const avoid = clean(input.avoid);
  const moveDo = clean(input.moveDo);
  const moveAvoid = clean(input.moveAvoid);
  const task = taskFocus(prioritize, moveDo);
  const softTalk = talkCaution(avoid, moveAvoid);
  const windows = (input.glanceWindows || []).filter((w) => clean(w.time_local));

  const mid =
    windows.length > 0
      ? timedPoints(windows)
      : dayFallbackPoints({ tone, task, softTalk });

  const evening: StoryDayFlowPoint = {
    id: "evening",
    phase: "Вечер",
    cue: "Итог",
    valence: "neutral",
    body: "Вечер — подведение итогов и благодарность: что сработало, что отпустить.",
  };

  const night: StoryDayFlowPoint = {
    id: "night",
    phase: "Ночь",
    cue: "Отдых",
    valence: "neutral",
    body: "Ночь — отпускание и отдых; день уже сделал своё.",
  };

  return [morningPoint(tone), ...mid, evening, night];
}
