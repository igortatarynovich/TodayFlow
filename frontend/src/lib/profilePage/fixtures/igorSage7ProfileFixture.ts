import type { CoreProfile } from "@/lib/types";

/** Etalon profile for taxonomy audit — Igor · Sage · Aquarius · LP 7 */
export const IGOR_SAGE_7_FIXTURE: CoreProfile = {
  profile_version: "fixture-1",
  generated_at: "2026-06-01T00:00:00.000Z",
  is_ready: true,
  missing_fields: [],
  profile_hash: "igor-sage-7-fixture",
  person: {
    first_name: "Igor",
    display_name: "Igor",
  },
  astro: {
    birth_date: "1990-01-28",
    sun_sign: "Aquarius",
    sun_element: "Air",
    location_name: "Moscow",
  },
  numerology: {
    full_name: "Igor",
    birth_date: "1990-01-28",
    life_path: 7,
    personality: 7,
    expression: 7,
    soul_urge: 7,
  },
  baseline: {
    archetype_seed: "Sage",
    rhythm_style: "Тебе нужны паузы для осмысления перед действием.",
  },
  interpretation: {
    identity:
      "Игорь — человек, который постоянно ищет смысл и глубину во всём, что его окружает.",
    strengths: ["Глубина", "анализирует неочевидные связи", "видит систему за фактами"],
    watchouts: ["закрытость", "уход в одиночество"],
    life_areas: {
      love: "Игорь ищет глубину и понимание, а не поверхностный контакт.",
      money: "Может быть осторожным и расчётливым, когда дело касается риска.",
      career: "Сильнее всего проявляется там, где нужен анализ и экспертиза.",
      decisions: "Тебе проще начинать, когда есть структура, первый шаг и пространство подумать.",
      body: "Восстановление через тишину и прогулку без разговоров.",
    },
  },
};

export const IGOR_SAGE_7_LABEL = "Igor / Sage / 7 / Aquarius";
