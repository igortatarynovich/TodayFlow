/** RU labels for CUM `active_themes[].id` — evolution path themes + head topics. */
const CUM_THEME_LABELS_RU: Record<string, string> = {
  discipline: "дисциплина",
  clarity: "ясность",
  energy: "энергия",
  relationships: "отношения",
  body: "тело",
  purpose: "смысл и направление",
  wealth: "деньги и ресурс",
  creativity: "творчество",
  healing: "восстановление",
  spirituality: "внутренняя жизнь",
  work_focus: "фокус на работе",
  work: "работа",
  love: "близость",
  money: "деньги",
  family: "семья",
  calm: "спокойствие",
  focus: "фокус",
};

export function formatCumThemeLabel(themeId: string): string {
  const id = themeId.trim().toLowerCase();
  if (!id) return "";
  const mapped = CUM_THEME_LABELS_RU[id];
  if (mapped) return mapped;
  return id.replace(/_/g, " ");
}
