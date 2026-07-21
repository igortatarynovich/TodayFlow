import type { NatalChartPreview } from "@/components/profile/profilePanelTypes";
import type { ProfileLifeSphere } from "@/components/profile/ProfileLifeSection";
import type { CoreProfile } from "@/lib/types";
import type { PlanetInSignEntry } from "@/lib/zodiacKnowledge";
import {
  getJupiterInSignEntry,
  getMarsInSignEntry,
  getMercuryInSignEntry,
  getMoonInSignEntry,
  getPlutoInSignEntry,
  getSaturnInSignEntry,
  getSunInSignEntry,
  getVenusInSignEntry,
} from "@/lib/zodiacKnowledge";
import { getPlanetSignId } from "./buildProfilePlanetaryData";
import { isProfilePortraitForming, PROFILE_PORTRAIT_FORMING_MESSAGE } from "./profilePortraitForming";
import { profileContractMatchesLocale } from "./profileCopySafety";
import { withLifeSphereHowFrame } from "./profileSphereCopy";

/** Chrome labels only — not user-facing portrait copy. */
const SPHERE_CHROME: Record<string, { title: string; accent: string }> = {
  love: { title: "Любовь", accent: "#d16a8d" },
  sex: { title: "Секс и сексуальность", accent: "#b45309" },
  money: { title: "Деньги", accent: "#8a6f49" },
  work: { title: "Работа и реализация", accent: "#6d5bd0" },
  family: { title: "Семья и дом", accent: "#0f9d7a" },
  kids: { title: "Дети и родительство", accent: "#0ea5e9" },
  body: { title: "Тело и энергия", accent: "#16a34a" },
  friends: { title: "Дружба и окружение", accent: "#a855f7" },
  decisions: { title: "Решения и дисциплина", accent: "#64748b" },
};

const HOW_MAX = 520;

/** Строка по интерпретации дома из превью карты (мульти-элементные сферы в профиле). */
export function chartHouseNarrativeLine(preview: NatalChartPreview | null, houseNum: number): string | null {
  const houses = preview?.interpretations?.houses;
  if (!houses || typeof houses !== "object") return null;
  const rec = houses as Record<string, { theme?: string; description?: string } | undefined>;
  const h = rec[String(houseNum)];
  if (!h) return null;
  const theme = (h.theme || "").trim();
  const desc = (h.description || "").trim();
  if (theme && desc) return `${theme}: ${desc}`.slice(0, 320);
  return desc || theme || null;
}

/** Portrait-layer slice: description only (PM-1 — no house theme label in sphere how). */
export function chartHousePortraitLine(preview: NatalChartPreview | null, houseNum: number): string | null {
  const houses = preview?.interpretations?.houses;
  if (!houses || typeof houses !== "object") return null;
  const rec = houses as Record<string, { description?: string } | undefined>;
  const desc = rec[String(houseNum)]?.description?.trim();
  return desc ? desc.slice(0, 320) : null;
}

function joinHow(pieces: Array<string | null | undefined>): string | null {
  const j = pieces.map((p) => (p || "").trim()).filter(Boolean).join(" ").trim();
  if (!j) return null;
  return j.length > HOW_MAX ? `${j.slice(0, HOW_MAX - 1)}…` : j;
}

function sphereHow(apiLine: string | undefined, defaultParagraph: string, chart: string | null, sphereId: string): string {
  // Live LLM/API copy wins; chart is enrichment only when portrait text is absent.
  const api = (apiLine || "").trim();
  if (api) return withLifeSphereHowFrame(sphereId, api);
  if (chart) return withLifeSphereHowFrame(sphereId, chart);
  return withLifeSphereHowFrame(sphereId, defaultParagraph);
}

export type BuildProfileLifeSpheresFromChartInput = {
  preview: NatalChartPreview | null;
  love: string;
  career: string;
  money: string;
  family: string;
  /** Из `interpretation.life_areas` (core profile), если бэкенд отдал. */
  sex?: string;
  sexPracticalTips?: string[];
  kids?: string;
  body?: string;
  friends?: string;
  decisions?: string;
  sunLine: string;
  moonLine: string;
  venusLine: string;
  marsLine: string;
  mercuryLine: string;
  saturnLine: string;
  jupiterLine: string;
  plutoLine: string;
};

const DEFAULTS = {
  love: "Здесь видно, как ты входишь в близость, где тебе нужна ясность, а где связь начинает забирать слишком много сил.",
  career: "Этот слой показывает, в какой роли ты становишься заметной, на что реально можно опереться в работе и где не стоит жить только в режиме обслуживания чужих задач.",
  money: "Через этот слой читается не только тема денег, но и чувство ценности себя, устойчивости и того, на чём тебе безопасно строить рост.",
  family: "Здесь видно, что для тебя значит дом, откуда идёт внутреннее восстановление и какие форматы близости дают опору, а не перегруз.",
  kids: "Если тема актуальна, она проявится в сфере дома и ответственности; иначе блок остаётся нейтральным якорем.",
  bodyMoonOnly: "Когда Луна в карте стабильна, здесь появится конкретика про сон, накопление и срывы.",
  friends: "Когда Меркурий в карте читается устойчиво, здесь появится срез дружбы и сети поддержки.",
  decisions: "Сатурн в карте покажет, где ты взрослеешь через структуру и честные ограничения.",
};

/**
 * Жизненные сферы профиля: при наличии срезов карты `how` собирается из нескольких домов/планет (PM-1),
 * иначе — из API `interpretation.life_areas` или дефолтного абзаца.
 */
function planetNarrativeLine(label: string, entry?: PlanetInSignEntry | null): string {
  const bullet = entry?.bullets?.[0]?.trim();
  if (!bullet) return "";
  return `${label}: ${bullet}`;
}

type ContractSphere = NonNullable<NonNullable<CoreProfile["profile_contract_v1"]>["life_spheres"]>[string];

function applyContractSphereOverlay(
  spheres: ProfileLifeSphere[],
  contractSpheres: NonNullable<CoreProfile["profile_contract_v1"]>["life_spheres"] | undefined,
): ProfileLifeSphere[] {
  if (!contractSpheres || typeof contractSpheres !== "object") return spheres;
  return spheres.map((sphere) => {
    const live = contractSpheres[sphere.id] as ContractSphere | undefined;
    if (!live || typeof live !== "object") return sphere;
    const how = (live.how || "").trim();
    const need = (live.need || "").trim();
    const risk = (live.risk || "").trim();
    const turnsOn = (live.turns_on || "").trim();
    const turnsOff = (live.turns_off || "").trim();
    const helps = (live.helps || "").trim();
    return {
      ...sphere,
      how: how ? withLifeSphereHowFrame(sphere.id, how) : sphere.how,
      need: need || sphere.need,
      risk: risk || sphere.risk,
      turnsOn: turnsOn || sphere.turnsOn,
      turnsOff: turnsOff || sphere.turnsOff,
      helps: helps || sphere.helps,
    };
  });
}

function buildSpheresFromContractOnly(
  contractSpheres: NonNullable<CoreProfile["profile_contract_v1"]>["life_spheres"],
): ProfileLifeSphere[] {
  const out: ProfileLifeSphere[] = [];
  for (const [id, chrome] of Object.entries(SPHERE_CHROME)) {
    const live = contractSpheres?.[id];
    if (!live || typeof live !== "object") continue;
    const how = (live.how || "").trim();
    const need = (live.need || "").trim();
    const risk = (live.risk || "").trim();
    const turnsOn = (live.turns_on || "").trim();
    const turnsOff = (live.turns_off || "").trim();
    const helps = (live.helps || "").trim();
    if (!how || !need || !risk || !turnsOn || !turnsOff || !helps) continue;
    out.push({
      id,
      title: chrome.title,
      accent: chrome.accent,
      how: withLifeSphereHowFrame(id, how),
      need,
      risk,
      turnsOn,
      turnsOff,
      helps,
      inSystem: "",
    });
  }
  return out;
}

/**
 * Life spheres for Profile V2.
 * Ready portrait → only LLM contract spheres (no chart/template silent fill).
 * Forming/partial → empty list; UI shows forming state.
 */
export function buildProfileLifeSpheresFromProfileData(
  preview: NatalChartPreview | null,
  core: CoreProfile | null,
): ProfileLifeSphere[] {
  void preview;
  if (isProfilePortraitForming(core)) {
    return [];
  }
  const contract = core?.profile_contract_v1;
  // Wrong-language portrait (e.g. EN contract on RU UI) → RU chart/template spheres, not English LLM.
  if (!profileContractMatchesLocale(contract)) {
    const withoutContract = core ? { ...core, profile_contract_v1: undefined } : null;
    return buildProfileLifeSpheresFromProfileDataLegacy(preview, withoutContract);
  }
  const contractSpheres = contract?.life_spheres;
  if (!contractSpheres || typeof contractSpheres !== "object") {
    return [];
  }
  const fromContract = buildSpheresFromContractOnly(contractSpheres);
  if (fromContract.length >= 9) {
    return fromContract;
  }
  // Incomplete contract → do not mix with hardcoded DEFAULTS.
  return [];
}

/** @deprecated chart/template path kept for legacy tests only — not used by Profile V2. */
export function buildProfileLifeSpheresFromProfileDataLegacy(
  preview: NatalChartPreview | null,
  core: CoreProfile | null,
): ProfileLifeSphere[] {
  const la = core?.interpretation?.life_areas;
  const contractSpheres = core?.profile_contract_v1?.life_spheres;
  const sun = getSunInSignEntry(getPlanetSignId(preview, "Sun", core?.astro?.sun_sign));
  const moon = getMoonInSignEntry(getPlanetSignId(preview, "Moon"));
  const venus = getVenusInSignEntry(getPlanetSignId(preview, "Venus"));
  const mars = getMarsInSignEntry(getPlanetSignId(preview, "Mars"));
  const mercury = getMercuryInSignEntry(getPlanetSignId(preview, "Mercury"));
  const saturn = getSaturnInSignEntry(getPlanetSignId(preview, "Saturn"));
  const jupiter = getJupiterInSignEntry(getPlanetSignId(preview, "Jupiter"));
  const pluto = getPlutoInSignEntry(getPlanetSignId(preview, "Pluto"));

  const base = buildProfileLifeSpheresFromChart({
    preview,
    love: (contractSpheres?.love?.how || la?.love || "").trim(),
    career: (contractSpheres?.work?.how || la?.career || "").trim(),
    money: (contractSpheres?.money?.how || la?.money || "").trim(),
    family: (contractSpheres?.family?.how || la?.family || "").trim(),
    sex: contractSpheres?.sex?.how || la?.sex,
    sexPracticalTips: core?.interpretation?.sex_practical_tips,
    kids: contractSpheres?.kids?.how || la?.kids,
    body: contractSpheres?.body?.how || la?.body,
    friends: contractSpheres?.friends?.how || la?.friends,
    decisions: contractSpheres?.decisions?.how || la?.decisions,
    sunLine: planetNarrativeLine("Солнце", sun),
    moonLine: planetNarrativeLine("Луна", moon),
    venusLine: planetNarrativeLine("Венера", venus),
    marsLine: planetNarrativeLine("Марс", mars),
    mercuryLine: planetNarrativeLine("Меркурий", mercury),
    saturnLine: planetNarrativeLine("Сатурн", saturn),
    jupiterLine: planetNarrativeLine("Юпитер", jupiter),
    plutoLine: planetNarrativeLine("Плутон", pluto),
  });

  return applyContractSphereOverlay(base, contractSpheres);
}

export { PROFILE_PORTRAIT_FORMING_MESSAGE };

export function buildProfileLifeSpheresFromChart(input: BuildProfileLifeSpheresFromChartInput): ProfileLifeSphere[] {
  const h = (n: number) => chartHousePortraitLine(input.preview, n);
  const { moonLine, venusLine, marsLine, mercuryLine, saturnLine, sunLine, jupiterLine, plutoLine } = input;

  const sexChart = joinHow([h(8), plutoLine, venusLine, marsLine]);
  const sexPlanetaryFallback =
    venusLine && marsLine ? `${venusLine} ${marsLine}`.trim() : venusLine || marsLine || "";
  const sexDefault =
    sexPlanetaryFallback ||
    "Когда в карте стабильно видны Венера и Марс, здесь появится прямой разбор желания, темпа в сексе и телесных границ.";
  const sexCore = sphereHow(input.sex, sexDefault, sexChart, "sex");
  const sexTips = (input.sexPracticalTips || []).filter((t) => t.trim());

  const loveHow = sphereHow(input.love, DEFAULTS.love, joinHow([h(7), venusLine, moonLine]), "love");
  const moneyHow = sphereHow(input.money, DEFAULTS.money, joinHow([h(2), h(8), jupiterLine, saturnLine]), "money");
  const workHow = sphereHow(input.career, DEFAULTS.career, joinHow([h(10), sunLine, saturnLine]), "work");
  const familyHow = sphereHow(input.family, DEFAULTS.family, joinHow([h(4), moonLine]), "family");
  const kidsHow = sphereHow(input.kids, DEFAULTS.kids, joinHow([h(5), moonLine]), "kids");
  const bodyChart = joinHow([h(6), marsLine, moonLine, saturnLine]);
  const bodyApi = (input.body || "").trim();
  const bodyHow = bodyChart
    ? withLifeSphereHowFrame("body", bodyChart)
    : bodyApi
      ? withLifeSphereHowFrame("body", bodyApi)
      : (moonLine || "").trim()
        ? withLifeSphereHowFrame("body", `эмоциональный фон и восстановление сильнее всего читаются через Луну: ${moonLine.trim()}`)
        : withLifeSphereHowFrame("body", DEFAULTS.bodyMoonOnly);
  const friendsHow = sphereHow(input.friends, DEFAULTS.friends, joinHow([h(11), mercuryLine]), "friends");
  const decisionsHow = sphereHow(input.decisions, DEFAULTS.decisions, joinHow([h(9), saturnLine, mercuryLine]), "decisions");

  return [
    {
      id: "love",
      title: "Любовь",
      accent: "#d16a8d",
      how: loveHow,
      need: "Ясность, честный контакт и право на свои чувства без обесценивания.",
      risk: "Смешивать близость с контролем или жить в ожидании, что другой «должен угадать».",
      turnsOn: "Спокойные разговоры, совпадение по смыслу, мягкая устойчивость партнёра.",
      turnsOff: "Пассивная агрессия, обесценивание, хаотичные послания без действия.",
      helps: "Короткие договорённости и один честный шаг за раз — не «про всё сразу».",
      inSystem: "В «Я сегодня» и подсказках — границы; в Совместимости — стиль близости. На карте: 7 дом, Венера, Луна.",
    },
    {
      id: "sex",
      title: "Секс и сексуальность",
      accent: "#b45309",
      how: sexCore,
      need: "Право хотеть и говорить о сексе прямо: темп, инициатива, телесная безопасность и эмоциональная связь в одном разговоре.",
      risk: "Замалчивание желания; смешение возбуждения с тревогой; контроль и проверки вместо контакта.",
      turnsOn: "Глубина, внимание к телу, устойчивый интерес и уважение к «нет».",
      turnsOff: "Давление, обесценивание желания, непредсказуемость границ.",
      helps: "Короткие прямые фразы о том, чего хочешь сейчас; один безопасный шаг, а не игра в догадки.",
      practicalTips:
        sexTips.length > 0
          ? sexTips
          : [
              "Если хочешь, но стесняешься — начни с одной прямой фразы о темпе, а не с «намека» телом без слов.",
              "Поза на боку с зрительным контактом часто снижает давление, когда важны и страсть, и чувство безопасности.",
              "После отказа партнёра не проверяй «ещё раз» в тот же вечер — спроси, когда вернуться к теме.",
            ],
      inSystem: "Подсказки и Совместимость; на карте: 8 дом, Плутон, Венера, Марс.",
    },
    {
      id: "money",
      title: "Деньги",
      accent: "#8a6f49",
      how: moneyHow,
      need: "Понятные правила ценности времени и ощущение, что ресурс не «утекает» незаметно.",
      risk: "Склонность к импульсу или, наоборот, к постоянному ужесточению контроля.",
      turnsOn: "Простые цифры, малые регулярные шаги, честный учёт без морализаторства.",
      turnsOff: "Сравнение с другими, стыд за запросы, хаос во взаиморасчётах.",
      helps: "Один финансовый фокус на неделю и фиксация «что сработало».",
      inSystem: "«Я сегодня» и подсказки; на карте: 2 и 8 дома, Юпитер, Сатурн.",
    },
    {
      id: "work",
      title: "Работа и реализация",
      accent: "#6d5bd0",
      how: workHow,
      need: "Роль, где виден смысл, и понятный критерий «что считается достаточно хорошо».",
      risk: "Раствориться в задачах других или гнаться за статусом без опоры на здоровье.",
      turnsOn: "Ясная постановка задач, обратная связь и возможность доводить до конца.",
      turnsOff: "Размытые ожидания, вечная срочность, отсутствие восстановления.",
      helps: "Один главный результат в день и защищённые окна без созвонов.",
      inSystem: "«Я сегодня» и подсказки; на карте: 10 дом, Солнце, Сатурн.",
    },
    {
      id: "family",
      title: "Семья и дом",
      accent: "#0f9d7a",
      how: familyHow,
      need: "Базовое чувство безопасности и предсказуемости, чтобы отдыхать, а не только «держать всё».",
      risk: "Слияние с чужими эмоциями и чувство вины за свои границы.",
      turnsOn: "Тёплый быт без лишней суеты, честные распределения обязанностей.",
      turnsOff: "Недосказанность, скрытые ожидания, хронический аврал.",
      helps: "Одна договорённость на неделю и короткие чек-ины «как мы сейчас».",
      inSystem: "«Я сегодня» и Совместимость; на карте: 4 дом, Луна.",
    },
    {
      id: "kids",
      title: "Дети и родительство",
      accent: "#0ea5e9",
      how: kidsHow,
      need: "Понятный ритм заботы без постоянного чувства вины.",
      risk: "Перекладывать на себя всё или, наоборот, отстраняться от эмоционального контакта.",
      turnsOn: "Малые ритуалы, последовательность, юмор и опора на партнёра/сеть.",
      turnsOff: "Сравнение с «идеальными» семьями, хаос без границ.",
      helps: "Один устойчивый ритуал и реалистичный план на день.",
      inSystem: "Подсказки и Совместимость; на карте: 5 дом, Луна.",
    },
    {
      id: "body",
      title: "Тело и энергия",
      accent: "#16a34a",
      how: bodyHow,
      need: "Регулярный сон, еда без крайностей и честный сигнал усталости.",
      risk: "Игнорировать усталость до срыва или лечить тревогу только активностью.",
      turnsOn: "Мягкий режим, прогулки, вода, предсказуемый вечер.",
      turnsOff: "Нерегулярный сон, перегруз стимулами, стыд за отдых.",
      helps: "Один якорь тела в день (сон / еда / движение) без идеала.",
      inSystem: "«Я сегодня» и Практики; на карте: 6 дом, Марс, Луна, Сатурн.",
    },
    {
      id: "friends",
      title: "Дружба и окружение",
      accent: "#a855f7",
      how: friendsHow,
      need: "Люди, с которыми можно быть собой без постоянного объяснения.",
      risk: "Либо замкнутость, либо поверхностный круг, который не держит в трудный момент.",
      turnsOn: "Малые группы, общие интересы, уважение к границам.",
      turnsOff: "Сплетни, пассивная агрессия, вечное «надо» в соцсетях.",
      helps: "Один осознанный контакт в неделю вместо размытого «надо всем ответить».",
      inSystem: "Подсказки; на карте: 11 дом, Меркурий.",
    },
    {
      id: "decisions",
      title: "Решения и дисциплина",
      accent: "#64748b",
      how: decisionsHow,
      need: "Понятные правила и право на паузу перед обязательством.",
      risk: "Жёсткий самоконтроль или откладывание до паники.",
      turnsOn: "Малые дедлайны, чек-листы на один шаг, внешняя подотчётность.",
      turnsOff: "Размытые цели, многозадачность, вечное «потом».",
      helps: "Правило «один следующий шаг» и фиксация результата в конце дня.",
      inSystem: "«Я сегодня», Практики и подсказки; на карте: 9 дом, Сатурн, Меркурий.",
    },
  ];
}
