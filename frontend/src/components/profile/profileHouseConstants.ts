/** Тексты и маршруты по домам для экрана профиля / натала. */

export type ProfileHouseRow = {
  house: number;
  cusp_longitude?: number;
  sign?: string;
  degree?: number;
};

const ZODIAC_EN = [
  "Aries",
  "Taurus",
  "Gemini",
  "Cancer",
  "Leo",
  "Virgo",
  "Libra",
  "Scorpio",
  "Sagittarius",
  "Capricorn",
  "Aquarius",
  "Pisces",
] as const;

function signDegreeFromLongitude(lon: number): { sign: string; degree: number } {
  const x = ((lon % 360) + 360) % 360;
  const idx = Math.min(11, Math.floor(x / 30));
  return { sign: ZODIAC_EN[idx], degree: x % 30 };
}

const ZODIAC_RU_TO_EN: Record<string, (typeof ZODIAC_EN)[number]> = {
  Овен: "Aries",
  Телец: "Taurus",
  Близнецы: "Gemini",
  Рак: "Cancer",
  Лев: "Leo",
  Дева: "Virgo",
  Весы: "Libra",
  Скорпион: "Scorpio",
  Стрелец: "Sagittarius",
  Козерог: "Capricorn",
  Водолей: "Aquarius",
  Рыбы: "Pisces",
};

/** Долгота ASC 0..360: только longitude или знак+градус в знаке (не путать degree с полной долготой). */
function ascendantBaseLongitude(
  asc: { longitude?: number; sign?: string; degree?: number } | null | undefined,
): number | null {
  if (!asc) return null;
  if (asc.longitude != null && !Number.isNaN(Number(asc.longitude))) {
    return ((Number(asc.longitude) % 360) + 360) % 360;
  }
  const signRaw = asc.sign?.trim();
  const degInSign = asc.degree;
  if (signRaw == null || degInSign == null || Number.isNaN(Number(degInSign))) return null;
  let en = ZODIAC_EN.includes(signRaw as (typeof ZODIAC_EN)[number])
    ? (signRaw as (typeof ZODIAC_EN)[number])
    : ZODIAC_RU_TO_EN[signRaw];
  if (!en) return null;
  const idx = ZODIAC_EN.indexOf(en);
  if (idx < 0) return null;
  return (idx * 30 + (Number(degInSign) % 30)) % 360;
}

function hasAnyPositions(preview: { positions?: Record<string, unknown> | null } | null): boolean {
  const p = preview?.positions;
  return Boolean(p && typeof p === "object" && Object.keys(p).length > 0);
}

/**
 * Если бэкенд не прислал cusp-лист домов, строим равные дома от ASC (longitude или знак+градус).
 * Если ASC нет, но есть позиции планет — показываем 12 карточек с текстами HOUSE_* (без куспидов).
 */
export function ensureTwelveProfileHouses(
  preview: {
    houses?: ProfileHouseRow[] | null;
    ascendant?: { longitude?: number; sign?: string; degree?: number } | null;
    positions?: Record<string, unknown> | null;
  } | null,
): ProfileHouseRow[] {
  const existing = preview?.houses;
  if (existing && existing.length > 0) return existing;

  const base = ascendantBaseLongitude(preview?.ascendant ?? null);
  if (base != null) {
    const out: ProfileHouseRow[] = [];
    for (let i = 1; i <= 12; i++) {
      const cusp = (base + (i - 1) * 30) % 360;
      const { sign, degree } = signDegreeFromLongitude(cusp);
      out.push({ house: i, cusp_longitude: cusp, sign, degree });
    }
    return out;
  }

  if (hasAnyPositions(preview)) {
    return Array.from({ length: 12 }, (_, i) => ({ house: i + 1 }));
  }

  return existing ?? [];
}

export const HOUSE_FALLBACK: Record<number, string> = {
  1: "Личность, самопрезентация, первый импульс действия.",
  2: "Ресурсы, деньги, ценности и чувство опоры.",
  3: "Общение, обучение, ближайшее окружение.",
  4: "Дом, семья, корни, внутреннее основание.",
  5: "Творчество, радость, самовыражение, романтика.",
  6: "Режим, работа, здоровье, дисциплина.",
  7: "Партнерство, договоренности, баланс с другими.",
  8: "Трансформация, глубина, доверие, общие ресурсы.",
  9: "Смыслы, мировоззрение, путешествия, расширение.",
  10: "Карьера, статус, социальная реализация.",
  11: "Сообщество, друзья, долгие цели и идеи.",
  12: "Подсознание, восстановление, духовная работа.",
};

export const HOUSE_LAYER: Record<number, { title: string; prompt: string }> = {
  1: { title: "Как ты заходишь в мир", prompt: "это видно в первом впечатлении и поведении по умолчанию" },
  2: { title: "Что для тебя ценно", prompt: "это проявляется в теме денег, ценности и внутренней опоры" },
  3: { title: "Как ты думаешь и общаешься", prompt: "это проявляется в речи, обучении и восприятии информации" },
  4: { title: "Где ты настоящий", prompt: "это сильнее всего проживается в доме, семье и внутреннем состоянии" },
  5: { title: "Где ты живешь ради себя", prompt: "это проявляется в удовольствии, любви и самовыражении" },
  6: { title: "Как ты живешь каждый день", prompt: "это проявляется в рутине, работе и состоянии тела" },
  7: { title: "Как ты строишь связь", prompt: "это проявляется в партнерстве и в теме другого человека" },
  8: { title: "Где ты меняешься", prompt: "это проявляется в кризисах, глубине и потере контроля" },
  9: { title: "Как ты ищешь смысл", prompt: "это проявляется в вере, расширении и поиске зачем" },
  10: { title: "Как ты хочешь выглядеть в мире", prompt: "это проявляется в карьере, статусе и реализации" },
  11: { title: "С кем ты идешь в будущее", prompt: "это проявляется в окружении, друзьях и общей линии будущего" },
  12: { title: "Где ты теряешь или находишь себя", prompt: "это проявляется в подсознании, уходе и скрытых страхах" },
};

export const HOUSE_CONTEXT_LABELS: Record<number, string> = {
  1: "в том, как ты входишь в мир",
  2: "в деньгах, ценности и внутренней опоре",
  3: "в общении, мышлении и ежедневном обмене",
  4: "в доме, семье и внутреннем состоянии",
  5: "в любви, удовольствии и самовыражении",
  6: "в работе, рутине и состоянии тела",
  7: "в отношениях и теме другого человека",
  8: "в кризисах, глубине и потере контроля",
  9: "в смыслах, вере и расширении горизонта",
  10: "в карьере, статусе и реализации",
  11: "в окружении, друзьях и линии будущего",
  12: "в скрытых процессах, подсознании и том, что трудно сразу назвать",
};

export const HOUSE_ACTION_GUIDE: Record<number, { strengthen: string; avoid: string; routeLabel: string; href: string }> = {
  1: {
    strengthen: "Опирайся на свой естественный способ входить в ситуацию, а не на попытку подстроиться под чужой тон еще до первого шага.",
    avoid: "Не теряйся в самопрезентации и не пытайся понравиться раньше, чем сам понимаешь, чего хочешь.",
    routeLabel: "Перейти в Today",
    href: "/today",
  },
  2: {
    strengthen: "Укрепляй все, что возвращает чувство ценности, ресурса и материальной опоры: понятные границы, темп и способ обращаться с деньгами.",
    avoid: "Не принимай тревогу за сигнал срочно усиливать контроль, покупки или работу без ясного смысла.",
    routeLabel: "Открыть денежный слой",
    href: "/tarot?topic=money",
  },
  3: {
    strengthen: "Собирай мысли в ясный короткий обмен: разговор, заметку, вопрос или один точный запрос вместо внутреннего шума.",
    avoid: "Не распыляйся на лишние сообщения и не превращай любой контакт в попытку объяснить всё сразу.",
    routeLabel: "Разобрать вопрос",
    href: "/tarot",
  },
  4: {
    strengthen: "Усиливай бытовую ясность, спокойный ритм дома и контакт с теми, рядом с кем тебе не нужно быть в постоянной защите.",
    avoid: "Не оставляй семейное напряжение в подвешенном состоянии, если уже ясно, что оно вытягивает ресурс.",
    routeLabel: "Открыть круг людей",
    href: "/account/profiles",
  },
  5: {
    strengthen: "Оставляй место для живого желания, игры, романтики и той формы самовыражения, где ты не работаешь на оценку.",
    avoid: "Не превращай удовольствие в выступление на публику и не подменяй близость драмой ради ощущения жизни.",
    routeLabel: "Перейти в отношения",
    href: "/compatibility?relation_mode=romantic",
  },
  6: {
    strengthen: "Укрепляй режим, повторяемость, простые телесные опоры и одну понятную рабочую линию на день.",
    avoid: "Не геройствуй на усталости и не считай перегруз доказательством своей нужности.",
    routeLabel: "Собрать день",
    href: "/today",
  },
  7: {
    strengthen: "Усиливай договоренности, ясность ожиданий и формат связи, где есть второй человек, а не только твоя интерпретация его поведения.",
    avoid: "Не живи в гадании о партнере и не пытайся решить напряжение только внутренним анализом.",
    routeLabel: "Открыть совместимость",
    href: "/compatibility?relation_mode=romantic",
  },
  8: {
    strengthen: "Опирайся на честность, глубину и способность назвать, где реально включается страх потери контроля или доверия.",
    avoid: "Не заходи в крайности, скрытые проверки и силовые сценарии, если вопрос пока можно выдержать в ясном разговоре.",
    routeLabel: "Разобрать сложный вопрос",
    href: "/tarot",
  },
  9: {
    strengthen: "Усиливай длинный смысл: обучение, расширение взгляда, разговор с тем, что больше текущей рутины.",
    avoid: "Не убегай в абстракции и большие идеи только чтобы не решать текущий конкретный шаг.",
    routeLabel: "Открыть прогнозы",
    href: "/forecasts",
  },
  10: {
    strengthen: "Укрепляй роль, в которой ты становишься видимым, собранным и социально считываемым без лишнего внутреннего раскола.",
    avoid: "Не строй реализацию только на внешнем одобрении и не считай карьерный темп единственным критерием ценности.",
    routeLabel: "Перейти в карьерный слой",
    href: "/tarot?topic=money",
  },
  11: {
    strengthen: "Поддерживай связи, идеи и сообщества, в которых есть линия будущего, а не только привычное присутствие.",
    avoid: "Не растворяй личный вектор в коллективных ожиданиях и не оставайся в контактах только из чувства долга.",
    routeLabel: "Открыть круг людей",
    href: "/account/profiles",
  },
  12: {
    strengthen: "Усиливай тишину, восстановление и те практики, где можно увидеть скрытую причину напряжения до того, как она выйдет в перегруз.",
    avoid: "Не путай отдых с исчезновением и не откладывай всё в молчание, если внутри уже накопилось слишком много.",
    routeLabel: "Вернуться в Today",
    href: "/today?slot=evening",
  },
};
