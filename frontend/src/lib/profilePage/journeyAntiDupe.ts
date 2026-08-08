/**
 * Journey anti-dupe: Act 1 = recognition; Act 2 = other facts/meanings.
 * Never invent mechanism-explaining fallbacks («как устроено имя/ASC»).
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

/** Person-facing fact lines only — no product/engine how-it-works copy. */
const FACT_FALLBACK: Record<string, string> = {
  archetype_from_life_path: "Число пути — опора имени в портрете.",
  life_path: "Число пути — опора имени в портрете.",
  sun: "Солнце окрашивает, как ты проявляешь силу в мире.",
  moon: "Луна окрашивает, как ты чувствуешь и восстанавливаешься.",
  asc: "В первом контакте тебя считывают по темпу и дистанции.",
  rising: "В первом контакте тебя считывают по темпу и дистанции.",
  mc: "Публичная роль — след, по которому судят о результате.",
  element: "Стихия Солнца окрашивает темперамент.",
  rhythm: "Ритм развития — как ты стартуешь и держишь темп.",
};

/**
 * If Act-2 meaning overlaps Act-1 recognition, replace with a short fact line
 * so the same story is not printed twice.
 */
export function applyAct2AntiDupeMeaning(input: {
  meaning: string;
  anchorId: string;
  recognitionLine?: string | null;
  identityCore?: string | null;
  overlapThreshold?: number;
}): string {
  const meaning = input.meaning.trim();
  const id = input.anchorId.toLowerCase();
  const fallback = FACT_FALLBACK[id] || FACT_FALLBACK.sun;
  if (!meaning) return fallback;
  const threshold = input.overlapThreshold ?? 0.42;
  const banned = [input.recognitionLine, input.identityCore]
    .map((s) => String(s || "").trim())
    .filter((s) => s.length > 12);

  for (const ban of banned) {
    if (normalize(meaning) === normalize(ban)) return fallback;
    if (textOverlapRatio(meaning, ban) >= threshold) return fallback;
  }
  return meaning;
}
