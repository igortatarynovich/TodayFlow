/**
 * Hard value gate for Today/Profile user-facing copy.
 * Hide system leaks, raw keys, truncated quotes, address mix — never show kitchen text.
 */

const SYSTEM_LEAK_PHRASES = [
  "слой собран",
  "собран слабо",
  "профиль видит",
  "профиль в основном опирается",
  "общий фон дня",
  "при твоём стиле",
  "при твоем стиле",
  "при вашем стиле",
  "портрет звучит",
  "опоры портрета",
  "узнавание в одном",
  "почему портрет",
  "один узел — не",
  "повтор уже назван",
  "всплывает тема",
  "тема «общий",
  'тема "общий',
  "generation_gate",
  "source_depth",
  "eligibility",
  "мы рассчитали",
  "система видит",
  "система знает",
  "недостаточно данных",
  "нам не хватает",
] as const;

const TEXTBOOK_HOUSE_PHRASES = [
  "первый дом отвечает",
  "второй дом отвечает",
  "третий дом отвечает",
  "четвёртый дом отвечает",
  "четвертый дом отвечает",
  "пятый дом отвечает",
  "шестой дом отвечает",
  "седьмой дом отвечает",
  "восьмой дом отвечает",
  "девятый дом отвечает",
  "десятый дом отвечает",
  "одиннадцатый дом отвечает",
  "двенадцатый дом отвечает",
  "дом отвечает за",
] as const;

const RAW_KEY_RE =
  /(?:тема\s+[`«"']([a-z][a-z0-9_]{1,32})[`»"'])|(?:`([a-z][a-z0-9_]{2,32})`)/i;
const TY_RE = /\b(ты|тебе|тебя|тобой|твой|твоя|твоё|твое|твои|твоих|твоим)\b/i;
const VY_RE = /\b(вы|вам|вас|вами|ваш|ваша|ваше|ваши|ваших|вашим)\b/i;

function norm(text: string): string {
  return (text ?? "").replace(/\s+/g, " ").trim();
}

function low(text: string): string {
  return norm(text).toLowerCase().replace(/ё/g, "е");
}

export function findValueGateHits(
  text: string | null | undefined,
  opts?: { allowTextbook?: boolean },
): string[] {
  const raw = norm(text ?? "");
  if (!raw) return [];
  const l = low(raw);
  const hits: string[] = [];

  for (const phrase of SYSTEM_LEAK_PHRASES) {
    if (l.includes(low(phrase))) hits.push(`system_leak:${phrase}`);
  }
  if (!opts?.allowTextbook) {
    for (const phrase of TEXTBOOK_HOUSE_PHRASES) {
      if (l.includes(low(phrase))) hits.push(`textbook:${phrase}`);
    }
  }
  if (RAW_KEY_RE.test(raw)) hits.push("raw_topic_key");

  if (
    (/[«"'].{0,40}(?:\.\.\.|…)/.test(raw) || /(?:\.\.\.|…)\s*$/.test(raw)) &&
    raw.length < 220 &&
    (l.includes("стиль") || l.includes("тема") || l.includes("фон"))
  ) {
    hits.push("truncated_quote");
  }

  if (TY_RE.test(raw) && VY_RE.test(raw)) hits.push("address_mix_ty_vy");

  return hits;
}

/** Return text only if it passes the value gate; otherwise null (hide block). */
export function scrubUserFacingText(
  text: string | null | undefined,
  opts?: { allowTextbook?: boolean },
): string | null {
  const raw = norm(text ?? "");
  if (!raw) return null;
  if (findValueGateHits(raw, opts).length) return null;
  return raw;
}

export function nearDuplicateClaim(a: string, b: string): boolean {
  const x = low(a);
  const y = low(b);
  if (!x || !y) return false;
  if (x === y) return true;
  if (x.length >= 24 && (x.includes(y) || y.includes(x))) return true;
  const aw = new Set(x.match(/[a-zа-яё0-9]{4,}/g) ?? []);
  const bw = y.match(/[a-zа-яё0-9]{4,}/g) ?? [];
  if (!aw.size || !bw.length) return false;
  const overlap = bw.filter((w) => aw.has(w)).length;
  return overlap >= Math.max(3, Math.ceil(bw.length * 0.55));
}
