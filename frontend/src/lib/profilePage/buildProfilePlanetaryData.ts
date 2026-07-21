import type { AspectCallout } from "@/lib/types";
import type { CombinedPlanetaryProfile, LifeMapSection, NatalChartPreview } from "@/components/profile/profilePanelTypes";
import type { LifePathEntry, NameNumberEntry, PlanetInSignEntry, ProfileScenarioEntry } from "@/lib/zodiacKnowledge";
import { getProfileScenarioEntry, getZodiacEntry, resolveZodiacSignId } from "@/lib/zodiacKnowledge";
import { lookupNatalBodyPosition } from "@/lib/natalChartPositions";
import {
  HOUSE_CONTEXT_LABELS,
  HOUSE_FALLBACK,
  HOUSE_LAYER,
  ensureTwelveProfileHouses,
} from "@/components/profile/profileHouseConstants";
import { natalBodyLabelRu } from "@/lib/profileAstroLabelsRu";
import { PROFILE_CHART_DEEP_PATH } from "@/lib/profileRoutes";

const ASPECT_INTERPRETATIONS: Record<string, { title: string; category: "fusion" | "tension" | "polarity" | "strength" | "potential"; text: string }> = {
  "sun_moon_conjunction": {
    title: "Солнце соединение Луна",
    category: "fusion",
    text: "Ты не делишь то, что думаешь, и то, что чувствуешь. Внутри больше цельности, чем у многих, но иногда из-за этого сложнее выйти из собственной субъективности.",
  },
  "sun_mercury_conjunction": {
    title: "Солнце соединение Меркурий",
    category: "fusion",
    text: "Твоя личность сильно слита с мышлением. Ты говоришь то, что думаешь, и идеи у тебя почти не отделяются от ощущения себя.",
  },
  "sun_venus_conjunction": {
    title: "Солнце соединение Венера",
    category: "fusion",
    text: "В тебе естественно соединяются личность, симпатия и притяжение. Тебе важно нравиться и быть в красивом, живом контакте с миром.",
  },
  "sun_mars_conjunction": {
    title: "Солнце соединение Марс",
    category: "fusion",
    text: "Энергия и действие встроены прямо в твой способ быть. Ты не любишь долгого ожидания и чаще всего идешь в шаг сразу.",
  },
  "moon_venus_conjunction": {
    title: "Луна соединение Венера",
    category: "fusion",
    text: "Ты чувствуешь через близость и мягкость. Внутри много потребности в тепле, симпатии и живом эмоциональном контакте.",
  },
  "moon_mars_conjunction": {
    title: "Луна соединение Марс",
    category: "fusion",
    text: "У тебя эмоции быстро превращаются в действие. Реакция идет почти сразу, и иногда пауза дается труднее, чем импульс.",
  },
  "mercury_venus_conjunction": {
    title: "Меркурий соединение Венера",
    category: "fusion",
    text: "Ты умеешь притягивать словами. Общение, симпатия и стиль речи у тебя естественно связаны друг с другом.",
  },
  "mercury_mars_conjunction": {
    title: "Меркурий соединение Марс",
    category: "fusion",
    text: "Твой язык быстрый и прямой. Это дает силу в споре и точность в моменте, но может делать речь резче, чем ты планировал.",
  },
  "venus_mars_conjunction": {
    title: "Венера соединение Марс",
    category: "fusion",
    text: "Любовь, желание и физическое притяжение у тебя идут одним потоком. Это усиливает харизму и делает включение очень сильным.",
  },
  "sun_moon_square": {
    title: "Солнце квадрат Луна",
    category: "tension",
    text: "Ты можешь хотеть одного, а чувствовать другое. Из-за этого согласие с собой не всегда дается легко, даже если внешне все выглядит собранно.",
  },
  "sun_mars_square": {
    title: "Солнце квадрат Марс",
    category: "tension",
    text: "Внутри много давления и импульса. Ты можешь постоянно подгонять себя и с трудом выходить из режима внутреннего напряжения.",
  },
  "moon_mercury_square": {
    title: "Луна квадрат Меркурий",
    category: "tension",
    text: "Ты чувствуешь одно, а объясняешь другое. Из-за этого бывает ощущение, что тебя не до конца понимают или ты не успеваешь перевести чувства в слова.",
  },
  "moon_mars_square": {
    title: "Луна квадрат Марс",
    category: "tension",
    text: "Эмоции легко превращаются в резкую реакцию. Внутреннее напряжение быстро выходит наружу действием, а не проживанием.",
  },
  "mercury_mars_square": {
    title: "Меркурий квадрат Марс",
    category: "tension",
    text: "Ты думаешь быстро и говоришь резко. Это усиливает интеллект и скорость, но делает словесные конфликты более вероятными.",
  },
  "venus_mars_square": {
    title: "Венера квадрат Марс",
    category: "tension",
    text: "Притяжение сильное, но удерживать стабильность труднее. Любовь и желание могут идти через напряжение, а не через плавность.",
  },
  "venus_saturn_square": {
    title: "Венера квадрат Сатурн",
    category: "tension",
    text: "Ты можешь хотеть любви и одновременно сомневаться, что она безопасна или вообще возможна. Близость здесь часто проходит через внутренний барьер.",
  },
  "sun_saturn_square": {
    title: "Солнце квадрат Сатурн",
    category: "tension",
    text: "Внутри много давления и сомнений в себе. Часто кажется, что до права проявляться еще нужно доработать или дотянуться.",
  },
  "moon_saturn_square": {
    title: "Луна квадрат Сатурн",
    category: "tension",
    text: "Эмоции легче держать внутри, чем показывать. Открытость и уязвимость могут ощущаться как риск, а не как естественное состояние.",
  },
  "sun_moon_opposition": {
    title: "Солнце оппозиция Луна",
    category: "polarity",
    text: "Внутри как будто живут две разные личности. Важнейшая задача здесь — не выбрать одну часть, а научиться держать между ними баланс.",
  },
  "sun_saturn_opposition": {
    title: "Солнце оппозиция Сатурн",
    category: "polarity",
    text: "Ты хочешь проявляться, но одновременно держишь себя назад. Здесь часто идет качание между желанием выйти в мир и страхом ошибки.",
  },
  "moon_venus_opposition": {
    title: "Луна оппозиция Венера",
    category: "polarity",
    text: "Ты тянешься к любви, но не всегда умеешь принимать ее спокойно. Между чувствами и формой близости может быть внутренний разрыв.",
  },
  "moon_mars_opposition": {
    title: "Луна оппозиция Марс",
    category: "polarity",
    text: "Эмоции и действия тянут в разные стороны. Из-за этого внутри может накапливаться напряжение между импульсом и чувствительностью.",
  },
  "venus_mars_opposition": {
    title: "Венера оппозиция Марс",
    category: "polarity",
    text: "Сильное притяжение сочетается с качелями. Любовь и желание здесь не сливаются спокойно, а скорее поляризуют друг друга.",
  },
  "venus_saturn_opposition": {
    title: "Венера оппозиция Сатурн",
    category: "polarity",
    text: "Есть тяга к любви и одновременно страх близости. Хочется связи, но доверие и расслабление даются не сразу.",
  },
  "mercury_neptune_opposition": {
    title: "Меркурий оппозиция Нептун",
    category: "polarity",
    text: "Мысли и ощущения могут путаться между собой. Здесь трудно сразу отделить реальность от внутреннего образа, особенно под эмоциональной нагрузкой.",
  },
  "sun_moon_trine": {
    title: "Солнце тригон Луна",
    category: "strength",
    text: "У тебя есть редкое внутреннее согласие с собой. Быть собой и чувствовать себя собой здесь легче, чем при напряженных аспектах.",
  },
  "sun_mars_trine": {
    title: "Солнце тригон Марс",
    category: "strength",
    text: "Энергия идет естественно, без большого внутреннего сопротивления. Ты легче включаешься в действие и меньше тратишь сил на борьбу с собой.",
  },
  "moon_venus_trine": {
    title: "Луна тригон Венера",
    category: "strength",
    text: "Внутри много мягкости, тепла и естественной способности к любви. Эмоции и симпатия здесь поддерживают друг друга, а не спорят.",
  },
  "mercury_uranus_trine": {
    title: "Меркурий тригон Уран",
    category: "strength",
    text: "У тебя быстрый и нестандартный ум. Идеи приходят легко, особенно там, где нужно увидеть неочевидное решение или выйти за привычную логику.",
  },
  "venus_mars_trine": {
    title: "Венера тригон Марс",
    category: "strength",
    text: "Любовь и желание здесь соединяются естественно. Это дает живую притягательность и меньше внутреннего напряжения между нежностью и страстью.",
  },
  "sun_jupiter_trine": {
    title: "Солнце тригон Юпитер",
    category: "strength",
    text: "Внутри есть естественное чувство роста и разрешения на большее. Уверенность здесь чаще усиливает тебя, чем обманывает.",
  },
  "sun_moon_sextile": {
    title: "Солнце секстиль Луна",
    category: "potential",
    text: "Гармония между тем, кто ты, и тем, что ты чувствуешь, здесь достижима. Это не автоматическая легкость, а потенциал, который реально можно прожить.",
  },
  "mercury_venus_sextile": {
    title: "Меркурий секстиль Венера",
    category: "potential",
    text: "У тебя есть потенциал говорить мягко, красиво и притягательно. Особенно это раскрывается, когда ты не спешишь и не входишь в защиту.",
  },
  "venus_jupiter_sextile": {
    title: "Венера секстиль Юпитер",
    category: "potential",
    text: "Любовь и рост здесь могут усиливать друг друга. В отношениях часто открываются хорошие возможности, если ты не закрываешься раньше времени.",
  },
  "mars_saturn_sextile": {
    title: "Марс секстиль Сатурн",
    category: "potential",
    text: "У тебя есть ресурс соединить импульс и дисциплину. Когда включаешься осознанно, можешь быть очень собранным и результативным.",
  },
  "moon_neptune_sextile": {
    title: "Луна секстиль Нептун",
    category: "potential",
    text: "Тонкое чувство, интуиция и эмпатия здесь работают как врожденный потенциал. Если не уходить в перегруз, это может стать очень сильной внутренней опорой.",
  },
};

const ASPECT_PRIORITY = ["conjunction", "square", "opposition", "trine", "sextile"] as const;
const ASPECT_BODY_ORDER = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"] as const;

const LIFE_MAP_BLUEPRINT: Array<{
  house: number;
  title: string;
  routeTitle: string;
  href: string;
  accent: string;
}> = [
  {
    house: 1,
    title: "Кто ты и как входишь в мир",
    routeTitle: "В Guidance",
    href: "/tarot",
    accent: "#8a6f49",
  },
  {
    house: 4,
    title: "Дом, корни и внутренняя опора",
    routeTitle: "К кругу людей",
    href: "/account/profiles",
    accent: "#0f9d7a",
  },
  {
    house: 7,
    title: "Связи и значимые отношения",
    routeTitle: "К совместимости",
    href: "/compatibility?relation_mode=romantic",
    accent: "#d16a8d",
  },
  {
    house: 10,
    title: "Реализация и социальная роль",
    routeTitle: "К карте в профиле",
    href: PROFILE_CHART_DEEP_PATH,
    accent: "#6d5bd0",
  },
];

export function buildLifeMapSections(
  natalPreview: NatalChartPreview | null,
): LifeMapSection[] {
  const houses = ensureTwelveProfileHouses(natalPreview);
  return LIFE_MAP_BLUEPRINT.map((item) => {
    const house = houses.find((entry) => entry.house === item.house);
    const interpretation = natalPreview?.interpretations?.houses?.[item.house];

    return {
      house: item.house,
      title: item.title,
      routeTitle: item.routeTitle,
      href: item.href,
      accent: item.accent,
      summary:
        interpretation?.description ||
        interpretation?.theme ||
        HOUSE_FALLBACK[item.house],
    };
  });
}

export function getPlanetSignId(
  natalPreview: NatalChartPreview | null,
  planet: "Sun" | "Moon" | "Venus" | "Mars" | "Mercury" | "Jupiter" | "Saturn" | "Uranus" | "Neptune" | "Pluto",
  fallback?: string | null,
) {
  const pos = lookupNatalBodyPosition(natalPreview?.positions, planet);
  const fromChart = resolveZodiacSignId(pos?.sign, pos?.longitude ?? null);
  if (fromChart) return fromChart;
  return resolveZodiacSignId(fallback || "", null);
}

export function getRisingSignId(natalPreview: NatalChartPreview | null) {
  if (!natalPreview) return null;
  if (
    natalPreview.time_unknown ||
    natalPreview.mode === "unknown_time" ||
    natalPreview.ascendant_precision === "unavailable"
  ) {
    return null;
  }
  const h1 = ensureTwelveProfileHouses(natalPreview).find((h) => h.house === 1);
  let id = resolveZodiacSignId(h1?.sign, h1?.cusp_longitude ?? null);
  if (id) return id;
  const asc = natalPreview?.ascendant;
  return resolveZodiacSignId(asc?.sign, asc?.longitude ?? null);
}

export function layerSignLabel(entry: PlanetInSignEntry | null | undefined, fallback: string) {
  const match = getZodiacEntry(entry?.signId || "");
  return match?.ruName || fallback;
}

export function resolveMcSignLabel(preview: NatalChartPreview | null): string | null {
  const houseTen = preview?.houses?.find((house) => house.house === 10);
  if (!houseTen?.sign) return null;
  const signId = resolveZodiacSignId(houseTen.sign, houseTen.cusp_longitude ?? null);
  const entry = signId ? getZodiacEntry(signId) : undefined;
  return entry?.ruName ?? houseTen.sign;
}

export function buildRisingOverviewHint(entry: PlanetInSignEntry | undefined, hasAscendantData: boolean) {
  if (!hasAscendantData) {
    return "Асцендент появится, когда в профиле будет надёжное время рождения.";
  }
  if (entry?.bullets?.[0]) return entry.bullets[0];
  return "Показывает первый импульс, стиль контакта и то, как ты входишь в новые процессы.";
}

function planetHouse(natalPreview: NatalChartPreview | null, planet: "Sun" | "Moon" | "Venus" | "Mars" | "Mercury" | "Jupiter" | "Saturn" | "Uranus" | "Neptune" | "Pluto") {
  return lookupNatalBodyPosition(natalPreview?.positions, planet)?.house;
}

function buildHouseManifestationLine({
  planet,
  sign,
  house,
}: {
  planet: string;
  sign: string;
  house?: number;
}) {
  if (!house || !HOUSE_LAYER[house]) {
    return null;
  }
  const houseMeta = HOUSE_LAYER[house];
  const planetRu = natalBodyLabelRu(planet);
  return {
    planet,
    signLabel: sign,
    house,
    houseTitle: houseMeta.title,
    text: `${planetRu} в ${sign} сильнее всего проявляется ${HOUSE_CONTEXT_LABELS[house] || houseMeta.prompt}.`,
  };
}

function buildHouseFocus(natalPreview: NatalChartPreview | null) {
  const trackedPlanets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"] as const;
  const grouped = new Map<number, string[]>();

  for (const planet of trackedPlanets) {
    const house = lookupNatalBodyPosition(natalPreview?.positions, planet)?.house;
    if (!house) continue;
    const current = grouped.get(house) || [];
    current.push(planet);
    grouped.set(house, current);
  }

  let bestHouse: number | null = null;
  let bestPlanets: string[] = [];
  Array.from(grouped.entries()).forEach(([house, planets]) => {
    if (planets.length >= 3 && planets.length > bestPlanets.length) {
      bestHouse = house;
      bestPlanets = planets;
    }
  });

  if (!bestHouse || !bestPlanets.length) {
    return null;
  }

  const title = HOUSE_LAYER[bestHouse]?.title || `${bestHouse} дом`;
  const houseContext = HOUSE_CONTEXT_LABELS[bestHouse] || HOUSE_LAYER[bestHouse]?.prompt || HOUSE_FALLBACK[bestHouse];
  const planetLabels = bestPlanets.join(", ");

  return {
    house: bestHouse,
    title,
    planets: bestPlanets,
    text: `У тебя многое завязано ${houseContext}. Это не просто одна из тем жизни: через нее проходят сразу несколько важных частей карты (${planetLabels}), поэтому именно здесь ты проживаешь особенно много.`,
  };
}

function normalizeAspectBodies(bodies: string | undefined | null) {
  if (bodies == null || typeof bodies !== "string") return [];
  return bodies
    .split(/[\u00b7•,-]| and /i)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => item.replace(/\s+/g, " "));
}

function normalizeAspectBodyName(value: string) {
  return value
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ")
    .replace("north node", "north node")
    .replace("south node", "south node");
}

function canonicalAspectBodies(bodies: string) {
  return normalizeAspectBodies(bodies).sort((left, right) => {
    const leftKey = normalizeAspectBodyName(left);
    const rightKey = normalizeAspectBodyName(right);
    const leftIndex = ASPECT_BODY_ORDER.indexOf(leftKey as (typeof ASPECT_BODY_ORDER)[number]);
    const rightIndex = ASPECT_BODY_ORDER.indexOf(rightKey as (typeof ASPECT_BODY_ORDER)[number]);
    const leftRank = leftIndex === -1 ? 999 : leftIndex;
    const rightRank = rightIndex === -1 ? 999 : rightIndex;
    if (leftRank !== rightRank) return leftRank - rightRank;
    return leftKey.localeCompare(rightKey);
  });
}

function aspectKey(callout: AspectCallout) {
  const parts = canonicalAspectBodies(callout.bodies);
  if (parts.length < 2) {
    return "";
  }
  return `${normalizeAspectBodyName(parts[0]).replace(/\s+/g, "_")}_${normalizeAspectBodyName(parts[1]).replace(/\s+/g, "_")}_${String(callout.aspect_id || "").toLowerCase()}`;
}

function buildAspectSummary(insights: CombinedPlanetaryProfile["aspectInsights"]) {
  if (!insights.length) {
    return null;
  }

  const fusion = insights.find((item) => item.category === "fusion");
  const tension = insights.find((item) => item.category === "tension" || item.category === "polarity");
  const strength = insights.find((item) => item.category === "strength" || item.category === "potential");
  const selfBlock = insights.find((item) => item.category === "tension")
    || insights.find((item) => item.category === "polarity");

  return {
    coherence: fusion
      ? `${fusion.text} Это одно из мест, где части тебя работают не вразнобой, а как единое поведение.`
      : strength
        ? `${strength.text} Здесь видно, что у тебя есть врожденная опора, к которой можно сознательно возвращаться.`
        : "В карте есть точки, где части тебя могут работать согласованно, даже если это не всегда ощущается автоматически.",
    conflict: tension
      ? `${tension.text} Именно такие аспекты чаще всего создают ощущение, что ты хочешь одного, а проживаешь другое.`
      : "Напряженные места в карте проявляются как внутренние расхождения между чувствами, решениями и формой действия.",
    advantage: strength
      ? `${strength.text} Это не случайный бонус, а твое встроенное преимущество, которое особенно заметно в нужной среде.`
      : fusion
        ? `${fusion.text} Если опираться на эту связность, она начинает работать как сильная естественная опора.`
        : "В карте есть сильные линии, через которые ты можешь действовать легче и точнее, чем тебе кажется.",
    selfBlock: selfBlock
      ? `${selfBlock.text} Здесь особенно легко самому усиливать перегруз, если не замечать, какой именно внутренний механизм включается первым.`
      : "Самоблок обычно появляется там, где одна часть тебя пытается перекрыть другую вместо того, чтобы дать ей место.",
  };
}

function signElement(signId?: string) {
  return getZodiacEntry(signId || "")?.element || "";
}

function hasHardAspect(
  callouts: AspectCallout[] | undefined,
  keys: string[],
) {
  const normalized = new Set((callouts || []).map((item) => aspectKey(item)));
  return keys.some((key) => normalized.has(key));
}

function houseInRange(house?: number, values: number[] = []) {
  return typeof house === "number" && values.includes(house);
}

function scenarioEntry(id: string): ProfileScenarioEntry {
  return getProfileScenarioEntry(id) || { id, title: id, bullets: [] };
}

function buildScenarioReading(id: string, evidence: string[]) {
  if (id === "relationships_hard") {
    return [
      "Ты хочешь близости, но закрываешься, когда становится по-настоящему.",
      "Ты чувствуешь больше, чем говоришь, и не всегда показываешь это сразу.",
      "Тебя может тянуть к сложной, интенсивной связи сильнее, чем к спокойной устойчивости.",
    ];
  }
  if (id === "burnout") {
    return [
      "Ты не устаешь только от работы, ты устаешь от давления, отсутствия смысла и невозможности остановиться.",
      "Ты берешь больше, чем можешь удержать, и замечаешь перегруз не в начале, а уже на пике.",
      "Усталость у тебя часто связана не со слабостью, а с внутренним принуждением держать высокий темп.",
    ];
  }
  if (id === "income_max") {
    return [
      "Ты можешь работать много, но не туда.",
      "Ты недооцениваешь себя или не используешь возможности, которые у тебя уже есть.",
      "Рост тормозится не отсутствием потенциала, а тем, как ты обходишься со своей ценностью и расширением.",
    ];
  }
  return evidence.slice(0, 3).map((item) => item.charAt(0).toUpperCase() + item.slice(1) + ".");
}

function houseScenarioLine(house?: number) {
  if (!house) return null;
  const label = HOUSE_CONTEXT_LABELS[house];
  if (!label) return null;
  return `Это особенно сильно проявляется ${label}.`;
}

function numerologyScenarioNudge(id: string, lifePath?: LifePathEntry) {
  if (!lifePath) return null;
  if (id === "relationships_hard") {
    if (lifePath.number === 2) return "Число 2 усиливает потребность в гармонии и связи, поэтому тебе особенно трудно выдерживать напряжение, не растворяясь в другом человеке.";
    if (lifePath.number === 6) return "Число 6 добавляет тему заботы и ответственности, из-за чего любовь легко превращается в контроль или спасательство.";
    if (lifePath.number === 8) return "Число 8 усиливает тему контроля и силы, поэтому полностью расслабиться в близости у тебя может быть сложнее, чем кажется.";
    if (lifePath.number === 9) return "Число 9 делает тебя очень эмпатичным, а значит в отношениях особенно важно не терять свою границу.";
  }
  if (id === "burnout") {
    if (lifePath.number === 1) return "Число 1 усиливает импульс тянуть на себе и идти первым, поэтому остановка может ощущаться почти как слабость.";
    if (lifePath.number === 4) return "Число 4 добавляет долг, структуру и выносливость, из-за чего ты можешь держать перегруз дольше, чем это уже полезно.";
    if (lifePath.number === 6) return "Число 6 усиливает привычку брать ответственность за все вокруг, а это быстро выматывает.";
    if (lifePath.number === 8) return "Число 8 усиливает давление результата, поэтому ты можешь измерять себя достижением даже тогда, когда ресурс уже закончился.";
  }
  if (id === "income_max") {
    if (lifePath.number === 4) return "Число 4 делает тебя сильнее в системе и долгой стратегии, но может удерживать в слишком безопасной модели роста.";
    if (lifePath.number === 5) return "Число 5 добавляет свободу и движение, из-за чего деньги могут идти волнами, если у роста нет структуры.";
    if (lifePath.number === 8) return "Число 8 само по себе про силу, деньги и масштаб. Если доход не раскрыт, это часто ощущается как недожитый потенциал.";
    if (lifePath.number === 9) return "Число 9 усиливает тему смысла и пользы, поэтому ты можешь выбирать нужное и важное, но не самое выгодное для себя.";
  }
  return null;
}

function buildScenarioLayers(
  id: string,
  context: {
    moon?: PlanetInSignEntry;
    venus?: PlanetInSignEntry;
    mars?: PlanetInSignEntry;
    jupiter?: PlanetInSignEntry;
    saturn?: PlanetInSignEntry;
    neptune?: PlanetInSignEntry;
    moonHouse?: number;
    venusHouse?: number;
    marsHouse?: number;
    jupiterHouse?: number;
    saturnHouse?: number;
    neptuneHouse?: number;
    callouts?: AspectCallout[];
    lifePath?: LifePathEntry;
  },
) {
  const layers: Array<{ label: string; reason: string }> = [];

  if (id === "relationships_hard") {
    if (context.moon) {
      if (["gemini"].includes(context.moon.signId)) {
        layers.push({ label: "Луна", reason: "Ты проговариваешь чувства через голову, и из-за этого глубина может утомлять быстрее, чем кажется." });
      } else if (["cancer", "pisces"].includes(context.moon.signId)) {
        layers.push({ label: "Луна", reason: "Ты чувствуешь слишком много и легко растворяешься в связи, а потом труднее понять, где заканчиваешься ты." });
      } else if (["capricorn", "aquarius"].includes(context.moon.signId)) {
        layers.push({ label: "Луна", reason: "Ты держишь эмоции под контролем и можешь казаться холодным, хотя на деле это способ защиты." });
      }
    }
    if (context.venus) {
      if (["gemini", "sagittarius"].includes(context.venus.signId)) {
        layers.push({ label: "Венера", reason: "В любви тебе нужен интерес и движение. Скука разрушает связь даже тогда, когда человек сам по себе тебе подходит." });
      } else if (context.venus.signId === "scorpio") {
        layers.push({ label: "Венера", reason: "Ты не умеешь любить вполсилы. Страх предательства делает связь очень глубокой, но и очень уязвимой." });
      } else if (context.venus.signId === "capricorn") {
        layers.push({ label: "Венера", reason: "Ты не доверяешь сразу и можешь упустить живую связь из-за осторожности и внутренней проверки." });
      }
    }
    if (hasHardAspect(context.callouts, ["venus_saturn_square", "venus_saturn_opposition"])) {
      layers.push({ label: "Сатурн", reason: "Ты хочешь любви, но не до конца веришь, что она безопасна или возможна. Поэтому дистанция включается даже при реальном шансе." });
    } else if (hasHardAspect(context.callouts, ["moon_saturn_square"])) {
      layers.push({ label: "Сатурн", reason: "Есть страх быть отвергнутым, поэтому чувства легче держать в себе, чем показать напрямую." });
    }
    if (hasHardAspect(context.callouts, ["venus_neptune_conjunction", "venus_neptune_square", "venus_neptune_opposition"])) {
      layers.push({ label: "Нептун", reason: "Ты можешь влюбляться в образ, потенциал и обещание связи, а не в то, что реально есть между вами." });
    }
    if (context.mars) {
      if (["aries", "scorpio"].includes(context.mars.signId)) {
        layers.push({ label: "Марс", reason: "В поведении ты можешь заходить слишком резко, давить или ускорять то, что должно раскрываться медленнее." });
      } else if (["libra", "pisces"].includes(context.mars.signId)) {
        layers.push({ label: "Марс", reason: "Ты избегаешь прямого напряжения, и из-за этого важные проблемы остаются внутри связи дольше, чем нужно." });
      }
    }
    if (houseInRange(context.venusHouse, [7]) || houseInRange(context.moonHouse, [7])) {
      layers.push({ label: "7 дом", reason: "Отношения у тебя не фон, а одна из центральных жизненных тем. Поэтому любой любовный сценарий ощущается сильнее." });
    } else if (houseInRange(context.venusHouse, [12]) || houseInRange(context.moonHouse, [12])) {
      layers.push({ label: "12 дом", reason: "В отношениях у тебя могут включаться скрытые сценарии и повторяющиеся паттерны, которые трудно увидеть сразу." });
    }
    const nudge = numerologyScenarioNudge(id, context.lifePath);
    if (nudge) layers.push({ label: "Число пути", reason: nudge });
  }

  if (id === "burnout") {
    if (context.mars) {
      if (["aries", "sagittarius"].includes(context.mars.signId)) {
        layers.push({ label: "Марс", reason: "Ты работаешь на импульсе и не всегда замечаешь момент, когда уже давно пора остановиться." });
      } else if (["virgo", "capricorn"].includes(context.mars.signId)) {
        layers.push({ label: "Марс", reason: "Ты перегружаешь себя через требовательность, контроль и желание сделать все идеально или безошибочно." });
      }
    }
    if (hasHardAspect(context.callouts, ["sun_saturn_square", "sun_saturn_opposition", "sun_mars_square"])) {
      layers.push({ label: "Сатурн", reason: "Внутри много давления и ощущения, что сделанного все равно недостаточно. Это усиливает выгорание быстрее, чем сама нагрузка." });
    }
    if (hasHardAspect(context.callouts, ["sun_neptune_opposition", "mars_neptune_square"])) {
      layers.push({ label: "Нептун", reason: "Когда нет ясности и собранного смысла, энергия начинает уходить в туман, а не в результат." });
    }
    if (houseInRange(context.marsHouse, [6]) || houseInRange(context.saturnHouse, [6])) {
      layers.push({ label: "6 дом", reason: "Работа, рутина и ежедневная нагрузка у тебя быстро становятся зоной перегруза, если в них теряется баланс." });
    }
    const nudge = numerologyScenarioNudge(id, context.lifePath);
    if (nudge) layers.push({ label: "Число пути", reason: nudge });
  }

  if (id === "income_max") {
    if (context.jupiter) {
      layers.push({ label: "Юпитер", reason: "Твой максимум связан со способностью расширяться. Когда ты не используешь возможности или сужаешь себя, рост тормозится." });
    }
    if (houseInRange(context.saturnHouse, [2]) || (context.saturn && ["taurus", "capricorn"].includes(context.saturn.signId))) {
      layers.push({ label: "Сатурн", reason: "Тема денег и безопасности может быть связана со страхом потери, из-за чего ты выбираешь не рост, а контроль." });
    }
    if (context.venus) {
      layers.push({ label: "Венера", reason: "Через Венеру видно, как ты обращаешься со своей ценностью. Если здесь мало разрешения на большее, ты соглашаешься на меньшее." });
    }
    if (context.mars) {
      layers.push({ label: "Марс", reason: "Доход зависит не только от потенциала, но и от того, как ты действуешь: последовательно или рывками." });
    }
    if (houseInRange(context.jupiterHouse, [2, 10]) || houseInRange(context.saturnHouse, [2, 10])) {
      layers.push({ label: "2/10 дом", reason: "Деньги и реализация у тебя связаны напрямую, поэтому вопрос дохода почти всегда упирается еще и в самооценку и место в мире." });
    }
    const nudge = numerologyScenarioNudge(id, context.lifePath);
    if (nudge) layers.push({ label: "Число пути", reason: nudge });
  }

  return layers.slice(0, 5);
}

function buildScenarioMatches({
  natalPreview,
  sun,
  moon,
  venus,
  mars,
  mercury,
  jupiter,
  saturn,
  uranus,
  neptune,
  pluto,
  lifePath,
  aspectInsights,
}: {
  natalPreview: NatalChartPreview | null;
  sun?: PlanetInSignEntry;
  moon?: PlanetInSignEntry;
  venus?: PlanetInSignEntry;
  mars?: PlanetInSignEntry;
  mercury?: PlanetInSignEntry;
  jupiter?: PlanetInSignEntry;
  saturn?: PlanetInSignEntry;
  uranus?: PlanetInSignEntry;
  neptune?: PlanetInSignEntry;
  pluto?: PlanetInSignEntry;
  lifePath?: LifePathEntry;
  aspectInsights: CombinedPlanetaryProfile["aspectInsights"];
}) {
  const callouts = natalPreview?.aspects?.callouts;
  const moonHouse = planetHouse(natalPreview, "Moon");
  const venusHouse = planetHouse(natalPreview, "Venus");
  const marsHouse = planetHouse(natalPreview, "Mars");
  const sunHouse = planetHouse(natalPreview, "Sun");
  const mercuryHouse = planetHouse(natalPreview, "Mercury");
  const jupiterHouse = planetHouse(natalPreview, "Jupiter");
  const saturnHouse = planetHouse(natalPreview, "Saturn");
  const neptuneHouse = planetHouse(natalPreview, "Neptune");
  const plutoHouse = planetHouse(natalPreview, "Pluto");

  const matches: CombinedPlanetaryProfile["scenarios"] = [];

  const pushScenario = (id: string, evidence: string[]) => {
    const entry = scenarioEntry(id);
    if (!evidence.length) return;
    const layers = buildScenarioLayers(id, {
      moon,
      venus,
      mars,
      jupiter,
      saturn,
      neptune,
      moonHouse,
      venusHouse,
      marsHouse,
      jupiterHouse,
      saturnHouse,
      neptuneHouse,
      callouts,
      lifePath,
    });
    const primaryHouse =
      id === "relationships_hard"
        ? venusHouse || moonHouse
        : id === "burnout"
          ? marsHouse || saturnHouse || sunHouse
          : id === "income_max"
            ? jupiterHouse || saturnHouse || sunHouse
            : id === "trust"
              ? moonHouse || plutoHouse
              : id === "wrong_people"
                ? venusHouse || neptuneHouse
                : id === "letting_go"
                  ? moonHouse || neptuneHouse || plutoHouse
                  : id === "income_swings"
                    ? jupiterHouse || marsHouse
                    : id === "not_my_place"
                      ? sunHouse || planetHouse(natalPreview, "Uranus")
                      : moonHouse || neptuneHouse;
    const houseLine = houseScenarioLine(primaryHouse);
    matches.push({
      id,
      title: entry.title,
      summary: `Этот сценарий может повторяться у тебя, потому что ${evidence.slice(0, 2).join(" и ").toLowerCase()}.${houseLine ? ` ${houseLine}` : ""}`,
      evidence,
      bullets: entry.bullets.slice(0, 3),
      reading: buildScenarioReading(id, evidence),
      layers,
    });
  };

  {
    const evidence: string[] = [];
    if (hasHardAspect(callouts, ["venus_saturn_square", "venus_saturn_opposition"])) {
      evidence.push("в любви у тебя есть напряжение между тягой к близости и внутренней защитой");
    }
    if (hasHardAspect(callouts, ["moon_saturn_square", "moon_venus_opposition", "venus_mars_square", "venus_mars_opposition"])) {
      evidence.push("чувства, близость и желание не всегда двигаются у тебя в одном ритме");
    }
    if (moon && signElement(moon.signId) === "Вода") {
      evidence.push("эмоционально ты проживаешь связь глубже, чем обычно показываешь");
    }
    if (houseInRange(venusHouse, [7, 8, 12]) || houseInRange(moonHouse, [7, 8, 12])) {
      evidence.push("тема отношений у тебя включается не поверхностно, а как сильная жизненная зона");
    }
    pushScenario("relationships_hard", evidence);
  }

  {
    const evidence: string[] = [];
    if (hasHardAspect(callouts, ["sun_mars_square", "moon_mars_square", "mercury_mars_square"])) {
      evidence.push("внутреннее напряжение у тебя быстро превращается в действие и расход энергии");
    }
    if (mars && ["aries", "capricorn"].includes(mars.signId)) {
      evidence.push("ты действуешь в высоком темпе и можешь долго не замечать момент истощения");
    }
    if (houseInRange(marsHouse, [6, 10]) || houseInRange(sunHouse, [6, 10]) || houseInRange(saturnHouse, [6, 10])) {
      evidence.push("работа, результат и ежедневная нагрузка у тебя стоят слишком близко к самоощущению");
    }
    if (saturn && ["virgo", "capricorn"].includes(saturn.signId)) {
      evidence.push("внутренний контроль и требовательность к себе у тебя выше среднего");
    }
    pushScenario("burnout", evidence);
  }

  {
    const evidence: string[] = [];
    if (jupiter && ["taurus", "capricorn", "virgo"].includes(jupiter.signId)) {
      evidence.push("ты растешь сильнее через систему и долгую стратегию, чем через рывки");
    }
    if (saturn && ["aries", "leo", "capricorn"].includes(saturn.signId)) {
      evidence.push("внутри у тебя есть страх выйти в большее и реально занять больше места");
    }
    if (houseInRange(jupiterHouse, [2, 10]) || houseInRange(sunHouse, [2, 10])) {
      evidence.push("тема денег и реализации у тебя напрямую связана с темой личной ценности");
    }
    if (mercury && ["gemini", "pisces", "sagittarius"].includes(mercury.signId)) {
      evidence.push("ты можешь распыляться между несколькими направлениями вместо одной сильной линии");
    }
    pushScenario("income_max", evidence);
  }

  {
    const evidence: string[] = [];
    if (saturn && ["libra", "virgo", "capricorn"].includes(saturn.signId)) {
      evidence.push("ты можешь застревать в выборе, анализе и страхе ошибки");
    }
    if (mercury && ["virgo", "libra", "taurus"].includes(mercury.signId)) {
      evidence.push("ты долго взвешиваешь и не всегда быстро переходишь к шагу");
    }
    if (houseInRange(saturnHouse, [10, 12]) || houseInRange(plutoHouse, [8, 12])) {
      evidence.push("старая опора может уже не работать, но отпускается медленно");
    }
    if (hasHardAspect(callouts, ["sun_saturn_square", "sun_saturn_opposition"])) {
      evidence.push("внутреннее давление у тебя легко тормозит движение даже при сильном потенциале");
    }
    pushScenario("stuck", evidence);
  }

  {
    const evidence: string[] = [];
    if (hasHardAspect(callouts, ["moon_saturn_square", "venus_saturn_square", "venus_saturn_opposition"])) {
      evidence.push("доверие и близость у тебя проходят через внутреннюю проверку и защиту");
    }
    if (pluto && ["scorpio", "capricorn"].includes(pluto.signId)) {
      evidence.push("ты не склонен открываться сразу и интуитивно держишь контроль");
    }
    if (houseInRange(moonHouse, [8, 12]) || houseInRange(plutoHouse, [8, 12])) {
      evidence.push("самые чувствительные темы у тебя живут глубоко и редко показываются сразу");
    }
    pushScenario("trust", evidence);
  }

  {
    const evidence: string[] = [];
    if (neptune && ["pisces", "libra", "scorpio"].includes(neptune.signId)) {
      evidence.push("тебя может тянуть к сильному ощущению, символике и эмоциональной недоступности");
    }
    if (hasHardAspect(callouts, ["venus_mars_square", "venus_mars_opposition", "moon_venus_opposition"])) {
      evidence.push("в любви тебя может сильнее цеплять напряжение, чем спокойная устойчивость");
    }
    if (houseInRange(venusHouse, [8, 12]) || houseInRange(neptuneHouse, [7, 12])) {
      evidence.push("сценарий притяжения у тебя легко связывается с глубиной, тайной или фантазией");
    }
    pushScenario("wrong_people", evidence);
  }

  {
    const evidence: string[] = [];
    if (neptune && ["cancer", "pisces", "taurus"].includes(neptune.signId)) {
      evidence.push("ты можешь удерживать не только человека, но и атмосферу, которая с ним была связана");
    }
    if (pluto && ["cancer", "scorpio", "pisces"].includes(pluto.signId)) {
      evidence.push("переживание потери и трансформации у тебя проходит глубже, чем это видно снаружи");
    }
    if (houseInRange(moonHouse, [4, 8, 12]) || houseInRange(neptuneHouse, [4, 8, 12]) || houseInRange(plutoHouse, [4, 8, 12])) {
      evidence.push("прошлое, память и внутренние привязанности у тебя держатся особенно сильно");
    }
    pushScenario("letting_go", evidence);
  }

  {
    const evidence: string[] = [];
    if (jupiter && ["gemini", "sagittarius", "pisces"].includes(jupiter.signId)) {
      evidence.push("твой рост идет волнами, через движение, идеи и состояние");
    }
    if (mars && ["gemini", "pisces", "sagittarius"].includes(mars.signId)) {
      evidence.push("тебе трудно долго держать один и тот же темп без смены фокуса");
    }
    if (houseInRange(jupiterHouse, [2, 6, 10]) || houseInRange(marsHouse, [2, 6, 10])) {
      evidence.push("деньги у тебя напрямую завязаны на режиме работы и способности держать ритм");
    }
    pushScenario("income_swings", evidence);
  }

  {
    const evidence: string[] = [];
    if (sun && ["aquarius", "pisces", "cancer"].includes(sun.signId)) {
      evidence.push("твоя внутренняя правда может не совпадать с ожидаемой от тебя ролью");
    }
    if (saturn && ["capricorn", "libra"].includes(saturn.signId)) {
      evidence.push("ты легко остаешься в правильной или привычной роли дольше, чем она тебе подходит");
    }
    if (uranus && ["aquarius", "capricorn", "taurus"].includes(uranus.signId)) {
      evidence.push("внутри тебя уже есть потребность переписать старую систему, а не только встроиться в нее");
    }
    if (houseInRange(sunHouse, [10, 11, 12]) || houseInRange(uranus ? planetHouse(natalPreview, "Uranus") : undefined, [10, 11, 12])) {
      evidence.push("тема места в мире и собственной роли у тебя проживается особенно остро");
    }
    pushScenario("not_my_place", evidence);
  }

  {
    const evidence: string[] = [];
    if (moon && signElement(moon.signId) === "Вода") {
      evidence.push("ты очень тонко считываешь состояние других людей");
    }
    if (neptune && ["pisces", "cancer"].includes(neptune.signId)) {
      evidence.push("границы между своим и чужим могут размываться быстрее обычного");
    }
    if (houseInRange(moonHouse, [7, 11, 12]) || houseInRange(neptuneHouse, [7, 11, 12])) {
      evidence.push("люди и их состояние сильно заходят в твою внутреннюю систему");
    }
    if (hasHardAspect(callouts, ["moon_neptune_sextile", "mercury_neptune_opposition"])) {
      evidence.push("ты можешь очень тонко чувствовать атмосферу, но не всегда быстро отделяешь ее от себя");
    }
    pushScenario("people_overload", evidence);
  }

  return matches
    .sort((left, right) => right.evidence.length - left.evidence.length)
    .slice(0, 3);
}

function buildAspectInsights(callouts: AspectCallout[] | undefined) {
  if (!callouts?.length) {
    return [];
  }

  const ranked = [...callouts].sort((a, b) => {
    const aPriority = ASPECT_PRIORITY.indexOf((a.aspect_id || "").toLowerCase() as (typeof ASPECT_PRIORITY)[number]);
    const bPriority = ASPECT_PRIORITY.indexOf((b.aspect_id || "").toLowerCase() as (typeof ASPECT_PRIORITY)[number]);
    const aRank = aPriority === -1 ? 99 : aPriority;
    const bRank = bPriority === -1 ? 99 : bPriority;
    if (aRank !== bRank) return aRank - bRank;
    const strengthWeight = (value: string) => (value === "exact" ? 0 : value === "tight" ? 1 : 2);
    return strengthWeight(a.strength) - strengthWeight(b.strength);
  });

  const picked: CombinedPlanetaryProfile["aspectInsights"] = [];
  const seen = new Set<string>();

  for (const callout of ranked) {
    const key = aspectKey(callout);
    const preset = ASPECT_INTERPRETATIONS[key];
    if (!preset || seen.has(key)) continue;
    seen.add(key);
    picked.push({
      key,
      title: preset.title,
      category: preset.category,
      text: preset.text,
      bodies: callout.bodies,
    });
    if (picked.length >= 6) break;
  }

  return picked;
}

function elementGroup(signId: string) {
  const sign = getZodiacEntry(signId);
  const element = sign?.element || "";
  if (element === "Огонь" || element === "Воздух") return "fast";
  if (element === "Земля" || element === "Вода") return "deep";
  return "neutral";
}

function firstBullet(entry?: PlanetInSignEntry) {
  return entry?.bullets?.[0] || "";
}

function buildNameConflictLine({
  soulUrge,
  mars,
}: {
  soulUrge?: NameNumberEntry;
  mars?: PlanetInSignEntry;
}) {
  if (!soulUrge || !mars) return "";
  if (soulUrge.number === 2 && mars.signId === "aries") {
    return " Внутри тебе нужна близость и гармония, но действуешь ты так, будто в контакте нельзя задерживаться слишком долго.";
  }
  if (soulUrge.number === 5 && ["taurus", "capricorn"].includes(mars.signId)) {
    return " Внутри тебе нужна свобода, но в действии ты можешь становиться намного жестче и осторожнее, чем сам от себя ожидаешь.";
  }
  if (soulUrge.number === 7 && ["aries", "leo"].includes(mars.signId)) {
    return " Внутри тебе важно понять и прожить глубже, а действуешь ты местами резко и быстрее, чем успеваешь все объяснить себе.";
  }
  if (soulUrge.number === 8 && ["pisces", "libra"].includes(mars.signId)) {
    return " Внутри тебе важны контроль и сила, но действуешь ты мягче, чем чувствуешь, и из-за этого напряжение может копиться внутри.";
  }
  return "";
}

function buildNameFirstContactLine({
  personality,
  moon,
}: {
  personality?: NameNumberEntry;
  moon?: PlanetInSignEntry;
}) {
  if (!personality) return "";
  if (personality.number === 3 && moon && ["scorpio", "cancer", "pisces"].includes(moon.signId)) {
    return " Со стороны ты можешь выглядеть легче и открытее, чем есть внутри: люди сначала считывают твою общительность, а глубину замечают позже.";
  }
  if (personality.number === 8 && moon && ["pisces", "cancer"].includes(moon.signId)) {
    return " Снаружи ты можешь казаться сильнее и жестче, чем чувствуешь себя внутри, поэтому окружающие не сразу видят твою чувствительность.";
  }
  return ` ${personality.personality.charAt(0).toUpperCase()}${personality.personality.slice(1)}.`;
}

export function buildCombinedPlanetaryProfile({
  natalPreview,
  sun,
  moon,
  venus,
  mars,
  mercury,
  rising,
  jupiter,
  saturn,
  uranus,
  neptune,
  pluto,
  lifePath,
  expressionNumber,
  soulUrgeNumber,
  personalityNumber,
}: {
  natalPreview: NatalChartPreview | null;
  sun?: PlanetInSignEntry;
  moon?: PlanetInSignEntry;
  venus?: PlanetInSignEntry;
  mars?: PlanetInSignEntry;
  mercury?: PlanetInSignEntry;
  rising?: PlanetInSignEntry;
  jupiter?: PlanetInSignEntry;
  saturn?: PlanetInSignEntry;
  uranus?: PlanetInSignEntry;
  neptune?: PlanetInSignEntry;
  pluto?: PlanetInSignEntry;
  lifePath?: LifePathEntry;
  expressionNumber?: NameNumberEntry;
  soulUrgeNumber?: NameNumberEntry;
  personalityNumber?: NameNumberEntry;
}): CombinedPlanetaryProfile | null {
  if (!sun || !moon || !venus || !mars) {
    return null;
  }

  const sunSign = layerSignLabel(sun, "этом знаке");
  const moonSign = layerSignLabel(moon, "этом знаке");
  const venusSign = layerSignLabel(venus, "этом знаке");
  const marsSign = layerSignLabel(mars, "этом знаке");
  const mercurySign = layerSignLabel(mercury, "этом знаке");
  const risingSign = layerSignLabel(rising, "этом знаке");
  const jupiterSign = layerSignLabel(jupiter, "этом знаке");
  const saturnSign = layerSignLabel(saturn, "этом знаке");
  const uranusSign = layerSignLabel(uranus, "этом знаке");
  const neptuneSign = layerSignLabel(neptune, "этом знаке");
  const plutoSign = layerSignLabel(pluto, "этом знаке");

  const outerFast = elementGroup(sun.signId) === "fast";
  const innerDeep = elementGroup(moon.signId) === "deep";
  const loveDeep = elementGroup(venus.signId) === "deep";
  const actionFast = elementGroup(mars.signId) === "fast";

  const recognition = outerFast && innerDeep
    ? `Снаружи ты входишь быстро и подвижно, но внутри переживаешь глубже, чем обычно показываешь. Из-за этого люди часто считывают твою легкость раньше, чем замечают твою чувствительность.`
    : !outerFast && actionFast
      ? `Снаружи ты можешь казаться более спокойным и собранным, чем есть в действии. Но как только появляется цель или вызов, в тебе включается более резкий и быстрый импульс.`
      : `Ты считываешься не по одному качеству, а по сочетанию темпа, чувствительности, близости и способа действия. Именно это и делает тебя узнаваемым живым человеком, а не набором отдельных описаний.`;

  const explanation = `Базовый центр личности идет через ${sun.ruTitle.toLowerCase()}: ${firstBullet(sun)}. Эмоционально ты проживаешь мир через ${moon.ruTitle.toLowerCase()}: ${firstBullet(moon)}. В любви твой сценарий читается через ${venus.ruTitle.toLowerCase()}: ${firstBullet(venus)}. В действии тебя двигает ${mars.ruTitle.toLowerCase()}: ${firstBullet(mars)}. ${mercury ? `Мышление и речь идут через ${mercury.ruTitle.toLowerCase()}: ${firstBullet(mercury)}.` : ""} ${rising ? `А в мир ты заходишь через ${rising.ruTitle.toLowerCase()}: ${firstBullet(rising)}.` : ""} ${jupiter ? `Твой рост читается через ${jupiter.ruTitle.toLowerCase()}: ${firstBullet(jupiter)}.` : ""} ${saturn ? `А главное внутреннее ограничение идет через ${saturn.ruTitle.toLowerCase()}: ${firstBullet(saturn)}.` : ""} ${uranus ? `Твой бунт и способ ломать старое читаются через ${uranus.ruTitle.toLowerCase()}: ${firstBullet(uranus)}.` : ""} ${neptune ? `Тонкая чувствительность, идеализация и магия идут через ${neptune.ruTitle.toLowerCase()}: ${firstBullet(neptune)}.` : ""} ${pluto ? `А глубинная трансформация проходит через ${pluto.ruTitle.toLowerCase()}: ${firstBullet(pluto)}.` : ""}`;

  const tension = loveDeep && actionFast
    ? `Главное внутреннее напряжение здесь в том, что в близости тебе, скорее всего, нужна устойчивость и чувство надежности, а в действии ты быстрее, резче и нетерпеливее. Из-за этого можно хотеть глубокой связи, но не всегда давать ей время построиться.`
    : outerFast && innerDeep
      ? `Главный конфликт здесь между внешним темпом и внутренней глубиной. Ты можешь быстро входить в разговор, решение или связь, но внутри проживать все заметно дольше и тяжелее, чем это видно снаружи.`
      : `Главное напряжение в том, что разные части тебя хотят разного темпа и разной формы контакта. Поэтому иногда появляется ощущение, что ты сам себе противоречишь, хотя на деле просто пытаешься удержать сразу несколько сильных линий.`;
  const tensionWithName = `${tension}${buildNameConflictLine({ soulUrge: soulUrgeNumber, mars })}`;

  const strength = outerFast && innerDeep
    ? `Сила этой комбинации в том, что ты можешь соединять скорость и глубину. Ты не только быстро схватываешь, но и по-настоящему проживаешь. Если не разрывать эти части, из этого собирается очень сильный личный стиль.`
    : loveDeep && actionFast
      ? `Сила этой комбинации в том, что ты можешь быть одновременно надежным в важном и очень решительным в моменте. Это дает и глубину в отношениях, и способность двигать жизнь вперед без долгого зависания.`
      : `Сила этой комбинации в объеме. В тебе уже есть несколько разных способов быть: чувствовать, любить, действовать и проявляться. Когда они собираются в одну линию, появляется очень сильное ощущение внутреннего стержня.`;

  const manifestation = `В жизни это обычно проявляется так: личность идет через ${sunSign}, эмоциональная реакция через ${moonSign}, сценарий любви через ${venusSign}, способ действия через ${marsSign}${mercury ? `, мышление через ${mercurySign}` : ""}${rising ? `, первый контакт через ${risingSign}` : ""}${jupiter ? `, рост через ${jupiterSign}` : ""}${saturn ? `, внутренний стоп через ${saturnSign}` : ""}${uranus ? `, бунт через ${uranusSign}` : ""}${neptune ? `, тонкая магия и туман через ${neptuneSign}` : ""}${pluto ? `, а глубокая перестройка через ${plutoSign}` : ""}${lifePath ? `, а жизненный сценарий через число пути ${lifePath.number}` : ""}${expressionNumber ? `, а способ проявляться во внешнем мире через число имени ${expressionNumber.number}` : ""}. Поэтому твоя логика редко сводится к одному слову: в тебе есть и базовый характер, и способ любить, и способ сопротивляться, и глубинная линия изменения.`;

  const risk = `Основной риск здесь — перегруз и ощущение «я сам себя не понимаю». Это случается в момент, когда скорость, чувства, близость и действие начинают тянуть в разные стороны и у тебя не остается общей внутренней сборки.`;
  const lifeVector = lifePath
    ? `Число пути ${lifePath.number} добавляет не новый характер, а жизненный сценарий. ${lifePath.reading?.[0] || lifePath.essence} Через него видно, почему ты снова и снова приходишь к похожим задачам: ${lifePath.pattern.toLowerCase()}`
    : "Числовой слой станет точнее, когда число пути будет уверенно собрано в ядре.";
  const expressionLine = expressionNumber
    ? `Имя добавляет внешний стиль проявления: ${expressionNumber.expression}.`
    : "Слой имени станет точнее, когда будут доступны числовые сигналы полного имени.";
  const mind = mercury
    ? `Твой способ думать и говорить читается через ${mercury.ruTitle.toLowerCase()}. Это влияет на то, как ты принимаешь решения, споришь, формулируешь себя и доносишь свою правду до других.`
    : "Способ мышления станет виден, когда в карте будет явно прочитан слой Меркурия.";
  const firstContact = rising
    ? `Первое впечатление о тебе идет через ${rising.ruTitle.toLowerCase()}. Это не вся личность, а именно способ входа: как ты выглядишь для мира до того, как люди узнают тебя глубже.${buildNameFirstContactLine({ personality: personalityNumber, moon })}`
    : "Слой первого контакта станет точнее, когда в карте будет явно считан асцендент.";
  const growthLine = jupiter
    ? `Твоя линия роста идет через ${jupiter.ruTitle.toLowerCase()}. Это показывает, где открываются возможности, через что усиливается удача и какой способ расширения работает для тебя естественнее всего.`
    : "Линия роста станет точнее, когда в карте будет явно прочитан Юпитер.";
  const constraintLine = saturn
    ? `Твоя главная точка внутреннего напряжения идет через ${saturn.ruTitle.toLowerCase()}. Это не приговор, а место, где чаще всего включаются страх, контроль или сомнение, и где поэтому лежит ключевой рост.`
    : "Линия ограничений станет точнее, когда в карте будет явно прочитан Сатурн.";
  const rebellionLine = uranus
    ? `Твой внутренний бунт идет через ${uranus.ruTitle.toLowerCase()}. Это показывает, где ты не можешь жить по старым правилам, где тебя тянет переписать систему и что именно в тебе не выносит фальшивую норму.`
    : "Линия бунта станет точнее, когда в карте будет явно прочитан Уран.";
  const magicLine = neptune
    ? `Тонкая чувствительность, идеализация и творческая магия читаются через ${neptune.ruTitle.toLowerCase()}. Это показывает, где ты вдохновляешься, где улавливаешь то, что не видно сразу, и где легко спутать интуицию с туманом.`
    : "Линия тонкой чувствительности станет точнее, когда в карте будет явно прочитан Нептун.";
  const transformationLine = pluto
    ? `Глубокая внутренняя перестройка идет через ${pluto.ruTitle.toLowerCase()}. Это показывает, через что тебя по-настоящему меняют кризисы, где проходит тема силы и что в тебе уже не может жить в слабой или старой форме.`
    : "Линия глубокой трансформации станет точнее, когда в карте будет явно прочитан Плутон.";
  const manifestationAreas = [
    buildHouseManifestationLine({ planet: "Sun", sign: sunSign, house: planetHouse(natalPreview, "Sun") }),
    buildHouseManifestationLine({ planet: "Moon", sign: moonSign, house: planetHouse(natalPreview, "Moon") }),
    buildHouseManifestationLine({ planet: "Venus", sign: venusSign, house: planetHouse(natalPreview, "Venus") }),
    buildHouseManifestationLine({ planet: "Mars", sign: marsSign, house: planetHouse(natalPreview, "Mars") }),
    buildHouseManifestationLine({ planet: "Mercury", sign: mercurySign, house: planetHouse(natalPreview, "Mercury") }),
    buildHouseManifestationLine({ planet: "Jupiter", sign: jupiterSign, house: planetHouse(natalPreview, "Jupiter") }),
    buildHouseManifestationLine({ planet: "Saturn", sign: saturnSign, house: planetHouse(natalPreview, "Saturn") }),
  ].filter(Boolean) as CombinedPlanetaryProfile["manifestationAreas"];
  const houseFocus = buildHouseFocus(natalPreview);
  const aspectInsights = buildAspectInsights(natalPreview?.aspects?.callouts);
  const aspectSummary = buildAspectSummary(aspectInsights);
  const scenarios = buildScenarioMatches({
    natalPreview,
    sun,
    moon,
    venus,
    mars,
    mercury,
    jupiter,
    saturn,
    uranus,
    neptune,
    pluto,
    aspectInsights,
  });

  return {
    placements: [
      { key: "sun", label: "Sun", signLabel: sunSign },
      { key: "moon", label: "Moon", signLabel: moonSign },
      { key: "venus", label: "Venus", signLabel: venusSign },
      { key: "mars", label: "Mars", signLabel: marsSign },
      ...(mercury ? [{ key: "mercury" as const, label: "Mercury", signLabel: mercurySign }] : []),
      ...(rising ? [{ key: "rising" as const, label: "Rising", signLabel: risingSign }] : []),
      ...(jupiter ? [{ key: "jupiter" as const, label: "Jupiter", signLabel: jupiterSign }] : []),
      ...(saturn ? [{ key: "saturn" as const, label: "Saturn", signLabel: saturnSign }] : []),
      ...(uranus ? [{ key: "uranus" as const, label: "Uranus", signLabel: uranusSign }] : []),
      ...(neptune ? [{ key: "neptune" as const, label: "Neptune", signLabel: neptuneSign }] : []),
      ...(pluto ? [{ key: "pluto" as const, label: "Pluto", signLabel: plutoSign }] : []),
    ],
    recognition,
    explanation,
    tension: tensionWithName,
    strength,
    manifestation,
    risk,
    lifeVector,
    expressionLine,
    mind,
    firstContact,
    growthLine,
    constraintLine,
    rebellionLine,
    magicLine,
    transformationLine,
    manifestationAreas,
    houseFocus,
    aspectInsights,
    aspectSummary,
    scenarios,
  };
}
