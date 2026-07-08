/** Sphere copy framing — portrait layers, not natal house summaries (PM-1). */

export function withRelationshipFrame(text: string): string {
  const t = text.trim();
  if (!t) return t;
  if (/^(в отношениях|в близости|в любви|когда рядом|ты в отношениях)/i.test(t)) return t;
  const body = t.charAt(0).toLowerCase() + t.slice(1);
  return `В отношениях ${body}`;
}

export function withRealizationFrame(text: string): string {
  const t = text.trim();
  if (!t) return t;
  if (/^(в реализации|в работе|в деньгах|в карьере|когда дело|ты в реализации)/i.test(t)) return t;
  const body = t.charAt(0).toLowerCase() + t.slice(1);
  return `В реализации ${body}`;
}

export function withCareerFrame(text: string): string {
  const t = text.trim();
  if (!t) return t;
  if (/^(в работе|в карьере|в реализации|на работе)/i.test(t)) return t;
  const body = t.charAt(0).toLowerCase() + t.slice(1);
  return `В работе ${body}`;
}

export function withHomeFrame(text: string): string {
  const t = text.trim();
  if (!t) return t;
  if (/^(дома|в семье|в доме|когда дом)/i.test(t)) return t;
  const body = t.charAt(0).toLowerCase() + t.slice(1);
  return `Дома ${body}`;
}

export function withBodyFrame(text: string): string {
  const t = text.trim();
  if (!t) return t;
  if (/^(в теле|для тела|тело|энергия)/i.test(t)) return t;
  const body = t.charAt(0).toLowerCase() + t.slice(1);
  return `Для тела ${body}`;
}

export function withIntimacyFrame(text: string): string {
  const t = text.trim();
  if (!t) return t;
  if (/^(в интимности|в сексуальности|сексуально|в сексе)/i.test(t)) return t;
  const body = t.charAt(0).toLowerCase() + t.slice(1);
  return `В сексе ${body}`;
}

/** Strip natal house theme prefix so sphere copy ≠ collapsed house row. */
export function stripHouseThemePrefix(text: string): string {
  const trimmed = text.trim();
  const withoutHouse = trimmed.replace(/(?:^|\s)\d+\s*дом:\s*/gi, " ").replace(/\s+/g, " ").trim();
  return withoutHouse || trimmed;
}

const LIFE_SPHERE_HOW_FRAMES: Partial<Record<string, (text: string) => string>> = {
  love: withRelationshipFrame,
  sex: withIntimacyFrame,
  money: withRealizationFrame,
  work: withCareerFrame,
  family: withHomeFrame,
  body: withBodyFrame,
};

/** Portrait-layer framing for life sphere `how` — never raw house summary. */
export function withLifeSphereHowFrame(sphereId: string, text: string): string {
  const normalized = stripHouseThemePrefix(text);
  const frame = LIFE_SPHERE_HOW_FRAMES[sphereId];
  return frame ? frame(normalized) : normalized;
}

/** Short sphere tags for Quick Map — not raw life-area paragraphs. */
export const PROFILE_SPHERE_THRIVE_TAGS: Record<string, string> = {
  love: "Близость",
  career: "Карьера",
  money: "Реализация",
  sex: "Интимность",
  decisions: "Решения",
};
