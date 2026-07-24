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

export type TodaySkyCard = {
  id: string;
  emoji: string;
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
}): TodaySkyCard[] {
  const cards: TodaySkyCard[] = [];
  const celestial = input.morningRitualData?.celestial_events;
  const lunar = celestial?.lunar_phase;
  const apiSymbols = celestial?.daily_symbols;
  const ritualComplete = Boolean(input.ritualComplete);

  const pushCard = (card: TodaySkyCard) => {
    if (cards.some((c) => c.id === card.id)) return;
    cards.push(card);
  };

  if (lunar?.name) {
    const story = sanitizeRuCopy(
      lunar.guidance ?? lunar.themes,
      "Луна задаёт эмоциональный фон — замечай, что сегодня становится заметнее.",
    );
    pushCard({
      id: "moon",
      emoji: "🌙",
      label: "Луна",
      title: lunar.name,
      story: input.registry.claim(story) ?? story,
    });
  }

  const mainTransit = celestial?.personal_transits?.[0];
  if (mainTransit?.title && mainTransit.story_ru) {
    pushCard({
      id: "personal-transit",
      emoji: "✨",
      label: "Твой транзит",
      title: mainTransit.title,
      story: input.registry.claim(mainTransit.story_ru) ?? mainTransit.story_ru,
    });
  }

  const mainAspect = celestial?.sky_aspects?.[0];
  if (mainAspect?.title && mainAspect.story_ru) {
    pushCard({
      id: "sky-aspect",
      emoji: "⭐",
      label: "Аспект дня",
      title: mainAspect.title,
      story: input.registry.claim(mainAspect.story_ru) ?? mainAspect.story_ru,
    });
  }

  const retro = celestial?.retrogrades?.[0];
  if (retro?.planet_ru && retro.story_ru) {
    pushCard({
      id: `retro-${retro.planet ?? "planet"}`,
      emoji: "↩️",
      label: "Ретроград",
      title: retro.planet_ru,
      story: input.registry.claim(retro.story_ru) ?? retro.story_ru,
    });
  }

  const ingress = celestial?.ingresses?.[0];
  if (ingress?.planet_ru && ingress?.story_ru) {
    pushCard({
      id: "ingress",
      emoji: "♈",
      label: "Переход",
      title: `${ingress.planet_ru} → ${ingress.sign_ru ?? "новый знак"}`,
      story: input.registry.claim(ingress.story_ru) ?? ingress.story_ru,
    });
  }

  if (input.sunSignLabel) {
    pushCard({
      id: "sun",
      emoji: "☀️",
      label: "Солнце",
      title: input.sunSignLabel,
      story:
        input.registry.claim(
          `Солнце в ${input.sunSignLabel} подсвечивает базовый стиль дня — как ты естественно реагируешь на давление и неопределённость.`,
        ) ??
        `Солнце в ${input.sunSignLabel} задаёт базовый тон реакций на день.`,
    });
  }

  const headline = input.morningRitualData?.daily_horoscope?.headline?.trim();
  if (headline && isRuUserFacingText(headline) && headline.length >= 16) {
    pushCard({
      id: "day-axis",
      emoji: "📡",
      label: "Фон дня",
      title: "Главный акцент",
      story: input.registry.claim(headline) ?? headline,
    });
  }

  if (ritualComplete && input.cardName && input.cardId != null) {
    const card = getTodayTarotCardRu(input.cardId);
    pushCard({
      id: "tarot",
      emoji: "🎴",
      label: "Карта",
      title: card?.nameRu ?? input.cardName,
      story: card?.focusRu ?? card?.leadRu ?? "Символ дня открывается после ритуала.",
    });
  }

  if (ritualComplete && input.numerologyValue && input.numerologyValue !== "—") {
    pushCard({
      id: "number",
      emoji: "🔢",
      label: "Число",
      title: input.numerologyValue,
      story: NUMBER_RHYTHM_BY_VALUE[input.numerologyValue] ?? "Ритм дня через число откроется после ритуала.",
    });
  }

  const totem = apiSymbols?.totem;
  if (totem?.name && totem.story_ru) {
    pushCard({
      id: "totem",
      emoji: totem.emoji ?? "🐺",
      label: "Тотем",
      title: totem.name,
      story: totem.story_ru,
    });
  }

  const stoneName = apiSymbols?.stone?.name ?? input.stoneLine?.trim();
  if (stoneName) {
    pushCard({
      id: "stone",
      emoji: "💎",
      label: "Камень",
      title: stoneName,
      story: apiSymbols?.stone?.story_ru ?? "Тихий якорь — можно вернуться к нему, когда день ускоряется.",
    });
  }

  const colorName = apiSymbols?.color?.name ?? input.colorLine?.trim();
  if (colorName) {
    const guide = resolveTodayDayColorGuide({ name: colorName, api: apiSymbols?.color });
    pushCard({
      id: "color",
      emoji: "🎨",
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
  });

  const eveningLine = buildEveningLivingLine({
    dayGoal: input.dayGoal ?? null,
    moodId: input.moodId ?? null,
    thesis,
    ritualComplete: input.ritualComplete,
  });

  const ritualUnlockHint = input.ritualComplete
    ? null
    : "Открой карту и число — практика, медитация и аффирмация соберутся под твой день.";

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
