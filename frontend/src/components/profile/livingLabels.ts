export function livingClosureLabel(state?: string | null): string {
  if (state === "stable") return "день чаще собирается";
  if (state === "fragile") return "дню часто не хватает завершения";
  if (state === "building") return "собранность только выстраивается";
  if (state === "mixed") return "собранность пока неровная";
  return "живой ритм ещё не проявился";
}

export function livingClarityLabel(state?: string | null): string {
  if (state === "growing") return "решения становятся яснее";
  if (state === "unclear") return "неясность решений повторяется";
  if (state === "mixed") return "ясность и зависание чередуются";
  return "слой решений ещё не собран";
}
