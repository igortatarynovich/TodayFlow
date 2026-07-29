export type TarotShellStep = -1 | 0 | 1 | 2 | 3;

export const TAROT_SHELL_STEPPER = [
  { id: 1, title: "Вопрос", hint: "Сформулировать без спешки" },
  { id: 2, title: "Карты", hint: "Выбрать формат и открыть смысл" },
  { id: 3, title: "История", hint: "Narrative + friction tags" },
  { id: 4, title: "Мост", hint: "Сохранить действие в Today" },
] as const;

export function tarotShellStepFromPath(pathname: string): TarotShellStep {
  if (pathname.startsWith("/tarot/result")) return 3;
  if (pathname.startsWith("/tarot/spread")) return 1;
  if (pathname.startsWith("/tarot/question")) return 0;
  return -1;
}

export const TAROT_HUB_SPREADS = [
  {
    spreadId: "three_cards",
    count: 3,
    title: "Три карты",
    description: "Покажет, что привело к ситуации, что происходит сейчас и какой шаг уместен дальше.",
  },
  {
    spreadId: "guidance_choice_two",
    count: 5,
    title: "Выбор из двух путей",
    description: "Сравнит два варианта: что даёт каждый, где риск и какой следующий шаг спокойнее.",
  },
  {
    spreadId: "one_card",
    count: 1,
    title: "Одна карта",
    description: "Один ясный фокус на день — для намерения, короткой практики или вечернего итога.",
  },
] as const;
