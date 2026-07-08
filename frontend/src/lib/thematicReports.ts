export type ThematicThemeKey = "career" | "love" | "family" | "children";

export type ThematicReportMeta = {
  id: ThematicThemeKey;
  title: string;
  description: string;
  icon: string;
  color: string;
  sections: string[];
  ctaLabel: string;
};

export const THEMATIC_REPORTS: ThematicReportMeta[] = [
  {
    id: "career",
    title: "Разбор: Карьера",
    description: "Глубокий анализ ваших паттернов в работе, ответственности, деньгах и профессиональном развитии.",
    icon: "💼",
    color: "#4A90E2",
    sections: ["Career & Responsibility", "Money & Security"],
    ctaLabel: "Открыть карьерный разбор",
  },
  {
    id: "love",
    title: "Разбор: Отношения",
    description: "Фокус на близости, привязанности, эмоциональной динамике и том, как вы входите в романтический контакт.",
    icon: "💕",
    color: "#EC4899",
    sections: ["Relationships", "Emotional Patterns"],
    ctaLabel: "Открыть разбор отношений",
  },
  {
    id: "family",
    title: "Разбор: Семья",
    description: "Семейные сценарии, границы, паттерны конфликта и способы выстраивать устойчивый контакт с близкими.",
    icon: "👨‍👩‍👧‍👦",
    color: "#8B5CF6",
    sections: ["Relationships", "Emotional Patterns"],
    ctaLabel: "Открыть семейный разбор",
  },
  {
    id: "children",
    title: "Разбор: Дети",
    description: "Подход к воспитанию, эмоциональной регуляции и связи с ребёнком через вашу собственную внутреннюю модель.",
    icon: "👶",
    color: "#10B981",
    sections: ["Relationships", "Emotional Patterns"],
    ctaLabel: "Открыть разбор о детях",
  },
];

export const THEMATIC_REPORTS_BY_ID: Record<ThematicThemeKey, ThematicReportMeta> = Object.fromEntries(
  THEMATIC_REPORTS.map((report) => [report.id, report]),
) as Record<ThematicThemeKey, ThematicReportMeta>;

export function getThematicReportMeta(theme: string): ThematicReportMeta | null {
  if (theme in THEMATIC_REPORTS_BY_ID) {
    return THEMATIC_REPORTS_BY_ID[theme as ThematicThemeKey];
  }
  return null;
}
