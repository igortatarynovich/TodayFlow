/**
 * Story-deck «Поток дня» — 4–5 phase points across the whole day.
 * Not glance_timeline (exact aspect windows). Presentation from day signals only.
 */

export type StoryDayFlowValence = "favorable" | "caution" | "neutral";

export type StoryDayFlowPoint = {
  id: string;
  /** Утро / День / Диалоги / Вечер / Ночь */
  phase: string;
  /** Clear human guidance — what this part of the day is for. */
  body: string;
  valence: StoryDayFlowValence;
  /** Short cue above the body (Благоприятно / Осторожнее / Старт …). */
  cue: string;
};

export type BuildStoryDayFlowInput = {
  energyLine?: string | null;
  prioritize?: string | null;
  avoid?: string | null;
  moveDo?: string | null;
  moveAvoid?: string | null;
};

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

/**
 * Always returns 5 points: start → tasks → dialogues → evening close → night rest.
 * Bodies adapt to energy / focus / avoid when present; otherwise calm defaults.
 */
export function buildStoryDayFlow(input: BuildStoryDayFlowInput = {}): StoryDayFlowPoint[] {
  const energy = clean(input.energyLine);
  const prioritize = clean(input.prioritize);
  const avoid = clean(input.avoid);
  const moveDo = clean(input.moveDo);
  const moveAvoid = clean(input.moveAvoid);
  const tone = energyTone(energy);
  const task = taskFocus(prioritize, moveDo);
  const softTalk = talkCaution(avoid, moveAvoid);

  const start: StoryDayFlowPoint =
    tone === "soft"
      ? {
          id: "start",
          phase: "Утро",
          cue: "Старт",
          valence: "caution",
          body: "Тяжёлый или медленный старт — без разгона: сначала тело, потом дела.",
        }
      : tone === "fast"
        ? {
            id: "start",
            phase: "Утро",
            cue: "Старт",
            valence: "favorable",
            body: "Быстрый старт: энергия уже есть — направь её в одно ясное дело.",
          }
        : {
            id: "start",
            phase: "Утро",
            cue: "Старт",
            valence: "favorable",
            body: "Лёгкий старт, без спешки — день ещё открыт.",
          };

  const tasks: StoryDayFlowPoint = {
    id: "tasks",
    phase: "День",
    cue: tone === "soft" ? "Осторожнее" : "Благоприятно",
    valence: tone === "soft" ? "caution" : "favorable",
    body: task
      ? `Задачи: ${task[0]!.toLowerCase()}${task.slice(1)}.`
      : tone === "soft"
        ? "Задачи покороче и по одному фронту — без гонки за объёмом."
        : "Задачи, где нужна ясность — удобнее в середине дня.",
  };

  const dialogues: StoryDayFlowPoint = softTalk
    ? {
        id: "dialogues",
        phase: "Диалоги",
        cue: "Осторожнее",
        valence: "caution",
        body: "Разговоры — короче и мягче; острые темы лучше не разгонять.",
      }
    : {
        id: "dialogues",
        phase: "Диалоги",
        cue: "Благоприятно",
        valence: "favorable",
        body: "Диалоги и гибкость — хорошее окно для живых разговоров.",
      };

  const evening: StoryDayFlowPoint = {
    id: "evening",
    phase: "Вечер",
    cue: "Итог",
    valence: "neutral",
    body: "Подведение итогов и благодарность — что сработало, что можно отпустить.",
  };

  const night: StoryDayFlowPoint = {
    id: "night",
    phase: "Ночь",
    cue: "Отдых",
    valence: "neutral",
    body: "Отпускание и отдых — день уже сделал своё.",
  };

  return [start, tasks, dialogues, evening, night];
}
