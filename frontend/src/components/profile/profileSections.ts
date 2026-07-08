export const PROFILE_SECTION_IDS = ["overview", "chart", "spheres", "patterns", "pulse", "circle", "accuracy"] as const;

export type ProfileSectionId = (typeof PROFILE_SECTION_IDS)[number];

const LEGACY_SECTION_MAP: Record<string, ProfileSectionId> = {
  /** Раньше планеты были отдельной вкладкой — теперь часть «Карта рождения». */
  synthesis: "chart",
  weave: "patterns",
  life: "spheres",
  rhythm: "pulse",
  achievements: "accuracy",
};

export const PROFILE_SECTION_META: Record<ProfileSectionId, { label: string; description: string }> = {
  overview: {
    label: "Портрет",
    description: "Короткая сборка: кто ты, опоры, риски и правила подсказок",
  },
  chart: {
    label: "Карта рождения",
    description: "Опоры, колесо, дома, планеты и аспекты",
  },
  spheres: {
    label: "Сферы жизни",
    description: "Любовь, работа, деньги, тело, сексуальность и остальное — как это у тебя устроено",
  },
  patterns: {
    label: "Паттерны",
    description: "Синтез: решения, стресс, отношения, деньги, восстановление",
  },
  pulse: {
    label: "Живой слой",
    description: "Что система видит по ответам и действиям",
  },
  circle: {
    label: "Круг людей",
    description: "Люди для совместимости и разборов",
  },
  accuracy: {
    label: "Точность",
    description: "Насколько полон профиль и что его улучшит",
  },
};

export function parseProfileSection(raw: string | null | undefined): ProfileSectionId {
  if (!raw) return "overview";
  if (PROFILE_SECTION_IDS.includes(raw as ProfileSectionId)) {
    return raw as ProfileSectionId;
  }
  const mapped = LEGACY_SECTION_MAP[raw];
  if (mapped) return mapped;
  return "overview";
}
