/**
 * Убираем из UI ритуала «псевдотексты»: сырые slug'и, метки-рубрики вместо действий,
 * шаблон «Не заходить в линию 'general'» из кэша/старого бэка.
 */
import { isDiscardableMorningFocus } from "@/components/today/todayRitualCopy";

/** Паритет `ritual_cue_sanitize._TOPIC_LABELS_NOT_ACTIONS` (O3). */
export const RU_TOPIC_LABELS_NOT_ACTIONS = new Set([
  "смысл и коммуникация",
  "смысл и коммуникации",
  "смысл и коммуникацию",
  "общий фокус дня",
  "общий фон дня",
  "общение и контакт",
  "смысл дня",
  "контекст дня",
  "рамка дня",
  "общая картина",
  "картина дня",
  "настрой на день",
  "тональность дня",
  "вектор дня",
  "форма дня",
  "сигнал дня",
  "паттерн дня",
]);

const TOPIC_LABELS_NOT_ACTIONS = RU_TOPIC_LABELS_NOT_ACTIONS;

/** O3: заголовок day_layer не должен быть только рубрикой (паритет бэкенда `is_ru_abstract_topic_headline`). */
export function isRuAbstractTopicHeadline(text: string | null | undefined): boolean {
  const t = String(text ?? "")
    .trim()
    .toLowerCase();
  if (!t) return true;
  return TOPIC_LABELS_NOT_ACTIONS.has(t);
}

const SLUG_TOPIC_JUNK = new Set([
  "general",
  "overall",
  "dialogue",
  "communication",
  "mixed",
  "none",
  "other",
  "default",
]);

const SLUG_TO_RU: Record<string, string> = {
  general: "общий фон дня",
  love: "любовь и близость",
  relations: "отношения",
  career: "работа и карьера",
  work: "работа и карьера",
  money: "деньги и границы",
  family: "семья и дом",
  home: "семья и дом",
  body: "тело и восстановление",
  health: "тело и восстановление",
  dialogue: "общение и контакт",
  communication: "общение и контакт",
  decision: "решение, которое надо принять",
  identity: "линия про себя",
  self: "линия про себя",
};

/** Паритет `day_narrative_brief_v0` / `ritual_cue_sanitize._HEAD_TOPIC_SLUG_RU` (O5). */
const HEAD_TOPIC_SLUG_RU: Record<string, string> = {
  general: "общий фон дня",
  body: "тело и энергия",
  money: "деньги",
  dialogue: "общение и контакт",
  family: "семья и дом",
  career: "работа и дела",
  love: "близость и отношения",
};

/** Паритет `day_narrative_brief_v0._MOOD_ID_RU` / `ritual_cue_sanitize._MOOD_SLUG_TO_RU` (O5). */
const MOOD_SLUG_RU: Record<string, string> = {
  calm: "спокойно",
  anxious: "тревожно",
  tired: "устало",
  driven: "в драйве",
  irritated: "раздражённо",
  other: "другое",
  motivated: "в драйве",
  confused: "неясно",
  quiet_wish: "хочется тишины",
  move_wish: "хочется движения",
  heavy: "тяжело",
  hopeful: "с надеждой",
  distant: "на дистанции",
};

const QUOTED_SERVICE_SLUG_TO_RU: Record<string, string> = {
  ...SLUG_TO_RU,
  ...HEAD_TOPIC_SLUG_RU,
  ...MOOD_SLUG_RU,
};

const QUOTED_EN_SERVICE_SLUG_RE = /(?:['"]|«)([a-z][a-z0-9_]{0,31})(?:['"]|»)/gi;

/** O5: в RU-тексте не показываем сырые 'tired' / 'general' в кавычках. */
export function replaceQuotedEnSlugsForRuDisplay(text: string | null | undefined): string {
  const raw = String(text ?? "").trim();
  if (!raw) return "";
  return raw.replace(QUOTED_EN_SERVICE_SLUG_RE, (full, g1: string) => {
    const slug = String(g1 || "")
      .trim()
      .toLowerCase();
    const label = QUOTED_SERVICE_SLUG_TO_RU[slug];
    return label ? `«${label}»` : full;
  });
}

const DO_NOT_ENTER_CHAOS_RU =
  "Осторожнее, если день начинает скатываться в хаос, резкие реакции и потерю своего ритма — держи одну линию, не хватайся за всё сразу.";

export function humanizeFocusSlugForUi(slug: string): string {
  const k = slug.trim().toLowerCase();
  if (SLUG_TO_RU[k]) return SLUG_TO_RU[k];
  if (/^[a-z][a-z0-9_]{0,22}$/.test(k)) return "узкая тема дня";
  return slug.trim();
}

/** Строка «что делать» не должна быть только рубрикой/темой без прикладного действия. */
export function isGarbageRitualActionCue(line: string | null | undefined): boolean {
  const raw = (line || "").trim();
  if (!raw) return true;
  if (isDiscardableMorningFocus(raw)) return true;
  const t = raw.toLowerCase();
  if (TOPIC_LABELS_NOT_ACTIONS.has(t)) return true;
  if (/^[\s_a-z]+$/.test(t) && t.length <= 32) return true;
  return false;
}

/**
 * Починка кэшированных/старых do_not_enter с кавычками и англ. slug.
 * Если паттерн узнаётся — отдаём одну нормальную фразу без «линии 'general'».
 */
export function repairRitualDoNotEnterLine(raw: string | null | undefined): string {
  const t = replaceQuotedEnSlugsForRuDisplay(raw);
  if (!t) return "";
  const quoted = t.match(/['«]([a-z][a-z0-9_]{0,24})['»]/i);
  if (quoted) {
    const slug = (quoted[1] || "").trim().toLowerCase();
    if (isDiscardableMorningFocus(slug) || SLUG_TOPIC_JUNK.has(slug)) {
      return DO_NOT_ENTER_CHAOS_RU;
    }
    const label = humanizeFocusSlugForUi(quoted[1]);
    return `Осторожнее с темой «${label}», если она начинает проживаться как хаос, резкие реакции и потеря своего ритма.`;
  }
  if (/\bgeneral\b/i.test(t) && /линию|линия/i.test(t)) {
    return DO_NOT_ENTER_CHAOS_RU;
  }
  return t;
}

/** Паритет `ritual_cue_sanitize._LLM_META_NEEDLES` / `strip_llm_meta_commentary` (Python). */
export const LLM_META_NEEDLES: readonly string[] = [
  "не дублирую",
  "не дублируем",
  "я не дублиру",
  "чтобы экран не перегруж",
  "экран не перегружа",
  "карта и число остаются",
  "не дублирую их",
  "не дублируем их",
  "в сводке и в",
  "чтобы не перегруж",
  "чтобы не дублировать",
  "не дублирую информацию",
  "не дублируем информацию",
  "не повторяю блок",
  "не повторяю уже сказанное",
  "как просили в промпте",
  "как указано в задании",
  "в рамках формата ответа",
  "по требованиям к ответу",
  "согласно инструкции для модели",
  "убираю дублирование",
  "исключил дублирование",
  "дублирование с предыдущим",
  "уже было в предыдущем блоке",
  "из предыдущего абзаца",
  "as per the prompt",
  "as instructed, i will not",
  "i won't repeat the",
  "to avoid duplication",
  "avoiding repeating",
  "not repeating the card",
  "not repeating the number",
];

/** Убираем предложения с мета-комментарием модели (не пользовательский смысл дня). */
export function stripLlmMetaCommentary(text: string | null | undefined): string {
  const raw = String(text ?? "").trim();
  if (!raw) return "";
  const low = raw.toLowerCase();
  if (!LLM_META_NEEDLES.some((n) => low.includes(n))) return raw;
  const parts = raw.split(/(?<=[.!?])\s+/);
  const kept = parts
    .map((p) => p.trim())
    .filter((pl) => pl.length > 0 && !LLM_META_NEEDLES.some((n) => pl.toLowerCase().includes(n)));
  return kept.join(" ").trim();
}
