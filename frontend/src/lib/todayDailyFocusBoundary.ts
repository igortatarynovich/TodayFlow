/**
 * PR1 S5 — отсекаем guidance / action / goal-подобный текст из Daily Focus.
 * Daily Focus = описание дня («о чём»), не инструкция («как прожить»).
 */

/** Подстроки (lowercase) — надёжнее word-boundary для кириллицы в JS. */
const GUIDANCE_NEEDLES = [
  "если хочешь",
  "если хочешь продвинуть",
  "если выбрать",
  "до обеда",
  "до вечера",
  "стоит ",
  "стоит сосредоточиться",
  "лучше ",
  "обратить внимание",
  "сосредоточься",
  "сделай ",
  "обсуди ",
  "закрой ",
  "проверь ",
  "не бери ",
  "не хвататься",
  "не тороп",
  "выбери ",
  "выбрать ",
  "держи ",
  "главный шаг",
  "лучший ход",
  "первый шаг",
  "риск:",
  "лучший ход:",
] as const;

export function isDailyFocusGuidanceLeak(text: string): boolean {
  const low = text.replace(/\s+/g, " ").trim().toLowerCase();
  if (!low) return false;
  return GUIDANCE_NEEDLES.some((n) => low.includes(n));
}

export function filterDailyFocusLines(lines: string[]): string[] {
  return lines
    .flatMap((line) =>
      line
        .split(/(?<=[.!?])\s+/)
        .map((s) => s.trim())
        .filter(Boolean),
    )
    .filter((l) => l && !isDailyFocusGuidanceLeak(l));
}
