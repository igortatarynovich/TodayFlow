/**
 * Day spine — one thesis, distinct facets per block, global dedup.
 * Theme = what · Pulse = why today · Card = symbol · Number = rhythm · Tools = action.
 */

import { getTodayTarotCardRu } from "@/components/today/todayTarotCardsRu";
import type { MorningRitualData } from "@/components/today/todayPageUtils";
import type { TodayContractV1 } from "@/lib/todayContract";
import { isDomainLensPresent } from "@/lib/todayContract";
import { focusTopicLabel, moodLabelRu } from "@/lib/todayDayDialogue";
import { colorGuideSkyStory, resolveTodayDayColorGuide } from "@/lib/todayDayColorGuide";
import { dayStoryHeadline, dayStoryPulseLine, hasAuthoritativeDayStory } from "@/lib/todayContractMapper";
import { isRuUserFacingText, sanitizeRuCopy } from "@/lib/todaySynthesisTextPolicy";
import { redactUnrevealedRitualProse } from "@/lib/todayRitualRevealSanitize";

/** Ready day_scenario nest — Level-1 SoT when present (DAY_SCENARIO_V1). */
export function readyDayScenario(contract: TodayContractV1) {
  const sc = contract.day_story?.day_scenario;
  if (!sc || typeof sc !== "object") return null;
  if (sc.ready === false || sc.runtime_sot === false) return null;
  const shortName = sc.conflict?.short_name?.trim();
  if (!shortName) return null;
  if (!Array.isArray(sc.scenes) || sc.scenes.length < 1) return null;
  return sc;
}

/** Hero conflict from scenario (preferred over registry day_thesis slogan). */
export function scenarioConflictLabel(contract: TodayContractV1): string | null {
  const sc = readyDayScenario(contract);
  const raw = sc?.conflict?.short_name?.trim();
  if (!raw || !isRuUserFacingText(raw)) return null;
  // Heal cached mashed labels: "A или B — пока <fact…>" / calendar glue
  let name = raw.replace(/[.!?]+$/u, "").trim();
  const mashed = name.match(/^(.+?\s+или\s+.+?)\s+[—–-]\s+(?:пока\s+|календарн)/iu);
  if (mashed?.[1]) name = mashed[1].trim();
  if (/\sили\s/iu.test(name) && /\s+[—–-]\s+/.test(name)) {
    const [before, after = ""] = name.split(/\s+[—–-]\s+/);
    if (
      before &&
      /\sили\s/iu.test(before) &&
      (/^пока\s/iu.test(after) || /календарн/iu.test(after) || after.includes("…"))
    ) {
      name = before.trim();
    }
  }
  if (name.includes("…") && /\sили\s/iu.test(name)) {
    const before = name.split(/\s+[—–-]\s+/)[0]?.trim();
    if (before && /\sили\s/iu.test(before)) name = before;
  }
  return name || null;
}

export type TodaySkyIconKey =
  | "moon"
  | "sparkles"
  | "star"
  | "refresh"
  | "compass"
  | "sun"
  | "orbital"
  | "tarot"
  | "hash"
  | "mountain"
  | "gem"
  | "palette";

export type TodaySkyCard = {
  id: string;
  /** Linear icon from design-system (no emoji — consistent across platforms). */
  icon: TodaySkyIconKey;
  label: string;
  title: string;
  story: string;
};

export type TodayDaySpine = {
  thesis: string;
  themeShort: string;
  pulse: string;
  tarotBody: string | null;
  numberBody: string | null;
  skyCards: TodaySkyCard[];
  eveningLine: string;
  ritualUnlockHint: string | null;
};

export class SpineRegistry {
  private seen = new Set<string>();

  private fingerprint(text: string): string {
    return text
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s]/gu, "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 56);
  }

  overlaps(text: string): boolean {
    const fp = this.fingerprint(text);
    if (!fp || fp.length < 10) return false;
    for (const s of Array.from(this.seen)) {
      if (fp.includes(s) || s.includes(fp)) return true;
      const wordsA = new Set(fp.split(" ").filter((w) => w.length > 3));
      const wordsB = new Set(s.split(" ").filter((w) => w.length > 3));
      let shared = 0;
      for (const w of Array.from(wordsA)) if (wordsB.has(w)) shared += 1;
      if (shared >= 3) return true;
    }
    return false;
  }

  claim(text: string): string | null {
    const t = text.replace(/\s+/g, " ").trim();
    if (!t || this.overlaps(t)) return null;
    this.seen.add(this.fingerprint(t));
    return t.endsWith(".") || t.endsWith("?") || t.endsWith("!") ? t : `${t}.`;
  }

  reserve(text: string): void {
    const fp = this.fingerprint(text);
    if (fp) this.seen.add(fp);
  }
}

function stripTodayLead(text: string): string {
  return text.replace(/^сегодня\s+[^.]{0,40}[.:]\s*/i, "").replace(/[.!?]+$/, "").trim();
}

export function buildDayThesis(
  contract: TodayContractV1,
  moodId?: string | null,
  ritualComplete = true,
): string {
  const reveal = { numberRevealed: ritualComplete, tarotRevealed: ritualComplete };
  // C4: scenario conflict is Level-1 SoT; day_thesis is Act III registry projection.
  const scenarioLabel = scenarioConflictLabel(contract);
  if (scenarioLabel) {
    return scenarioLabel.endsWith(".") ? scenarioLabel : `${scenarioLabel}.`;
  }
  const thesisLabel =
    contract.day_story?.day_thesis?.label_ru?.trim() ||
    contract.day_story?.day_thesis?.label?.trim() ||
    contract.day_story?.primary_conflict?.trim() ||
    "";

  if (hasAuthoritativeDayStory(contract)) {
    const themeRaw = contract.day_story?.theme?.trim();
    const theme = themeRaw ? redactUnrevealedRitualProse(themeRaw, reveal) : "";
    if (!ritualComplete && theme && isRuUserFacingText(theme) && theme.length <= 96) {
      return theme;
    }
    const story = contract.day_story?.story?.trim();
    if (story && isRuUserFacingText(story) && ritualComplete) {
      const first = story.split(/(?<=[.!?])\s+/)[0]?.trim();
      if (first && first.length >= 24 && first.length <= 220) {
        return first.endsWith(".") ? first : `${first}.`;
      }
    }
    if (theme && isRuUserFacingText(theme)) {
      return theme.endsWith(".") ? theme : theme;
    }
    const headlineRaw = dayStoryHeadline(contract);
    const headline = headlineRaw ? redactUnrevealedRitualProse(headlineRaw, reveal) : "";
    if (headline && isRuUserFacingText(headline)) {
      return headline.endsWith(".") ? headline : `${headline}.`;
    }
  }

  // Registry day_thesis only when scenario nest is not ready.
  if (thesisLabel && isRuUserFacingText(thesisLabel)) {
    return thesisLabel.endsWith(".") ? thesisLabel : `${thesisLabel}.`;
  }

  const growth = contract.personal_growth.development_point?.trim() ?? "";
  const corpus = `${contract.global_context.period} ${growth}`.toLowerCase();

  if (/ускор|тревог|спеш/i.test(corpus) || moodId === "anxious" || moodId === "overloaded") {
    return "Сегодня выигрывает не тот, кто делает больше, а тот, кто вовремя перестаёт спешить.";
  }
  if (/пауз|останов|жд|повешен/i.test(corpus)) {
    return "Сегодня сила — не в скорости, а в умении выбрать паузу, которая даёт ясность.";
  }
  if (/ясност|наблюд|вниман/i.test(corpus)) {
    return "Сегодня решает не количество дел, а ясность одного выбора.";
  }
  if (/терпен|последователь|ритм/i.test(corpus)) {
    return "Сегодня результат приходит не от рывка, а от ровного темпа, который можно удержать.";
  }

  if (growth && isRuUserFacingText(growth)) {
    const first = growth.split(/(?<=[.!?])\s+/)[0]?.trim();
    if (first && first.length <= 120) {
      return first.endsWith(".") ? first : `${first}.`;
    }
  }

  return "Сегодня важнее один честный шаг, чем десять половинчатых решений.";
}

export function buildThemeShort(contract: TodayContractV1, thesis: string): string {
  const scenarioLabel = scenarioConflictLabel(contract);
  if (scenarioLabel && scenarioLabel.length <= 96) {
    return scenarioLabel;
  }
  const conflict =
    contract.day_story?.day_thesis?.label_ru?.trim() ||
    contract.day_story?.day_thesis?.label?.trim() ||
    contract.day_story?.primary_conflict?.trim();
  if (conflict && isRuUserFacingText(conflict) && conflict.length <= 96) {
    return conflict.replace(/[.!?]+$/, "").trim();
  }
  const anchor = contract.day_story?.headline_anchor?.trim();
  if (anchor && isRuUserFacingText(anchor) && anchor.length <= 96) {
    return anchor.replace(/[.!?]+$/, "").trim();
  }
  const theme = contract.day_story?.theme?.trim();
  if (theme && isRuUserFacingText(theme) && theme.length <= 96) {
    return theme.replace(/[.!?]+$/, "").trim();
  }
  const period = contract.global_context.period.trim();
  const dash = period.split(/\s*[—–]\s+/);
  if (dash.length >= 2) {
    const short = dash.slice(1).join(" ").replace(/[.!?]+$/, "").trim();
    if (short && isRuUserFacingText(short) && short.length <= 72) {
      return short.charAt(0).toUpperCase() + short.slice(1);
    }
  }
  const low = thesis.toLowerCase();
  if (/спеш|ритм|пауз/.test(low)) return "Спокойный ритм без суеты";
  if (/ясност|выбор/.test(low)) return "Ясность и один фокус";
  return "Главная линия дня";
}

function buildPulseFacet(input: {
  contract: TodayContractV1;
  morningRitualData: MorningRitualData | null;
  registry: SpineRegistry;
  ritualComplete: boolean;
}): string {
  const reveal = {
    numberRevealed: input.ritualComplete,
    tarotRevealed: input.ritualComplete,
  };

  if (hasAuthoritativeDayStory(input.contract)) {
    const fromStory = dayStoryPulseLine(input.contract);
    const cleaned = redactUnrevealedRitualProse(fromStory, reveal);
    if (cleaned) {
      const claimed = input.registry.claim(cleaned);
      if (claimed) return claimed;
    }
  }

  const lunar = input.morningRitualData?.celestial_events?.lunar_phase;
  const celestial = input.morningRitualData?.celestial_events;
  const candidates: string[] = [];

  const mainTransit = celestial?.personal_transits?.[0]?.story_ru;
  if (mainTransit && isRuUserFacingText(mainTransit)) {
    candidates.push(`В твоей карте сегодня: ${mainTransit.replace(/[.!?]+$/, "")}.`);
  }

  const mainAspect = celestial?.sky_aspects?.[0]?.story_ru;
  if (mainAspect && isRuUserFacingText(mainAspect)) {
    candidates.push(`На небе сегодня: ${mainAspect.replace(/[.!?]+$/, "")}.`);
  }

  const retro = celestial?.retrogrades?.[0]?.story_ru;
  if (retro && isRuUserFacingText(retro)) {
    candidates.push(retro.endsWith(".") ? retro : `${retro}.`);
  }

  if (lunar?.name) {
    const guidance = sanitizeRuCopy(
      lunar.guidance ?? lunar.themes,
      "день просит внимательности к тому, что обычно остаётся в фоне",
    );
    candidates.push(
      `${lunar.name} сегодня задаёт фон: ${guidance.replace(/[.!?]+$/, "").toLowerCase()}.`,
    );
    if (lunar.next_phase?.name && lunar.next_phase.in_days != null && lunar.next_phase.in_days <= 3) {
      candidates.push(
        `Через ${lunar.next_phase.in_days} дн. фаза сменится на «${lunar.next_phase.name}» — сегодня удобно подвести промежуточный итог.`,
      );
    }
  }

  const spine = input.morningRitualData?.daily_horoscope?.spine;
  const axis = spine?.day_axis?.trim();
  if (axis && isRuUserFacingText(axis) && axis.length >= 20) {
    candidates.push(axis.endsWith(".") ? axis : `${axis}.`);
  }

  for (const id of ["money_work", "relationships", "family"] as const) {
    const domain = input.contract.domains[id];
    if (!isDomainLensPresent(domain)) continue;
    const opp = domain.opportunity?.trim();
    if (!opp || !isRuUserFacingText(opp)) continue;
    const clean = stripTodayLead(opp);
    candidates.push(`На практике это может проявиться так: ${clean.charAt(0).toLowerCase() + clean.slice(1)}.`);
    break;
  }

  if (candidates.length === 0) {
    candidates.push("День складывается в одну линию — без необходимости удерживать всё сразу.");
  }

  const out: string[] = [];
  for (const c of candidates) {
    const claimed = input.registry.claim(c);
    if (claimed) out.push(claimed);
    if (out.length >= 2) break;
  }
  return out.join(" ");
}

const TAROT_SYMBOL_INTRO: Partial<Record<number, string>> = {
  12: "Повешенный редко появляется в дни, когда нужно действовать быстрее. Сегодня он предлагает изменить не ситуацию, а угол зрения.",
  9: "Отшельник приходит, когда внешний шум мешает услышать себя. Он не про изоляцию — про честный разговор с собой.",
  16: "Башня — не про катастрофу, а про момент, когда старая схема больше не держится. Сегодня важнее не спасать конструкцию, а увидеть правду.",
  0: "Шут открывает день, где можно пробовать без обещания идеального результата.",
};

export function buildTarotSymbolFacet(cardId: number, registry: SpineRegistry): string | null {
  const card = getTodayTarotCardRu(cardId);
  if (!card) return null;

  const intro =
    TAROT_SYMBOL_INTRO[cardId] ??
    `${card.nameRu} сегодня — архетип дня: он говорит о другом слое, чем общая тема.`;
  const detail = card.bodyRu?.trim() || card.questionRu;
  const raw = `${intro} ${detail}`.replace(/\s+/g, " ").trim();
  return registry.claim(raw);
}

const NUMBER_RHYTHM_BY_VALUE: Record<string, string> = {
  "1": "Число 1 задаёт ритм инициативы: один первый шаг важнее десяти задуманных.",
  "2": "Число 2 усиливает диалог и баланс — сегодня лучше договориться, чем давить.",
  "3": "Число 3 добавляет лёгкость и связи: идеи раскрываются через разговор и движение.",
  "4": "Число 4 просит структуру: закрепить одну опору надёжнее, чем начать пять новых.",
  "5": "Число 5 приносит смену темпа — гибкость сегодня важнее жёсткого плана.",
  "6": "Число 6 смягчает день: забота и ответственность работают лучше, чем жёсткий контроль.",
  "7": "Число 7 замедляет поверхность: ответы приходят через наблюдение, не через давление.",
  "8": "Число 8 усиливает результат — но только там, где есть ясная договорённость и границы.",
  "9": "Число 9 завершает цикл: полезно закрыть одно, прежде чем открывать новое.",
  "11": "Число 11 обостряет интуицию — доверяй первому честному импульсу, но проверяй его действием.",
  "20": "Число 20 усиливает терпение: важные изменения редко видны сразу, зато сегодня удобно заложить будущий результат.",
  "22": "Число 22 просит масштаб мысли — но реализовать его через один конкретный шаг.",
};

function isWeakNumerologyMeaning(meaning: string | null | undefined): boolean {
  const m = (meaning ?? "").trim();
  if (!m || !isRuUserFacingText(m)) return true;
  if (m.length < 22) return true;
  return /путь жизни|life path|expression|soul urge|personality/i.test(m);
}

export function buildNumberRhythmFacet(
  value: string,
  meaning: string | null,
  registry: SpineRegistry,
): string | null {
  const preset = NUMBER_RHYTHM_BY_VALUE[value.trim()];
  if (preset) return registry.claim(preset);

  if (!isWeakNumerologyMeaning(meaning) && meaning) {
    const m = meaning.replace(/[.!?]+$/, "").trim();
    const line = `Число ${value} сегодня про ритм: ${m.charAt(0).toLowerCase() + m.slice(1)}.`;
    return registry.claim(line);
  }

  return registry.claim(
    `Число ${value} напоминает: большие сдвиги складываются из маленьких решений, которые легко не заметить.`,
  );
}

export function buildSkyInfluenceCards(input: {
  morningRitualData: MorningRitualData | null;
  cardName: string | null;
  cardId: number | null;
  numerologyValue: string | null;
  colorLine?: string | null;
  stoneLine?: string | null;
  sunSignLabel?: string | null;
  registry: SpineRegistry;
  /** Card/number only after ritual — they are the interpretive layer, not the foundation. */
  ritualComplete?: boolean;
  /** Scenario talisman — preferred over morning catalog for color card (B4). */
  scenarioColor?: {
    name?: string | null;
    note?: string | null;
    avoidColor?: string | null;
    avoidWhy?: string | null;
  } | null;
  /** Chorus overlay — how card/number color today's conflict (same day, no rebuild). */
  chorus?: {
    day_card?: { named?: string | null; role?: string | null } | null;
    day_number?: {
      named?: string | null;
      tempo?: string | null;
      for_conflict?: string | null;
    } | null;
  } | null;
}): TodaySkyCard[] {
  const cards: TodaySkyCard[] = [];
  const celestial = input.morningRitualData?.celestial_events;
  const lunar = celestial?.lunar_phase;
  const apiSymbols = celestial?.daily_symbols;
  const ritualComplete = Boolean(input.ritualComplete);
  const pack = celestial?.day_events_pack;

  const pushCard = (card: TodaySkyCard) => {
    if (cards.some((c) => c.id === card.id)) return;
    cards.push(card);
  };

  const iconForKind = (kind: string | undefined): TodaySkyIconKey => {
    const k = (kind || "").toLowerCase();
    if (k.includes("moon") || k.includes("phase") || k.includes("lunar")) return "moon";
    if (k.includes("station") || k.includes("retro")) return "refresh";
    if (k.includes("ingress")) return "compass";
    if (k.includes("aspect")) return "star";
    if (k.includes("solar") || k.includes("seasonal")) return "sun";
    if (k.includes("personal")) return "sparkles";
    return "orbital";
  };

  // Prefer ranked drivers from day_events_pack — one plot, not a fact wall.
  if (pack?.ranked_drivers?.length && pack.events?.length) {
    const byId = new Map((pack.events || []).filter((e) => e?.id).map((e) => [String(e.id), e]));
    for (const did of pack.ranked_drivers.slice(0, 5)) {
      const ev = byId.get(String(did));
      if (!ev?.title_ru && !ev?.fact_ru) continue;
      if (
        String(ev.id || "").startsWith("calendar-doy") ||
        String(ev.kind || "") === "calendar" ||
        /календарн\w*\s+день|\d+-й\s+день\s+года/i.test(String(ev.fact_ru || ev.title_ru || ""))
      ) {
        continue;
      }
      if (cards.length >= 3) break;
      const story = sanitizeRuCopy(
        ev.fact_ru,
        ev.title_ru || "Сигнал дня — держи один главный конфликт.",
      );
      pushCard({
        id: `driver-${ev.id}`,
        icon: iconForKind(ev.kind),
        label: "Драйвер дня",
        title: ev.title_ru || "Сигнал неба",
        story: input.registry.claim(story) ?? story,
      });
    }
  }

  if (cards.length < 2 && lunar?.name) {
    const story = sanitizeRuCopy(
      lunar.guidance ?? lunar.themes,
      "Луна задаёт эмоциональный фон — замечай, что сегодня становится заметнее.",
    );
    pushCard({
      id: "moon",
      icon: "moon",
      label: "Луна",
      title: lunar.name,
      story: input.registry.claim(story) ?? story,
    });
  }

  if (cards.length < 3) {
    const mainTransit = celestial?.personal_transits?.[0];
    if (
      mainTransit?.title &&
      mainTransit.story_ru &&
      !/Firdaria|ZR\s*Fortune|Лоты\s*soft/i.test(mainTransit.story_ru)
    ) {
      pushCard({
        id: "personal-transit",
        icon: "sparkles",
        label: "Твой транзит",
        title: mainTransit.title,
        story: input.registry.claim(mainTransit.story_ru) ?? mainTransit.story_ru,
      });
    }
  }

  if (cards.length < 3) {
    const mainAspect = celestial?.sky_aspects?.[0];
    if (mainAspect?.title && mainAspect.story_ru) {
      pushCard({
        id: "sky-aspect",
        icon: "star",
        label: "Аспект дня",
        title: mainAspect.title,
        story: input.registry.claim(mainAspect.story_ru) ?? mainAspect.story_ru,
      });
    }
  }

  if (cards.length < 3) {
    const retro = celestial?.retrogrades?.[0];
    if (retro?.planet_ru && retro.story_ru) {
      pushCard({
        id: `retro-${retro.planet ?? "planet"}`,
        icon: "refresh",
        label: "Ретроград",
        title: retro.planet_ru,
        story: input.registry.claim(retro.story_ru) ?? retro.story_ru,
      });
    }
  }

  if (cards.length < 3) {
    const ingress = celestial?.ingresses?.[0];
    if (ingress?.planet_ru && ingress?.story_ru) {
      pushCard({
        id: "ingress",
        icon: "compass",
        label: "Переход",
        title: `${ingress.planet_ru} → ${ingress.sign_ru ?? "новый знак"}`,
        story: input.registry.claim(ingress.story_ru) ?? ingress.story_ru,
      });
    }
  }

  if (cards.length < 2 && input.sunSignLabel) {
    pushCard({
      id: "sun",
      icon: "sun",
      label: "Солнце",
      title: input.sunSignLabel,
      story:
        input.registry.claim(
          `Солнце в ${input.sunSignLabel} подсвечивает базовый стиль дня — как ты естественно реагируешь на давление и неопределённость.`,
        ) ??
        `Солнце в ${input.sunSignLabel} задаёт базовый тон реакций на день.`,
    });
  }

  if (cards.length < 2) {
    const headline = input.morningRitualData?.daily_horoscope?.headline?.trim();
    if (headline && isRuUserFacingText(headline) && headline.length >= 16) {
      pushCard({
        id: "day-axis",
        icon: "orbital",
        label: "Фон дня",
        title: "Главный акцент",
        story: input.registry.claim(headline) ?? headline,
      });
    }
  }

  if (ritualComplete && input.cardName && input.cardId != null) {
    const card = getTodayTarotCardRu(input.cardId);
    const chorusRole = input.chorus?.day_card?.role?.trim();
    const story =
      (chorusRole && isRuUserFacingText(chorusRole) ? chorusRole : null) ||
      card?.focusRu ||
      card?.leadRu ||
      "Карта дня окрашивает уже собранный сюжет — не меняет его.";
    pushCard({
      id: "tarot",
      icon: "tarot",
      label: "Карта",
      title: card?.nameRu ?? input.cardName,
      story: input.registry.claim(story) ?? story,
    });
  }

  if (ritualComplete && input.numerologyValue && input.numerologyValue !== "—") {
    const chorusNumber =
      input.chorus?.day_number?.for_conflict?.trim() ||
      input.chorus?.day_number?.tempo?.trim() ||
      null;
    const story =
      (chorusNumber && isRuUserFacingText(chorusNumber) ? chorusNumber : null) ||
      NUMBER_RHYTHM_BY_VALUE[input.numerologyValue] ||
      "Число дня задаёт темп прохождения уже выбранного сюжета.";
    pushCard({
      id: "number",
      icon: "hash",
      label: "Число",
      title: input.numerologyValue,
      story: input.registry.claim(story) ?? story,
    });
  }

  const totem = apiSymbols?.totem;
  if (totem?.name && totem.story_ru) {
    pushCard({
      id: "totem",
      icon: "mountain",
      label: "Тотем",
      title: totem.name,
      story: totem.story_ru,
    });
  }

  const stoneName = apiSymbols?.stone?.name ?? input.stoneLine?.trim();
  if (stoneName) {
    pushCard({
      id: "stone",
      icon: "gem",
      label: "Камень",
      title: stoneName,
      story: apiSymbols?.stone?.story_ru ?? "Тихий якорь — можно вернуться к нему, когда день ускоряется.",
    });
  }

  const colorName =
    input.scenarioColor?.name?.trim() ||
    apiSymbols?.color?.name ||
    input.colorLine?.trim();
  if (colorName) {
    const guide = resolveTodayDayColorGuide({
      name: colorName,
      api: apiSymbols?.color,
      scenario: input.scenarioColor?.name
        ? {
            name: input.scenarioColor.name,
            note: input.scenarioColor.note,
            avoidColor: input.scenarioColor.avoidColor,
            avoidWhy: input.scenarioColor.avoidWhy,
          }
        : null,
    });
    pushCard({
      id: "color",
      icon: "palette",
      label: "Цвет",
      title: colorName,
      story: guide ? colorGuideSkyStory(guide) : apiSymbols?.color?.story_ru ?? "Оттенок, который помогает удержать сегодняшний ритм.",
    });
  }

  return cards.slice(0, 8);
}

export function buildEveningLivingLine(input: {
  dayGoal: string | null;
  moodId: string | null;
  thesis: string;
  ritualComplete: boolean;
}): string {
  if (input.dayGoal) {
    const promise = input.dayGoal.replace(/^сегодня\s+я\s+/i, "").replace(/[.!?]+$/, "");
    return `Утром ты обещал себе: «${promise}». Давай посмотрим, удалось ли сохранить это решение хотя бы в одном важном моменте.`;
  }
  const mood = moodLabelRu(input.moodId);
  if (mood && input.ritualComplete) {
    return `Похоже, сегодня ты входил в день в состоянии «${mood.toLowerCase()}». Осталось понять, помог ли выбранный ритм прожить день так, как хотелось.`;
  }
  return "Перед закрытием дня — один честный взгляд назад: что сегодня оказалось важнее, чем казалось утром?";
}

export function buildTodayDaySpine(input: {
  contract: TodayContractV1;
  morningRitualData: MorningRitualData | null;
  moodId?: string | null;
  dayGoal?: string | null;
  cardId: number | null;
  cardName: string | null;
  numerologyValue: string | null;
  numerologyMeaning: string | null;
  colorLine?: string | null;
  stoneLine?: string | null;
  sunSignLabel?: string | null;
  ritualComplete: boolean;
  tarotPicked?: boolean;
}): TodayDaySpine {
  const registry = new SpineRegistry();
  const thesis = buildDayThesis(input.contract, input.moodId ?? null, input.ritualComplete);
  registry.reserve(thesis);

  const themeShort = buildThemeShort(input.contract, thesis);
  const pulseRaw = buildPulseFacet({
    contract: input.contract,
    morningRitualData: input.morningRitualData,
    registry,
    ritualComplete: input.ritualComplete,
  });
  const pulse = redactUnrevealedRitualProse(pulseRaw, {
    numberRevealed: input.ritualComplete,
    tarotRevealed: input.ritualComplete,
  });

  const showTarot = input.cardId != null && (input.tarotPicked || input.ritualComplete);
  const tarotBody = showTarot ? buildTarotSymbolFacet(input.cardId!, registry) : null;

  const numberBody =
    input.numerologyValue && input.numerologyValue !== "—" && input.ritualComplete
      ? buildNumberRhythmFacet(input.numerologyValue, input.numerologyMeaning, registry)
      : null;

  const talisman = input.contract.day_story?.talisman;
  const skyCards = buildSkyInfluenceCards({
    morningRitualData: input.morningRitualData,
    cardName: input.cardName,
    cardId: input.cardId,
    numerologyValue: input.numerologyValue,
    colorLine: input.colorLine,
    stoneLine: input.stoneLine,
    sunSignLabel: input.sunSignLabel,
    registry,
    ritualComplete: input.ritualComplete,
    scenarioColor: talisman?.color
      ? {
          name: talisman.color,
          note: talisman.note,
          avoidColor: talisman.avoid_color,
          avoidWhy: talisman.avoid_why,
        }
      : null,
    chorus: input.contract.day_story?.interpretive_chorus ?? null,
  });

  const eveningLine = buildEveningLivingLine({
    dayGoal: input.dayGoal ?? null,
    moodId: input.moodId ?? null,
    thesis,
    ritualComplete: input.ritualComplete,
  });

  // When day_scenario is ready, props/affirmations already come from scenes —
  // ritual is complement, not unlock slogan.
  const ritualUnlockHint = null;

  return {
    thesis,
    themeShort,
    pulse,
    tarotBody,
    numberBody,
    skyCards,
    eveningLine,
    ritualUnlockHint,
  };
}
