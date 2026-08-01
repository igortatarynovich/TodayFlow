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

const COLOR_GUIDE: Record<string, ColorGuideRow> = {
  Лазурь: {
    name: "Лазурь",
    hex: "#4A9FD8",
    benefit: "Успокаивает ум и помогает держать ясность, когда день требует решений.",
    clothing: "Светлая рубашка, шарф или носки лазурного оттенка.",
    accessory: "Тонкий браслет, часы с голубым циферблатом или блокнот в мягком синем.",
    amount: "Достаточно одного акцента — 10–15% образа. Не нужно «весь образ в синем».",
    avoidColor: "Кислотно-оранжевый",
    avoidWhy: "Сегодня он разгоняет темп и мешает тому спокойному фокусу, который даёт лазурь.",
  },
  "Глубокий синий": {
    name: "Глубокий синий",
    hex: "#1F3A6B",
    benefit: "Даёт опору и глубину — легче не сорваться на суету.",
    clothing: "Тёмно-синий свитер, пиджак или джинсы глубокого синего.",
    accessory: "Сумка, ремень или перстень в спокойном синем.",
    amount: "Один заметный элемент или два мелких. Глубокий синий любит точность, не объём.",
    avoidColor: "Неоновый жёлтый",
    avoidWhy: "Резкий контраст перегружает день, который просит собранности.",
  },
  Индиго: {
    name: "Индиго",
    hex: "#453B8C",
    benefit: "Усиливает интуицию и внутреннюю честность — про «услышать себя до действия».",
    clothing: "Индиго в нижнем слое: футболка, колготки, носки.",
    accessory: "Платок, шарф или обложка телефона.",
    amount: "Мягкий акцент ближе к телу — его достаточно почувствовать, не демонстрировать.",
    avoidColor: "Красный «сигнал тревоги»",
    avoidWhy: "Сегодня он толкает к реакции раньше, чем ты успеешь понять, что действительно важно.",
  },
    Изумрудный: {
    name: "Изумрудный",
    hex: "#1F9D6E",
    benefit: "Поддерживает восстановление и мягкий рост — телу и отношениям.",
    clothing: "Изумрудный шарф, кардиган или одна деталь у лица.",
    accessory: "Серьги, брошь или чашка — маленький якорь зелени.",
    amount: "Один живой акцент. Зелёного много не нужно — он работает как «дыхание».",
    avoidColor: "Серый «офисный бетон»",
    avoidWhy: "Гасит ту живость, которую изумруд сегодня может дать.",
  },
  Янтарный: {
    name: "Янтарный",
    hex: "#C68A2E",
    benefit: "Согревает и возвращает энергию без суеты — хорош для дней, где нужен тёплый тон.",
    clothing: "Янтарный шарф, бежево-медный свитер или тёплые аксессуары.",
    accessory: "Украшение с янтарным или медовым оттенком.",
    amount: "Тёплый акцент у лица или на руках — достаточно одного.",
    avoidColor: "Холодный стальной",
    avoidWhy: "Режет тёплую линию дня и может ощущаться как лишняя строгость.",
  },
  Коралловый: {
    name: "Коралловый",
    hex: "#F27A5E",
    benefit: "Смягчает общение — легче говорить без давления и упрёка.",
    clothing: "Коралловый топ под пиджак, шарф или помада мягкого коралла.",
    accessory: "Небольшая брошь, nail-accent или телефонный чехол.",
    amount: "Небольшой тёплый штрих — коралл работает как приглашение, не как крик.",
    avoidColor: "Чёрный «всё или ничего»",
    avoidWhy: "Может сделать разговоры тяжелее, чем нужно сегодня.",
  },
  Бордовый: {
    name: "Бордовый",
    hex: "#6E1F35",
    benefit: "Даёт собранность и глубину — помогает не распыляться.",
    clothing: "Бордовый шарф, ремень или один слой outerwear.",
    accessory: "Кожаный аксессуар бордового или винного тона.",
    amount: "Один насыщенный акцент. Бордо не терпит конкуренции с другими яркими цветами.",
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
    benefit: "Заземляет и помогает идти ровно — без рывков и самокритики.",
    clothing: "Оливковый кардиган, брюки или кроссовки.",
    accessory: "Рюкзак, ремень или часы в оливковом/хаки.",
    amount: "Спокойный базовый оттенок — можно чуть больше, чем яркий акцент.",
    avoidColor: "Ярко-фиолетовый",
    avoidWhy: "Уводит от простой опоры, которая сегодня работает лучше.",
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
