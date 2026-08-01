/**
 * Color of the day — thin FE resolve (hex + fill gaps).
 *
 * @deprecated Meaning SoT = BE `day_color_catalog_v1` / `props.color` / `color_hook_reveal`
 * (Foundation v1 §3). Do not add new prose rows here; prefer API/scenario fields.
 * Local `COLOR_GUIDE` is a visual/hex fallback only until full cutover.
 */

export type TodayDayColorGuide = {
  name: string;
  hex: string;
  benefit: string;
  clothing: string;
  accessory: string;
  amount: string;
  avoidColor: string;
  avoidWhy: string;
};

type ColorGuideRow = TodayDayColorGuide;

/** Hex / visual fallback only for the 8 BE catalog colors. benefit mirrors BE symbolic_property. */
const COLOR_GUIDE: Record<string, ColorGuideRow> = {
  Лазурь: {
    name: "Лазурь",
    hex: "#4A9FD8",
    benefit: "ясность без тяжести — ровный фон для решения, не для дистанцирования",
    clothing: "Светлая рубашка, шарф или носки лазурного оттенка.",
    accessory: "Тонкий браслет или блокнот в мягком синем.",
    amount: "10–15% образа — один акцент",
    avoidColor: "Кислотно-оранжевый",
    avoidWhy: "Разгоняет темп и мешает спокойному фокусу лазури.",
  },
  "Глубокий синий": {
    name: "Глубокий синий",
    hex: "#1F3A6B",
    benefit: "дистанция, которая снижает реактивность, — сформулировать позицию раньше, чем ответить",
    clothing: "Тёмно-синий свитер, пиджак или джинсы глубокого синего.",
    accessory: "Сумка, ремень или перстень в спокойном синем.",
    amount: "один заметный элемент или два мелких",
    avoidColor: "Неоновый жёлтый",
    avoidWhy: "Резкий контраст перегружает день, который просит дистанции и ясности.",
  },
  Индиго: {
    name: "Индиго",
    hex: "#453B8C",
    benefit: "пауза внутрь, не наружу — услышать свою честную реакцию до того, как её озвучить",
    clothing: "Индиго в нижнем слое ближе к телу.",
    accessory: "Платок или обложка телефона.",
    amount: "мягкий акцент ближе к телу",
    avoidColor: "Красный «сигнал тревоги»",
    avoidWhy: "Толкает к реакции раньше внутренней честности.",
  },
  Изумрудный: {
    name: "Изумрудный",
    hex: "#1F9D6E",
    benefit: "мягкое восстановление через тело и связь, не через изоляцию",
    clothing: "Изумрудный шарф или кардиган.",
    accessory: "Маленький зелёный якорь.",
    amount: "один живой акцент",
    avoidColor: "Серый «офисный бетон»",
    avoidWhy: "Гасит живость восстановления давлением и жёстким контролем.",
  },
  Янтарный: {
    name: "Янтарный",
    hex: "#C68A2E",
    benefit: "тёплая поддержка энергии тела без разгона и без суеты",
    clothing: "Янтарный шарф или тёплый свитер.",
    accessory: "Украшение медового оттенка.",
    amount: "тёплый акцент у лица или на руках",
    avoidColor: "Холодный стальной",
    avoidWhy: "Режет тёплую линию дня жёсткостью и сверхконтролем.",
  },
  Коралловый: {
    name: "Коралловый",
    hex: "#F27A5E",
    benefit: "тёплый контакт без напора — говорить прямо, но не колко",
    clothing: "Коралловый топ под пиджак или шарф.",
    accessory: "Небольшая брошь или чехол.",
    amount: "небольшой тёплый штрих",
    avoidColor: "Чёрный «всё или ничего»",
    avoidWhy: "Делает разговор жёстче и категоричнее, чем нужно сегодня.",
  },
  Бордовый: {
    name: "Бордовый",
    hex: "#6E1F35",
    benefit: "серьёзная собранность — граница, которая не кричит, а просто есть",
    clothing: "Бордовый шарф или один слой outerwear.",
    accessory: "Кожаный аксессуар винного тона.",
    amount: "один насыщенный акцент",
    avoidColor: "Кислотно-розовый",
    avoidWhy: "Сбивает серьёзный тон дня в поверхностную суету.",
  },
  Перламутровый: {
    name: "Перламутровый",
    hex: "#E4DCEC",
    benefit: "Смягчает края дня — помогает не цепляться за мелочи.",
    clothing: "Перламутровая блуза, светлый жакет или платье с перламутровым отливом.",
    accessory: "Жемчуг, светлые серьги или перламутровый manicure.",
    amount: "Лёгкий блеск — буквально одна деталь. Перламутр не любит перегруза.",
    avoidColor: "Грубый хаки",
    avoidWhy: "Может сделать день визуально тяжелее, чем ты хочешь прожить его внутри.",
  },
  Оливковый: {
    name: "Оливковый",
    hex: "#71773A",
    benefit: "заземление в рабочем темпе — устойчивость без рывков и без демонстрации усилия",
    clothing: "Оливковый слой outerwear или брюки.",
    accessory: "Ремень или сумка спокойного оливкового.",
    amount: "один спокойный слой",
    avoidColor: "Неоновый жёлтый",
    avoidWhy: "Срывает ровный рабочий темп в суету и разгон.",
  },
  Сливовый: {
    name: "Сливовый",
    hex: "#6B3E63",
    benefit: "Усиливает концентрацию — один фокус вместо десяти.",
    clothing: "Сливовый шарф, носки или внутренний слой.",
    accessory: "Тёмная сумка, перчатки или обложка.",
    amount: "Один глубокий акцент. Сливовый — про качество внимания, не про площадь.",
    avoidColor: "Рассеянный мультиколор",
    avoidWhy: "Размывает фокус, который сливовый как раз помогает удержать.",
  },
  Песочный: {
    name: "Песочный",
    hex: "#C9A96E",
    benefit: "Даёт мягкую стабильность — день легче переносить без жёстких контрастов.",
    clothing: "Песочный свитер, бежевый trench или нейтральный слой.",
    accessory: "Сумка natural tone, шляпа или шарф.",
    amount: "Можно надеть базой — песочный сегодня может быть «фоном дня».",
    avoidColor: "Резкий чёрно-белый контраст",
    avoidWhy: "Может ощущаться как лишнее давление там, где нужна мягкость.",
  },
  Серебряный: {
    name: "Серебряный",
    hex: "#A9ADB4",
    benefit: "Охлаждает реакции и помогает смотреть на день спокойнее.",
    clothing: "Серебристая футболка, серый металлик в аксессуарах.",
    accessory: "Серебряные украшения, часы, браслет.",
    amount: "Мелкий блеск — серёжки или кольцо достаточно.",
    avoidColor: "Агрессивный красный",
    avoidWhy: "Разогревает там, где серебро сегодня помогает сохранить дистанцию.",
  },
};

const DEFAULT_COLOR: TodayDayColorGuide = {
  name: "Лазурь",
  hex: "#4A9FD8",
  benefit: "Поддерживает спокойный фокус и помогает не ускоряться раньше времени.",
  clothing: "Один предмет одежды спокойного оттенка — рубашка, шарф или носки.",
  accessory: "Небольшой аксессуар того же тона — браслет, чехол, блокнот.",
  amount: "Достаточно одного акцента. Цвет дня — якорь, не костюм.",
  avoidColor: "Слишком кричащий неон",
  avoidWhy: "Перегружает день и мешает удержать выбранный ритм.",
};

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
  } | null;
}): TodayDayColorGuide | null {
  const asText = (value: unknown): string =>
    typeof value === "string" ? value.trim() : "";

  const name = asText(input.scenario?.name) || asText(input.api?.name) || asText(input.name);
  if (!name) return null;

  const preset = COLOR_GUIDE[name] ?? { ...DEFAULT_COLOR, name };
  const scenarioBenefit = [input.scenario?.benefit, input.scenario?.note]
    .map((s) => asText(s))
    .filter(Boolean)
    .join(" ");

  return {
    name,
    hex: preset.hex,
    benefit: scenarioBenefit || asText(input.api?.benefit_ru) || preset.benefit,
    clothing: asText(input.api?.clothing_ru) || preset.clothing,
    accessory: asText(input.api?.accessory_ru) || preset.accessory,
    amount: asText(input.api?.amount_ru) || preset.amount,
    avoidColor:
      asText(input.scenario?.avoidColor) ||
      asText(input.api?.avoid_color_ru) ||
      preset.avoidColor,
    avoidWhy:
      asText(input.scenario?.avoidWhy) ||
      asText(input.api?.avoid_why_ru) ||
      preset.avoidWhy,
  };
}

export function colorGuideSkyStory(guide: TodayDayColorGuide): string {
  return guide.benefit;
}
