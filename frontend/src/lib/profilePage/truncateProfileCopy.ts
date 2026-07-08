/** Короткая версия без «…» — только целые слова или первое предложение. */
export function firstSentence(text: string): string {
  const m = text.trim().match(/^(.+?[.!?])(?:\s|$)/);
  return m ? m[1].trim() : text.trim();
}

export function compactProfileCopy(text: string, maxChars: number): string {
  const t = text.trim();
  if (!t || t.length <= maxChars) return t;

  const one = firstSentence(t);
  if (one.length <= maxChars) return one;

  const words = t.split(/\s+/).filter(Boolean);
  let out = "";
  for (const word of words) {
    const next = out ? `${out} ${word}` : word;
    if (next.length > maxChars) break;
    out = next;
  }
  return out || one.slice(0, maxChars).trim();
}

/** @deprecated use compactProfileCopy — never appends ellipsis */
export function truncateProfileCopy(text: string, maxChars: number): string {
  return compactProfileCopy(text, maxChars);
}
