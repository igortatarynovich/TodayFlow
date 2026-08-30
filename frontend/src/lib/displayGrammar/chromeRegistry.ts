/**
 * Registered chrome literals / copy keys. Presence in a copy file is not enough.
 * Canon: Inventory chrome rows + TF.no_connection / TF.unavailable.
 */

export const REGISTERED_CHROME: Record<string, string> = {
  "Нет соединения.": "TF.no_connection",
  "Не удалось загрузить.": "TF.unavailable",
  Сегодня: "T1-date.eyebrow",
  "Энергия дня": "T1-hero.eyebrow",
  "Сегодня поддерживает": "T1-strength.label",
  Риски: "T1-risk.label",
  "Мой фокус": "T3.focus_label",
  "В приоритете": "T3.priority_label",
  Осторожнее: "T3.caution_label",
  "Мой ритм дня": "T3.rhythm_label",
  "Ритм дня": "T3.rhythm_label",
  "За что ты благодарен сегодняшнему дню?": "T4.title",
  "Твоя суть": "P1.signal",
  Узнавание: "P2.step_title",
  "Почему именно так": "P2.step_title",
  Опоры: "P3.grounded_label",
  "Что важно понять": "P3.step_title",
  Узел: "P3.step_title",
  "Куда усилия": "P4.step_title",
  Вектор: "P4.step_title",
  "Мост в день": "P5.step_title",
  "В день": "P5.step_title",
  "Открыть Today": "P5.cta",
  "Выбрало имя": "P2.selected_section",
  "Расширяет портрет": "P2.influenced_section",
  "Что помогает": "P3.help_label",
  "Как это уже проявлялось": "P3.living_label",
  "Контекст из отметок — не доказательство этого узла.": "P3.living_note",
  "Одно направление — не ещё одно описание «кто ты».": "P4.lead",
  "Где это проявится сильнее": "P4.sphere.title",
  "Нажми — подробнее": "P2.expand_hint",
  "Как проявляется": "P4.sphere.expand",
  Нужно: "P4.sphere.expand",
  Риск: "P4.sphere.expand",
};

export const NON_UI_FILTER_LITERALS = new Set([
  "механизм проявляется",
  "identity-линии",
]);

export function chromeSlotForLiteral(text: string): string | undefined {
  return REGISTERED_CHROME[text.trim()];
}
