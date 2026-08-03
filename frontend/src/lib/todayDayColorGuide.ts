/**
 * Color of the day — FE visual layer only (name → hex).
 *
 * Meaning SoT = BE `day_color_catalog_v1` / `props.color` / `color_hook_reveal`
 * via `input.api.*_ru` / `input.scenario.*`. No FE prose dictionary.
 */

export type TodayDayColorIntensity = "мягко" | "ярко";

export type TodayDayColorGuide = {
  name: string;
  hex: string;
  benefit: string;
  clothing: string;
  accessory: string;
  amount: string;
  avoidColor: string;
  avoidWhy: string;
  /** v3.1 Move — visible intensity; drives how-to-apply emphasis */
  intensity: TodayDayColorIntensity;
  /** True when BE did not supply usable prose — UI must show honest absence, not invent. */
  unavailable: boolean;
};

/** Map catalog intensity / amount prose → soft|bright label for Move UI. */
export function resolveColorIntensityLabel(
  raw: string | null | undefined,
): TodayDayColorIntensity {
  const t = (raw || "").toLowerCase();
  if (/мягк|незамет|приглуш|лёгк|легк|фон|баз|почти/.test(t)) return "мягко";
  if (/ярк|насыщ|заметн|крича|акцент/.test(t)) return "ярко";
  return "мягко";
}

/** Canonical palette — matches BE COLOR_CATALOG_V1 (hex visual only). */
export const COLOR_HEX: Record<string, string> = {
  Лазурь: "#4A9FD8",
  "Глубокий синий": "#1F3A6B",
  Индиго: "#453B8C",
  Изумрудный: "#1F9D6E",
  Янтарный: "#C68A2E",
  Коралловый: "#F27A5E",
  Бордовый: "#6E1F35",
  Оливковый: "#71773A",
  // Layer A expansion
  Малахитовый: "#0B6E4F",
  "Пыльная роза": "#C9A7A0",
  Мускатный: "#8B5A2B",
  Аметистовый: "#6B3FA0",
  Кобальтовый: "#0047AB",
  "Слоновая кость": "#F3EDE0",
  // Layer B (Champagne via day_favorable)
  Шафрановый: "#E39B2E",
  Терракотовый: "#C65D3B",
  Гранатовый: "#7B1E3A",
  Хризолитовый: "#A8C256",
  "Дымчато-сиреневый": "#A89BB0",
  Шампань: "#F5E6C8",
};

export const COLOR_DAY_UNAVAILABLE_RU = "Цвет дня не определён.";

function asText(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

export function resolveTodayDayColorGuide(input: {
  name?: string | null;
  api?: {
    name?: string;
    story_ru?: string;
    benefit_ru?: string;
    clothing_ru?: string;
    accessory_ru?: string;
    amount_ru?: string;
    avoid_color_ru?: string;
    avoid_why_ru?: string;
  } | null;
  /** Scenario / day_story.talisman — meaning SoT when present (B4). */
  scenario?: {
    name?: string | null;
    benefit?: string | null;
    note?: string | null;
    avoidColor?: string | null;
    avoidWhy?: string | null;
    intensity?: string | null;
  } | null;
}): TodayDayColorGuide | null {
  const name = asText(input.scenario?.name) || asText(input.api?.name) || asText(input.name);
  if (!name) return null;

  const scenarioBenefit = [input.scenario?.benefit, input.scenario?.note]
    .map((s) => asText(s))
    .filter(Boolean)
    .join(" ");

  const benefit = scenarioBenefit || asText(input.api?.benefit_ru) || asText(input.api?.story_ru);
  const clothing = asText(input.api?.clothing_ru);
  const accessory = asText(input.api?.accessory_ru);
  const amount = asText(input.api?.amount_ru);
  const avoidColor = asText(input.scenario?.avoidColor) || asText(input.api?.avoid_color_ru);
  const avoidWhy = asText(input.scenario?.avoidWhy) || asText(input.api?.avoid_why_ru);
  const intensity = resolveColorIntensityLabel(
    asText(input.scenario?.intensity) || amount,
  );
  const hex = COLOR_HEX[name] ?? "";

  const hasProse = Boolean(benefit || clothing || accessory || amount || (avoidColor && avoidWhy));
  // Unknown name outside catalog with no BE prose → honest failure (no silent Лазурь default).
  if (!hasProse && !hex) {
    return {
      name,
      hex: "",
      benefit: "",
      clothing: "",
      accessory: "",
      amount: "",
      avoidColor: "",
      avoidWhy: "",
      intensity: "мягко",
      unavailable: true,
    };
  }

  return {
    name,
    hex,
    benefit,
    clothing,
    accessory,
    amount,
    avoidColor,
    avoidWhy,
    intensity,
    unavailable: !hasProse,
  };
}

export function colorGuideSkyStory(guide: TodayDayColorGuide): string {
  if (guide.unavailable || !guide.benefit.trim()) {
    return COLOR_DAY_UNAVAILABLE_RU;
  }
  return guide.benefit;
}
