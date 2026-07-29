/**
 * Journey anti-dupe (#6): Act 1 = recognition only; Act 2 = mechanism.
 * Strip or rewrite Act-2 meaning that paraphrases Act-1 recognition text.
 */

function normalize(text: string): string {
  return text
    .toLowerCase()
    .replace(/[«»""„]/g, "")
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function tokenSet(text: string): Set<string> {
  return new Set(
    normalize(text)
      .split(" ")
      .map((t) => t.trim())
      .filter((t) => t.length > 3),
  );
}

/** Jaccard-ish overlap on tokens longer than 3 chars. */
export function textOverlapRatio(a: string, b: string): number {
  const A = tokenSet(a);
  const B = tokenSet(b);
  if (!A.size || !B.size) return 0;
  let inter = 0;
  A.forEach((t) => {
    if (B.has(t)) inter += 1;
  });
  const union = A.size + B.size - inter;
  return union ? inter / union : 0;
}

const MECHANISM_FALLBACK: Record<string, string> = {
  archetype_from_life_path:
    "Имя портрета берётся только из числа пути — не из Солнца и не из стихии.",
  sun: "Механизм проявления силы в портрете — не повтор узнавания.",
  moon: "Механизм внутренней реакции в портрете — не повтор узнавания.",
  asc: "Механизм первого контакта — как считывают снаружи.",
  rising: "Механизм первого контакта — как считывают снаружи.",
  mc: "Механизм публичной роли — след результата.",
  element: "Фон темперамента в портрете; имя архетипа не выбирает.",
  rhythm: "Способ стартовать и держать темп — рядом с именем, не вместо него.",
};

/**
 * If Act-2 meaning overlaps Act-1 recognition (or identity kitchen text),
 * replace with a short mechanism-only line so the fact stays once.
 */
export function applyAct2AntiDupeMeaning(input: {
  meaning: string;
  anchorId: string;
  recognitionLine?: string | null;
  identityCore?: string | null;
  overlapThreshold?: number;
}): string {
  const meaning = input.meaning.trim();
  if (!meaning) return MECHANISM_FALLBACK[input.anchorId] || MECHANISM_FALLBACK.sun;
  const threshold = input.overlapThreshold ?? 0.42;
  const banned = [input.recognitionLine, input.identityCore]
    .map((s) => String(s || "").trim())
    .filter((s) => s.length > 12);

  for (const ban of banned) {
    if (normalize(meaning) === normalize(ban)) {
      return MECHANISM_FALLBACK[input.anchorId] || MECHANISM_FALLBACK.sun;
    }
    if (textOverlapRatio(meaning, ban) >= threshold) {
      return MECHANISM_FALLBACK[input.anchorId] || MECHANISM_FALLBACK.sun;
    }
  }
  return meaning;
}
