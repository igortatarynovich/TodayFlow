import { dayPhaseFromHour } from "@/lib/dayPhaseAtmosphere";

export type TodayDayPhase = "morning" | "day" | "evening" | "night";

export type TodayDayGreeting = {
  salutation: string;
  line: string;
};

/** Warm openers — never day theme / thesis / plot. Stable per date+phase, varies across days. */
const WARM_LINES: Record<TodayDayPhase, readonly string[]> = {
  morning: [
    "Мягкое начало — день ещё открыт, без спешки.",
    "Хорошее утро начинается с одного спокойного вдоха.",
    "Сегодня можно войти в день тихо и по-своему.",
    "Пусть утро будет бережным — темп подстроится.",
    "День только начинается: достаточно одного ясного шага.",
    "Сначала тепло к себе — потом дела.",
  ],
  day: [
    "Середина дня — хороший момент свериться с собой.",
    "День уже идёт. Можно чуть замедлиться и выбрать, что важно.",
    "Сейчас важнее ясность, чем скорость.",
    "Держись своего ритма — день ещё многое покажет.",
    "Есть пространство сделать один спокойный ход.",
    "Пусть день держит тебя, а не наоборот.",
  ],
  evening: [
    "Вечер — время собрать день без оценки.",
    "Можно мягко закрыть день и оставить лишнее.",
    "День почти прожит. Сейчас важнее тепло, чем итог.",
    "Пусть вечер будет тихим — день уже сделал своё.",
    "Хороший вечер начинается с короткой паузы.",
    "Сейчас можно отпустить темп и просто быть.",
  ],
  night: [
    "Ночь для отдыха. Завтра можно начать заново.",
    "Пора беречь силы — день уже позади.",
    "Тишина ночи — хорошее место, чтобы отпустить день.",
    "Пусть ночь будет спокойной: всё важное подождёт утра.",
  ],
};

const FIRST_TODAY_LINES = [
  "Мы только что сверили первые линии карты — теперь посмотрим, как звучит твой день.",
  "Карта уже рядом. Дальше — мягко, без спешки, шаг за шагом.",
  "Первый день вместе: начнём спокойно и посмотрим, что откликается.",
] as const;

/** Single clock → phase SoT (aligned with `dayPhaseAtmosphere`). */
export function resolveTodayDayPhase(hour = new Date().getHours()): TodayDayPhase {
  return dayPhaseFromHour(hour);
}

function formatName(name: string | null | undefined): string | null {
  const trimmed = name?.trim();
  if (!trimmed) return null;
  return trimmed.split(/\s+/)[0] ?? trimmed;
}

function salutationForPhase(phase: TodayDayPhase, name: string | null): string {
  const who = name ? `, ${name}` : "";
  switch (phase) {
    case "morning":
      return `Доброе утро${who}`;
    case "day":
      return `Добрый день${who}`;
    case "evening":
      return `Добрый вечер${who}`;
    case "night":
      return `Доброй ночи${who}`;
  }
}

function hashSeed(key: string): number {
  let h = 0;
  for (let i = 0; i < key.length; i++) {
    h = (Math.imul(31, h) + key.charCodeAt(i)) | 0;
  }
  return Math.abs(h);
}

export function pickWarmGreetingLine(
  phase: TodayDayPhase,
  seedKey: string,
  pool: readonly string[] = WARM_LINES[phase],
): string {
  if (pool.length === 0) return "Сегодня — твой день.";
  return pool[hashSeed(seedKey) % pool.length]!;
}

/**
 * Greeting = salutation by clock phase + warm rotating line.
 * Does **not** use day theme / thesis / tagline (those live in Опора).
 */
export function buildTodayDayGreeting(input: {
  phase: TodayDayPhase;
  userName?: string | null;
  /** Calendar day for stable rotation within the phase. */
  dateISO?: string | null;
  yesterdayClosed?: boolean;
  todayOpened?: boolean;
  isEveningSurface?: boolean;
  isFirstToday?: boolean;
  /** @deprecated Ignored — theme/thesis must not become the greeting. */
  tagline?: string;
}): TodayDayGreeting {
  const name = formatName(input.userName);
  const salutation = salutationForPhase(input.phase, name);
  const seedBase = `${input.dateISO || "day"}|${input.phase}`;

  if (input.isFirstToday && !input.todayOpened) {
    return {
      salutation,
      line: pickWarmGreetingLine(input.phase, `${seedBase}|first`, FIRST_TODAY_LINES),
    };
  }

  if (input.isEveningSurface || input.phase === "evening" || input.phase === "night") {
    const eveningPhase: TodayDayPhase = input.phase === "night" ? "night" : "evening";
    return {
      salutation,
      line: pickWarmGreetingLine(eveningPhase, `${seedBase}|close`),
    };
  }

  if (input.phase === "morning" && input.yesterdayClosed && !input.todayOpened) {
    return {
      salutation,
      line: pickWarmGreetingLine("morning", `${seedBase}|after-close`, [
        "Вчерашний день закрыт — сегодня можно начать с ясного и тёплого темпа.",
        "Вчера уже собрано. Сегодня — новое мягкое начало.",
        "Закрытое вчера даёт спокойный вход в сегодня.",
      ]),
    };
  }

  return {
    salutation,
    line: pickWarmGreetingLine(input.phase, seedBase),
  };
}
