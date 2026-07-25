/** Person-facing living labels — never describe pipeline fullness. */

export function livingClosureLabel(state?: string | null): string | null {
  if (state === "stable") return "день чаще собирается";
  if (state === "fragile") return "дню часто не хватает завершения";
  if (state === "building") return "собранность только выстраивается";
  if (state === "mixed") return "часть дней складывается, часть обрывается";
  return null;
}

export function livingClarityLabel(state?: string | null): string | null {
  if (state === "growing") return "решения становятся яснее";
  if (state === "unclear") return "неясность решений повторяется";
  if (state === "mixed") return "ясность и зависание чередуются";
  return null;
}
