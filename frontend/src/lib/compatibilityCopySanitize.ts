/** Strip social-style hashtag lines and camelCase tag garbage from user-visible compatibility copy. */
const HASHTAG_LINE = /^#[A-Za-z][A-Za-z0-9_]*$/;
const HASHTAG_TOKEN = /(?:^|\s)(#[A-Za-z][A-Za-z0-9_]*)(?=\s|$)/g;

export function stripCompatibilityDisplayGarbage(text: string | null | undefined): string {
  const raw = (text || "").trim();
  if (!raw) return "";

  const lines = raw
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !HASHTAG_LINE.test(line));

  let out = lines.join("\n").replace(HASHTAG_TOKEN, " ").replace(/\s+/g, " ").trim();
  return out;
}

export function filterCompatibilityParagraphs(paragraphs: string[] | null | undefined, max = 6): string[] {
  if (!Array.isArray(paragraphs)) return [];
  const seen = new Set<string>();
  const out: string[] = [];
  for (const paragraph of paragraphs) {
    const cleaned = stripCompatibilityDisplayGarbage(paragraph);
    if (!cleaned) continue;
    const key = cleaned.toLowerCase();
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(cleaned);
    if (out.length >= max) break;
  }
  return out;
}
